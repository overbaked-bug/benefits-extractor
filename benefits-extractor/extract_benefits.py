import base64
import json
import sys
import anthropic
from dotenv import load_dotenv

load_dotenv()


def extract_benefits(pdf_path: str) -> dict:
    with open(pdf_path, "rb") as f:
        pdf_data = base64.standard_b64encode(f.read()).decode("utf-8")

    client = anthropic.Anthropic()

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
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "document",
                        "source": {
                            "type": "base64",
                            "media_type": "application/pdf",
                            "data": pdf_data,
                        },
                    },
                    {"type": "text", "text": prompt},
                ],
            }
        ],
    ) as stream:
        message = stream.get_final_message()

    # Extract text content from response
    text_content = next(
        (block.text for block in message.content if block.type == "text"), ""
    )

    # Parse JSON from response
    start = text_content.find("{")
    end = text_content.rfind("}") + 1
    if start != -1 and end > start:
        result = json.loads(text_content[start:end])
    else:
        result = {"raw_response": text_content}

    return result


def main():
    pdf_path = sys.argv[1] if len(sys.argv) > 1 else "benefits_policy.pdf"

    print(f"Extracting benefits from: {pdf_path}\n")
    result = extract_benefits(pdf_path)

    if "benefits" in result:
        benefits = result["benefits"]
        print(f"Found {len(benefits)} benefit(s):\n")
        for i, benefit in enumerate(benefits, 1):
            print(f"{i}. {benefit.get('benefit_name', 'Unknown')}")
            print(f"   Category: {benefit.get('category', 'N/A')}")
            print(f"   Description: {benefit.get('description', 'N/A')}")
            if benefit.get("eligibility"):
                print(f"   Eligibility: {benefit['eligibility']}")
            if benefit.get("coverage_details"):
                print(f"   Coverage: {benefit['coverage_details']}")
            if benefit.get("enrollment_info"):
                print(f"   Enrollment: {benefit['enrollment_info']}")
            print()
    else:
        print(json.dumps(result, indent=2))

    output_path = "benefits_extracted.json"
    with open(output_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"Full results saved to: {output_path}")


if __name__ == "__main__":
    main()
