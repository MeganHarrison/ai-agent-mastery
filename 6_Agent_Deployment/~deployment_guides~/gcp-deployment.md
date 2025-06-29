# Dynamous AI Agent — Google Cloud Deployment Guide

Deploy the full Dynamous AI Agent stack — React front‑end, FastAPI agent API, and RAG pipeline — on **Google Cloud Platform (GCP)**. Terraform provisions the infrastructure and Cloud Build delivers continuous deployment.

---

## 1  Prerequisites

1. **Google Cloud project** — [Create one](https://console.cloud.google.com/projectcreate) and note its **`PROJECT_ID`** & **`PROJECT_NUMBER`**. Be sure to add billing information as well or you'll get an error with enabling services below.
2. **Google Cloud SDK** — Install via the [SDK install guide](https://cloud.google.com/sdk/docs/install) then initialise:

   ```bash
   gcloud init
   gcloud config set project PROJECT_ID
   ```
3. **Terraform CLI ≥ 1.7** — [Download Terraform](https://developer.hashicorp.com/terraform/downloads).
4. **Supabase project** — create, then run the schema script: `6_Agent_Deployment/sql/0-all-tables.sql`
5. **Google Drive service account** — JSON key + Drive folder ID from local setup.
6. **Domain names ready** — You'll need access to your DNS provider to add records.
7. **Enable required GCP APIs** (run once):

   ```bash
   gcloud services enable run.googleapis.com runapps.googleapis.com artifactregistry.googleapis.com storage.googleapis.com cloudbuild.googleapis com cloudscheduler.googleapis.com secretmanager.googleapis.com
   ```

> **Note**  — `infra/terraform.tfvars` is in the **`.gitignore`** so secrets never reach Git.  You can later migrate any secret value to **Secret Manager** and reference it from Terraform if you wish as well.

---

## 2  Repository layout

```text
6_Agent_Deployment/
├─ backend_agent_api/        # FastAPI service (Dockerfile)
├─ backend_rag_pipeline/     # RAG pipeline (Dockerfile)
└─ frontend/                 # React (Vite) source
infra/
├─ main.tf
├─ variables.tf
├─ versions.tf
└─ terraform.tfvars.example
cloudbuild.yaml
```

---

## 3  Configure `infra/terraform.tfvars` (copy example → real file)

```hcl
project_id      = "ai-agent-mastery"
region          = "us-central1"

frontend_domain = "chat.dynamous.ai"
api_domain      = "agent.dynamous.ai"

# ---------- Agent API env vars ----------
agent_env = { … }

# ---------- RAG pipeline env vars ----------
rag_env  = { … }
```

*(Insert the full maps exactly as in the example file; keep secrets here or pull from Secret Manager.)*

---

## 4  Initial bootstrap (one‑time)

> **Why this order?**  The first Cloud Build run creates the build service‑account.  We grant roles **before** a second run so the full deploy succeeds.

1. **Kick‑start Cloud Build** (creates service‑account & only needs Storage + Artifact Registry which are already allowed for the default SA):

   ```bash
   gcloud builds submit --config cloudbuild.yaml . --substitutions=_BOOTSTRAP_ONLY=yes
   ```

   This step just builds & pushes images; deploys are skipped (the YAML checks `_BOOTSTRAP_ONLY`).

2. **Grant roles** to `PROJECT_NUMBER@cloudbuild.gserviceaccount.com`:

   * `roles/run.admin`
   * `roles/artifactregistry.writer`
   * `roles/storage.admin`
   * `roles/cloudscheduler.admin`
   * `roles/secretmanager.secretAccessor`

3. **Provision infrastructure**:

   ```bash
   cd infra
   
   # FIRST: Create state bucket and update versions.tf
   gsutil mb gs://tfstate-${PROJECT_ID}
   # Edit versions.tf line 11: replace YOUR-PROJECT-ID with your actual project ID
   
   terraform init
   terraform apply      # review → yes
   ```

4. **Full Cloud Build run** (now succeeds with new roles):

   ```bash
   gcloud builds submit --config cloudbuild.yaml .
   ```

   Terraform can now find the pushed `:latest` images; Cloud Run and Scheduler come up green.

---

## 5  Continuous deployment trigger

1. **Connect GitHub** → Cloud Build → Repositories → Connect → GitHub.
2. **Create trigger**  (Cloud Build → Triggers):

   * *Event*: Push to `main`
   * *Config*: `cloudbuild.yaml`
   * *Variables* tab ➜ add **only the three public build‑time values** used for the React bundle:

     ```
     VITE_SUPABASE_URL
     VITE_SUPABASE_ANON_KEY
     VITE_LANGFUSE_HOST_WITH_PROJECT
     ```

> **Why no API keys here?**  Runtime secrets (OpenAI key, Brave key, Supabase service key, GDrive JSON, etc.) are injected by **Terraform** straight into Cloud Run and Cloud Run Job. Cloud Build never needs to read them, so they stay local in `terraform.tfvars` **or** in Secret Manager referenced by Terraform.  Cloud Build only needs Secret Manager access if you later decide to bake a secret into the React bundle.

---

## 6  `cloudbuild.yaml` at a glance

| Step                | Action                                                                                     |
| ------------------- | ------------------------------------------------------------------------------------------ |
| **build-agent-api** | Build FastAPI image → push → `gcloud run deploy`                                           |
| **build-rag**       | Build RAG image → push → `gcloud beta run jobs deploy`                                     |
| **build-frontend**  | Create `.env.production` from build variables → `npm run build` → `gsutil rsync` to bucket |

`_BOOTSTRAP_ONLY=yes` skips deploy commands so the very first run can succeed without Run‑Admin role.

---

## 7  DNS Configuration

After running `terraform apply`, you need to configure DNS records at your domain provider.

### Get the frontend IP

```bash
gcloud compute forwarding-rules list
# Look for EXTERNAL_IP of frontend-lb-forwarding-rule
```

### Create DNS records

At your DNS provider, create these two records:

**Frontend (A record)**:
- Name: `chat` (just the subdomain, not full domain)
- Type: A
- Value: [IP address from step above]
- TTL: 300

**API (CNAME record)**:
- Name: `agent` (just the subdomain, not full domain)
- Type: CNAME
- Value: `ghs.googlehosted.com`
- TTL: 300

### Verify DNS

After 5-30 minutes, verify DNS propagation:

```bash
dig chat.dynamous.ai    # Should show your load balancer IP
dig agent.dynamous.ai   # Should show ghs.googlehosted.com
```

> **Troubleshooting**: If SSL certificates stay "PROVISIONING" for over an hour, double-check your DNS records. The certificates won't provision until DNS is properly configured.

## 8  Smoke test

1. Visit `https://chat.dynamous.ai` (your frontend URL) — page loads, no 404/403.
2. `curl https://agent.dynamous.ai/api/pydantic-agent` (your agent API URL) — returns 200.
3. Upload a doc to the RAG Google Drive folder → wait ≤ 10 min → ask agent → the new content is referenced.

---

## 8  Troubleshooting quick‑hits

| Symptom                         | Fix                                                                  |
| ------------------------------- | -------------------------------------------------------------------- |
| Build fails on deploy           | Confirm Cloud Build SA roles; ensure second run after granting roles |
| Cert stuck "PROVISIONING"       | Set DNS: Frontend A→[LB IP], API CNAME→ghs.googlehosted.com          |
| Scheduler firing but job absent | IAM on Scheduler SA: must have Run Invoker role on the job           |
| Old JS/CSS                      | `gsutil rsync -d` deletes stale assets; invalidate CDN if enabled    |

---

**You’re live!**  From now on, every commit to *main* rebuilds and redeploys automatically — fully IaC, fully automated. 🚀
