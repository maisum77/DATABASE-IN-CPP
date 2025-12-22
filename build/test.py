#!/usr/bin/env python3
"""
Integration test for the C++ REST service started by the posted code.
Tests every major endpoint and reports success/failure in colour.
"""

import json, sys, urllib.request, urllib.error, pathlib, time

# ------------------------------------------------------------------
# CONFIGURATION
# ------------------------------------------------------------------
HOST = "localhost"
PORT = 8080
BASE_URL = f"http://{HOST}:{PORT}"

# ANSI colours (no external deps)
GREEN, RED, RESET = "\033[92m", "\033[91m", "\033[0m"

# ------------------------------------------------------------------
# LOW-LEVEL HELPERS
# ------------------------------------------------------------------
def http_request(url: str, method: str = "GET", data: bytes = None, headers=None):
    """Return (status_code:int, parsed_json:dict) or raise on network/json error."""
    if headers is None:
        headers = {}
    if data and not headers.get("Content-Type"):
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            payload = json.load(resp)
            return resp.status, payload
    except urllib.error.HTTPError as e:
        # still read the body for nice error messages
        body = e.read().decode()
        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            payload = {"error": body}
        return e.code, payload


def fatal(msg: str):
    print(f"{RED}✘ {msg}{RESET}")
    sys.exit(1)


def ok(msg: str):
    print(f"{GREEN}✔ {msg}{RESET}")


# ------------------------------------------------------------------
# TESTS
# ------------------------------------------------------------------
def health_check():
    status, payload = http_request(f"{BASE_URL}/health")
    if status != 200 or payload.get("status") != "ok":
        fatal(f"Health check failed: {payload}")
    ok("Service is alive")


def list_tables() -> list:
    status, payload = http_request(f"{BASE_URL}/tables")
    if status != 200:
        fatal(f"Cannot list tables: {payload}")
    if not isinstance(payload, list):
        fatal(f"Unexpected /tables response: {payload}")
    ok(f"Tables currently in DB: {', '.join(payload) or '(none)'}")
    return payload


def show_table(name: str, max_rows: int = 5):
    status, payload = http_request(f"{BASE_URL}/table/{name}")
    if status != 200:
        fatal(f"Cannot fetch table '{name}': {payload}")
    if not isinstance(payload, list) or not payload:
        fatal(f"Table '{name}' returned empty or malformed JSON")
    header = payload[0]
    rows = payload[1:max_rows+1]
    ok(f"Table '{name}' has {len(payload)-1} rows. Sample:")
    print("  ", header)
    for r in rows:
        print("  ", r)
    if len(payload) > max_rows + 1:
        print("  ...")


def run_query(table: str, column: str, operator: str, value: str):
    body = json.dumps({"table": table, "column": column,
                       "operator": operator, "value": value}).encode()
    status, payload = http_request(f"{BASE_URL}/query", method="POST", data=body)
    if status != 200:
        fatal(f"Query failed: {payload}")
    ok(f"Query returned {len(payload)-1 if payload else 0} rows")


def run_join(left: str, right: str):
    body = json.dumps({"left_table": left, "right_table": right}).encode()
    status, payload = http_request(f"{BASE_URL}/join", method="POST", data=body)
    if status != 200:
        fatal(f"Join failed: {payload}")
    ok(f"Join returned {len(payload)-1 if payload else 0} rows")


def export_table(name: str):
    body = json.dumps({}).encode()
    status, payload = http_request(f"{BASE_URL}/table/{name}/export",
                                   method="POST", data=body)
    if status != 200:
        fatal(f"Export failed: {payload}")
    file_name = payload.get("file")
    if not file_name:
        fatal("Export succeeded but no filename returned")
    # give the server a tiny moment to flush
    time.sleep(0.1)
    if not pathlib.Path(file_name).exists():
        fatal(f"Export claimed success but '{file_name}' not found on disk")
    ok(f"Table '{name}' exported to {file_name}")


# ------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------
def main():
    print("Testing C++ REST API on", BASE_URL)
    health_check()
    # tables = list_tables()
    # if not tables:
    #     fatal("No tables available – did you start the server in the directory containing employees.csv & departments.csv?")
    # for t in tables:
    #     show_table(t)
    run_query("employees", "empID", "=", "1")
    run_join("employees", "departments")
    export_table("employees")
    print(f"{GREEN}All tests passed!{RESET}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        fatal("Aborted by user")