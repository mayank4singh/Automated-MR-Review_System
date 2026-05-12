import json
import os
import urllib.request

def post_review(body):
    object_attributes = body.get("object_attributes", {})
    mr_iid = object_attributes.get("iid")
    project_id = body.get("project", {}).get("id")
    mr_title = object_attributes.get("title", "")
    mr_author = body.get("user", {}).get("name", "Unknown")

    GITLAB_TOKEN = os.environ["GITLAB_TOKEN"]
    GITLAB_URL = os.environ["GITLAB_URL"]

    # Fetch diff
    diff_url = f"{GITLAB_URL}/api/v4/projects/{project_id}/merge_requests/{mr_iid}/diffs"
    req = urllib.request.Request(
        diff_url,
        headers={"PRIVATE-TOKEN": GITLAB_TOKEN}
    )
    with urllib.request.urlopen(req) as resp:
        diffs = json.loads(resp.read())

    diff_text = ""
    for d in diffs:
        diff_text += f"\n\n### File: {d.get('new_path')}\n{d.get('diff', '')}"

    if not diff_text.strip():
        print("Empty diff — skipping")
        return

    # LangGraph pipeline
    from langgraph.graph import StateGraph, END
    from langchain_aws import ChatBedrock
    from langchain_core.messages import HumanMessage
    from typing import TypedDict

    class ReviewState(TypedDict):
        diff: str
        security_issues: str
        quality_issues: str
        bug_issues: str

    llm = ChatBedrock(
        model_id="amazon.nova-lite-v1:0",
        region_name="us-east-1"
    )

    def security_agent(state: ReviewState) -> ReviewState:
        prompt = f"""You are a security code reviewer.
Analyze this diff ONLY for security issues.
Hardcoded secrets, injection risks, broken auth.

For each issue use EXACTLY this format:
ISSUE: <description>
SEVERITY: <High | Medium | Low>
FILE: <filename>
LINE: <line number or N/A>
SUGGESTION: <fix>

If nothing found write: NO SECURITY ISSUES FOUND

Diff:
{state['diff']}"""
        response = llm.invoke([HumanMessage(content=prompt)])
        return {**state, "security_issues": response.content}

    def quality_agent(state: ReviewState) -> ReviewState:
        prompt = f"""You are a code quality reviewer.
Analyze this diff ONLY for quality issues.
Poor naming, duplication, complexity, missing error handling.

For each issue use EXACTLY this format:
ISSUE: <description>
SEVERITY: <High | Medium | Low>
FILE: <filename>
LINE: <line number or N/A>
SUGGESTION: <fix>

If nothing found write: NO QUALITY ISSUES FOUND

Diff:
{state['diff']}"""
        response = llm.invoke([HumanMessage(content=prompt)])
        return {**state, "quality_issues": response.content}

    def bug_agent(state: ReviewState) -> ReviewState:
        prompt = f"""You are a bug detection expert.
Analyze this diff ONLY for bugs.
Null pointers, off-by-one, race conditions, unhandled exceptions.

For each issue use EXACTLY this format:
ISSUE: <description>
SEVERITY: <High | Medium | Low>
FILE: <filename>
LINE: <line number or N/A>
SUGGESTION: <fix>

If nothing found write: NO BUGS FOUND

Diff:
{state['diff']}"""
        response = llm.invoke([HumanMessage(content=prompt)])
        return {**state, "bug_issues": response.content}

    def aggregator(state: ReviewState) -> ReviewState:
        return state

    # Build graph
    builder = StateGraph(ReviewState)
    builder.add_node("security", security_agent)
    builder.add_node("quality", quality_agent)
    builder.add_node("bugs", bug_agent)
    builder.add_node("aggregate", aggregator)

    builder.set_entry_point("security")
    builder.add_edge("security", "quality")
    builder.add_edge("quality", "bugs")
    builder.add_edge("bugs", "aggregate")
    builder.add_edge("aggregate", END)

    graph = builder.compile()

    result = graph.invoke({
        "diff": diff_text,
        "security_issues": "",
        "quality_issues": "",
        "bug_issues": ""
    })

    # Build comment
    comment = f"""## 🤖 AI Code Review — {mr_title}
> **Author:** {mr_author} | **MR:** !{mr_iid}

---

### 🔒 Security Review
{result['security_issues']}

---

### 🧹 Code Quality Review
{result['quality_issues']}

---

### 🐛 Bug Detection
{result['bug_issues']}

---
*Reviewed by AI pipeline — Security · Quality · Bug agents*"""

    # Post comment to GitLab
    comment_url = f"{GITLAB_URL}/api/v4/projects/{project_id}/merge_requests/{mr_iid}/notes"
    payload = json.dumps({"body": comment}).encode()
    post_req = urllib.request.Request(
        comment_url,
        data=payload,
        headers={
            "PRIVATE-TOKEN": GITLAB_TOKEN,
            "Content-Type": "application/json"
        },
        method="POST"
    )
    with urllib.request.urlopen(post_req) as resp:
        print(f"Comment posted: {resp.getcode()} for MR !{mr_iid}")


def lambda_handler(event, context):
    print("Processor Lambda started")

    try:
        # Event payload from Lambda A
        body = json.loads(event.get("body", "{}"))
        post_review(body)
        print("Review completed successfully")

    except Exception as e:
        print(f"ERROR in processor: {str(e)}")
        import traceback
        traceback.print_exc()