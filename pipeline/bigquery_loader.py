import os
from google.cloud import bigquery

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
    os.path.dirname(__file__), "..", "service_account.json"
)
PROJECT_ID = "doorstep-lagos"
DATASET_ID =  "doorstep_lagos"
TABLE_ID = "orders"

def get_client():
    return bigquery.Client(project = PROJECT_ID)

def create_table_if_not_exists():
    client = get_client()
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

    schema = [
        bigquery.SchemaField("order_id", "STRING"),
        bigquery.SchemaField("date", "DATE"),
        bigquery.SchemaField("vehicle", "STRING"),
        bigquery.SchemaField("origin", "STRING"),
        bigquery.SchemaField("destination", "STRING"),
        bigquery.SchemaField("address", "STRING"),
        bigquery.SchemaField("distance_km", "FLOAT"),
        bigquery.SchemaField("traffic", "STRING"),
        bigquery.SchemaField("revenue_ngn", "FLOAT"),
        bigquery.SchemaField("fuel_cost_ngn", "FLOAT"),
        bigquery.SchemaField("gross_profit_ngn", "FLOAT"),
        bigquery.SchemaField("dispatch_time", "TIMESTAMP"),
        bigquery.SchemaField("estimated_delivery_time", "TIMESTAMP"),
        bigquery.SchemaField("eta_minutes", "INTEGER"),
        bigquery.SchemaField("status", "STRING"),
        bigquery.SchemaField("driver", "STRING"),
        bigquery.SchemaField("customer", "STRING"),
        bigquery.SchemaField("phone_number", "STRING"),


    ]
    table = bigquery.Table(table_ref, schema=schema)
    table = client.create_table(table, exists_ok=True)
    print(f"Table {table_ref} ready.")

def load_orders(orders):
    client =get_client()
    table_ref = f"{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}"

    errors = client.insert_rows_json(table_ref, orders)

    if errors:
        print(f"Errors inserting rows: {errors}")
    else:
        print(f"{len(orders)} orders inserted into BigQuery.")

if __name__ == "__main__":
    create_table_if_not_exists()