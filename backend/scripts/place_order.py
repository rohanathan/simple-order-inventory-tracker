"""
python place_order.py --region us-east-1 --orders-table orders --sku SKU-BLU-002 --qty 7

"""
import argparse, time
from datetime import datetime, timezone
import boto3

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
    p.add_argument("--orders-table", default="orders")
    p.add_argument("--sku", required=True, help="SKU to order")
    p.add_argument("--qty", type=int, default=1, help="Quantity to order")
    args = p.parse_args()

    session = boto3.Session(region_name=args.region)
    ddb = session.resource("dynamodb")
    orders_tbl = ddb.Table(args.orders_table)

    order_id = f"ORD-{int(time.time()*1000)}"
    put_order(orders_tbl, order_id, [{"sku": args.sku, "qty": args.qty}])

    print(f"Placed order {order_id} for {args.qty}x {args.sku}")

if __name__ == "__main__":
    main()
