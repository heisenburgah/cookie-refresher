# https://hydroxide.solutions
# https://discord.gg/fnpNyCsG4u
# https://github.com/heisenburgah

import os
import requests

from modules.config import (
    W, G, GR, R, C, Y, RST,
    BANNER, AM_PORT, ROGUE_PLACE_ID, ROGUE_BADGES,
    STELLA_API_URL, STELLA_API_TOKEN,
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
    print(f"  {G}--------------------------------------{RST}")
    print(f"  {C}hydroxide.solutions{RST}  {G}|{RST}  {C}discord.gg/fnpNyCsG4u{RST}  {G}|{RST}  {C}github.com/heisenburgah{RST}\n")


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


def get_stella_info(user_id) -> dict:
    if not STELLA_API_URL or not STELLA_API_TOKEN:
        return {}
    try:
        resp = requests.get(
            f"{STELLA_API_URL.rstrip('/')}/api/player/lookup",
            params={"roblox_id": str(user_id)},
            headers={"Authorization": f"Bearer {STELLA_API_TOKEN}"},
            timeout=10,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get("player", {})
    except:
        pass
    return {}


def print_stella_info(user_id, info=None):
    if info is None:
        info = get_stella_info(user_id)
    if not info:
        return

    print(f"\n  {W}Stella Build Info:{RST}")

    char_name = info.get("first_name", "")
    house = info.get("house", "")
    is_lord = info.get("is_lord", False)
    is_male = info.get("is_male", True)
    prefix = ("Lord " if is_male else "Lady ") if is_lord else ""
    full_name = f"{prefix}{char_name} {house}".strip()
    if full_name:
        print(f"    {C}{'Character':<16}{RST} {full_name}")

    fields = [
        ("Class", "class"),
        ("Subclass", "subclass"),
        ("Race", "race"),
        ("Edict", "edict"),
        ("Artifact", "artifacts"),
        ("Spec", "spec"),
        ("Gender", "gender"),
        ("Dye", "dye"),
        ("Vampire", "vampire"),
    ]
    for label, key in fields:
        val = info.get(key)
        if val:
            print(f"    {C}{label:<16}{RST} {val}")

    remarks = info.get("remarks")
    if remarks:
        print(f"    {C}{'Remarks':<16}{RST} {', '.join(remarks)}")

    blessings = info.get("blessings")
    if blessings:
        print(f"    {C}{'Blessings':<16}{RST} {blessings}")

    server = info.get("server")
    if server:
        srv_name = server.get("name", "Unknown")
        region = server.get("region", "?")
        players = server.get("players", "?")
        max_p = server.get("max_players", "?")
        print(f"    {C}{'Server':<16}{RST} {srv_name} | {region} | {players}/{max_p}")
    else:
        print(f"    {C}{'Server':<16}{RST} {G}Not in a server{RST}")

    last_updated = info.get("last_updated")
    if last_updated:
        print(f"    {G}Updated: {last_updated}{RST}")
