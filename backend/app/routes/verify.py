from fastapi import APIRouter, UploadFile, File, Form
from fastapi.responses import JSONResponse
from app.services.face_service import FaceNotDetectedError, verify_faces
import os
import shutil
import tempfile
import base64
import requests
from io import BytesIO
from PIL import Image

router = APIRouter()  # <-- important, c’est ça que tu importes

UPLOADS_DIR = "uploads/"
# créer dossier si n'existe pas
if not os.path.exists(UPLOADS_DIR):
    os.makedirs(UPLOADS_DIR)


def _guess_suffix(upload: UploadFile) -> str:
    filename = upload.filename or ""
    _, ext = os.path.splitext(filename)
    ext = ext.lower()
    return ext if ext in {".jpg", ".jpeg", ".png", ".webp", ".avif"} else ".png"


def _save_temp_upload(upload: UploadFile, prefix: str) -> str:
    suffix = _guess_suffix(upload)
    fd, temp_path = tempfile.mkstemp(prefix=prefix, suffix=suffix, dir=UPLOADS_DIR)
    os.close(fd)

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(upload.file, buffer)

    try:
        upload.file.seek(0)
    except Exception:
        pass

    return temp_path


def _profile_suffix_from_reference(profile_image: str) -> str:
    if profile_image.startswith("data:image/jpeg"):
        return ".jpg"
    if profile_image.startswith("data:image/avif"):
        return ".avif"
    if profile_image.startswith("data:image/webp"):
        return ".webp"
    if profile_image.startswith("data:image/png"):
        return ".png"

    lowered = profile_image.lower().split("?")[0]
    _, ext = os.path.splitext(lowered)
    return ext if ext in {".jpg", ".jpeg", ".png", ".webp", ".avif"} else ".png"


def _save_profile_image_from_reference(profile_image: str) -> str:
    value = (profile_image or "").strip()
    if not value:
        raise ValueError("profile_image is empty")

    if value.startswith("data:image"):
        marker = "base64,"
        marker_index = value.find(marker)
        if marker_index <= 0:
            raise ValueError("Invalid data URL for profile_image")

        encoded = value[marker_index + len(marker):]
        binary = base64.b64decode(encoded)

        # Convert data URL payloads to PNG so DeepFace/OpenCV can read them reliably.
        fd, temp_path = tempfile.mkstemp(prefix="profile_", suffix=".png", dir=UPLOADS_DIR)
        os.close(fd)
        try:
            with Image.open(BytesIO(binary)) as image:
                image.convert("RGB").save(temp_path, format="PNG")
        except Exception as exc:
            try:
                os.remove(temp_path)
            except Exception:
                pass
            raise ValueError(f"Unable to decode profile_image data URL: {exc}")

        return temp_path

    suffix = _profile_suffix_from_reference(value)
    fd, temp_path = tempfile.mkstemp(prefix="profile_", suffix=suffix, dir=UPLOADS_DIR)
    os.close(fd)

    if value.startswith("http://") or value.startswith("https://"):
        response = requests.get(value, timeout=20)
        response.raise_for_status()
        with open(temp_path, "wb") as f:
            f.write(response.content)
        return temp_path

    if os.path.exists(value):
        shutil.copyfile(value, temp_path)
        return temp_path

    raise ValueError("Unsupported profile_image format")


@router.post("/verify")
async def verify(
    live_file: UploadFile = File(default=None),
    profile_image: str = Form(default=None),
    profile_file: UploadFile = File(default=None),
    file: UploadFile = File(default=None),
):
    # Backward compatibility: legacy clients send only "file".
    if live_file is None and file is not None:
        live_file = file

    if live_file is None:
        return JSONResponse(
            status_code=400,
            content={"error": "live_file is required"},
        )

    live_path = None
    profile_path = None

    try:
        live_path = _save_temp_upload(live_file, "live_")

        if profile_image is not None and profile_image.strip() != "":
            profile_path = _save_profile_image_from_reference(profile_image)
        elif profile_file is not None:
            profile_path = _save_temp_upload(profile_file, "profile_")
        else:
            return JSONResponse(
                status_code=400,
                content={"error": "profile_image is required"},
            )

        result = verify_faces(profile_path, live_path)
    except FaceNotDetectedError:
        return JSONResponse(
            status_code=200,
            content={
                "verified": False,
                "distance": None,
                "threshold": None,
                "confidence": 0,
                "reason": "no_face_detected",
            },
        )
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
    finally:
        for temp_path in [live_path, profile_path]:
            if temp_path and isinstance(temp_path, str) and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except Exception:
                    pass

    return result