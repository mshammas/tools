import json
import subprocess
from csvformatter import main as csvformatter_main  # if you refactor main() to accept parameters
# Alternatively, if you want to use csvformatter.py as a library, you might extract the formatting logic
# into functions that you can call from this handler.

def handler(request, response):
    # Ensure we only allow POST requests.
    if request.method != "POST":
        response.status_code = 405
        response.body = json.dumps({"error": "Method not allowed"})
        return response

    try:
        body = request.json()  # Vercel’s built‑in method to parse JSON request bodies.
    except Exception as e:
        response.status_code = 400
        response.body = json.dumps({"error": "Invalid JSON", "details": str(e)})
        return response

    csv_data = body.get("csv")
    option = body.get("option")
    if not csv_data or not option:
        response.status_code = 400
        response.body = json.dumps({"error": "Missing csv data or option"})
        return response

    # Write CSV content to a temporary file (Vercel allows writing only to /tmp)
    temp_csv_path = "/tmp/input.csv"
    try:
        with open(temp_csv_path, "w") as f:
            f.write(csv_data)
    except Exception as e:
        response.status_code = 500
        response.body = json.dumps({"error": "File write error", "details": str(e)})
        return response

    # Build the command. Adjust the path to csvformatter.py if needed.
    # Here we assume csvformatter.py is now outside the api folder.
    cmd = ["python3", "csvformatter.py", option, temp_csv_path]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        output = result.stdout
    except subprocess.CalledProcessError as e:
        response.status_code = 500
        response.body = json.dumps({"error": "Processing error", "details": e.stderr})
        return response
    except Exception as e:
        response.status_code = 500
        response.body = json.dumps({"error": "Subprocess error", "details": str(e)})
        return response

    response.status_code = 200
    response.headers["Content-Type"] = "application/json"
    response.body = json.dumps({"output": output})
    return response
