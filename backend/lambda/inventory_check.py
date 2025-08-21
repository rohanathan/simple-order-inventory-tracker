
import os
import json
import boto3
from decimal import Decimal
from typing import Any, Dict, List

dynamodb = boto3.resource("dynamodb")
sns = boto3.client("sns")

ORDERS_TABLE = os.environ["ORDERS_TABLE"]
INVENTORY_TABLE = os.environ["INVENTORY_TABLE"]
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")  # optional

orders_tbl = dynamodb.Table(ORDERS_TABLE)
inventory_tbl = dynamodb.Table(INVENTORY_TABLE)

def _decimal_to_float(obj):
    if isinstance(obj, list):
        return [_decimal_to_float(x) for x in obj]
    if isinstance(obj, dict):
        return {k: _decimal_to_float(v) for k, v in obj.items()}
    if isinstance(obj, Decimal):
        return float(obj)
    return obj

def adjust_inventory(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Decrement inventory for each item in an order.
    Each item should look like {"sku":"ABC123","qty":2}
    """
    results = []
    for line in items:
        sku = line["sku"]
        qty = int(line.get("qty", 1))
        # get current stock
        resp = inventory_tbl.get_item(Key={"sku": sku})
        current = resp.get("Item") or {"sku": sku, "stock": 0, "reorderThreshold": 5}
        new_stock = int(current.get("stock", 0)) - qty
        if new_stock < 0:
            new_stock = 0
        # update
        inventory_tbl.put_item(
            Item={
                "sku": sku,
                "stock": new_stock,
                "reorderThreshold": int(current.get("reorderThreshold", 5)),
                "lastUpdatedAt": datetime_now_iso(),
            }
        )
        current["newStock"] = new_stock
        results.append(current)
    return results

def datetime_now_iso():
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()

def maybe_notify_lows(items_after: List[Dict[str, Any]]):
    if not SNS_TOPIC_ARN:
        return
    low = [i for i in items_after if int(i.get("newStock", i.get("stock", 0))) <= int(i.get("reorderThreshold", 5))]
    if not low:
        return
    subject = "[Demo] Low inventory alert"
    body = "The following SKUs are at or below threshold:\\n\\n" + json.dumps(_decimal_to_float(low), indent=2)
    sns.publish(TopicArn=SNS_TOPIC_ARN, Subject=subject, Message=body)

def lambda_handler(event, context):
    # Event from DynamoDB Stream on ORDERS_TABLE
    # Expect NEW_IMAGE with items attribute: [{"sku": "...", "qty": 2}, ...]
    try:
        records = event.get("Records", [])
        for r in records:
            if r.get("eventName") not in ("INSERT","MODIFY"):
                continue
            new_image = r.get("dynamodb", {}).get("NewImage")
            if not new_image:
                continue
            # Convert DynamoDB stream image to python types
            items_attr = new_image.get("items", {})
            # Streams encode types with {'L':[{'M':{...}}, ...]} style. Use TypeDeserializer.
            from boto3.dynamodb.types import TypeDeserializer
            deser = TypeDeserializer()
            python_image = {k: deser.deserialize(v) for k, v in new_image.items()}
            items = python_image.get("items", [])
            if items:
                after = adjust_inventory(items)
                maybe_notify_lows(after)
        return {"statusCode": 200, "body": json.dumps({"ok": True})}
    except Exception as e:
        print("ERROR:", e)
        return {"statusCode": 500, "body": json.dumps({"ok": False, "error": str(e)})}
