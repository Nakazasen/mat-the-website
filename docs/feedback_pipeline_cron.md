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

## 4. Scheduled Runner Setup

It is recommended to run this cron endpoint periodically using an external scheduler (e.g. GitHub Actions, Cron-Job.org, or Cloudflare Workers) depending on traffic:

- **High Traffic**: Every 15 minutes (`*/15 * * * *`).
- **Low Traffic / Standard**: Every 1 hour (`0 * * * *`).

### Example GitHub Action Workflow (`.github/workflows/feedback_pipeline.yml`)

```yaml
name: Scheduled Feedback Pipeline

on:
  schedule:
    - cron: '0 * * * *' # Run hourly
  workflow_dispatch: # Allow manual triggering

jobs:
  run-pipeline:
    runs-on: ubuntu-latest
    steps:
      - name: Trigger Feedback Pipeline Cron
        run: |
          curl -s -X POST "${{ secrets.BACKEND_API_URL }}/oracle/admin/run-feedback-policy-pipeline" \
            -H "Content-Type: application/json" \
            -H "X-Oracle-Pipeline-Cron-Token: ${{ secrets.ORACLE_FEEDBACK_PIPELINE_CRON_TOKEN }}" \
            -d '{"dry_run": false, "clear_cache": true, "limit": 5000}'
```
