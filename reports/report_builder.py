import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import date
from google.cloud import bigquery
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT

gcp_creds = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON")
if gcp_creds:
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        f.write(gcp_creds)
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = f.name
else:
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = os.path.join(
        os.path.dirname(__file__), "..", "service_account.json"
    )
PROJECT_ID = "doorstep-lagos"
DATASET_ID = "doorstep_lagos"
TABLE_ID = "orders"

BRAND_GREEN = colors.black
BRAND_DARK = colors.black
MID_GRAY = colors.HexColor("#888888")


def fetch_daily_data(target_date):
    client = bigquery.Client(project=PROJECT_ID)
    query = f"""
        SELECT * FROM `{PROJECT_ID}.{DATASET_ID}.{TABLE_ID}`
        WHERE date = '{target_date}'
    """
    return list(client.query(query).result())


def build_report(target_date=None):
    if target_date is None:
        target_date = date.today()

    rows = fetch_daily_data(target_date)
    if not rows:
        print(f"No data found for {target_date}")
        return

    # --- Aggregations ---
    total_orders = len(rows)
    delivered = sum(1 for r in rows if r["status"] == "delivered")
    failed = sum(1 for r in rows if r["status"] == "failed")
    pending = sum(1 for r in rows if r["status"] == "pending")
    delivery_rate = round((delivered / total_orders) * 100, 1)

    total_revenue = sum(r["revenue_ngn"] for r in rows)
    total_fuel = sum(r["fuel_cost_ngn"] for r in rows)
    total_profit = round(total_revenue - total_fuel, 2)
    failed_revenue = sum(r["revenue_ngn"] for r in rows if r["status"] == "failed")

    # Zone stats
    zone_counts = {}
    zone_profit = {}
    zone_failures = {}
    for r in rows:
        z = r["destination"]
        zone_counts[z] = zone_counts.get(z, 0) + 1
        zone_profit[z] = zone_profit.get(z, 0) + r["gross_profit_ngn"]
        if r["status"] == "failed":
            zone_failures[z] = zone_failures.get(z, 0) + 1

    top_zone = max(zone_counts, key=zone_counts.get)
    top_zone_count = zone_counts[top_zone]
    best_profit_zone = max(zone_profit, key=zone_profit.get)
    worst_zone = max(zone_failures, key=zone_failures.get) if zone_failures else "None"

    # Traffic
    heavy_orders = sum(1 for r in rows if r["traffic"] == "heavy")
    heavy_fuel = sum(r["fuel_cost_ngn"] for r in rows if r["traffic"] == "heavy")
    low_fuel = sum(r["fuel_cost_ngn"] for r in rows if r["traffic"] == "low")

    # Vehicle
    moto_orders = sum(1 for r in rows if r["vehicle"] == "motorcycle")
    van_orders = sum(1 for r in rows if r["vehicle"] == "van")

    # 1. Best and worst driver
    driver_delivered = {}
    for r in rows:
        d = r["driver"]
        if r["status"] == "delivered":
            driver_delivered[d] = driver_delivered.get(d, 0) + 1

    if driver_delivered:
        max_deliveries = max(driver_delivered.values())
        top_drivers = [d for d, count in driver_delivered.items() if count == max_deliveries]
        second_max = sorted(set(driver_delivered.values()))[-2] if len(set(driver_delivered.values())) > 1 else 0

        if len(top_drivers) == 1 and max_deliveries > second_max:
            best_driver = top_drivers[0]
            best_driver_count = max_deliveries
        else:
            best_driver = None
    else:
        best_driver = None

    # 2. Average delivery time
    avg_eta = round(sum(r["eta_minutes"] for r in rows if r["eta_minutes"] is not None) / total_orders)

    # 4. Fuel efficiency per km
    moto_rows = [r for r in rows if r["vehicle"] == "motorcycle"]
    van_rows = [r for r in rows if r["vehicle"] == "van"]

    moto_fuel_per_km = round(
        sum(r["fuel_cost_ngn"] for r in moto_rows) / sum(r["distance_km"] for r in moto_rows), 2
    ) if moto_rows else 0

    van_fuel_per_km = round(
        sum(r["fuel_cost_ngn"] for r in van_rows) / sum(r["distance_km"] for r in van_rows), 2
    ) if van_rows else 0

    # 5. Busiest dispatch hour
    hour_counts = {}
    for r in rows:
        hour = r["dispatch_time"]
        if hasattr(hour, "hour"):
            h = hour.hour
        else:
            from datetime import datetime
            h = datetime.strptime(str(hour), "%Y-%m-%d %H:%M:%S").hour
        hour_counts[h] = hour_counts.get(h, 0) + 1
    peak_hour = max(hour_counts, key=hour_counts.get)
    peak_hour_count = hour_counts[peak_hour]
    peak_hour_label = f"{peak_hour}:00 - {peak_hour + 1}:00"

    # 6. Island vs mainland
    from config import ISLAND_ZONES
    island_revenue = sum(r["revenue_ngn"] for r in rows if r["destination"] in ISLAND_ZONES)
    mainland_revenue = sum(r["revenue_ngn"] for r in rows if r["destination"] not in ISLAND_ZONES)
    island_orders = sum(1 for r in rows if r["destination"] in ISLAND_ZONES)
    mainland_orders = sum(1 for r in rows if r["destination"] not in ISLAND_ZONES)

    # --- Build PDF ---
    output_path = os.path.join(os.path.dirname(__file__), f"report_{target_date}.pdf")
    doc = SimpleDocTemplate(
        output_path, pagesize=A4,
        rightMargin=2.5*cm, leftMargin=2.5*cm,
        topMargin=2.5*cm, bottomMargin=2.5*cm
    )

    elements = []

    title_style = ParagraphStyle("title", fontSize=30, textColor=colors.black,
                                  fontName="Helvetica-Bold", spaceAfter=25)
    date_style = ParagraphStyle("date", fontSize=15, textColor=MID_GRAY,
                                 fontName="Helvetica", spaceBefore=8, spaceAfter=20)
    section_style = ParagraphStyle("section", fontSize=20, textColor=colors.black,
                                fontName="Helvetica-Bold", spaceBefore=22, spaceAfter=14)

    body_style = ParagraphStyle("body", fontSize=15, textColor=colors.black,
                             fontName="Helvetica", leading=20, spaceAfter=10)

    bullet_style = ParagraphStyle("bullet", fontSize=15, textColor=colors.black,
                               fontName="Helvetica", leading=20,
                               leftIndent=18, spaceAfter=7)
    footer_style = ParagraphStyle("footer", fontSize=12, textColor=MID_GRAY,
                                   alignment=TA_CENTER)

    def bullet(text):
        return Paragraph(f"• {text}", bullet_style)

    # Header
    elements.append(Paragraph("Doorstep Lagos", title_style))
    elements.append(Paragraph(
        f"Daily Operations Report — {target_date.strftime('%A, %d %B %Y')}",
        date_style
    ))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceAfter=12))

    # 1. Operations Overview
    elements.append(Paragraph("Operations Overview", section_style))
    elements.append(Paragraph(
        f"Today, Doorstep Lagos dispatched <b>{total_orders} orders</b> across Lagos. "
        f"Of these, <b>{delivered} were successfully delivered</b>, {failed} failed, "
        f"and {pending} are still pending. This gives an overall delivery success rate of "
        f"<b>{delivery_rate}%</b> for the day. Also, Average delivery time across all orders: {avg_eta} minutes.",
        body_style
    ))
    if best_driver:
        delivery_word = "delivery" if best_driver_count == 1 else "deliveries"
        elements.append(bullet(f"Driver with the most deliveries: {best_driver} — with {best_driver_count}\u00a0successful\u00a0{delivery_word}"))
    

    # 2. Financial Summary
    elements.append(Paragraph("Financial Summary", section_style))
    elements.append(Paragraph(
        f"Total revenue locked on dispatch today came to <b>N{total_revenue:,.2f}</b>. "
        f"After accounting for fuel costs of <b>N{total_fuel:,.2f}</b>, "
        f"the gross profit for the day stands at <b>N{total_profit:,.2f}</b>.",
        body_style
    ))
    elements.append(bullet(
        f"{failed} failed deliveries represent <b>N{failed_revenue:,.2f}</b> in at-risk customer retention"
    ))

    # 3. Zone Performance
    elements.append(Paragraph("Zone Performance", section_style))
    elements.append(Paragraph(
        f"The busiest delivery zone today was <b>{top_zone}</b> with {top_zone_count} orders. "
        f"<b>{best_profit_zone}</b> generated the highest gross profit among all zones.",
        body_style
    ))
    elements.append(bullet(f"Highest failure zone: {worst_zone}"))

    # 4. Island vs Mainland
    elements.append(Paragraph("Island vs Mainland", section_style))
    elements.append(Paragraph(
        f"Island zones (Victoria Island, Lekki, Ikoyi etc.) accounted for "
        f"<b>{island_orders} orders</b> generating <b>N{island_revenue:,.2f}</b> in revenue. "
        f"Mainland zones handled <b>{mainland_orders} orders</b> with "
        f"<b>N{mainland_revenue:,.2f}</b> in revenue.",
        body_style
    ))

    # 5. Traffic Impact
    elements.append(Paragraph("Traffic Impact", section_style))
    elements.append(Paragraph(
        f"{heavy_orders} orders were dispatched under heavy traffic conditions today. "
        f"Heavy traffic routes consumed <b>N{heavy_fuel:,.2f}</b> in fuel versus "
        f"<b>N{low_fuel:,.2f}</b> on low traffic routes — highlighting the direct "
        f"margin impact of Lagos road congestion.",
        body_style
    ))
    elements.append(bullet(f"Peak dispatch hour: {peak_hour_label} with {peak_hour_count} orders"))

    # 6. Fleet Performance
    elements.append(Paragraph("Fleet Performance", section_style))
    elements.append(Paragraph(
        f"The fleet today comprised motorcycles and vans. "
        f"Motorcycles handled <b>{moto_orders} orders</b> at an average fuel cost of "
        f"<b>N{moto_fuel_per_km}/km</b>. Vans handled <b>{van_orders} orders</b> "
        f"at <b>N{van_fuel_per_km}/km</b>.",
        body_style
    ))

    # 7. Manager Notes
    elements.append(Paragraph("Manager Notes", section_style))
    elements.append(bullet("Monthly trend report will be issued at end of month."))
    elements.append(bullet("All revenue figures are locked at point of dispatch."))
    elements.append(bullet("Next operations day: tomorrow."))

    # Footer
    elements.append(Spacer(1, 0.8*cm))
    elements.append(HRFlowable(width="100%", thickness=0.5, color=MID_GRAY, spaceAfter=6))
    elements.append(Paragraph(
    f"Generated automatically by Doorstep Lagos Pipeline — {date.today().strftime('%d %B %Y')}",
    footer_style
    ))

    doc.build(elements)
    print(f"Report saved: {output_path}")
    return output_path


if __name__ == "__main__":
    build_report()

