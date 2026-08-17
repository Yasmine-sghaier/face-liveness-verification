from fastapi import FastAPI
from app.routes.verify import router as verify_router  # ça doit matcher le router
from fastapi.middleware.cors import CORSMiddleware
from app.services.face_service import warmup_face_model
import os
import threading
app = FastAPI()
app.include_router(verify_router)



app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def startup_warmup_face_model():
    if os.getenv("IDENTITY_WARMUP_ON_STARTUP", "true").strip().lower() not in {"1", "true", "yes", "on"}:
        print("[identity_ai_service] Face model warmup skipped (IDENTITY_WARMUP_ON_STARTUP disabled)")
        return

    def _run_warmup() -> None:
        try:
            warmup_face_model()
            print("[identity_ai_service] Face model warmup OK")
        except Exception as exc:
            print(f"[identity_ai_service] Face model warmup failed: {exc}")

    # Avoid blocking API readiness on model download / initialization.
    threading.Thread(target=_run_warmup, daemon=True).start()

