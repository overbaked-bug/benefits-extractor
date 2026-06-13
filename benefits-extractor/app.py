import base64
import json
import os
import tempfile
import anthropic
from dotenv import load_dotenv
from flask import Flask, jsonify, render_template_string, request
from supabase import create_client

load_dotenv()

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 32 * 1024 * 1024  # 32 MB max upload

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
  <title>Benefits Extractor</title>
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

    body {
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: #f5f7fa;
      color: #1a1a2e;
      min-height: 100vh;
    }

    header {
      background: #fff;
      border-bottom: 1px solid #e2e8f0;
      padding: 18px 40px;
    }
    header h1 { font-size: 1.25rem; font-weight: 700; color: #1a1a2e; }
    header p  { font-size: 0.82rem; color: #64748b; margin-top: 2px; }

    .container { max-width: 1100px; margin: 40px auto; padding: 0 24px; }

    /* Upload card */
    .upload-card {
      background: #fff;
      border: 1px solid #e2e8f0;
      border-radius: 12px;
      padding: 40px;
      text-align: center;
      margin-bottom: 32px;
    }
    .upload-card h2 { font-size: 1.05rem; font-weight: 600; margin-bottom: 6px; }
    .upload-card p  { font-size: 0.85rem; color: #64748b; margin-bottom: 24px; }

    .drop-zone {
      border: 2px dashed #cbd5e1;
      border-radius: 10px;
      padding: 36px 24px;
      cursor: pointer;
      transition: border-color .2s, background .2s;
      position: relative;
    }
    .drop-zone:hover, .drop-zone.dragover {
      border-color: #22c55e;
      background: #f0fdf4;
    }
    .drop-zone input[type=file] {
      position: absolute; inset: 0; opacity: 0; cursor: pointer; width: 100%; height: 100%;
    }
    .drop-icon { font-size: 2rem; margin-bottom: 10px; }
    .drop-zone p { font-size: 0.85rem; color: #64748b; margin: 0; }
    .drop-zone strong { color: #22c55e; }
    #file-name { margin-top: 10px; font-size: 0.8rem; color: #475569; }

    .btn {
      display: inline-flex; align-items: center; gap: 8px;
      padding: 10px 28px; border: none; border-radius: 8px;
      font-size: 0.9rem; font-weight: 600; cursor: pointer; transition: opacity .15s;
    }
    .btn:hover { opacity: .88; }
    .btn:disabled { opacity: .5; cursor: not-allowed; }
    .btn-primary { background: #1e293b; color: #fff; margin-top: 20px; }
    .btn-green   { background: #22c55e; color: #fff; }

    /* Spinner */
    .spinner {
      display: none; width: 18px; height: 18px;
      border: 3px solid #fff; border-top-color: transparent;
      border-radius: 50%; animation: spin .7s linear infinite;
    }
    @keyframes spin { to { transform: rotate(360deg); } }

    /* Status banner */
    #status {
      display: none; padding: 12px 18px; border-radius: 8px;
      font-size: 0.875rem; font-weight: 500; margin-bottom: 24px;
    }
    #status.info    { background: #eff6ff; color: #1d4ed8; border: 1px solid #bfdbfe; }
    #status.success { background: #f0fdf4; color: #15803d; border: 1px solid #bbf7d0; }
    #status.error   { background: #fef2f2; color: #b91c1c; border: 1px solid #fecaca; }

    /* Results section */
    #results { display: none; }
    .results-header {
      display: flex; align-items: center; justify-content: space-between;
      margin-bottom: 16px;
    }
    .results-header h2 { font-size: 1.05rem; font-weight: 700; }
    .badge {
      background: #f1f5f9; color: #475569;
      font-size: 0.78rem; font-weight: 600;
      padding: 3px 10px; border-radius: 20px;
      margin-left: 10px;
    }

    .table-wrap {
      background: #fff; border: 1px solid #e2e8f0;
      border-radius: 12px; overflow: hidden;
    }
    table { width: 100%; border-collapse: collapse; }
    thead { background: #f8fafc; }
    th {
      padding: 12px 16px; text-align: left;
      font-size: 0.78rem; font-weight: 700;
      text-transform: uppercase; letter-spacing: .05em;
      color: #64748b; border-bottom: 1px solid #e2e8f0;
    }
    td {
      padding: 14px 16px; font-size: 0.85rem;
      border-bottom: 1px solid #f1f5f9;
      vertical-align: top; line-height: 1.5;
    }
    tr:last-child td { border-bottom: none; }
    tr:hover td { background: #f8fafc; }

    .cat-badge {
      display: inline-block; padding: 2px 10px;
      border-radius: 20px; font-size: 0.75rem; font-weight: 600;
    }
    .cat-Retirement  { background: #ede9fe; color: #6d28d9; }
    .cat-Health      { background: #dcfce7; color: #166534; }
    .cat-Dental      { background: #dbeafe; color: #1e40af; }
    .cat-Vision      { background: #fce7f3; color: #9d174d; }
    .cat-Disability  { background: #ffedd5; color: #9a3412; }
    .cat-Other       { background: #f1f5f9; color: #475569; }

    .save-row {
      display: flex; align-items: center; justify-content: flex-end;
      gap: 14px; margin-top: 20px;
    }
    #save-status { font-size: 0.85rem; }
  </style>
</head>
<body>

<header>
  <h1>Benefits Extractor</h1>
  <p>Upload a benefits policy PDF to extract and save structured data</p>
</header>

<div class="container">

  <div id="status"></div>

  <div class="upload-card">
    <h2>Upload Benefits Policy PDF</h2>
    <p>Drag and drop your file here, or click to browse</p>
    <div class="drop-zone" id="drop-zone">
      <input type="file" id="pdf-input" accept=".pdf" />
      <div class="drop-icon">📄</div>
      <p><strong>Click to upload</strong> or drag and drop</p>
      <p style="margin-top:4px">PDF files only</p>
    </div>
    <div id="file-name"></div>
    <button class="btn btn-primary" id="extract-btn" onclick="extractBenefits()" disabled>
      <span class="spinner" id="extract-spinner"></span>
      <span id="extract-label">Extract Benefits</span>
    </button>
  </div>

  <div id="results">
    <div class="results-header">
      <h2>Extracted Benefits <span class="badge" id="count-badge"></span></h2>
    </div>
    <div class="table-wrap">
      <table>
        <thead>
          <tr>
            <th>#</th>
            <th>Benefit Name</th>
            <th>Category</th>
            <th>Eligibility</th>
            <th>Coverage Details</th>
          </tr>
        </thead>
        <tbody id="results-body"></tbody>
      </table>
    </div>
    <div class="save-row">
      <span id="save-status"></span>
      <button class="btn btn-green" onclick="saveToSupabase()">
        <span class="spinner" id="save-spinner"></span>
        <span id="save-label">💾 Save to Supabase</span>
      </button>
    </div>
  </div>

</div>

<script>
  let extractedBenefits = [];

  const dropZone = document.getElementById("drop-zone");
  const fileInput = document.getElementById("pdf-input");
  const extractBtn = document.getElementById("extract-btn");
  const fileNameEl = document.getElementById("file-name");

  fileInput.addEventListener("change", () => {
    if (fileInput.files[0]) {
      fileNameEl.textContent = "Selected: " + fileInput.files[0].name;
      extractBtn.disabled = false;
    }
  });

  dropZone.addEventListener("dragover", e => { e.preventDefault(); dropZone.classList.add("dragover"); });
  dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
  dropZone.addEventListener("drop", e => {
    e.preventDefault();
    dropZone.classList.remove("dragover");
    const file = e.dataTransfer.files[0];
    if (file && file.type === "application/pdf") {
      fileInput.files = e.dataTransfer.files;
      fileNameEl.textContent = "Selected: " + file.name;
      extractBtn.disabled = false;
    }
  });

  function showStatus(msg, type) {
    const el = document.getElementById("status");
    el.textContent = msg;
    el.className = type;
    el.style.display = "block";
  }

  function catClass(cat) {
    const known = ["Retirement","Health","Dental","Vision","Disability"];
    return known.includes(cat) ? "cat-" + cat : "cat-Other";
  }

  async function extractBenefits() {
    const file = fileInput.files[0];
    if (!file) return;

    extractBtn.disabled = true;
    document.getElementById("extract-spinner").style.display = "inline-block";
    document.getElementById("extract-label").textContent = "Extracting…";
    document.getElementById("results").style.display = "none";
    showStatus("Uploading and analysing PDF with Claude — this may take 30–60 seconds…", "info");

    const form = new FormData();
    form.append("pdf", file);

    try {
      const res = await fetch("/extract", { method: "POST", body: form });
      const data = await res.json();

      if (!res.ok || data.error) {
        showStatus("Error: " + (data.error || res.statusText), "error");
        return;
      }

      extractedBenefits = data.benefits;
      renderTable(extractedBenefits);
      showStatus(`Extraction complete — ${extractedBenefits.length} benefit(s) found.`, "success");
    } catch (err) {
      showStatus("Request failed: " + err.message, "error");
    } finally {
      extractBtn.disabled = false;
      document.getElementById("extract-spinner").style.display = "none";
      document.getElementById("extract-label").textContent = "Extract Benefits";
    }
  }

  function renderTable(benefits) {
    const tbody = document.getElementById("results-body");
    tbody.innerHTML = benefits.map((b, i) => `
      <tr>
        <td style="color:#94a3b8;font-weight:600">${i + 1}</td>
        <td><strong>${esc(b.benefit_name || "—")}</strong></td>
        <td><span class="cat-badge ${catClass(b.category)}">${esc(b.category || "—")}</span></td>
        <td>${esc(b.eligibility || "—")}</td>
        <td>${esc(b.coverage_details || "—")}</td>
      </tr>
    `).join("");

    document.getElementById("count-badge").textContent = benefits.length + " benefits";
    document.getElementById("results").style.display = "block";
    document.getElementById("save-status").textContent = "";
  }

  function esc(str) {
    return String(str)
      .replace(/&/g,"&amp;").replace(/</g,"&lt;")
      .replace(/>/g,"&gt;").replace(/"/g,"&quot;");
  }

  async function saveToSupabase() {
    if (!extractedBenefits.length) return;

    const saveBtn = document.querySelector(".btn-green");
    saveBtn.disabled = true;
    document.getElementById("save-spinner").style.display = "inline-block";
    document.getElementById("save-label").textContent = "Saving…";
    document.getElementById("save-status").textContent = "";

    try {
      const res = await fetch("/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ benefits: extractedBenefits }),
      });
      const data = await res.json();

      if (!res.ok || data.error) {
        document.getElementById("save-status").innerHTML =
          '<span style="color:#b91c1c">❌ ' + (data.error || res.statusText) + "</span>";
      } else {
        document.getElementById("save-status").innerHTML =
          '<span style="color:#15803d">✅ ' + data.inserted + " row(s) saved to Supabase</span>";
      }
    } catch (err) {
      document.getElementById("save-status").innerHTML =
        '<span style="color:#b91c1c">❌ ' + err.message + "</span>";
    } finally {
      saveBtn.disabled = false;
      document.getElementById("save-spinner").style.display = "none";
      document.getElementById("save-label").textContent = "💾 Save to Supabase";
    }
  }
</script>
</body>
</html>
"""


def run_extraction(pdf_bytes: bytes) -> dict:
    pdf_data = base64.standard_b64encode(pdf_bytes).decode("utf-8")
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    prompt = """Analyze this benefits policy document and extract all benefits information in a structured format.

For each benefit, provide:
- benefit_name: the name of the benefit
- category: the category (e.g., Health, Dental, Vision, Life Insurance, Retirement, PTO, Disability, Wellness, Other)
- description: a concise description of what the benefit covers
- eligibility: who is eligible (if specified)
- coverage_details: key coverage amounts, limits, or percentages (if specified)
- enrollment_info: enrollment period or requirements (if specified)

Return a JSON object with a single key "benefits" containing an array of benefit objects."""

    with client.messages.stream(
        model="claude-opus-4-8",
        max_tokens=8000,
        thinking={"type": "adaptive"},
        messages=[{
            "role": "user",
            "content": [
                {
                    "type": "document",
                    "source": {"type": "base64", "media_type": "application/pdf", "data": pdf_data},
                },
                {"type": "text", "text": prompt},
            ],
        }],
    ) as stream:
        message = stream.get_final_message()

    text_content = next(
        (block.text for block in message.content if block.type == "text"), ""
    )
    start = text_content.find("{")
    end = text_content.rfind("}") + 1
    if start != -1 and end > start:
        return json.loads(text_content[start:end])
    return {"benefits": []}


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/extract", methods=["POST"])
def extract():
    if "pdf" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    pdf_file = request.files["pdf"]
    if not pdf_file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "File must be a PDF"}), 400

    try:
        result = run_extraction(pdf_file.read())
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/save", methods=["POST"])
def save():
    data = request.get_json()
    benefits = data.get("benefits", [])
    if not benefits:
        return jsonify({"error": "No benefits to save"}), 400

    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        result = supabase.table("benefits").insert(benefits).execute()
        return jsonify({"inserted": len(result.data)})
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=8080)
