import json
import boto3
import urllib.request

# 🔹 Use profile
session = boto3.Session(profile_name="bedrock-test")

bedrock = session.client(
    "bedrock-runtime",
    region_name="us-east-1"
)

# =========================
# 🔹 BEDROCK CALL
# =========================
def call_bedrock(diff):

    prompt = f"""
You are a senior software engineer.

Review this code diff and give:
- Bugs
- Security issues
- Improvements

Be concise.

Code:
{diff}
"""

    response = bedrock.converse(
        modelId="amazon.nova-lite-v1:0",
        messages=[
            {
                "role": "user",
                "content": [{"text": prompt}]
            }
        ],
        inferenceConfig={
            "maxTokens": 50,
            "temperature": 0.3
        }
    )

    return response["output"]["message"]["content"][0]["text"]


# =========================
# 🔹 TEST DATA
# =========================
diff = """
+ def login(user, password):
+     if user == "admin" and password == "1234":
+         return True
+     return False
"""

print("🚀 Running local test...\n")

output = call_bedrock(diff)

print("🔥 OUTPUT:\n")
print(output)