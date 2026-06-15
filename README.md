# Benefits Extractor

> An AI-powered web app that reads employee benefits PDFs and turns them into structured, searchable data — built with Claude AI, Flask, and Supabase.

---

## The Problem

HR benefits documents are dense, inconsistent PDFs. Employees and administrators waste time hunting for coverage limits, eligibility rules, and enrollment deadlines buried across dozens of pages.

## The Solution

Benefits Extractor lets you drop in any benefits policy PDF and get back a clean, structured breakdown in seconds — automatically categorized and ready to save to a database.

---

## How It Works

1. User uploads a PDF through the drag-and-drop interface
2. The PDF is sent to Claude (Anthropic's AI) which reads and extracts every benefit
<img width="1377" height="646" alt="Screenshot 2026-06-15 at 6 26 14 pm" src="https://github.com/user-attachments/assets/ab98a4b3-530b-4052-a09c-3f6d79724f2a" />
3. Results are returned as structured JSON and displayed in a sortable table
<img width="866" height="734" alt="Screenshot 2026-06-15 at 6 27 52 pm" src="https://github.com/user-attachments/assets/fecda1ba-feb7-416e-ae96-b49fc869a322" />
4. User can save the extracted data to Supabase with one click

<img width="215" height="59" alt="Screenshot 2026-06-15 at 6 28 17 pm" src="https://github.com/user-attachments/assets/e27b9569-e2aa-4c52-9c81-f56118691bb1" />

<img width="1142" height="654" alt="Screenshot 2026-06-15 at 6 29 12 pm" src="https://github.com/user-attachments/assets/3e4bd2ab-645d-4b6b-a383-d60d512a637b" />

---

## Features

- Drag-and-drop PDF upload (up to 32 MB)
- AI extraction of benefit name, category, eligibility, and coverage details
- Clean results table with color-coded benefit categories
- One-click save to Supabase (PostgreSQL)
- Fully responsive, no frontend framework dependencies

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, Flask |
| AI / LLM | Claude (`claude-opus-4-8`) via Anthropic API |
| Database | Supabase (PostgreSQL) |
| Frontend | Vanilla HTML, CSS, JavaScript |
| Auth / Config | python-dotenv, environment variables |

---

## Local Setup

**Prerequisites:** Python 3.9+, an [Anthropic API key](https://console.anthropic.com/), and a [Supabase](https://supabase.com/) project.

```bash
git clone https://github.com/overbaked-bug/benefits-extractor.git
cd benefits-extractor/benefits-extractor
pip install flask anthropic supabase python-dotenv
cp .env.example .env   # then fill in your credentials
```

Create the `benefits` table in your Supabase SQL editor:

```sql
CREATE TABLE IF NOT EXISTS benefits (
    id BIGSERIAL PRIMARY KEY,
    benefit_name TEXT,
    category TEXT,
    description TEXT,
    eligibility TEXT,
    coverage_details TEXT,
    enrollment_info TEXT
);
```

Run the app:

```bash
python app.py
```

Open [http://localhost:8080](http://localhost:8080).

---

## Project Structure

```
benefits-extractor/
├── app.py                  # Flask server + routes + frontend HTML
├── extract_benefits.py     # Standalone CLI extraction script
├── save_to_supabase.py     # Standalone script to seed DB from JSON
├── .env.example            # Environment variable template
└── benefits_extracted.json # Sample output
```

---

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:

| Variable | Description |
|---|---|
| `ANTHROPIC_API_KEY` | Your Anthropic API key |
| `SUPABASE_URL` | Your Supabase project URL |
| `SUPABASE_KEY` | Your Supabase service role key |
| `SUPABASE_PROJECT_REF` | Your Supabase project reference ID |
