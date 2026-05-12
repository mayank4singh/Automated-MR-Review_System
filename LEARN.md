# Learn.md — Understanding ReviewFlow

This document explains the architecture, workflow, security model, and AI orchestration used inside ReviewFlow.

---

# 📌 What is ReviewFlow?

ReviewFlow is a secure asynchronous AI-powered Merge Request review platform built using:

- AWS Lambda
- Amazon Bedrock
- LangGraph
- GitLab Webhooks
- Python

The platform automatically reviews GitLab Merge Requests and posts AI-generated review comments directly onto the MR.

---

# 🎯 Goals of the Project

ReviewFlow was designed to solve common code review challenges:

- Slow review cycles
- Reviewer bottlenecks
- Inconsistent review quality
- Missed security vulnerabilities
- Difficulty scaling manual reviews

---

# 🏗️ Core Architecture

ReviewFlow uses an asynchronous event-driven serverless architecture.

```text
GitLab
   ↓
Webhook Lambda
   ↓
HMAC Verification
   ↓
Async Invocation
   ↓
Processor Lambda
   ↓
LangGraph Agents
   ↓
Amazon Bedrock
   ↓
GitLab MR Comment
```

---

# ⚡ Why Two Lambda Functions?

The architecture separates:

## Lambda A — Webhook Handler

Responsibilities:
- Receive webhook requests
- Verify HMAC signatures
- Return HTTP 200 quickly
- Trigger processing asynchronously

---

## Lambda B — MR Processor

Responsibilities:
- Fetch Merge Request diffs
- Run AI review workflow
- Call Amazon Bedrock
- Post comments onto GitLab

---

# ✅ Benefits of This Design

- Faster webhook acknowledgement
- Better scalability
- Fault isolation
- Parallel MR processing
- Reduced timeout risk

This pattern is commonly called:

```text
Ingress-Worker Architecture
```

---

# 🔐 Webhook Security

ReviewFlow uses GitLab webhook signing tokens and HMAC SHA256 verification.

The system validates:
- Request authenticity
- Payload integrity
- Signature validity

This prevents:
- Forged webhook requests
- Unauthorized Lambda triggers
- Malicious payload injection

---

# 🔑 Why Function URLs Were Used

AWS Lambda Function URLs were initially chosen because they:

- Reduce infrastructure complexity
- Simplify webhook setup
- Lower operational overhead
- Provide direct HTTPS access

Future versions may migrate to:
- API Gateway
- AWS WAF
- SQS-based buffering

for enterprise-scale deployments.

---

# 🤖 AI Review Pipeline

ReviewFlow uses LangGraph to orchestrate specialized review agents.

---

# 🔒 Security Agent

Detects:
- Hardcoded secrets
- Injection vulnerabilities
- Broken authentication
- Unsafe patterns

---

# 🧹 Code Quality Agent

Detects:
- Complexity issues
- Code duplication
- Poor naming
- Missing error handling

---

# 🐛 Bug Detection Agent

Detects:
- Edge cases
- Null pointer risks
- Race conditions
- Unhandled exceptions

---

# 🧠 LangGraph Orchestration

LangGraph coordinates the review pipeline.

```text
Security Agent
        ↓
Quality Agent
        ↓
Bug Agent
        ↓
Aggregator
        ↓
Structured MR Review
```

Each agent specializes in a different analysis domain.

---

# ☁️ Amazon Bedrock Integration

ReviewFlow uses Amazon Bedrock for LLM inference.

The system:
- Sends MR diffs to Bedrock
- Receives structured AI findings
- Aggregates reviews into a unified MR comment

---

# 🔄 Current Workflow

```text
Developer Opens MR
        ↓
GitLab Webhook Event
        ↓
Webhook Lambda
        ↓
HMAC Verification
        ↓
Async Processor Invocation
        ↓
Fetch MR Diff
        ↓
Run LangGraph Agents
        ↓
Amazon Bedrock Review
        ↓
Post MR Comment
```

---

# 📈 Scalability

ReviewFlow is horizontally scalable because AWS Lambda automatically scales per webhook request.

This allows:
- Multiple MR reviews in parallel
- Independent processing flows
- High concurrency support

Future improvements:
- SQS buffering
- Retry management
- Queue-based orchestration

---

# 🧩 Current Limitations

Current version analyzes:
- Merge Request diffs only

The system does NOT yet understand:
- Entire repository context
- Architecture-wide dependencies
- Cross-file semantic relationships

---

# 🚀 Future Improvements

## Retrieval Augmented Generation (RAG)

Future versions will use:
- ChromaDB
- Semantic search
- Repository embeddings

to provide repository-aware contextual reviews.

---

# 🛡️ Planned Security Enhancements

- Gitleaks integration
- Secret masking before LLM inference
- API Gateway + AWS WAF
- Replay protection persistence
- Advanced threat validation

---

# 📚 Technologies Used

| Technology | Purpose |
|---|---|
| AWS Lambda | Serverless execution |
| Amazon Bedrock | LLM inference |
| LangGraph | Multi-agent orchestration |
| GitLab Webhooks | Event source |
| CloudWatch | Logging |
| Python | Core implementation |

---

# 💡 Key Engineering Concepts Demonstrated

ReviewFlow demonstrates:

- Event-driven architecture
- Async serverless processing
- Multi-agent AI systems
- DevSecOps automation
- Webhook authentication
- Horizontal scalability
- AI orchestration
- Cloud-native design

---

# 📌 Final Note

ReviewFlow is designed as a scalable foundation for future AI-powered DevSecOps automation systems.

The current implementation focuses on:
- secure webhook ingestion
- asynchronous processing
- intelligent MR analysis
- production-style architecture design
