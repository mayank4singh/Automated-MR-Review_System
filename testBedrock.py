import json
import boto3
import re

# 🔹 Bedrock client
bedrock = boto3.client("bedrock-runtime", region_name="ap-south-1")


# 🔹 Safe JSON parser (CRITICAL FIX)
def safe_parse_json(raw_output):
    try:
        match = re.search(r"\[.*\]", raw_output, re.DOTALL)
        if match:
            return json.loads(match.group(0))
        else:
            print("⚠️ No JSON found")
            print(raw_output)
            return []
    except Exception as e:
        print("⚠️ Parsing failed:", e)
        print(raw_output)
        return []


# 🔹 Core Bedrock caller
def call_bedrock(prompt):
    body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 500,
        "temperature": 0.2,
        "messages": [
            {"role": "user", "content": prompt}
        ]
    }

    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-haiku-20240307-v1:0",
        body=json.dumps(body),
        contentType="application/json",
        accept="application/json"
    )

    result = json.loads(response["body"].read())
    raw_output = result["content"][0]["text"]

    return safe_parse_json(raw_output)


# 🔹 Base Prompt Template
def build_prompt(role, focus, diff):
    return f"""
You are a strict AI code reviewer acting as a {role}.

CRITICAL RULES:
- Output MUST be ONLY valid JSON array
- Do NOT include ANY text before or after JSON
- Do NOT include markdown
- If you violate format, system will fail

Return JSON array with:
- issue
- severity (LOW, MEDIUM, HIGH)
- suggestion
- file
- line

Focus ONLY on:
{focus}

Code:
{diff}
"""


# 🔹 Agents

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
        "logical errors, edge cases, incorrect conditions",
        diff
    ))


# 🔹 Aggregation (DEDUP FIXED)
def aggregate_results(*agent_outputs):
    seen = set()
    results = []

    for output in agent_outputs:
        if isinstance(output, list):
            for item in output:
                key = (
                    item.get("issue"),
                    item.get("file"),
                    item.get("line")
                )
                if key not in seen:
                    seen.add(key)
                    results.append(item)

    severity_order = {"HIGH": 3, "MEDIUM": 2, "LOW": 1}

    results.sort(
        key=lambda x: severity_order.get(x.get("severity", "LOW"), 1),
        reverse=True
    )

    return results


# 🔹 Formatter
def format_summary(results):
    summary = "🤖 AI Code Review Summary\n\n"

    for r in results:
        summary += (
            f"🔴 {r.get('severity')} - {r.get('issue')}\n"
            f"📁 {r.get('file')} : Line {r.get('line')}\n"
            f"💡 {r.get('suggestion')}\n\n"
        )

    return summary


# 🔹 Main Runner
def run_review():
    print("🚀 Multi-Agent AI Code Review Started")

    diff = """
+ def login(user, password):
+     if user == "admin" and password == "1234":
+         return True
+     return False
"""

    # 🔹 Run agents
    security = security_agent(diff)
    quality = quality_agent(diff)
    bugs = bug_agent(diff)

    # 🔹 Aggregate
    final_results = aggregate_results(security, quality, bugs)

    # 🔹 Output structured
    print("\n📦 STRUCTURED OUTPUT:\n")
    print(json.dumps(final_results, indent=2))

    # 🔹 Output summary
    print("\n🧾 HUMAN SUMMARY:\n")
    print(format_summary(final_results))


if __name__ == "__main__":
    run_review()