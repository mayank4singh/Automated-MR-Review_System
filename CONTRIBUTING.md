# Contributing to ReviewFlow

First off, thank you for considering contributing to ReviewFlow 🚀

ReviewFlow is an open-source AI-powered DevSecOps platform for automated GitLab Merge Request reviews using AWS Lambda, LangGraph, and Amazon Bedrock.

We welcome:
- Bug fixes
- Feature enhancements
- Documentation improvements
- Security improvements
- AI workflow enhancements
- Infrastructure optimizations

---

# 📌 Development Philosophy

ReviewFlow focuses on:

- Secure webhook processing
- Asynchronous serverless architecture
- Multi-agent AI orchestration
- Scalable DevSecOps automation
- Clean and maintainable code

---

# 🛠️ Getting Started

## 1. Fork the Repository

Click the **Fork** button on GitHub.

---

## 2. Clone Your Fork

```bash
git clone https://github.com/your-username/ReviewFlow.git
```

---

## 3. Create a Virtual Environment

```bash
python -m venv venv
```

Activate:

### Linux / macOS

```bash
source venv/bin/activate
```

### Windows

```bash
venv\Scripts\activate
```

---

## 4. Install Dependencies

```bash
pip install -r requirements.txt
```

---

# 🌱 Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

Examples:

```bash
feature/github-support
feature/gitleaks-integration
feature/rag-pipeline
```

---

# 🧪 Testing

Before submitting a Pull Request:

- Verify webhook flow works
- Validate Lambda execution
- Ensure no secrets are committed
- Test MR review generation
- Run static checks if applicable

---

# 🔐 Security Guidelines

Please DO NOT commit:

- GitLab tokens
- AWS credentials
- Webhook signing secrets
- `.env` files
- Internal repository URLs

Before pushing code:

```bash
gitleaks detect
```

---

# 📋 Pull Request Guidelines

When submitting a PR:

- Clearly describe the change
- Keep PRs focused and modular
- Add screenshots if UI/docs changed
- Update documentation if required
- Ensure existing functionality is not broken

---

# 🧠 Areas Open for Contribution

## AI & LangGraph
- Additional review agents
- Smarter orchestration
- Prompt optimization
- Structured review improvements

---

## Security
- Gitleaks integration
- Secret masking pipeline
- Replay attack prevention
- API Gateway + WAF integration

---

## Scalability
- SQS integration
- Step Functions orchestration
- Retry handling
- Queue-based processing

---

## Repository Context Awareness
- ChromaDB integration
- RAG pipelines
- Semantic code retrieval
- Repository embeddings

---

# 📚 Coding Standards

- Use meaningful variable names
- Keep functions modular
- Add comments where necessary
- Follow Python best practices
- Prefer readability over cleverness

---

# 🐛 Reporting Issues

If you find a bug:

1. Open a GitHub Issue
2. Include logs/screenshots if possible
3. Describe reproduction steps
4. Mention expected vs actual behavior

---

# 💡 Feature Requests

Feature requests are welcome.

Please include:
- Problem statement
- Proposed solution
- Expected benefits

---

# 📜 Code of Conduct

Please be respectful and constructive in discussions and reviews.

---

# ⭐ Thank You

Your contributions help improve ReviewFlow and make AI-powered code review systems more secure, scalable, and intelligent.

Happy Building 🚀
