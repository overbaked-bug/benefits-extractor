import json
import os
import sys
import httpx
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
PROJECT_REF = os.getenv("SUPABASE_PROJECT_REF")

CREATE_TABLE_SQL = """
CREATE TABLE IF NOT EXISTS benefits (
    id BIGSERIAL PRIMARY KEY,
    benefit_name TEXT,
    category TEXT,
    description TEXT,
    eligibility TEXT,
    coverage_details TEXT,
    enrollment_info TEXT
);
"""


def create_table():
    """Attempt table creation via Supabase Management API."""
    response = httpx.post(
        f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query",
        headers={
            "Authorization": f"Bearer {SUPABASE_KEY}",
            "Content-Type": "application/json",
        },
        json={"query": CREATE_TABLE_SQL},
        timeout=15,
    )
    return response.status_code == 200, response


def main():
    with open("benefits_extracted.json") as f:
        data = json.load(f)

    benefits = data["benefits"]
    print(f"Loaded {len(benefits)} benefits from benefits_extracted.json")

    # Try to create table via Management API
    print("\nAttempting to create 'benefits' table...")
    ok, resp = create_table()
    if ok:
        print("Table created (or already exists).")
    else:
        print(f"Management API returned {resp.status_code} — table may already exist, or needs manual creation.")
        print("\nIf the table doesn't exist yet, run this SQL in your Supabase SQL Editor")
        print(f"(https://supabase.com/dashboard/project/{PROJECT_REF}/sql/new):\n")
        print(CREATE_TABLE_SQL)

    # Insert rows
    print("\nInserting rows...")
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    try:
        result = supabase.table("benefits").insert(benefits).execute()
        inserted = len(result.data)
        print(f"Done. {inserted} row(s) inserted into 'benefits'.")
    except Exception as e:
        error_msg = str(e)
        if "42P01" in error_msg or "does not exist" in error_msg:
            print("\nThe 'benefits' table does not exist yet.")
            print(f"Please create it via the Supabase SQL Editor at:")
            print(f"  https://supabase.com/dashboard/project/{PROJECT_REF}/sql/new")
            print("\nRun this SQL:\n")
            print(CREATE_TABLE_SQL)
            print("\nThen re-run this script.")
        else:
            print(f"\nInsertion failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
