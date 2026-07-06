
import os
import sys
from datetime import date
from datetime import datetime
import pytz 
import time

from pipeline.generate_orders import generate_orders
from pipeline.bigquery_loader import create_table_if_not_exists, load_orders
from reports.report_builder import build_report
from reports.email_sender import send_report


def run_morning(target_date=None):
    """Runs at 9am, generates and saves orders for the day."""
    if target_date is None:
        target_date = date.today()

    print(f"[MORNING] Running order generation for {target_date}...")

    create_table_if_not_exists()
    orders = generate_orders(n=80, date=target_date)

    if not orders:
        print(f"[MORNING] No orders generated for {target_date}. Exiting.")
        return

    load_orders(orders)
    print(f"[MORNING] {len(orders)} orders saved to BigQuery.")


def run_evening(target_date=None):
    """Runs at 6pm, builds report and emails manager."""
    if target_date is None:
        target_date = date.today()

    print(f"[EVENING] Building report for {target_date}...")

    pdf_path = build_report(target_date=target_date)

    if not pdf_path:
        print(f"[EVENING] No report generated for {target_date}. Exiting.")
        return

    send_report(pdf_path, target_date=target_date)
    print(f"[EVENING] Report emailed successfully.")


def wait_until(hour, minute=0):
    """Wait until exact WAT time before executing."""
    wat = pytz.timezone("Africa/Lagos")
    now = datetime.now(wat)
    target = now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    wait_seconds = (target - now).total_seconds()
    if wait_seconds > 0:
        print(f"Waiting {round(wait_seconds/60)} minutes until {hour:02d}:{minute:02d} WAT...")
        time.sleep(wait_seconds)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Doorstep Lagos Pipeline")
    parser.add_argument(
        "job",
        choices=["morning", "evening"],
        help="morning or evening"
    )
    args = parser.parse_args()

    if args.job == "morning":
        wait_until(9, 0) # waits until 9am before executing 
        run_morning()
    elif args.job == "evening":
        wait_until(18, 0) # waits until 6pm before executing 
        run_evening()