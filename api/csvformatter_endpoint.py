import json
import subprocess
from http.server import BaseHTTPRequestHandler

def handler(request, response):
    # 1) Only allow POST requests
    if request.method != "POST":
        response.status_code = 405
        response.body = json.dumps({"error": "Method not allowed"})
        return response

    # 2) Parse the JSON body from the request
    try:
        body = request.json()  # Vercel's built-in method to get JSON from request
    except Exception as e:
        response.status_code = 400
        response.body = json.dumps({"error": "Invalid JSON", "details": str(e)})
        return response

    # 3) Extract csv data and the option (e.g., "-q" or "-r1-3")
    csv_data = body.get("csv")
    option   = body.get("option")
    if not csv_data or not option:
        response.status_code = 400
        response.body = json.dumps({"error": "Missing csv data or option"})
        return response

    # 4) Write CSV content to a temporary file (Vercel allows /tmp)
    temp_csv_path = "/tmp/input.csv"
    try:
        with open(temp_csv_path, "w") as f:
            f.write(csv_data)
    except Exception as e:
        response.status_code = 500
        response.body = json.dumps({"error": "Failed to write file", "details": str(e)})
        return response

    # 5) Call your csvformatter.py script
    #    Adjust path if csvformatter.py is in another folder, e.g. "api/csvformatter.py"
    cmd = ["python3", "api/csvformatter.py", option, temp_csv_path]
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

    # 6) Return the successful result
    response.status_code = 200
    response.headers["Content-Type"] = "application/json"
    response.body = json.dumps({"output": output})
    return response
