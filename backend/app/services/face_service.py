import os
from deepface import DeepFace


MODEL_NAME = os.getenv("IDENTITY_MODEL_NAME", "VGG-Face")
DETECTOR_BACKEND = os.getenv("IDENTITY_DETECTOR_BACKEND", "opencv")
DISTANCE_METRIC = os.getenv("IDENTITY_DISTANCE_METRIC", "cosine")


class FaceNotDetectedError(ValueError):
    pass


def _ensure_face_detected(image_path: str) -> None:
    try:
        faces = DeepFace.extract_faces(
            img_path=image_path,
            detector_backend=DETECTOR_BACKEND,
            enforce_detection=True,
            align=True,
        )
    except Exception as exc:
        raise FaceNotDetectedError("No human face detected") from exc

    if not faces:
        raise FaceNotDetectedError("No human face detected")


def warmup_face_model():
    # Warmup avoids first-request latency spikes that can trigger backend timeout.
    DeepFace.build_model(MODEL_NAME)


def verify_faces(profile_path, live_path):
    _ensure_face_detected(profile_path)
    _ensure_face_detected(live_path)

    result = DeepFace.verify(
        profile_path,
        live_path,
        model_name=MODEL_NAME,
        detector_backend=DETECTOR_BACKEND,
        distance_metric=DISTANCE_METRIC,
        # Faces were already validated above; avoid a third strict detection pass.
        enforce_detection=False,
    )

    distance = result["distance"]
    threshold = result["threshold"]

    # calcul score confiance (0 → 100)
    confidence = max(0, min(100, int((1 - distance) * 100)))

    return {
        "verified": result["verified"],
        "distance": distance,
        "threshold": threshold,
        "confidence": confidence
    }