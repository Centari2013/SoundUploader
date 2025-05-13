import os
import mimetypes
from pathlib import Path
from pydub.utils import mediainfo
from pprint import pprint

def extract_path_parts(full_path, root_dir):
    """Extracts bucket and relative path based on root_dir"""
    p = Path(full_path).resolve()
    root = Path(root_dir).resolve()
    
    try:
        relative = p.relative_to(root)
        parts = relative.parts
        bucket = parts[0] if len(parts) > 1 else None
        path = "/" + "/".join(parts[1:-1]) if len(parts) > 2 else "/"
        return bucket, path
    except ValueError:
        return None, None

def extract_metadata_from_directory(root_dir):
    all_data = []

    for root, _, files in os.walk(root_dir):
        for file in files:
            if file.startswith("."):
                continue  # skip hidden/system files

            path = os.path.join(root, file)
            mime_type, _ = mimetypes.guess_type(path)
            size = os.path.getsize(path)

            try:
                info = mediainfo(path)
                duration = float(info.get("duration", 0.0)) / 1000.0
            except Exception:
                duration = 0.0

            bucket, rel_path = extract_path_parts(path, root_dir)
            
            all_data.append({
                "path": f"{rel_path}/{file}",
                "bucket": bucket,
                "tags": [],  # will populate later
                "duration_seconds": round(duration, 3),
                "size": size,
                "mime_type": mime_type or "unknown",
                "cone_inner": None,
                "cone_outer": None
            })
            pprint(all_data[len(all_data) - 1])
    return all_data
