import os
import requests

from config import (
    W, G, GR, R, C, Y, RST,
    BANNER, AM_PORT, ROGUE_PLACE_ID, ROGUE_BADGES,
)


# === UI ===
def clear():
    os.system("cls" if os.name == "nt" else "clear")


def set_title(title: str):
    if os.name == "nt":
        os.system(f"title {title}")
    else:
        print(f"\033]0;{title}\007", end="", flush=True)


def show_header():
    clear()
    set_title("HYDROXIDE")
    print(BANNER)
    print(f"  {G}Roblox .ROBLOSECURITY Cookie Refresher{RST}")
    print(f"  {G}--------------------------------------{RST}\n")


def copy_to_clipboard(text: str) -> bool:
    try:
        import subprocess
        cmd = ["clip"] if os.name == "nt" else ["pbcopy"]
        process = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        process.communicate(text.encode())
        return True
    except:
        return False


def import_to_account_manager(cookie: str):
    try:
        resp = requests.get(
            f"http://localhost:{AM_PORT}/ImportCookie",
            params={"Cookie": cookie},
            timeout=5
        )
        if resp.status_code == 200:
            print(f"\n  {GR}Imported to Account Manager!{RST}")
        else:
            print(f"\n  {R}Import failed (status {resp.status_code}).{RST}")
    except requests.exceptions.ConnectionError:
        print(f"\n  {R}Could not connect to Account Manager on port {AM_PORT}.{RST}")
        print(f"  {Y}Open Account Manager > Settings (cog) > Developer tab{RST}")
        print(f"  {Y}Enable Web Server and set port to {AM_PORT}.{RST}")
    except Exception as e:
        print(f"\n  {R}Import failed: {e}{RST}")


def print_cookie(cookie: str):
    width = 80
    for i in range(0, len(cookie), width):
        print(f"    {cookie[i:i+width]}")


def print_progress(current, total, percent, status):
    bar_width = 30
    filled = int(bar_width * percent / 100)
    bar = f"{GR}{'|' * filled}{G}{'-' * (bar_width - filled)}{RST}"
    print(f"\r  [{current}/{total}] {bar}  {percent:3d}%  {status:<35}", end="", flush=True)


# === ROBLOX API ===
def get_account_info(cookie: str) -> dict:
    try:
        resp = requests.get(
            "https://users.roblox.com/v1/users/authenticated",
            cookies={".ROBLOSECURITY": cookie}
        )
        if resp.status_code == 200:
            return resp.json()
    except:
        pass
    return {}


def check_game_owned(user_id, cookie: str) -> bool:
    try:
        resp = requests.get(
            f"https://inventory.roblox.com/v1/users/{user_id}/items/1/{ROGUE_PLACE_ID}/is-owned",
            cookies={".ROBLOSECURITY": cookie}
        )
        if resp.status_code == 200:
            return resp.json() == True
    except:
        pass
    return False


def check_badges(user_id) -> dict:
    badge_ids = ",".join(str(b) for b in ROGUE_BADGES.keys())
    try:
        resp = requests.get(
            f"https://badges.roblox.com/v1/users/{user_id}/badges/awarded-dates?badgeIds={badge_ids}"
        )
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            owned = {item["badgeId"] for item in data}
            return {bid: (name, bid in owned) for bid, name in ROGUE_BADGES.items()}
    except:
        pass
    return {bid: (name, False) for bid, name in ROGUE_BADGES.items()}


def get_avatar_thumbnail(user_id) -> str:
    try:
        resp = requests.get(
            f"https://thumbnails.roblox.com/v1/users/avatar-headshot?userIds={user_id}&size=150x150&format=Png"
        )
        if resp.status_code == 200:
            data = resp.json().get("data", [])
            if data:
                return data[0].get("imageUrl", "")
    except:
        pass
    return ""


def get_account_age(user_id) -> str:
    try:
        resp = requests.get(f"https://users.roblox.com/v1/users/{user_id}")
        if resp.status_code == 200:
            created = resp.json().get("created", "")
            if created:
                from datetime import datetime as dt
                created_dt = dt.fromisoformat(created.replace("Z", "+00:00"))
                age = (dt.now(created_dt.tzinfo) - created_dt).days
                return f"{created[:10]} ({age} days)"
    except:
        pass
    return "Unknown"


def print_rogue_info(user_id, cookie: str = None):
    badges = check_badges(user_id)
    print(f"\n  {W}Rogue Lineage Badges:{RST}")
    for bid, (name, owned) in badges.items():
        status = f"{GR}Owned{RST}" if owned else f"{G}--{RST}"
        print(f"    {C}{name:<16}{RST} {status}")
