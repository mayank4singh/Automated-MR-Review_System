import json
import boto3

# 🔹 Use your AWS profile
session = boto3.Session(profile_name="bedrock-test")

bedrock = session.client(
    "bedrock-runtime",
    region_name="us-east-1"
)

# =========================
# 🔹 BEDROCK CALL
# =========================
def call_bedrock(prompt):

    print("🚀 CALLING BEDROCK...")

    formatted_prompt = f"""
<|begin_of_text|>
<|start_header_id|>user<|end_header_id|>
{prompt}
<|eot_id|>
<|start_header_id|>assistant<|end_header_id|>
"""

    body = {
        "prompt": formatted_prompt,
        "max_gen_len": 200,
        "temperature": 0.3
    }

    response = bedrock.invoke_model(
        modelId="meta.llama3-8b-instruct-v1:0",
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json"
    )

    print("✅ RESPONSE RECEIVED")

    raw = response["body"].read().decode()
    print("🔥 RAW STRING:", raw)

    result = json.loads(raw)
    print("🔥 PARSED JSON:", result)

    return result.get("generation", "No output")


# =========================
# 🔹 MAIN EXECUTION
# =========================
if __name__ == "__main__":

    print("🔥 SCRIPT STARTED")

    prompt = "Explain GitLab merge request in simple terms"

    output = call_bedrock(prompt)

    print("\n🔥 FINAL OUTPUT:\n")
    print(output)