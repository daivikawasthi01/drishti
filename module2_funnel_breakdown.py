"""Module 2 (Part 2): Purchase Funnel Broken Down by Device and Channel."""

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd
from google.cloud import bigquery

PROJECT_ID = "drishti-daivik-01"

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

FUNNEL_STEPS = [
    ("session_start", "Session Start"),
    ("view_item", "View Item"),
    ("add_to_cart", "Add to Cart"),
    ("begin_checkout", "Begin Checkout"),
    ("add_payment_info", "Add Payment Info"),
    ("purchase", "Purchase"),
]


def get_client():
    return bigquery.Client(project=PROJECT_ID)


def run_query(client, sql_path):
    query = Path(sql_path).read_text()
    return client.query(query).to_dataframe()


def reshape_breakdown(wide_df, group_col):
    records = []
    for _, row in wide_df.iterrows():
        group = row[group_col]
        top_users = int(row[FUNNEL_STEPS[0][0]])
        prev_users = None
        for step_key, label in FUNNEL_STEPS:
            users = int(row[step_key])
            step_conv = 100.0 if prev_users is None else (
                round(users / prev_users * 100, 2) if prev_users else 0.0
            )
            overall_conv = round(users / top_users * 100, 2) if top_users else 0.0
            records.append({
                group_col: group,
                "step": label,
                "users": users,
                "step_conversion_pct": step_conv,
                "overall_conversion_pct": overall_conv,
            })
            prev_users = users
    return pd.DataFrame(records)


def plot_comparison(long_df, group_col, title, output_path):
    fig, ax = plt.subplots(figsize=(9, 5.5))
    step_order = [label for _, label in FUNNEL_STEPS]

    for group, group_df in long_df.groupby(group_col):
        group_df = group_df.set_index("step").loc[step_order]
        ax.plot(step_order, group_df["overall_conversion_pct"], marker="o", label=str(group))

    ax.set_ylabel("% of top-of-funnel users remaining")
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.legend(title=group_col.replace("_", " ").title())
    plt.xticks(rotation=15)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)


def main():
    client = get_client()

    print("Running funnel by device...")
    device_wide = run_query(client, "queries/03_funnel_by_device.sql")
    device_long = reshape_breakdown(device_wide, "device")
    print(device_long.to_string(index=False))
    device_long.to_csv(DATA_DIR / "funnel_by_device.csv", index=False)
    plot_comparison(
        device_long, "device",
        "Purchase Funnel by Device — % of Top-of-Funnel Users Remaining",
        DATA_DIR / "funnel_by_device_chart.png",
    )

    print("\nRunning funnel by channel...")
    channel_wide = run_query(client, "queries/04_funnel_by_channel.sql")
    channel_wide["channel"] = channel_wide["channel"].fillna("(not set)")
    channel_long = reshape_breakdown(channel_wide, "channel")
    print(channel_long.to_string(index=False))
    channel_long.to_csv(DATA_DIR / "funnel_by_channel.csv", index=False)
    plot_comparison(
        channel_long, "channel",
        "Purchase Funnel by Channel — % of Top-of-Funnel Users Remaining",
        DATA_DIR / "funnel_by_channel_chart.png",
    )

    print("\nSaved: data/funnel_by_device.csv, data/funnel_by_device_chart.png")
    print("Saved: data/funnel_by_channel.csv, data/funnel_by_channel_chart.png")


if __name__ == "__main__":
    main()
