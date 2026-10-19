from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from agent import run_agent, SYSTEM_PROMPT

app = Flask(__name__)
CORS(app)
history: list = [{"role": "system", "content": SYSTEM_PROMPT}]


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    global history
    message = request.json.get("message", "").strip()
    if not message:
        return jsonify({"response": ""})
    response, history = run_agent(message, history)
    return jsonify({"response": response})


@app.route("/reset", methods=["POST"])
def reset():
    global history
    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    return jsonify({"ok": True})


if __name__ == "__main__":
    print("Öppna VS Code: Cmd+Shift+P → 'Simple Browser: Show' → http://localhost:5001")
    app.run(host="0.0.0.0", port=5001, debug=False)
