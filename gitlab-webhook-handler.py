import json
import boto3
import os
import hmac
import hashlib
import base64

lambda_client = boto3.client("lambda", region_name="us-east-1")
PROCESSOR_FUNCTION = "gitlab-mr-processor"
WEBHOOK_SIGNING_SECRET = os.environ["WEBHOOK_SIGNING_SECRET"]

def verify_signature(headers, event):
    received_sig = headers.get("webhook-signature", "")
    timestamp = headers.get("webhook-timestamp", "")
    webhook_id = headers.get("webhook-id", "")

    if received_sig.startswith("v1,"):
        received_sig = received_sig[3:]

    raw_body = event.get("body", "")
    if event.get("isBase64Encoded", False):
        raw_body = base64.b64decode(raw_body).decode("utf-8")

    signed_content = f"{webhook_id}.{timestamp}.{raw_body}"

    secret = WEBHOOK_SIGNING_SECRET
    if secret.startswith("whsec_"):
        secret = secret[6:]

    secret_bytes = base64.b64decode(secret)

    computed_sig = base64.b64encode(
        hmac.new(
            secret_bytes,
            signed_content.encode("utf-8"),
            hashlib.sha256
        ).digest()
    ).decode()

    print(f"Received: {received_sig}")
    print(f"Computed: {computed_sig}")

    return hmac.compare_digest(received_sig, computed_sig)


def lambda_handler(event, context):
    try:
        headers = {
            k.lower(): v
            for k, v in (event.get("headers") or {}).items()
        }

        raw_body = event.get("body", "")

        if not verify_signature(headers, event):
            print("Invalid signature")
            return {
                "statusCode": 403,
                "body": json.dumps({"error": "Unauthorized"})
            }

        body = json.loads(raw_body)
        action = body.get("object_attributes", {}).get("action", "")
        print(f"Action: {action}")

        if action not in ["open", "update", "reopen"]:
            return {
                "statusCode": 200,
                "body": "Ignored"
            }

        lambda_client.invoke(
            FunctionName=PROCESSOR_FUNCTION,
            InvocationType="Event",
            Payload=json.dumps({"body": raw_body})
        )

        print("Processor invoked")
        return {
            "statusCode": 200,
            "body": json.dumps({"status": "triggered"})
        }

    except Exception as e:
        print(f"ERROR: {str(e)}")
        return {
            "statusCode": 200,
            "body": json.dumps({"error": str(e)})
        }