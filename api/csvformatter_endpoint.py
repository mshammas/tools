import subprocess
import json

def handler(request):
    # Only allow POST requests.
    if request.method != "POST":
        return {
            "statusCode": 405,
            "body": json.dumps({"error": "Method not allowed"})
        }

    try:
        # Parse the incoming JSON body.
        body = request.get_json()
    except Exception:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Invalid JSON"})
        }

    # Extract CSV data and option (e.g., "-q" or "-r1-3").
    csv_data = body.get("csv")
    option = body.get("option")
    if not csv_data or not option:
        return {
            "statusCode": 400,
            "body": json.dumps({"error": "Missing csv data or option"})
        }
    
    # Save CSV content to a temporary file.
    temp_csv_path = "/tmp/input.csv"
    with open(temp_csv_path, "w") as f:
        f.write(csv_data)

    # Build the command.
    # Adjust the path to csvformatter.py if necessary.
    cmd = ["python", "csvformatter.py", option, temp_csv_path]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        output = result.stdout
    except subprocess.CalledProcessError as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": "Processing error", "details": e.stderr})
        }
    
    # Return the output from csvformatter.py.
    return {
        "statusCode": 200,
        "body": json.dumps({"output": output})
    }
