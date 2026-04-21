import json
import os
import boto3
import urllib.request
import re

# At the top of your file, change the client region just to confirm
bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")

# 🔹 Env variable
GITLAB_TOKEN = os.environ.get("GITLAB_TOKEN")


# =========================
# 🔹 SAFE JSON PARSER
# =========================
def safe_parse_json(raw_output):
    try:
        match = re.search(r"\[.*\]", raw_output, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        return []
    except:
        return []


# =========================
# 🔹 BEDROCK CALL
# =========================


# Change the model ID
def call_bedrock(prompt):
    response = bedrock.converse(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        messages=[
            {
                "role": "user",
                "content": [
                    {"text": prompt}
                ]
            }
        ],
        inferenceConfig={
            "maxTokens": 500,
            "temperature": 0.2
        }
    )
    output_text = response["output"]["message"]["content"][0]["text"]
    return output_text


# =========================
# 🔹 PROMPT BUILDER
# =========================
def build_prompt(role, focus, diff):
    return f"""
You are a {role}.

STRICT RULES:
- Output ONLY JSON array
- Do NOT include explanation
- Use given file names ONLY

Return:
issue, severity (LOW, MEDIUM, HIGH), suggestion, file, line

Focus:
{focus}

Code:
{diff}
"""


# =========================
# 🔹 AGENTS
# =========================
def security_agent(diff):
    return call_bedrock(build_prompt(
        "security expert",
        "security vulnerabilities, secrets, unsafe patterns",
        diff
    ))


def quality_agent(diff):
    return call_bedrock(build_prompt(
        "code quality reviewer",
        "readability, best practices, maintainability",
        diff
    ))


def bug_agent(diff):
    return call_bedrock(build_prompt(
        "bug detection expert",
        "logical errors, edge cases",
        diff
    ))


# =========================
# 🔹 AGGREGATION
# =========================
def aggregate_results(*outputs):
    seen = {}
    results = []

    severity_order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}

    for output in outputs:
        if isinstance(output, list):
            for item in output:
                key = item.get("issue")

                if key not in seen:
                    seen[key] = item
                else:
                    existing = seen[key]
                    if severity_order.get(item["severity"], 1) > severity_order.get(existing["severity"], 1):
                        seen[key] = item

    results = list(seen.values())

    results.sort(
        key=lambda x: severity_order.get(x.get("severity", "LOW"), 1),
        reverse=True
    )

    return results


# =========================
# 🔹 FORMAT OUTPUT
# =========================
def format_summary(results):
    summary = "🤖 AI Code Review Summary\n\n"

    for r in results:
        summary += (
            f"🔴 {r.get('severity')} - {r.get('issue')}\n"
            f"📁 {r.get('file')} : Line {r.get('line')}\n"
            f"💡 {r.get('suggestion')}\n\n"
        )

    return summary


# =========================
# 🔹 GITLAB API (FIXED)
# =========================
def fetch_mr_changes(project_id, mr_iid):
    url = f"https://gitlab.com/api/v4/projects/{project_id}/merge_requests/{mr_iid}/changes"

    req = urllib.request.Request(url)
    req.add_header("PRIVATE-TOKEN", GITLAB_TOKEN)

    with urllib.request.urlopen(req) as response:
        data = json.loads(response.read().decode())

    return data


def extract_diff(data):
    formatted = ""

    for change in data.get("changes", []):
        formatted += f"\nFile: {change['new_path']}\n{change['diff']}\n"

    return formatted


# =========================
# 🔹 LAMBDA HANDLER
# =========================
def lambda_handler(event, context):

    print("🚀 Webhook triggered")

    try:
        body = json.loads(event.get("body", "{}"))

        project_id = body["project"]["id"]
        mr_iid = body["object_attributes"]["iid"]
        action = body["object_attributes"]["action"]

        print("Project:", project_id)
        print("MR:", mr_iid)
        print("Action:", action)

        if action not in ["open", "update"]:
            return {
                "statusCode": 200,
                "body": "Ignored event"
            }

        # 🔹 Fetch diff
        mr_data = fetch_mr_changes(project_id, mr_iid)
        diff = extract_diff(mr_data)

        # 🔹 AI processing
        security = security_agent(diff)
        quality = quality_agent(diff)
        bugs = bug_agent(diff)

        final_results = aggregate_results(security, quality, bugs)

        summary = format_summary(final_results)

        print("🔥 OUTPUT:", summary)

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": "Success",
                "issues": len(final_results)
            })
        }

    except Exception as e:
        print("❌ ERROR:", str(e))

        # 👇 ALWAYS return 200 to GitLab
        return {
            "statusCode": 200,
            "body": json.dumps({
                "error": str(e)
            })
        }