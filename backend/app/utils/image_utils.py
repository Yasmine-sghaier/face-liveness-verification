import os
import uuid

UPLOAD_DIR = "uploads"

def save_upload_file(file):
    if not os.path.exists(UPLOAD_DIR):
        os.makedirs(UPLOAD_DIR)

    filename = f"{uuid.uuid4()}.jpg"
    filepath = os.path.join(UPLOAD_DIR, filename)

    with open(filepath, "wb") as f:
        f.write(file.file.read())

    return filepath