from flask import Flask, jsonify, request
import subprocess
import shlex

app = Flask(__name__)

def run_command(cmd_parts):
    try:
        result = subprocess.run(
            cmd_parts,
            capture_output=True,
            text=True,
            timeout=10
        )
        return {
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        }
    except subprocess.TimeoutExpired:
        return {"error": "Command timed out", "returncode": -1}
    except FileNotFoundError:
        return {"error": f"Command not found: {cmd_parts[0]}", "returncode": -1}


@app.route("/")
def index():
    return jsonify({
        "service": "Command Executor",
        "endpoints": {
            "GET  /run/<command>": "Run a command (e.g. /run/ls)",
            "GET  /run/<command>?args=-la": "Run command with args",
            "POST /run": "Run command via JSON body: {\"command\": \"ls\", \"args\": [\"-la\"]}"
        }
    })


@app.route("/run/<command>", methods=["GET"])
def run_get(command):
    raw_args = request.args.get("args", "")
    try:
        args = shlex.split(raw_args) if raw_args else []
    except ValueError as e:
        return jsonify({"error": f"Invalid args: {e}"}), 400

    output = run_command([command] + args)
    return jsonify({"command": command, "args": args, **output})


@app.route("/run", methods=["POST"])
def run_post():
    data = request.get_json(silent=True)
    if not data or "command" not in data:
        return jsonify({"error": "JSON body with 'command' field required"}), 400

    command = data["command"]
    args = data.get("args", [])
    if not isinstance(args, list):
        return jsonify({"error": "'args' must be a list"}), 400

    output = run_command([command] + args)
    return jsonify({"command": command, "args": args, **output})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
