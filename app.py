from flask import Flask, jsonify, request, render_template_string
import subprocess
import shlex

app = Flask(__name__)

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Shell Executor</title>
  <link href="https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Syne:wght@700;800&display=swap" rel="stylesheet"/>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    :root {
      --bg:        #0d0f14;
      --surface:   #13161e;
      --border:    #1f2433;
      --accent:    #00ffa3;
      --accent2:   #00c8ff;
      --danger:    #ff4f6a;
      --text:      #c8d0e0;
      --muted:     #4a5268;
      --mono:      'JetBrains Mono', monospace;
      --display:   'Syne', sans-serif;
    }

    body {
      background: var(--bg);
      color: var(--text);
      font-family: var(--mono);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 48px 16px 80px;
    }

    /* Subtle grid overlay */
    body::before {
      content: '';
      position: fixed;
      inset: 0;
      background-image:
        linear-gradient(rgba(0,255,163,.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,255,163,.03) 1px, transparent 1px);
      background-size: 40px 40px;
      pointer-events: none;
      z-index: 0;
    }

    .container {
      position: relative;
      z-index: 1;
      width: 100%;
      max-width: 860px;
    }

    header {
      margin-bottom: 40px;
    }

    .badge {
      display: inline-block;
      font-size: 11px;
      letter-spacing: .15em;
      text-transform: uppercase;
      color: var(--accent);
      border: 1px solid var(--accent);
      padding: 3px 10px;
      border-radius: 2px;
      margin-bottom: 12px;
      animation: fadeUp .4s ease both;
    }

    h1 {
      font-family: var(--display);
      font-size: clamp(2rem, 5vw, 3.2rem);
      font-weight: 800;
      line-height: 1.05;
      letter-spacing: -.02em;
      color: #fff;
      animation: fadeUp .4s .1s ease both;
    }

    h1 span { color: var(--accent); }

    .subtitle {
      margin-top: 8px;
      font-size: 13px;
      color: var(--muted);
      animation: fadeUp .4s .2s ease both;
    }

    /* Input panel */
    .panel {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      padding: 24px;
      margin-bottom: 24px;
      animation: fadeUp .4s .3s ease both;
    }

    .input-row {
      display: flex;
      gap: 10px;
      align-items: stretch;
    }

    .prompt-wrap {
      flex: 1;
      display: flex;
      align-items: center;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 6px;
      padding: 0 14px;
      transition: border-color .2s;
    }

    .prompt-wrap:focus-within {
      border-color: var(--accent);
      box-shadow: 0 0 0 3px rgba(0,255,163,.08);
    }

    .prompt-symbol {
      color: var(--accent);
      font-size: 15px;
      margin-right: 10px;
      user-select: none;
    }

    #cmdInput {
      flex: 1;
      background: transparent;
      border: none;
      outline: none;
      font-family: var(--mono);
      font-size: 15px;
      color: #fff;
      padding: 14px 0;
      caret-color: var(--accent);
    }

    #cmdInput::placeholder { color: var(--muted); }

    #runBtn {
      background: var(--accent);
      color: #000;
      border: none;
      border-radius: 6px;
      padding: 0 24px;
      font-family: var(--mono);
      font-size: 13px;
      font-weight: 700;
      letter-spacing: .08em;
      text-transform: uppercase;
      cursor: pointer;
      transition: background .2s, transform .1s;
      white-space: nowrap;
    }

    #runBtn:hover  { background: #00e891; }
    #runBtn:active { transform: scale(.97); }

    #runBtn:disabled {
      background: var(--muted);
      cursor: not-allowed;
    }

    .hint {
      margin-top: 12px;
      font-size: 11px;
      color: var(--muted);
    }

    .hint kbd {
      background: var(--border);
      border-radius: 3px;
      padding: 1px 5px;
      font-family: var(--mono);
      font-size: 10px;
      color: var(--text);
    }

    /* History */
    #history { display: flex; flex-direction: column; gap: 16px; }

    .entry {
      background: var(--surface);
      border: 1px solid var(--border);
      border-radius: 8px;
      overflow: hidden;
      animation: fadeUp .25s ease both;
    }

    .entry-header {
      display: flex;
      align-items: center;
      justify-content: space-between;
      padding: 10px 16px;
      border-bottom: 1px solid var(--border);
      background: rgba(255,255,255,.02);
    }

    .entry-cmd {
      font-size: 13px;
      color: var(--accent2);
      font-weight: 700;
    }

    .entry-cmd::before { content: '$ '; color: var(--muted); }

    .entry-meta {
      display: flex;
      align-items: center;
      gap: 10px;
    }

    .rc {
      font-size: 11px;
      padding: 2px 8px;
      border-radius: 3px;
      font-weight: 700;
    }

    .rc.ok    { background: rgba(0,255,163,.15); color: var(--accent); }
    .rc.err   { background: rgba(255,79,106,.15); color: var(--danger); }

    .entry-time {
      font-size: 11px;
      color: var(--muted);
    }

    .clear-btn {
      background: none;
      border: none;
      color: var(--muted);
      cursor: pointer;
      font-size: 16px;
      line-height: 1;
      padding: 0 2px;
      transition: color .15s;
    }
    .clear-btn:hover { color: var(--danger); }

    .entry-body { padding: 16px; }

    .stream-label {
      font-size: 10px;
      letter-spacing: .12em;
      text-transform: uppercase;
      color: var(--muted);
      margin-bottom: 6px;
    }

    pre {
      font-family: var(--mono);
      font-size: 13px;
      line-height: 1.7;
      white-space: pre-wrap;
      word-break: break-all;
      color: var(--text);
    }

    pre.stderr { color: var(--danger); }

    .empty-state {
      text-align: center;
      padding: 48px 0;
      color: var(--muted);
      font-size: 13px;
      animation: fadeUp .4s .4s ease both;
    }

    .empty-state .icon { font-size: 32px; margin-bottom: 12px; opacity: .4; }

    .spinner {
      display: inline-block;
      width: 14px; height: 14px;
      border: 2px solid var(--muted);
      border-top-color: var(--accent);
      border-radius: 50%;
      animation: spin .6s linear infinite;
      vertical-align: middle;
      margin-right: 6px;
    }

    @keyframes spin    { to { transform: rotate(360deg); } }
    @keyframes fadeUp  {
      from { opacity: 0; transform: translateY(10px); }
      to   { opacity: 1; transform: translateY(0);    }
    }
  </style>
</head>
<body>
<div class="container">
  <header>
    <div class="badge">&#9679; live shell</div>
    <h1>Shell <span>Executor</span></h1>
    <p class="subtitle">Run commands inside the container &mdash; output streams below.</p>
  </header>

  <div class="panel">
    <div class="input-row">
      <div class="prompt-wrap">
        <span class="prompt-symbol">$</span>
        <input id="cmdInput" type="text" placeholder="ls -la / uname -a / whoami …" autocomplete="off" spellcheck="false" />
      </div>
      <button id="runBtn">Run</button>
    </div>
    <p class="hint">Press <kbd>Enter</kbd> to execute &nbsp;&bull;&nbsp; Results appear below</p>
  </div>

  <div id="history">
    <div class="empty-state">
      <div class="icon">⌨️</div>
      No commands run yet. Type something above.
    </div>
  </div>
</div>

<script>
  const input   = document.getElementById('cmdInput');
  const runBtn  = document.getElementById('runBtn');
  const history = document.getElementById('history');

  function pad(n) { return String(n).padStart(2,'0'); }
  function timestamp() {
    const d = new Date();
    return `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
  }

  async function execute() {
    const raw = input.value.trim();
    if (!raw) return;

    // parse into command + args
    const parts = raw.match(/(?:[^\\s"']+|"[^"]*"|'[^']*')+/g) || [];
    const command = parts[0];
    const args    = parts.slice(1).map(a => a.replace(/^['"]|['"]$/g, ''));

    // clear empty state
    const emptyState = history.querySelector('.empty-state');
    if (emptyState) emptyState.remove();

    // create entry card
    const entry = document.createElement('div');
    entry.className = 'entry';
    entry.innerHTML = `
      <div class="entry-header">
        <span class="entry-cmd">${escHtml(raw)}</span>
        <div class="entry-meta">
          <span class="spinner"></span>
          <span class="entry-time">${timestamp()}</span>
          <button class="clear-btn" title="Remove">&#10005;</button>
        </div>
      </div>
      <div class="entry-body"><pre>running…</pre></div>
    `;
    history.insertBefore(entry, history.firstChild);
    entry.querySelector('.clear-btn').addEventListener('click', () => entry.remove());

    runBtn.disabled = true;
    input.value = '';

    try {
      const res  = await fetch('/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command, args })
      });
      const data = await res.json();

      const rc      = data.returncode ?? -1;
      const isOk    = rc === 0;
      const spinner = entry.querySelector('.spinner');
      spinner.outerHTML = `<span class="rc ${isOk ? 'ok' : 'err'}">rc&nbsp;${rc}</span>`;

      let bodyHtml = '';
      if (data.error) {
        bodyHtml = `<div class="stream-label">error</div><pre class="stderr">${escHtml(data.error)}</pre>`;
      } else {
        if (data.stdout) bodyHtml += `<div class="stream-label">stdout</div><pre>${escHtml(data.stdout)}</pre>`;
        if (data.stderr) bodyHtml += `<div class="stream-label">stderr</div><pre class="stderr">${escHtml(data.stderr)}</pre>`;
        if (!data.stdout && !data.stderr) bodyHtml = `<pre style="color:var(--muted)">(no output)</pre>`;
      }
      entry.querySelector('.entry-body').innerHTML = bodyHtml;

    } catch(e) {
      entry.querySelector('.spinner').outerHTML = `<span class="rc err">ERR</span>`;
      entry.querySelector('.entry-body').innerHTML =
        `<pre class="stderr">${escHtml(String(e))}</pre>`;
    } finally {
      runBtn.disabled = false;
      input.focus();
    }
  }

  function escHtml(s) {
    return String(s)
      .replace(/&/g,'&amp;')
      .replace(/</g,'&lt;')
      .replace(/>/g,'&gt;');
  }

  runBtn.addEventListener('click', execute);
  input.addEventListener('keydown', e => { if (e.key === 'Enter') execute(); });
  input.focus();
</script>
</body>
</html>
"""

def run_command(cmd_parts):
    try:
        result = subprocess.run(
            cmd_parts,
            capture_output=True,
            text=True,
            timeout=1000
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
    return render_template_string(HTML)


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
