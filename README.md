<div align="center">

# 🤖 Dev Team Orchestrator

### A multi-agent development pipeline — 3 AI agents, 5 workflow phases, and a self-healing code generation loop driven by Discord commands.

<br>

[![Agents](https://img.shields.io/badge/AI_Agents-3-blueviolet?style=for-the-badge&logo=robot&logoColor=white)](prompts/)
[![Phases](https://img.shields.io/badge/Pipeline_Phases-5-blue?style=for-the-badge&logo=git-merge&logoColor=white)](#-pipeline-phases)
[![Discord](https://img.shields.io/badge/Trigger-Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white)](#-discord-commands)
[![K8s](https://img.shields.io/badge/Verify-Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)](k8s/)

[![n8n](https://img.shields.io/badge/Orchestrator-n8n-EA4B71?style=for-the-badge&logo=n8n&logoColor=white)](https://n8n.io)
[![Claude](https://img.shields.io/badge/LLM-Claude_Sonnet_4-D97706?style=for-the-badge&logo=anthropic&logoColor=white)](https://anthropic.com)
[![Ollama](https://img.shields.io/badge/LLM-Ollama-000000?style=for-the-badge&logo=ollama&logoColor=white)](https://ollama.com)

[![License](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-Welcome-brightgreen?style=for-the-badge)](https://github.com/jonpol01/dev-team-orchestrator/pulls)
[![Stars](https://img.shields.io/github/stars/jonpol01/dev-team-orchestrator?style=for-the-badge&logo=github&color=gold)](https://github.com/jonpol01/dev-team-orchestrator/stargazers)

<br>

<img src="architecture.svg" alt="Dev Team Orchestrator Architecture" width="100%">

</div>

---

## ⚡ Quick Start

```bash
# 1. Clone the repo
git clone https://github.com/jonpol01/dev-team-orchestrator.git
cd dev-team-orchestrator

# 2. Start n8n + Ollama
docker compose -f ../n8n-docker-stack/docker-compose.yaml -f docker-compose.override.yaml up -d

# 3. Import the workflow into n8n
#    Open n8n → Workflows → Import → select workflows/dev-team-orchestrator.json

# 4. Set up Kubernetes (for build/test verification)
kubectl apply -f k8s/setup.yaml
docker build -t dev-team-runner:latest k8s/runner/

# 5. Trigger from Discord
$team "implement user auth" in your-org/your-repo
```

---

## 💬 Discord Commands

| Command | Mode | Description |
|---------|------|-------------|
| `$team <task> in owner/repo` | **Single pass** | Runs the full pipeline once — plan, code, review, verify, PR |
| `$ralph <task> in owner/repo` | **Self-healing** | Same pipeline but retries up to 3x on review or verification failure |

### Example

```
$ralph "add JWT authentication middleware with tests" in jonpol01/my-api
```

The bot responds with progress updates and a final PR link (or failure report).

---

## 🏗️ Agent Team

<img src="assets/agent-team.svg" alt="Agent Team" width="100%">

| Agent | Model | Role | Rules |
|-------|-------|------|-------|
| 🧠 **Architect** | Claude Sonnet 4 | Decomposes task into atomic steps with acceptance criteria | Never writes code. One file per step. |
| ⚡ **Executor** | Ollama (new files) / Claude Haiku (modifications) | Writes production-quality code for each step | Follows repo patterns. Fixes reviewer feedback. |
| 👁 **Reviewer** | Claude Sonnet 4 | Reviews code against acceptance criteria | Strict on criteria. Practical on style. Max 3 retries. |

---

## 🔄 Pipeline Phases

<img src="assets/pipeline.svg" alt="Pipeline Phases" width="100%">

### Phase 1: Discord Input
- Bot listens for `$team` / `$ralph` commands
- Parses task, repo, mode, and author
- Sends acknowledgment back to Discord

### Phase 2: Architect (Planning)
- Fetches repo file tree via GitHub API
- Claude Sonnet 4 produces a JSON execution plan
- Each step has: target file, action, description, acceptance criteria
- Creates a feature branch

### Phase 3: Executor → Reviewer Loop
- For each step in the plan:
  - **Executor** writes the code (Ollama for new files, Claude Haiku for modifications)
  - **Commits** to the feature branch via GitHub API
  - **Reviewer** checks code against acceptance criteria
  - On `FAIL` in `$ralph` mode: feeds feedback back to Executor (up to 3 retries)

### Phase 4: K8s Verification
- Spins up a **Kubernetes Job** that:
  - Clones the branch
  - Auto-detects and installs dependencies
  - Runs the Architect's verification commands (pytest, mypy, npm test, etc.)
- On `FAIL` in `$ralph` mode: feeds build/test errors back to Executor
- Jobs visible in **k9s** for 1 hour after completion

### Phase 5: Results & PR
- If all steps pass + verification passes → **creates a GitHub PR**
- Posts final summary to Discord with step results and PR link
- If failures → posts error report, no PR created

---

## 📁 Project Structure

```
dev-team-orchestrator/
├── 📄 README.md                          # You are here
├── 📊 architecture.svg                   # Visual architecture diagram
│
├── ⚡ workflows/
│   └── dev-team-orchestrator.json        # n8n workflow (import this)
│
├── 🤖 prompts/                           # Agent system prompts
│   ├── architect-system.md               #   Planning & decomposition
│   ├── executor-system.md                #   Code generation
│   └── reviewer-system.md                #   Quality assurance
│
├── ☸️  k8s/                               # Kubernetes verification infra
│   ├── setup.yaml                        #   Namespace, RBAC, ServiceAccount
│   ├── README.md                         #   Beginner-friendly K8s guide
│   └── runner/
│       └── Dockerfile                    #   Python 3.12 + Node 20 + git
│
└── 🐳 docker-compose.override.yaml      # Ollama + K8s env config
```

---

## 🛠️ Setup Guide

### Prerequisites

| Tool | Purpose |
|------|---------|
| [Docker Desktop](https://www.docker.com/products/docker-desktop/) | Run n8n, Ollama, and K8s |
| [n8n](https://n8n.io) | Workflow orchestration (self-hosted) |
| [kubectl](https://kubernetes.io/docs/tasks/tools/) | Talk to Kubernetes |
| [k9s](https://k9scli.io/) | Terminal UI for Kubernetes |

### Environment Variables

Set these in your n8n container:

| Variable | Description |
|----------|-------------|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `OLLAMA_CODE_MODEL` | Ollama model name (default: `deepseek-coder-v2:16b`) |
| `K8S_API_URL` | K8s API endpoint (default: `https://kubernetes.docker.internal:6443`) |
| `K8S_TOKEN` | ServiceAccount token (see [K8s setup guide](k8s/README.md)) |
| `K8S_NAMESPACE` | K8s namespace (default: `dev-team`) |
| `GITHUB_TOKEN` | GitHub PAT for cloning private repos |

### n8n Credentials

Replace the placeholder IDs in the workflow with your actual n8n credentials:

| Credential Type | Used By |
|-----------------|---------|
| Discord Bot API | Trigger, Ack, Post Result |
| GitHub API | Fetch tree, commit, create branch, create PR |

### Kubernetes Setup

New to Kubernetes? Follow the step-by-step guide: **[k8s/README.md](k8s/README.md)**

```bash
# TL;DR
kubectl apply -f k8s/setup.yaml
docker build -t dev-team-runner:latest k8s/runner/
# Then set K8S_TOKEN from the service account secret
```

---

## 🛡️ Safety & Quality

- **Dual review** — AI code review (Reviewer agent) + actual build/test verification (K8s Job)
- **Retry with feedback** — `$ralph` mode feeds specific errors back to the Executor, not blind retries
- **Shared retry counter** — reviewer failures and verification failures share a 3-retry cap
- **10-minute timeout** — K8s Jobs auto-kill after 600 seconds
- **Auto-cleanup** — completed K8s Jobs are garbage-collected after 1 hour
- **Minimal RBAC** — n8n service account can only create/read Jobs and read pod logs

---

## 🔌 Tech Stack

| Layer | Technology | Role |
|-------|-----------|------|
| **Orchestration** | n8n | Routes data between agents, APIs, and K8s |
| **Planning LLM** | Claude Sonnet 4 | Architect agent — task decomposition |
| **Coding LLM (new files)** | Ollama (deepseek-coder) | Executor agent — local, cost-efficient |
| **Coding LLM (modifications)** | Claude Haiku 4.5 | Executor agent — context-aware edits |
| **Review LLM** | Claude Sonnet 4 | Reviewer agent — acceptance criteria |
| **Build/Test** | Kubernetes Jobs | Clone, install, run tests in isolation |
| **Observability** | k9s | Watch verification jobs in real-time |
| **VCS** | GitHub API | Branches, commits, PRs |
| **Communication** | Discord Bot | Command input, status updates, results |

---

## 🤝 Contributing

PRs are welcome! If you want to add new agents, LLM backends, or verification strategies:

1. Fork the repo
2. Create a feature branch
3. Submit a PR with a clear description

---

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

---
