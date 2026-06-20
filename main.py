from src.caption_chain.base import generate_caption
import os
import shutil
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse

app = FastAPI(title="Image Caption API")

UPLOAD_DIR = "temp_uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}

MAX_FILE_SIZE_MB = 5


@app.get("/")
def health_check():
    """Simple endpoint to confirm the API is running"""
    return {
        "status": "ok",
        "message": "Image Caption API is running"
    }

@app.post("/caption")
async def caption_image(file: UploadFile = File(...)):
    """
    Accepts an image upload, runs it through the vision -> retrieval -> caption pipeline, and returns the description, retrieved style examples, and the final caption.
    """

    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type 'ext'. Allowed: {ALLOWED_EXTENSIONS}"
        )
    
    temp_filename = f"{uuid.uuid4().hex}{ext}"
    temp_path = os.path.join(UPLOAD_DIR, temp_filename)

    try:
        with open(temp_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        file_size_mb = os.path.getsize(temp_path) / (1024*1024)

        if file_size_mb > MAX_FILE_SIZE_MB:
            raise HTTPException(
                status_code=400,
                detail=f"File too large ({file_size_mb:.1f}MB). Max size: {MAX_FILE_SIZE_MB}MB",
            )
        result = generate_caption(temp_path)
        return JSONResponse(content=result)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Pipeline error: {str(e)}")
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
        