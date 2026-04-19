import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from endpoints import router

app = FastAPI(title="SIG-Lynx Server")

# Folder Configuration
UPLOAD_FOLDER = "uploads"
WEB_FOLDER = "web"
ASSETS_FOLDER = os.path.join(WEB_FOLDER, "assets")

# Ensure directories exist
for folder in [UPLOAD_FOLDER, WEB_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static directories
app.mount("/web", StaticFiles(directory=WEB_FOLDER), name="web")
if os.path.exists(ASSETS_FOLDER):
    app.mount("/assets", StaticFiles(directory=ASSETS_FOLDER), name="assets")
app.mount("/uploads", StaticFiles(directory=UPLOAD_FOLDER), name="uploads")

app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    # reload=False is safer for applications utilizing rclpy and background threads
    print("[SERVER] Launching SIG-Lynx Web Interface on port 8000...")
    uvicorn.run("launch_server:app", host="0.0.0.0", port=8000, reload=False)
