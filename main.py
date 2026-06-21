import os
import shutil
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException, status, Request, Depends
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from src.vector_store.base import build_vector_store
from src.config.env import API_KEY_VAR

security_scheme = HTTPBearer()

def verify_api_key(credentials: HTTPAuthorizationCredentials = Depends(security_scheme)):
    token = credentials.credentials
    # Replace this with your actual key validation or database check
    if not token.startswith("github_pat"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing token",
        )
    return token

# print(API_KEY)

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Building vector store on startup...")
    build_vector_store()
    print("Vector store ready.")
    yield
    # (nothing needed on shutdown)

app = FastAPI(title="Image Caption API", lifespan=lifespan)




# Middleware to extract the key from headers and assign it to the context
@app.middleware("http")
async def extract_api_key_middleware(request: Request, call_next):
    # Expecting header: "Authorization: Bearer YOUR_API_KEY"
    auth_header = request.headers.get("Authorization")

  
    
    if auth_header and auth_header.startswith("Bearer "):
        api_key = auth_header.split(" ")[1]
    else:
        # Fallback if you pass it as a custom header like X-API-Key
        api_key = request.headers.get("X-API-Key", "")
    print('API', api_key)

    # Set the token for the duration of this specific request execution
    token_token = API_KEY_VAR.set(api_key)
    try:
        response = await call_next(request)
        return response
    finally:
        # Clean up after the request finishes
        API_KEY_VAR.reset(token_token)


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
async def caption_image(file: UploadFile = File(...), token:str = Depends(verify_api_key)):
    """
    Accepts an image upload, runs it through the vision -> retrieval -> caption pipeline, and returns the description, retrieved style examples, and the final caption.
    """
    from src.caption_chain.base import generate_caption

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

@app.get('/security')
def lock_route(token:str = Depends(verify_api_key)):
  return {"result": token}
        