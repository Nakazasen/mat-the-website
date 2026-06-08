# Oracle Answer Feedback Pipeline Cron Automation

This document outlines the API endpoint, environment variables, GitHub Actions workflow, and safety policies for the Oracle Answer Feedback pipeline cron job.

## Endpoint Description

- **Path**: `POST /oracle/admin/run-oracle-answer-feedback-pipeline`
- **Method**: `POST`
- **Protected by Header**: `X-Oracle-Answer-Pipeline-Cron-Token`

### Request Body Schema

```json
{
  "dry_run": false,
  "clear_cache": true,
  "limit": 5000,
  "since_hours": null
}
```

- `dry_run` (boolean, default `false`): If `true`, simulates the pipeline run and does not write to the database or mutate data.
- `clear_cache` (boolean, default `true`): If `true`, deletes matching entries in `oracle_cache` selectively based on modified/patched query patterns.
- `limit` (integer, default `5000`, maximum `20000`): Maximum number of pending feedbacks to process in a single run.
- `since_hours` (integer | null, default `null`): If specified, only processes feedbacks created within the last N hours.

### Response Schema

```json
{
  "ok": true,
  "dry_run": false,
  "report": {
    "feedback_rows_read": 0,
    "summary_rows_written": 0,
    "patches_written": 0,
    "cache_rows_deleted": 0,
    "dry_run": false,
    "ok": true,
    "errors": []
  }
}
```

---

## Required Environment Variables & Secrets

To ensure secure execution, the pipeline requires an identical secure token set in both the Render backend environment and the GitHub Repository Secrets:

### 1. Render Environment Variable
- **Name**: `ORACLE_ANSWER_FEEDBACK_PIPELINE_CRON_TOKEN`
- **Value**: A secure, randomly-generated alphanumeric string.
- **Note**: If missing or unset on the server, the endpoint returns a `503 Service Unavailable` status code.

### 2. GitHub Actions Secret
- **Name**: `ORACLE_ANSWER_FEEDBACK_PIPELINE_CRON_TOKEN`
- **Value**: The identical token value configured in Render.
- **Note**: GitHub Actions runner will automatically redact the token from all workflow execution logs.

---

## GitHub Actions Cron Schedule

- **Workflow File**: `.github/workflows/oracle-answer-feedback-pipeline.yml`
- **Cadence**: Scheduled to run every 30 minutes.
- **Manual Trigger**: Can be manually dispatched via the GitHub Repository Actions UI page (`workflow_dispatch`).
  - Allows overriding `dry_run`, `clear_cache`, `limit`, and `since_hours`.

---

## Safety and Constraints

- **No Wiki Modifications**: The pipeline does NOT modify the canon core database (e.g., `wiki_entries`).
- **No Provisional Library Modifications**: The pipeline does NOT modify `provisional_library` records or attributes.
- **No LLM API Calls**: The pipeline relies purely on deterministic reader feedbacks, rules classification, and query matching, incurring zero token usage or LLM request overhead.
- **No Embeddings**: No vector database or embedding updates are invoked.
- **Secure Token Redaction**: The token is never logged, printed, or returned in any response payload.
