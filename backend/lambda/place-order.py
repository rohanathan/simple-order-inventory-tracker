import json
import os
import time
from datetime import datetime, timezone
import boto3

dynamodb = boto3.resource("dynamodb")
ORDERS_TABLE = os.environ["ORDERS_TABLE"]
orders_tbl = dynamodb.Table(ORDERS_TABLE)

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "*",
    "Access-Control-Allow-Methods": "OPTIONS,GET,POST"
}

def lambda_handler(event, context):
    try:
        print("Raw event:", json.dumps(event))  # Debug log
        
        # Check if data is in body (API Gateway) or direct in event (test/other)
        if "body" in event and event["body"]:
            # API Gateway format
            raw_body = event.get("body", "{}")
            print("Raw body:", raw_body)  # Debug log
            body = json.loads(raw_body)
        else:
            # Direct format (data is in event root)
            print("Using direct event format")  # Debug log
            body = event
        
        print("Parsed body:", json.dumps(body))  # Debug log

        # Expect JSON like: { "items": [ { "sku": "SKU-GRN-003", "qty": 2 } ] }
        items = body.get("items", [])
        print("Items extracted:", json.dumps(items))  # Debug log
        
        if not items:
            print("No items found in request")  # Debug log
            return {
                "statusCode": 400,
                "headers": CORS_HEADERS,
                "body": json.dumps({"ok": False, "error": "Missing items"})
            }

        # Generate order ID
        order_id = f"ORD-{int(time.time()*1000)}"

        # Write to DynamoDB
        orders_tbl.put_item(
            Item={
                "orderId": order_id,
                "createdAt": datetime.now(timezone.utc).isoformat(),
                "items": items,
                "status": "RECEIVED"
            }
        )

        return {
            "statusCode": 200,
            "headers": CORS_HEADERS,
            "body": json.dumps({"ok": True, "orderId": order_id})
        }

    except Exception as e:
        print("ERROR:", e)
        return {
            "statusCode": 500,
            "headers": CORS_HEADERS,
            "body": json.dumps({"ok": False, "error": str(e)})
        }