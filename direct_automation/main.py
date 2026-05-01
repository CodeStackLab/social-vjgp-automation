from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

# Mount static and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Path to store received credentials
DATA_DIR = "/app/data"
os.makedirs(DATA_DIR, exist_ok=True)
CREDENTIALS_FILE = os.path.join(DATA_DIR, "social_credentials.json")

@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse(request, "index.html")

@app.get("/api/status/{platform}")
async def get_status(platform: str):
    # Check .env first
    if platform == "facebook":
        connected = bool(os.getenv("FACEBOOK_PAGE_ACCESS_TOKEN"))
    elif platform == "instagram":
        connected = bool(os.getenv("INSTAGRAM_BUSINESS_ACCOUNT_ID"))
    else:
        connected = False
    
    return {"platform": platform, "connected": connected}

@app.get("/auth-callback")
async def handle_callback(
    request: Request,
    code: str = Query(None),
    state: str = Query(None),
    error: str = Query(None)
):
    timestamp = datetime.now().isoformat()
    
    if error:
        return HTMLResponse(content=f"<h1>Error</h1><p>{error}</p>", status_code=400)
    
    if not code:
        return HTMLResponse(content="<h1>Error</h1><p>No code received</p>", status_code=400)

    # Save the received code and state
    data = {
        "timestamp": timestamp,
        "code": code,
        "state": state,
        "params": dict(request.query_params)
    }
    
    # In a real scenario, we'd exchange the code for a token here.
    # For now, we save it so the user can see it works.
    with open(CREDENTIALS_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")

    return HTMLResponse(content=f"""
        <div style="font-family: sans-serif; text-align: center; padding: 50px;">
            <h1 style="color: #4CAF50;">Success!</h1>
            <p>Your social account has been successfully linked to <b>vjgu.online</b>.</p>
            <p>We have captured your authentication code. You can close this window now.</p>
            <div style="margin-top: 20px; color: #666; font-size: 12px;">
                Received at: {timestamp}
            </div>
        </div>
    """)

@app.get("/")
async def root():
    return {"status": "running", "service": "Direct Automation Listener"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
