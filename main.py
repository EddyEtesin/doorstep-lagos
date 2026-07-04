from datetime import date
from pipeline.generate_orders import generate_orders
from pipeline.bigquery_loader import create_table_if_not_exists,load_orders

def main():
    today = date.today()
    print(f"Running Doorstep Lagos Pipeline for {today}...")

    create_table_if_not_exists()

    orders = generate_orders(n = 80, date = today)

    if not orders:
        print(f"No orders generated {today}...")
        return
    
    load_orders(orders)
    print("Pipeline complete.")


if __name__ == "__main__":
    main()




