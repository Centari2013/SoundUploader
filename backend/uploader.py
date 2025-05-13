# backend/uploader.py
import os
import json
import mimetypes
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
BUCKET_NAME = "your-audio-bucket"  # Adjust as needed
UPLOAD_DIR = os.environ.get("WATCH_DIRECTORY")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def upload_to_supabase():
    approved_path = os.environ.get("APPROVED_FILE_PATH")
    if not os.path.exists(approved_path):
        print("No approved sounds to upload.")
        return

    with open(approved_path) as f:
        approved = json.load(f)

    for entry in approved:
        file_path = os.path.join(UPLOAD_DIR, entry["path"].lstrip("/"))
        if not os.path.exists(file_path):
            print(f"Missing file: {file_path}")
            continue

        with open(file_path, "rb") as f:
            file_data = f.read()

        mime_type = mimetypes.guess_type(file_path)[0] or "application/octet-stream"
        dest_path = f'{entry["bucket"]}/{os.path.basename(entry["path"])}'

        print(f"Uploading: {dest_path}")
        upload_resp = supabase.storage.from_(entry["bucket"]).upload(
            path=dest_path,
            file=file_data,
            file_options={"content-type": mime_type, "upsert": True},
        )

        if upload_resp.get("error"):
            print(f"Upload failed: {upload_resp['error']['message']}")
            continue

        db_resp = supabase.table("sound_files").insert({
            "path": entry["path"],
            "name": entry["name"],
            "bucket": entry["bucket"],
            "tags": entry["tags"],
            "duration_seconds": entry.get("duration_seconds"),
            "size": entry.get("size"),
            "mime_type": mime_type,
            "cone_inner": entry.get("cone_inner"),
            "cone_outer": entry.get("cone_outer")
        }).execute()

        if db_resp.get("error"):
            print(f"DB insert failed: {db_resp['error']['message']}")
        else:
            print("✓ Upload + DB insert successful.")

if __name__ == "__main__":
    upload_to_supabase()
