
"""
Quick local seeder for DynamoDB tables.
- Creates a few inventory rows if missing
- Inserts random orders into ORDERS_TABLE
Usage:
  python scripts/seed_orders.py --region us-east-1 --orders 5
  AWS credentials are configured locally.
"""
import argparse, random, time
from datetime import datetime, timezone
import boto3

def put_inventory(tbl, skus):
    for sku in skus:
        tbl.put_item(Item={"sku": sku, "stock": random.randint(5, 20), "reorderThreshold": 5, "lastUpdatedAt": datetime.now(timezone.utc).isoformat()})

def put_order(tbl, order_id, items):
    tbl.put_item(Item={
        "orderId": order_id,
        "createdAt": datetime.now(timezone.utc).isoformat(),
        "items": items,
        "status": "RECEIVED"
    })

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--region", default="us-east-1")
    p.add_argument("--orders", type=int, default=5)
    p.add_argument("--orders-table", default="orders")
    p.add_argument("--inventory-table", default="inventory")
    args = p.parse_args()

    session = boto3.Session(region_name=args.region)
    ddb = session.resource("dynamodb")
    orders_tbl = ddb.Table(args.orders_table)
    inv_tbl = ddb.Table(args.inventory_table)

    skus = ["SKU-RED-001", "SKU-BLU-002", "SKU-GRN-003", "SKU-YLW-004"]
    put_inventory(inv_tbl, skus)

    for i in range(args.orders):
        items = []
        for _ in range(random.randint(1, 3)):
            sku = random.choice(skus)
            qty = random.randint(1, 3)
            items.append({"sku": sku, "qty": qty})
        put_order(orders_tbl, f"ORD-{int(time.time()*1000)}-{i}", items)
        time.sleep(0.2)

    print(f"Seeded {args.orders} orders.")

if __name__ == "__main__":
    main()
