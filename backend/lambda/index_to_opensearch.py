
# Index DynamoDB Stream records into OpenSearch without external deps by signing the HTTP request (SigV4).
import os
import json
import hmac
import hashlib
from datetime import datetime, timezone
from urllib.parse import urlparse
import boto3
import botocore.vendored.requests as requests  # requests is vendored in botocore in older runtimes

from boto3.dynamodb.types import TypeDeserializer

OPENSEARCH_ENDPOINT = os.environ["OPENSEARCH_ENDPOINT"]  # e.g. https://search-demo-abc123.eu-west-2.es.amazonaws.com
OPENSEARCH_INDEX = os.environ.get("OPENSEARCH_INDEX", "orders")
AWS_REGION = os.environ.get("AWS_REGION") or os.environ.get("AWS_DEFAULT_REGION", "eu-west-2")

deser = TypeDeserializer()

def _aws4_sign(method, service, host, region, canonical_uri, payload):
    # Adapted minimal signer for OpenSearch
    access_key = os.environ.get("AWS_ACCESS_KEY_ID")
    secret_key = os.environ.get("AWS_SECRET_ACCESS_KEY")
    token = os.environ.get("AWS_SESSION_TOKEN")

    if not access_key or not secret_key:
        # Use instance/role creds
        session = boto3.Session()
        creds = session.get_credentials().get_frozen_credentials()
        access_key, secret_key, token = creds.access_key, creds.secret_key, creds.token

    t = datetime.utcnow()
    amz_date = t.strftime('%Y%m%dT%H%M%SZ')
    datestamp = t.strftime('%Y%m%d')

    canonical_querystring = ''
    payload_hash = hashlib.sha256(payload.encode('utf-8')).hexdigest()
    canonical_headers = f'host:{host}\n' + f'x-amz-date:{amz_date}\n'
    signed_headers = 'host;x-amz-date'

    if token:
        canonical_headers += f'x-amz-security-token:{token}\n'
        signed_headers += ';x-amz-security-token'

    canonical_request = '\n'.join([method, canonical_uri, canonical_querystring, canonical_headers, signed_headers, payload_hash])

    algorithm = 'AWS4-HMAC-SHA256'
    credential_scope = f'{datestamp}/{region}/{service}/aws4_request'
    string_to_sign = '\n'.join([algorithm, amz_date, credential_scope, hashlib.sha256(canonical_request.encode('utf-8')).hexdigest()])

    def sign(key, msg):
        return hmac.new(key, msg.encode('utf-8'), hashlib.sha256).digest()

    kDate = sign(('AWS4' + secret_key).encode('utf-8'), datestamp)
    kRegion = sign(kDate, region)
    kService = sign(kRegion, service)
    kSigning = sign(kService, 'aws4_request')
    signature = hmac.new(kSigning, string_to_sign.encode('utf-8'), hashlib.sha256).hexdigest()

    authorization_header = (
        f'{algorithm} Credential={access_key}/{credential_scope}, '
        f'SignedHeaders={signed_headers}, Signature={signature}'
    )

    headers = {'x-amz-date': amz_date, 'Authorization': authorization_header}
    if token:
        headers['x-amz-security-token'] = token
    headers['content-type'] = 'application/json'
    return headers

def index_document(doc):
    # POST /{index}/_doc
    u = urlparse(OPENSEARCH_ENDPOINT)
    host = u.netloc
    path = f'/{OPENSEARCH_INDEX}/_doc'
    payload = json.dumps(doc, default=str)
    headers = _aws4_sign('POST', 'es', host, AWS_REGION, path, payload)
    url = f"{u.scheme}://{host}{path}"
    resp = requests.post(url, data=payload, headers=headers, timeout=5)
    if resp.status_code >= 300:
        print("OpenSearch error:", resp.status_code, resp.text)
    return resp.status_code

def lambda_handler(event, context):
    for rec in event.get("Records", []):
        if rec.get("eventName") not in ("INSERT", "MODIFY"):
            continue
        new_image = rec.get("dynamodb", {}).get("NewImage")
        if not new_image:
            continue
        python_image = {k: deser.deserialize(v) for k, v in new_image.items()}
        # enrich with metadata
        python_image['_indexed_at'] = datetime.now(timezone.utc).isoformat()
        index_document(python_image)
    return {"ok": True}
