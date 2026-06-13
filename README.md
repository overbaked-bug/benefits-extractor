# Benefits Extractor

A web app that uses Claude AI to extract structured benefits data from PDF policy documents and saves it to Supabase.

## Features

- Upload any benefits policy PDF via drag-and-drop
- Claude AI parses and structures the benefits data automatically
- View extracted benefits in a clean table (name, category, eligibility, coverage details)
- Save results directly to a Supabase database

## Screenshots

<!-- Add screenshots here -->

## Setup

1. Clone the repo and enter the project directory:
   ```bash
   git clone https://github.com/YOUR_USERNAME/benefits-extractor.git
   cd benefits-extractor/benefits-extractor
   ```

2. Install dependencies:
   ```bash
   pip install flask anthropic supabase python-dotenv
   ```

3. Copy `.env.example` to `.env` and fill in your credentials:
   ```bash
   cp .env.example .env
   ```

   | Variable | Description |
   |---|---|
   | `ANTHROPIC_API_KEY` | Your Anthropic API key |
   | `SUPABASE_URL` | Your Supabase project URL |
   | `SUPABASE_KEY` | Your Supabase service role key |
   | `SUPABASE_PROJECT_REF` | Your Supabase project ref |

4. Create the `benefits` table in your Supabase SQL editor:
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

5. Run the app:
   ```bash
   python app.py
   ```

6. Open [http://localhost:8080](http://localhost:8080) in your browser.

## Tech Stack

- **Backend:** Python, Flask
- **AI:** Claude (Anthropic)
- **Database:** Supabase (PostgreSQL)
- **Frontend:** Vanilla HTML/CSS/JS
