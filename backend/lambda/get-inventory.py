import json
import os
import boto3
from boto3.dynamodb.conditions import Key, Attr

dynamodb = boto3.resource("dynamodb")
INVENTORY_TABLE = os.environ["INVENTORY_TABLE"]
inventory_tbl = dynamodb.Table(INVENTORY_TABLE)

def lambda_handler(event, context):
    try:
        # Scan all inventory items
        resp = inventory_tbl.scan()
        items = resp.get("Items", [])

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json"
            },
            "body": json.dumps(items, default=str)
        }

    except Exception as e:
        print("ERROR:", e)
        return {
            "statusCode": 500,
            "body": json.dumps({"ok": False, "error": str(e)})
        }
