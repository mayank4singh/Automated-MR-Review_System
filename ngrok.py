from flask import Flask, request, jsonify
import json
import boto3

app = Flask(__name__)

bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")


# =========================
# 🔹 BEDROCK CALL (Titan - safe)
# =========================
def call_bedrock(prompt):

    print("🚀 CALLING NOVA...")

    response = bedrock.converse(
        modelId="amazon.nova-lite-v1:0",   
        messages=[
            {
                "role": "user",
                "content": [{"text": prompt}]
            }
        ],
        inferenceConfig={
            "maxTokens": 100,
            "temperature": 0.3
        }
    )

    return response["output"]["message"]["content"][0]["text"]

# =========================
# 🔹 WEBHOOK ENDPOINT
# =========================
@app.route("/webhook", methods=["POST"])
def webhook():

    print("🚀 Webhook received")

    data = request.json
    print("📦 Payload:", json.dumps(data, indent=2))

    try:
        # 🔹 Extract basic info
        project_id = data.get("project", {}).get("id")
        mr_iid = data.get("object_attributes", {}).get("iid")

        print("Project:", project_id)
        print("MR:", mr_iid)

        # 🔹 Dummy prompt (replace later with diff)
        prompt = "Explain GitLab merge request simply"

        ai_output = call_bedrock(prompt)

        print("🔥 AI OUTPUT:\n", ai_output)

        return jsonify({"message": "Processed"}), 200

    except Exception as e:
        print("❌ ERROR:", str(e))
        return jsonify({"error": str(e)}), 200


# =========================
# 🔹 RUN SERVER
# =========================
if __name__ == "__main__":
    print("🔥 Local webhook server running...")
    app.run(port=5000)