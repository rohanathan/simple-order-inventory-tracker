import json
import os
import boto3

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
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "*",
                "Access-Control-Allow-Methods": "OPTIONS,GET,POST"
            },
            "body": json.dumps({"inventory": items}, default=str)
        }

    except Exception as e:
        print("ERROR:", e)
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({"ok": False, "error": str(e)})
        }
