from fastapi import FastAPI, HTTPException
from starlette.responses import RedirectResponse
import redis
import os

# --- ⚙️ CONFIGURATION ---
# The app will get the Redis URL from an environment variable set by Render in Phase 3.
REDIS_URL = "redis://red-d2p99ld6ubrc73c2o3s0:6379"
# ⬇️ PASTE YOUR WHATSAPP LINK HERE
REAL_WHATSAPP_LINK = "https://chat.whatsapp.com/JoUH2CBoPvjLkgVKQvPP24?mode=ems_share_c"
# --- END OF CONFIGURATION ---

app = FastAPI()
r = None

# This function runs when the server starts up
@app.on_event("startup")
def startup_event():
    global r
    try:
        r = redis.from_url(REDIS_URL, decode_responses=True)
        r.ping()
        print("✅ Successfully connected to Redis.")
    except Exception as e:
        print(f"❌ FATAL: Could not connect to Redis on startup. Error: {e}")
        r = None

@app.get("/invite/{token}")
def handle_invite(token: str):
    """Handles clicks, validates the token against Redis, and redirects."""
    if not r:
        raise HTTPException(status_code=503, detail="Service is temporarily unavailable.")

    if r.exists(token):
        current_clicks = r.hincrby(token, "clicks", 1)
        if current_clicks == 1:
            print(f"✅ SUCCESS: Token '{token}' validated. Redirecting...")
            return RedirectResponse(url=REAL_WHATSAPP_LINK)
        else:
            print(f"⚠️ DENIED: Token '{token}' has already been used.")
            raise HTTPException(status_code=403, detail="This invitation link has expired.")
    else:
        print(f"❌ DENIED: Invalid token '{token}' was provided.")
        raise HTTPException(status_code=404, detail="Invalid invitation link.")