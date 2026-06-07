# Feedback Policy Automation Pipeline Cron Runner

FastAPI backend endpoint to automate the community feedback pipeline, including feedback aggregation, knowledge patch building, DB inserts/upserts, and selective cache invalidation.

---

## 1. Configurations

To enable the cron runner, set the following environment variable on your deployment server (e.g., Render, Vercel, or local `.env`):

```bash
ORACLE_FEEDBACK_PIPELINE_CRON_TOKEN="your_secure_random_string_here"
```

> [!WARNING]
> Keep this token private. Never commit it to git repositories or expose it on the client-side UI.

---

## 2. API Reference

- **Endpoint**: `POST /oracle/admin/run-feedback-policy-pipeline`
- **Headers**:
  - `X-Oracle-Pipeline-Cron-Token`: Must match the server environment variable.
- **Payload Schema (JSON)**:
  ```json
  {
    "dry_run": false,
    "clear_cache": true,
    "limit": 5000,
    "since_hours": 24
  }
  ```

### Field Descriptions

| Parameter | Type | Default | Constraints | Description |
| :--- | :--- | :--- | :--- | :--- |
| `dry_run` | `boolean` | `false` | None | If `true`, runs the aggregation pipeline and returns a report of what *would* change without writing to the database or clearing the cache. |
| `clear_cache` | `boolean` | `true` | None | If `true`, selectively clears query/response entries from the `oracle_cache` table matching the names of patched entities. |
| `limit` | `integer` | `5000` | `1` to `20000` | The maximum number of feedback rows to fetch in a single run. |
| `since_hours` | `integer` | `null` | Optional | Limits feedback rows to those created within the last N hours. |

---

## 3. Usage Examples

### A. Dry-Run Check (Simulated Execution)

Simulate pipeline execution to review pending feedback summaries and cache invalidations:

```bash
curl -X POST "https://mat-the-website.onrender.com/oracle/admin/run-feedback-policy-pipeline" \
  -H "Content-Type: application/json" \
  -H "X-Oracle-Pipeline-Cron-Token: your_secure_random_string_here" \
  -d '{"dry_run": true, "clear_cache": true}'
```

### B. Committing Changes (Write Mode)

Process feedback, apply patches to Supabase, and invalidate cached query results:

```bash
curl -X POST "https://mat-the-website.onrender.com/oracle/admin/run-feedback-policy-pipeline" \
  -H "Content-Type: application/json" \
  -H "X-Oracle-Pipeline-Cron-Token: your_secure_random_string_here" \
  -d '{"dry_run": false, "clear_cache": true, "limit": 1000}'
```

**Success Response (200 OK)**:
```json
{
  "ok": true,
  "dry_run": false,
  "report": {
    "feedback_rows_read": 12,
    "summary_rows_built": 2,
    "summary_rows_written": 2,
    "patches_built": 1,
    "patches_written": 1,
    "cache_rows_deleted": 3,
    "dry_run": false
  }
}
```

---

## 4. GitHub Actions Scheduled Runner Setup

We have integrated an automated workflow in `.github/workflows/feedback-policy-pipeline.yml` to call the cron endpoint periodically.

### A. How to Configure GitHub Repo Secret

To authenticate the workflow with the production API, you must configure the cron token secret in your GitHub repository:
1. Navigate to your GitHub repository dashboard.
2. In the top tabs, select **Settings**.
3. In the left sidebar, click **Secrets and variables** -> **Actions**.
4. Click **New repository secret** (the green button).
5. Enter the following details:
   - **Name**: `ORACLE_FEEDBACK_PIPELINE_CRON_TOKEN`
   - **Secret**: *(Paste the exact same token value set in your Render dashboard environment variables)*
6. Click **Add secret**.

### B. Triggering Manual Executions (workflow_dispatch)

You can trigger a dry-run check or manual pipeline execution directly from GitHub:
1. Go to the **Actions** tab at the top of your GitHub repository.
2. In the left sidebar under "Workflows", select **Feedback Policy Pipeline Cron**.
3. On the right-hand side, click the **Run workflow** dropdown button.
4. Configure the trigger parameters:
   - **dry_run**: Tick/untick (default: `true` for safety). Set to `false` to write patches to production DB.
   - **clear_cache**: Tick/untick (default: `true`).
   - **limit**: Maximum feedback records to process (default: `5000`).
5. Click **Run workflow** to queue and start the execution.

### C. Scheduled Write Mode Cadence

- **Schedule Cadence**: Runs automatically **every hour** (`0 * * * *` cron) in **active write mode** (`dry_run: false`).
- **Cadence recommendation**: Every hour is proposed in the initial stages to ensure prompt cache invalidation and patch application without overloading the DB.
- **Workflow configuration file**: [.github/workflows/feedback-policy-pipeline.yml](file:///.github/workflows/feedback-policy-pipeline.yml).

### D. Viewing Execution Reports & Logs

1. Click on the completed workflow run inside the **Actions** tab.
2. Expand the `run-pipeline` job, and select the **Call Pipeline Endpoint** step.
3. Review the printed JSON report summarizing the run statistics (`feedback_rows_read`, `summary_rows_written`, `patches_written`, `cache_rows_deleted`).
4. *Security note*: All cron tokens are encrypted and masked, preventing them from being exposed in actions logs.

### E. How to Disable the Runner on Incident

If there is a database issue, API downtime, or feedback spam attack:
1. Navigate to **Actions** -> **Feedback Policy Pipeline Cron**.
2. Click the `...` menu on the right.
3. Select **Disable workflow** to halt all future scheduled executions.
4. Click **Enable workflow** to resume schedule once the issue is resolved.
