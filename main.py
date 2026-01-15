from fastapi import FastAPI, Query, Request, requests
from fastapi.responses import RedirectResponse
from urllib.parse import urlparse, urlencode

STEAM_OPENID_URL = "https://steamcommunity.com/openid/login"
BOT_USERNAME = "nj_steam_checker_bot"  # имя твоего Telegram бота
BASE_URL = "https://steam-login-for-bot.fly.dev"  # публичный URL FastAPI

app = FastAPI()

@app.get("/steam/login")
async def steamlogin(tg_id: int = Query(..., description="Telegram user ID")):
    return_to = f"{BASE_URL}/steam/callback?tg_id={tg_id}"

    params = {
        "openid.ns": "http://specs.openid.net/auth/2.0",
        "openid.mode": "checkid_setup",
        "openid.return_to": return_to,
        "openid.realm": BASE_URL,
        "openid.identity": "http://specs.openid.net/auth/2.0/identifier_select",
        "openid.claimed_id": "http://specs.openid.net/auth/2.0/identifier_select",
    }

    steam_url = f"{STEAM_OPENID_URL}?{urlencode(params)}"
    return RedirectResponse(steam_url)

@app.get("/steam/callback")
async def steamcallback(request: Request, tg_id: int):
    params = dict(request.query_params)

    params_check = params.copy()
    params_check["openid.mode"] = "check_authentication"
    resp = requests.post("https://steamcommunity.com/openid/login", data=params_check)

    if "is_valid:true" not in resp.text:
        return {"error": "Steam OpenID verification failed"}

    claimed_id = params.get("openid.claimed_id")
    match = re.search(r"/id/(\d+)$", claimed_id)
    if not match:
        return {"error": "SteamID not found"}
    steam_id = match.group(1)

    deep_link = f"https://t.me/{BOT_USERNAME}?start=steamlinked_{steam_id}_{tg_id}"
    return RedirectResponse(deep_link)