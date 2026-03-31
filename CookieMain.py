# https://hydroxide.solutions
# https://discord.gg/fnpNyCsG4u
# https://github.com/heisenburgah

import os
import subprocess
import sys


def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


try:
    import requests
except ImportError:
    print("Installing requests...")
    install("requests")

from modules.config import HISTORY_DIR, W, G, GR, R, C, Y, RST
from modules.bypass import Bypass
from modules.helpers import (
    show_header, set_title, print_cookie, copy_to_clipboard,
    import_to_account_manager, get_account_info, get_account_age,
    check_badges, print_rogue_info,
)
from modules.history import save_to_history, show_history
from modules.generator import generate_accounts


def show_menu():
    show_header()
    print(f"  {W}[1]{RST}  Refresh a cookie")
    print(f"  {W}[2]{RST}  Account history")
    print(f"  {W}[3]{RST}  Generate accounts")
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
            generate_accounts()
        elif choice == "q":
            break


if __name__ == "__main__":
    try:
        run()
    except KeyboardInterrupt:
        print()

