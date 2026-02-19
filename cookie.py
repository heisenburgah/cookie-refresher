import requests
import os
import json
from datetime import datetime

# === CONFIG ===
HISTORY_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "HYDROXIDE", "processed")

# === COLORS ===
W = "\033[97m"
G = "\033[90m"
GR = "\033[32m"
R = "\033[31m"
C = "\033[36m"
Y = "\033[33m"
RST = "\033[0m"

BANNER = f"""{G}
    ____              __   _         ____       ____              __
   / ___/____  ____  / /__(_)__     / __ \\___  / __/_____  ___  / /_
  / /   / __ \\/ __ \\/ //_/ / _ \\  / /_/ / _ \\/ /_/ ___/ _ \\/ ___/ __ \\
 / /___/ /_/ / /_/ / ,< / /  __/ / _, _/  __/ __/ /  /  __(__  ) / / /
 \\____/\\____/\\____/_/|_/_/\\___/ /_/ |_|\\___/_/ /_/   \\___/____/_/ /_/
{RST}"""


# === BYPASS CLASS ===
class Bypass:
    def __init__(self, cookie: str) -> None:
        self.cookie = cookie

    def start_process(self) -> str:
        self.xcsrf_token = self.get_csrf_token()
        self.rbx_authentication_ticket = self.get_rbx_authentication_ticket()
        return self.get_set_cookie()

    def get_set_cookie(self) -> str:
        response = requests.post(
            "https://auth.roblox.com/v1/authentication-ticket/redeem",
            headers={"rbxauthenticationnegotiation": "1"},
            json={"authenticationTicket": self.rbx_authentication_ticket}
        )
        set_cookie_header = response.headers.get("set-cookie")
        if not set_cookie_header:
            raise ValueError("Failed to redeem authentication ticket")
        return set_cookie_header.split(".ROBLOSECURITY=")[1].split(";")[0]

    def get_rbx_authentication_ticket(self) -> str:
        response = requests.post(
            "https://auth.roblox.com/v1/authentication-ticket",
            headers={
                "rbxauthenticationnegotiation": "1",
                "referer": "https://www.roblox.com/camel",
                "Content-Type": "application/json",
                "x-csrf-token": self.xcsrf_token
            },
            cookies={".ROBLOSECURITY": self.cookie}
        )
        ticket = response.headers.get("rbx-authentication-ticket")
        if not ticket:
            raise ValueError("Failed to get authentication ticket (invalid cookie?)")
        return ticket

    def get_csrf_token(self) -> str:
        response = requests.post(
            "https://auth.roblox.com/v2/logout",
            cookies={".ROBLOSECURITY": self.cookie}
        )
        xcsrf_token = response.headers.get("x-csrf-token")
        if not xcsrf_token:
            raise ValueError("Failed to get CSRF token (invalid cookie?)")
        return xcsrf_token


# === HELPERS ===
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
        process = subprocess.Popen(["clip"], stdin=subprocess.PIPE)
        process.communicate(text.encode())
        return True
    except:
        return False


AM_PORT = 7963

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


# === ROBLOX LOOKUPS ===
ROGUE_PLACE_ID = 3016661674

ROGUE_BADGES = {
    2124634287: "Edict",
    2124634281: "Uber Class",
    2124634270: "Ultra Class",
    2124634267: "Super Class",
    2124503714: "World Traveller",
}


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


def account_lookup():
    show_header()
    cookie = input(f"  {W}Cookie {G}>{RST} ").strip()

    if not cookie:
        print(f"\n  {R}No cookie provided.{RST}")
        input(f"\n  {G}Press Enter to go back...{RST}")
        return

    print(f"\n  {G}Fetching account info...{RST}")
    info = get_account_info(cookie)

    if not info.get("name"):
        print(f"\n  {R}Invalid cookie or failed to fetch account.{RST}")
        input(f"\n  {G}Press Enter to go back...{RST}")
        return

    user_id = info["id"]
    username = info["name"]
    display = info.get("displayName", "")

    set_title(f"HYDROXIDE - {username}")
    show_header()

    account_age = get_account_age(user_id)

    print(f"  {W}Account Info{RST}\n")
    print(f"  {G}{'=' * 50}{RST}")
    print(f"  {W}Username:{RST}  {C}{username}{RST}")
    print(f"  {W}User ID:{RST}   {G}{user_id}{RST}")
    if display and display != username:
        print(f"  {W}Display:{RST}   {G}{display}{RST}")
    print(f"  {W}Created:{RST}   {G}{account_age}{RST}")
    print(f"  {G}{'=' * 50}{RST}")

    print_rogue_info(user_id, cookie)

    choice = input(f"\n  {W}[c]{RST} Copy cookie  {W}[Enter]{RST} Go back\n\n  {W}Select {G}>{RST} ").strip().lower()
    if choice == "c":
        if copy_to_clipboard(cookie):
            print(f"\n  {GR}Copied to clipboard!{RST}")
        else:
            print(f"\n  {R}Failed to copy.{RST}")
        input(f"\n  {G}Press Enter to go back...{RST}")


# === HISTORY ===
def save_to_history(username, user_id, display_name, old_cookie, new_cookie, badges_owned=None, account_age=None):
    os.makedirs(HISTORY_DIR, exist_ok=True)
    history_file = os.path.join(HISTORY_DIR, "history.json")

    history = []
    if os.path.exists(history_file):
        try:
            with open(history_file, "r") as f:
                history = json.load(f)
        except:
            history = []

    entry = {
        "username": username,
        "user_id": user_id,
        "display_name": display_name,
        "old_cookie": old_cookie,
        "new_cookie": new_cookie,
        "badges_owned": badges_owned or [],
        "account_age": account_age or "Unknown",
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

    # Deduplicate: update existing entry if same user_id, otherwise append
    existing_idx = None
    for i, h in enumerate(history):
        if h.get("user_id") == user_id:
            existing_idx = i
            break

    if existing_idx is not None:
        history[existing_idx] = entry
    else:
        history.append(entry)

    with open(history_file, "w") as f:
        json.dump(history, f, indent=2)


def load_history() -> list:
    history_file = os.path.join(HISTORY_DIR, "history.json")
    if not os.path.exists(history_file):
        return []
    try:
        with open(history_file, "r") as f:
            return json.load(f)
    except:
        return []


def show_history():
    show_header()
    history = load_history()

    if not history:
        print(f"  {G}No history found.{RST}")
        input(f"\n  {G}Press Enter to go back...{RST}")
        return

    print(f"  {W}Account History{RST}  {G}({len(history)} entries){RST}\n")

    for i, entry in enumerate(history):
        name = entry.get("username", "Unknown")
        uid = entry.get("user_id", "?")
        ts = entry.get("timestamp", "")
        print(f"  {W}[{i + 1}]{RST}  {C}{name}{RST}  {G}(ID: {uid}){RST}  {G}{ts}{RST}")

    print(f"\n  {G}Enter a number to view details, or 'b' to go back{RST}")
    choice = input(f"\n  {W}Select {G}>{RST} ").strip().lower()

    if choice == "b":
        return

    try:
        idx = int(choice) - 1
        if idx < 0 or idx >= len(history):
            print(f"\n  {R}Invalid selection.{RST}")
            input(f"\n  {G}Press Enter to go back...{RST}")
            return
    except ValueError:
        print(f"\n  {R}Invalid input.{RST}")
        input(f"\n  {G}Press Enter to go back...{RST}")
        return

    show_history_detail(history[idx])


def show_history_detail(entry: dict):
    show_header()
    name = entry.get("username", "Unknown")
    uid = entry.get("user_id", "?")
    display = entry.get("display_name", "")
    ts = entry.get("timestamp", "")

    set_title(f"HYDROXIDE - {name}")

    print(f"  {W}Account Details{RST}\n")
    print(f"  {G}{'=' * 50}{RST}")
    print(f"  {W}Username:{RST}   {C}{name}{RST}")
    print(f"  {W}User ID:{RST}    {G}{uid}{RST}")
    if display and display != name:
        print(f"  {W}Display:{RST}    {G}{display}{RST}")
    age = entry.get("account_age", "Unknown")
    print(f"  {W}Created:{RST}    {G}{age}{RST}")
    print(f"  {W}Refreshed:{RST}  {G}{ts}{RST}")
    print(f"  {G}{'=' * 50}{RST}")

    badges = entry.get("badges_owned", [])
    if badges:
        print(f"\n  {W}Rogue Lineage Badges:{RST}  {GR}{', '.join(badges)}{RST}")

    print(f"\n  {W}Original Cookie:{RST}\n")
    print_cookie(entry.get("old_cookie", "N/A"))

    print(f"\n  {W}Refreshed Cookie:{RST}\n")
    print_cookie(entry.get("new_cookie", "N/A"))

    choice = input(f"\n  {W}[1]{RST} Import to Account Manager\n  {W}[2]{RST} Copy refreshed cookie\n  {W}[Enter]{RST} Go back\n\n  {W}Select {G}>{RST} ").strip().lower()
    if choice == "1":
        import_to_account_manager(entry.get("new_cookie", ""))
        input(f"\n  {G}Press Enter to go back...{RST}")
    elif choice in ("2", "c"):
        if copy_to_clipboard(entry.get("new_cookie", "")):
            print(f"\n  {GR}Copied to clipboard!{RST}")
        else:
            print(f"\n  {R}Failed to copy.{RST}")
        input(f"\n  {G}Press Enter to go back...{RST}")


# === MAIN MENU ===
def show_menu():
    show_header()
    print(f"  {W}[1]{RST}  Refresh a cookie")
    print(f"  {W}[2]{RST}  Account history")
    print(f"  {W}[3]{RST}  Account lookup")
    print(f"  {W}[q]{RST}  Quit\n")
    return input(f"  {W}Select {G}>{RST} ").strip().lower()


def refresh_cookie():
    show_header()
    cookie = input(f"  {W}Cookie {G}>{RST} ").strip()

    if not cookie:
        print(f"\n  {R}No cookie provided.{RST}")
        input(f"\n  {G}Press Enter to retry...{RST}")
        return

    print(f"\n  {G}[1/4]{RST} Validating old cookie...")
    old_info = get_account_info(cookie)
    if old_info.get("name"):
        set_title(f"HYDROXIDE - {old_info['name']}")
        print(f"  {G}[---]{RST} Logged in as {C}{old_info['name']}{RST} {G}(ID: {old_info.get('id', '?')}){RST}")
    else:
        print(f"  {Y}[---]{RST} Could not verify old cookie (may still work)")

    try:
        print(f"  {G}[2/4]{RST} Fetching CSRF token...")
        bypasser = Bypass(cookie)
        bypasser.xcsrf_token = bypasser.get_csrf_token()

        print(f"  {G}[3/4]{RST} Getting authentication ticket...")
        bypasser.rbx_authentication_ticket = bypasser.get_rbx_authentication_ticket()

        print(f"  {G}[4/4]{RST} Redeeming new cookie...")
        new_cookie = bypasser.get_set_cookie()

        new_info = get_account_info(new_cookie)
        username = new_info.get("name") or old_info.get("name") or "Unknown"
        user_id = new_info.get("id") or old_info.get("id") or "?"
        display_name = new_info.get("displayName") or old_info.get("displayName") or ""

        age = get_account_age(user_id)
        badges = check_badges(user_id)
        badges_owned = [name for bid, (name, owned) in badges.items() if owned]
        save_to_history(username, user_id, display_name, cookie, new_cookie, badges_owned=badges_owned, account_age=age)

        show_header()
        print(f"  {GR}SUCCESS{RST}")
        print(f"  {G}{'=' * 50}{RST}")
        if username != "Unknown":
            set_title(f"HYDROXIDE - {username} (Done)")
            print(f"  {W}Account:{RST}  {C}{username}{RST}")
            print(f"  {W}User ID:{RST}  {G}{user_id}{RST}")
            if display_name and display_name != username:
                print(f"  {W}Display:{RST}  {G}{display_name}{RST}")
            print(f"  {W}Created:{RST}  {G}{age}{RST}")
        print(f"  {G}{'=' * 50}{RST}")

        print_rogue_info(user_id, new_cookie)

        print(f"\n  {W}Original Cookie:{RST}\n")
        print_cookie(cookie)

        print(f"\n  {W}New Cookie:{RST}\n")
        print_cookie(new_cookie)

        choice = input(f"\n  {W}[1]{RST} Import to Account Manager\n  {W}[2]{RST} Copy new cookie\n  {W}[Enter]{RST} Go back\n\n  {W}Select {G}>{RST} ").strip().lower()
        if choice == "1":
            import_to_account_manager(new_cookie)
            input(f"\n  {G}Press Enter to go back...{RST}")
        elif choice in ("2", "c"):
            if copy_to_clipboard(new_cookie):
                print(f"\n  {GR}Copied to clipboard!{RST}")
            else:
                print(f"\n  {R}Failed to copy.{RST}")
            input(f"\n  {G}Press Enter to go back...{RST}")

    except (ValueError, Exception) as e:
        print(f"\n  {R}ERROR:{RST} {e}")
        input(f"\n  {G}Press Enter to retry...{RST}")


def run():
    os.makedirs(HISTORY_DIR, exist_ok=True)
    while True:
        choice = show_menu()
        if choice == "1":
            refresh_cookie()
        elif choice == "2":
            show_history()
        elif choice == "3":
            account_lookup()
        elif choice == "q":
            break


if __name__ == "__main__":
    run()
