# Kubernetes Setup Guide (Beginner-Friendly)

This guide walks you through setting up Kubernetes for the Dev Team Orchestrator's build/test verification phase.

## What is Kubernetes (K8s)?

Think of Kubernetes as a **manager for containers** (like Docker containers). When your orchestrator needs to build and test code, it asks Kubernetes to spin up a temporary container (called a **Job**), run the tests inside it, and report the results back. The container is automatically cleaned up after.

**k9s** is a terminal UI that lets you watch these Jobs run in real-time — like a dashboard for your cluster.

## Prerequisites

- Docker Desktop installed (you already have this for n8n + Ollama)
- `kubectl` CLI tool
- `k9s` CLI tool

---

## Step 1: Enable Kubernetes in Docker Desktop

1. Open **Docker Desktop**
2. Go to **Settings** (gear icon) → **Kubernetes**
3. Check **Enable Kubernetes**
4. Click **Apply & Restart**
5. Wait 2-3 minutes for the green dot to appear next to "Kubernetes is running"

That's it — you now have a local Kubernetes cluster.

### Verify it works:

```bash
kubectl cluster-info
```

You should see something like:
```
Kubernetes control plane is running at https://127.0.0.1:6443
```

---

## Step 2: Install kubectl (if not already installed)

```bash
# macOS
brew install kubectl

# Verify
kubectl version --client
```

---

## Step 3: Install k9s

```bash
# macOS
brew install derailed/k9s/k9s

# Verify
k9s version
```

---

## Step 4: Apply the Kubernetes manifests

This creates the namespace, service account, and permissions that n8n needs:

```bash
cd /path/to/dev-team-orchestrator

kubectl apply -f k8s/setup.yaml
```

You should see:
```
namespace/dev-team created
serviceaccount/n8n-job-runner created
role.rbac.authorization.k8s.io/job-runner created
rolebinding.rbac.authorization.k8s.io/n8n-job-runner-binding created
secret/n8n-job-runner-token created
```

### What did this create?

| Resource | Purpose |
|----------|---------|
| `dev-team` namespace | An isolated area in K8s for your verification jobs |
| `n8n-job-runner` service account | An identity that n8n uses to talk to K8s |
| `job-runner` role | Permissions: create/read jobs, read pod logs |
| `n8n-job-runner-token` secret | The auth token n8n uses (like a password) |

---

## Step 5: Get the service account token

n8n needs this token to authenticate with the Kubernetes API:

```bash
kubectl get secret n8n-job-runner-token -n dev-team -o jsonpath='{.data.token}' | base64 -d
```

Copy the output — this is your `K8S_SA_TOKEN`.

---

## Step 6: Build the runner image

This is the Docker image that your verification Jobs will use. It has Python, Node.js, git, and common test tools:

```bash
cd k8s/runner

docker build -t dev-team-runner:latest .
```

> **Note:** Since you're using Docker Desktop's built-in K8s, images built locally are automatically available to Kubernetes. No need to push to a registry.

---

## Step 7: Configure n8n environment variables

Add these to your n8n container's environment (in your n8n-docker-stack docker-compose.yaml or .env file):

```env
K8S_API_URL=https://kubernetes.docker.internal:6443
K8S_NAMESPACE=dev-team
K8S_TOKEN=<paste the token from Step 5>
GITHUB_TOKEN=<your GitHub personal access token>
```

The `docker-compose.override.yaml` in this repo has commented-out examples of these.

---

## Step 8: Import the updated workflow

1. Open n8n in your browser
2. Go to **Workflows** → **Import from File**
3. Select `workflows/dev-team-orchestrator.json`
4. Replace the credential placeholder IDs with your actual n8n credential IDs

---

## Using k9s to watch Jobs

Once everything is set up, you can watch your verification jobs run:

```bash
# Launch k9s looking at the dev-team namespace
k9s -n dev-team
```

### k9s Quick Reference

| Key | Action |
|-----|--------|
| `:jobs` + Enter | View all Jobs |
| `:pods` + Enter | View all Pods (running containers) |
| `l` | View logs of selected pod |
| `d` | Describe (detailed info) of selected resource |
| `Ctrl+d` | Delete selected resource |
| `/` | Filter/search |
| `Esc` | Go back |
| `q` or `Ctrl+c` | Quit k9s |

### What you'll see during a verification run:

1. A Job appears named `verify-feature-xxx-<timestamp>`
2. A Pod spins up (status: `ContainerCreating` → `Running`)
3. The pod clones your repo, installs deps, runs tests
4. Pod completes (status: `Completed` or `Error`)
5. Job stays visible for 1 hour, then auto-cleans

Press `l` on the pod to see the live test output.

---

## Troubleshooting

### "connection refused" when n8n tries to create a Job

- Make sure Kubernetes is enabled in Docker Desktop (green dot)
- Check that `K8S_API_URL` is set to `https://kubernetes.docker.internal:6443`
- The HTTP Request nodes have "Ignore SSL Issues" enabled since Docker Desktop uses a self-signed cert

### Jobs fail with "ImagePullBackOff"

- The runner image isn't available. Rebuild it:
  ```bash
  docker build -t dev-team-runner:latest k8s/runner/
  ```

### "Forbidden" errors

- The service account token may be expired or incorrect
- Re-extract it: `kubectl get secret n8n-job-runner-token -n dev-team -o jsonpath='{.data.token}' | base64 -d`

### Pod logs show "git clone failed"

- For private repos, make sure `GITHUB_TOKEN` is set in n8n's environment
- The token needs `repo` scope (create one at github.com/settings/tokens)

### How to clean up old jobs manually

```bash
kubectl delete jobs --all -n dev-team
```
