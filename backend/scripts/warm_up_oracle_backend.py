import sys
import os
import time
import urllib.request
import json
import argparse
import ssl

def main():
    parser = argparse.ArgumentParser(description="Warm up production backend to trigger cold start wake-up.")
    parser.add_argument("--base-url", required=True, help="Base URL of the target backend service.")
    parser.add_argument("--attempts", type=int, default=5, help="Number of attempts to wake up backend.")
    parser.add_argument("--timeout", type=int, default=90, help="Timeout in seconds for each request.")
    parser.add_argument("--backoff-seconds", type=int, default=10, help="Seconds to sleep between retries.")
    parser.add_argument("--json", action="store_true", help="Print output in JSON format.")

    args = parser.parse_args()
    base_url = args.base_url.rstrip('/')
    url = f"{base_url}/api/health"

    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    success = False
    log_data = []

    for attempt in range(1, args.attempts + 1):
        t0 = time.time()
        status_code = None
        git_commit = None
        error_msg = None

        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 Warmup"})
        try:
            with urllib.request.urlopen(req, context=ctx, timeout=args.timeout) as resp:
                status_code = resp.status
                body = resp.read().decode("utf-8")
                latency = int((time.time() - t0) * 1000)

                if status_code == 200:
                    try:
                        data = json.loads(body)
                        if data.get("status") == "ok":
                            success = True
                            git_commit = data.get("git_commit")
                        else:
                            error_msg = f"JSON status not ok: {data.get('status')}"
                    except Exception as je:
                        error_msg = f"JSON decode error: {je}"
                else:
                    error_msg = f"HTTP status not 200: {status_code}"
        except Exception as e:
            latency = int((time.time() - t0) * 1000)
            error_msg = f"Request error: {e}"

        attempt_log = {
            "attempt": attempt,
            "status_code": status_code,
            "latency_ms": latency,
            "git_commit": git_commit,
            "error": error_msg
        }
        log_data.append(attempt_log)

        if not args.json:
            if success:
                print(f"Attempt {attempt} SUCCESS! Status: {status_code}, Latency: {latency} ms, Git Commit: {git_commit}")
            else:
                print(f"Attempt {attempt} FAILED: {error_msg} (Latency: {latency} ms)")

        if success:
            break

        if attempt < args.attempts:
            if not args.json:
                print(f"Sleeping for {args.backoff_seconds} seconds before next attempt...")
            time.sleep(args.backoff_seconds)

    result = {
        "success": success,
        "attempts_log": log_data
    }

    if args.json:
        print(json.dumps(result, indent=2))

    if success:
        sys.exit(0)
    else:
        if not args.json:
            print("ERROR: Warm-up failed after maximum attempts.", file=sys.stderr)
        sys.exit(2) # exit 2 for infra_failure

if __name__ == "__main__":
    main()
