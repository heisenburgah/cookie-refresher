import os
import json
from datetime import datetime

from modules.config import HISTORY_DIR, W, G, GR, R, C, RST
from modules.helpers import show_header, set_title, print_cookie, copy_to_clipboard, import_to_account_manager


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
