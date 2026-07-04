import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


from datetime import date, timedelta
from pipeline.generate_orders import generate_orders
from pipeline.bigquery_loader import create_table_if_not_exists, load_orders

def backfill(days =30):
    create_table_if_not_exists()
    today = date.today()

    for i in range(days,0,-1):
        target_date = today -timedelta(days=i)

        if target_date.weekday == 6:
            print(f"Skipping sunday {target_date}")
            continue

        orders = generate_orders(n=80,date=target_date)
        load_orders(orders)

        print(f"loaded {len(orders)} orders for {target_date}")

    print("Backfill complete.")

if __name__ == "__main__":
    backfill(days=30)

