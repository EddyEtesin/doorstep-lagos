import uuid
import random
import sys
import os
from datetime import datetime, timedelta
from faker import Faker
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__),"..")))


from config import (ALL_ZONES,ISLAND_ZONES,ISLAND_SURCHARGE,
    ZONE_DISTANCES,ZONES,BASE_FARE,RATE_PER_KM,VEHICLE_CONSUMPTION,
    FUEL_PRICE_PER_LITRE,TRAFFIC_LEVELS)

fake = Faker()

def generate_orders(n = 80, date = None):
    """
    Generate n delivery orders for a given date.
    If date is None, defaults to today.
    """
    if date is None:
        date = datetime.today().date()

    if date.weekday() == 6:
        print(f"No operations on Sunday {date}. Skipping")
        return []
    
    orders = []

    for i in range (n):
        order_id = str(uuid.uuid4())[:8].upper()
        vehicle = random.choice(["motorcycle","van"])
        destination = random.choice(ALL_ZONES)
        street_number = random.randint(1,120)
        stree_name = fake.street_name()
        address = f"{stree_name} {street_number}, {destination}, Lagos"
        distance_km = ZONE_DISTANCES[destination]

        traffic = random.choices(
            TRAFFIC_LEVELS,
            weights=[0.3, 0.4, 0.3]
        )[0]

        traffic_key = "heavy" if traffic == "heavy" else "normal"

        #Revenue - locked on dispatch 
        island_surcharge =  ISLAND_SURCHARGE if destination in ISLAND_ZONES else 0
        revenue = BASE_FARE + (RATE_PER_KM * distance_km) + island_surcharge

        #fuel cost 
        litres_used = distance_km/ VEHICLE_CONSUMPTION[vehicle][traffic_key]
        fuel_cost = round(litres_used * FUEL_PRICE_PER_LITRE,2)

        #Gross Profit 
        gross_profit = round(revenue - fuel_cost,2)
        
        #dispatch time
        dispatch_hour = random.randint(9,17)
        dispatch_minute = random.randint(0,59)
        dispatch_time = datetime(date.year, date.month, date.day,
            dispatch_hour, dispatch_minute,0
        )

        # Expected time of Arrival 
        speed = {"low" : 40, "moderate" : 25 , "heavy" : 12 }[traffic]
        eta_minutes = round((distance_km / speed) * 60)
        delivery_time = dispatch_time + timedelta(minutes=eta_minutes)

        #status weighted  realistically 
        status = random.choices(
            ["delivered","failed","pending"],
            weights= [0.75,0.15, 0.10]
        )[0]

        orders.append({
            "order_id": order_id,
            "date": str(date),
            "vehicle": vehicle,
            "origin": "Ikeja",
            "destination": destination,
            "address": address,
            "distance_km": distance_km,
            "traffic" : traffic,
            "revenue_ngn": revenue,
            "fuel_cost_ngn": fuel_cost,
            "gross_profit_ngn" : gross_profit,
            "dispatch_time" : dispatch_time,
            "estimated_delivery_time": delivery_time.strftime("%Y-%m-%d %H-%M-%S"),
            "Status" : status,
            "driver": fake.name(),
            "customer": fake.name(),
            "phone_number": fake.phone_number(),

        })
    return orders 

if __name__ == "__main__":
    from datetime import  date
    orders = generate_orders(n =80, date = date.today())

    for o in orders[:3]:
        print(o)

    print(f"\nTotal orders Generated : len {orders}")