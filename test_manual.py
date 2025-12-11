import sys
import os
sys.path.append(os.path.join(os.getcwd(), "src"))
from log_mcp_server.server import read_log, search_log

try:
    # Setup test file
    log_file = os.path.abspath("Linux_2k.log")
    print(f"Testing with file: {log_file}")

    print("--- Testing read_log ---")
    # mcp tools might be wrapped, let's see if we can call them directly
    # If using FastMCP, usually the decorated function is still callable or accessible
    try:
        res = read_log(log_file, lines=5)
        print("Result (first 100 chars):", res[:100])
        if "Error" in res and "not found" in res:
            print("FAILED: File not found")
        else:
            print("SUCCESS: read_log returned content")
    except Exception as e:
        print(f"FAILED: read_log raised {e}")

    print("\n--- Testing search_log ---")
    try:
        res = search_log(log_file, "kernel")
        print("Result (first 100 chars):", res[:100])
        if "Error" in res:
             print("FAILED: search_log returned error")
        elif "No matches" in res:
             print("WARNING: No matches found (might be expected)")
        else:
             print("SUCCESS: search_log returned matches")
    except Exception as e:
        print(f"FAILED: search_log raised {e}")

except Exception as e:
    print(f"Import failed or other error: {e}")
