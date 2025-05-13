import json
import subprocess
import re
from pprint import pprint
import os

TAGGED_FILE_PATH = os.environ.get('TAGGED_OUTPUT_FILE')
METADATA_FILE_PATH = os.environ.get('RAW_METADATA_FILE_PATH')

def extract_json(response):
    # Strip triple backtick code blocks if present
    match = re.search(r'\{[\s\S]*?\}', response)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return None

# ai_prompt_builder.py
def build_prompt(metadata):
    return f"""You are an expert at organizing sound libraries.

Given the following audio metadata, return:
- 5 to 10 descriptive tags (lowercase, no spaces, use underscores)
- A short, clean, user-friendly display name (e.g. "Waterfall Flow", "Construction Ambience")

Filename rules:
- Capitalize each word
- Use plain English only
- No special characters (no underscores, hyphens, quotes, etc.)
- Add spaces between words as needed
- Shorten long names for clarity

Output ONLY valid JSON with two keys: "tags" and "name"

Metadata:
{metadata}
"""


def run_ollama_prompt(prompt):
    result = subprocess.run(
        ["ollama", "run", "gemma3"],
        input=prompt,
        capture_output=True,
        text=True,
        timeout=60
    )
    if result.returncode != 0:
        print(f"Ollama error: {result.stderr}")
        return ""
    return result.stdout.strip()

def suggest_for_metadata(metadata_path, output_path):
    with open(metadata_path) as f:
        data = json.load(f)

    results = []
    for item in data:
        prompt = build_prompt(json.dumps(item, indent=2))
        print(f"Running AI for: {item['path']}")
        raw_response = run_ollama_prompt(prompt)
        suggestion = extract_json(raw_response)
        if suggestion:
            item.update(suggestion)
            results.append(item)
            pprint(item)
        else:
            print(f"Bad AI output for {item['path']}: {raw_response}")
    with open(output_path, "w") as out:
        json.dump(results, out, indent=2)

suggest_for_metadata(METADATA_FILE_PATH, TAGGED_FILE_PATH)
