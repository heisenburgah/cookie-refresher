import os
import sys
import json
import re
import asyncio
from datetime import datetime

from config import HISTORY_DIR, SIGNUP_DIR, CHROMIUM_PATH, NOPECHA_EXT_DIR, W, G, GR, R, C, Y, RST
from helpers import show_header, print_progress, copy_to_clipboard, import_to_account_manager


def save_generated_account(username, password, email, email_password, cookie, verified):
    os.makedirs(HISTORY_DIR, exist_ok=True)
    gen_file = os.path.join(HISTORY_DIR, "generated_accounts.json")

    accounts = []
    if os.path.exists(gen_file):
        try:
            with open(gen_file, "r") as f:
                accounts = json.load(f)
        except:
            accounts = []

    entry = {
        "username": username,
        "password": password,
        "email": email,
        "email_password": email_password,
        "cookie": cookie,
        "verified": verified,
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    accounts.append(entry)

    with open(gen_file, "w") as f:
        json.dump(accounts, f, indent=2)


def generate_accounts():
    show_header()
    print(f"  {W}Generate Accounts{RST}\n")

    count_str = input(f"  {W}How many accounts? {G}>{RST} ").strip()
    if not count_str:
        count_str = "1"
    try:
        count = int(count_str)
        if count <= 0:
            print(f"\n  {R}Must be a positive number.{RST}")
            input(f"\n  {G}Press Enter to go back...{RST}")
            return
    except ValueError:
        print(f"\n  {R}Invalid number.{RST}")
        input(f"\n  {G}Press Enter to go back...{RST}")
        return

    verify_input = input(f"  {W}Verify with email? (y/n) {G}>{RST} ").strip().lower()
    verify = verify_input in ("y", "yes", "")

    default_key = "I-DTLJG52UVWRP"
    nopecha_key = input(f"  {W}NopeCHA API key (Enter for default) {G}>{RST} ").strip()
    if not nopecha_key:
        nopecha_key = default_key
    if nopecha_key and not re.match(r'^[a-zA-Z0-9_-]+$', nopecha_key):
        print(f"\n  {Y}Invalid API key format, skipping.{RST}")
        nopecha_key = ""

    try:
        from DrissionPage import Chromium, ChromiumOptions
        from DrissionPage import errors as dp_errors
    except ImportError:
        print(f"\n  {Y}Installing DrissionPage...{RST}")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "DrissionPage"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            from DrissionPage import Chromium, ChromiumOptions
            from DrissionPage import errors as dp_errors
            print(f"  {GR}DrissionPage installed!{RST}")
        except Exception as e:
            print(f"  {R}Failed to install DrissionPage: {e}{RST}")
            input(f"\n  {G}Press Enter to go back...{RST}")
            return

    try:
        sys.path.insert(0, SIGNUP_DIR)
        from lib.lib import Main as SignupMain
    except ImportError:
        print(f"\n  {Y}Installing pymailtm...{RST}")
        try:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pymailtm"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            sys.path.insert(0, SIGNUP_DIR)
            from lib.lib import Main as SignupMain
            print(f"  {GR}pymailtm installed!{RST}")
        except Exception as e:
            print(f"  {R}Failed to install pymailtm: {e}{RST}")
            input(f"\n  {G}Press Enter to go back...{RST}")
            return
    finally:
        if SIGNUP_DIR in sys.path:
            sys.path.remove(SIGNUP_DIR)

    print(f"\n  {G}Starting generation...{RST}\n")

    results = []
    try:
        asyncio.run(_generate_accounts_async(
            results, count, verify, nopecha_key,
            Chromium, ChromiumOptions, dp_errors, SignupMain
        ))
    except KeyboardInterrupt:
        print(f"\n\n  {Y}Interrupted.{RST}")

    _show_generation_results(results)


async def _generate_accounts_async(results, count, verify, nopecha_key, Chromium, ChromiumOptions, dp_errors, SignupMain):
    lib = SignupMain()
    password = "Qing762.chy"

    for x in range(count):
        result = {
            "username": None, "email": None, "email_password": None,
            "cookie": None, "verified": False, "error": None
        }
        chrome = None
        page = None
        max_captcha_retries = 3

        # Generate username
        print_progress(x + 1, count, 10, "Generating username")
        username = lib.usernameCreator(None, scrambled=True)
        result["username"] = username

        # Generate temp email
        email = None
        email_password = None
        emailID = None
        if verify:
            print_progress(x + 1, count, 20, "Generating temp email")
            try:
                email, email_password, token, emailID = await lib.generateEmail(password)
                result["email"] = email
                result["email_password"] = email_password
            except Exception as e:
                result["error"] = f"Email generation failed: {str(e) or type(e).__name__}"
                print_progress(x + 1, count, 100, "Failed (email)")
                print()
                results.append(result)
                continue

        for attempt in range(max_captcha_retries):
            chrome = None
            page = None

            try:
                # Set up browser
                print_progress(x + 1, count, 30, f"Setting up browser{f' (retry {attempt})' if attempt else ''}")
                co = ChromiumOptions()
                co.set_argument("--lang", "en")
                co.mute(True)
                co.auto_port()
                if nopecha_key:
                    # Chrome 137+ removed --load-extension for branded Chrome.
                    # Use Chromium (open-source) which still supports it.
                    if CHROMIUM_PATH and os.path.exists(CHROMIUM_PATH):
                        co.set_browser_path(CHROMIUM_PATH)
                    co.add_extension(NOPECHA_EXT_DIR)
                else:
                    co.incognito()

                # Open browser and fill signup form
                print_progress(x + 1, count, 40, "Filling signup form")
                chrome = Chromium(addr_or_opts=co)
                page = chrome.latest_tab
                page.set.window.max()

                if nopecha_key:
                    page.get(f"https://nopecha.com/setup#{nopecha_key}")
                    await asyncio.sleep(2)
                page.get("https://www.roblox.com/CreateAccount")

                # Dismiss cookie banner
                try:
                    page.ele('@class=btn-cta-lg cookie-btn btn-primary-md btn-min-width', timeout=3).click()
                except dp_errors.ElementNotFoundError:
                    pass

                # Wait for form to render and detect page version
                page.ele("#signup-username", timeout=15)
                await asyncio.sleep(1)

                is_classic = page.run_js('return !!document.getElementById("MonthDropdown")')
                current_month = datetime.now().month
                current_day = datetime.now().day
                current_year = datetime.now().year - 19

                if is_classic:
                    page.run_js(f'document.getElementById("MonthDropdown").selectedIndex = {current_month}')
                    page.run_js('document.getElementById("MonthDropdown").dispatchEvent(new Event("change", {bubbles: true}))')
                    page.run_js(f'document.getElementById("DayDropdown").selectedIndex = {current_day}')
                    page.run_js('document.getElementById("DayDropdown").dispatchEvent(new Event("change", {bubbles: true}))')
                    page.run_js(f'var y=document.getElementById("YearDropdown"); for(var i=0;i<y.options.length;i++){{if(y.options[i].value=="{current_year}"){{y.selectedIndex=i;break;}}}}')
                    page.run_js('document.getElementById("YearDropdown").dispatchEvent(new Event("change", {bubbles: true}))')
                else:
                    page.run_js('document.querySelector("button[aria-label=\'Month\']").click()')
                    await asyncio.sleep(0.3)
                    page.run_js(f'document.querySelectorAll("[role=option]")[{current_month - 1}].click()')
                    await asyncio.sleep(0.3)

                    page.run_js('document.querySelector("button[aria-label=\'Day\']").click()')
                    await asyncio.sleep(0.3)
                    page.run_js(f'document.querySelectorAll("[role=option]")[{current_day - 1}].click()')
                    await asyncio.sleep(0.3)

                    page.run_js('document.querySelector("button[aria-label=\'Year\']").click()')
                    await asyncio.sleep(0.3)
                    page.run_js(f'var o=document.querySelectorAll("[role=option]"); for(var i=0;i<o.length;i++){{if(o[i].textContent.trim()=="{current_year}"){{o[i].click();break;}}}}')
                    await asyncio.sleep(0.3)

                page.ele("#signup-username", timeout=10).input(username)
                page.ele("#signup-password", timeout=10).input(password)
                await asyncio.sleep(1)

                if is_classic:
                    try:
                        page.ele('@@id=signup-checkbox@@class=checkbox').click()
                    except dp_errors.ElementNotFoundError:
                        pass

                await asyncio.sleep(1.5)
                if is_classic:
                    page.run_js('document.getElementById("signup-button").click()')
                else:
                    page.run_js('document.querySelector("button[type=submit]").click()')

                # Wait for captcha or redirect
                if nopecha_key:
                    print_progress(x + 1, count, 55, f"Waiting (NopeCHA){f' attempt {attempt+1}/{max_captcha_retries}' if attempt else ''}")
                    try:
                        page.wait.url_change("https://www.roblox.com/home", timeout=300)
                    except Exception:
                        pass
                else:
                    print_progress(x + 1, count, 55, "Waiting for redirect")
                    try:
                        page.wait.url_change("https://www.roblox.com/home", timeout=120)
                    except Exception:
                        pass

                try:
                    current_url = page.url.lower()
                except Exception:
                    current_url = ""

                if "home" in current_url:
                    break  # Success — continue to cookie extraction

                # Captcha failed — retry with fresh browser
                print_progress(x + 1, count, 55, f"Captcha failed, retrying ({attempt+1}/{max_captcha_retries})")
                print()

            except Exception as e:
                result["error"] = str(e) or type(e).__name__

            finally:
                try:
                    if chrome:
                        chrome.quit()
                        chrome = None
                        page = None
                except Exception:
                    pass
        else:
            # All retries exhausted
            if not result["error"]:
                result["error"] = f"Captcha not solved after {max_captcha_retries} attempts"
            print_progress(x + 1, count, 100, "Failed (captcha)")
            print()
            results.append(result)
            continue

        try:
            print_progress(x + 1, count, 70, "Signup complete")

            # Email verification
            if verify and email:
                print_progress(x + 1, count, 75, "Starting email verification")
                try:
                    page.ele(".btn-primary-md btn-primary-md btn-min-width", timeout=5).click()
                    if page.ele("@@class=phone-verification-nonpublic-text text-description font-caption-body", timeout=3):
                        page.get("https://www.roblox.com/my/account#!/info")
                        page.ele("@@class=account-field-edit-action@@text()=Add Email", timeout=10).click()
                        await asyncio.sleep(0.5)
                        page.ele("@@id=emailAddress@@name=userInfo.emailAddress@@type=email@@class=form-control input-field@@placeholder=Enter email@@autocomplete=off", timeout=10).input(email)
                        page.ele("@@class=modal-full-width-button btn-primary-md btn-min-width@@text()=Add Email", timeout=10).click()
                        await asyncio.sleep(0.5)
                    elif page.ele(". form-control input-field verification-upsell-modal-input", timeout=3):
                        page.ele(". form-control input-field verification-upsell-modal-input").input(email)
                        page.ele(".modal-button verification-upsell-btn btn-cta-md btn-min-width").click()
                    elif page.ele(".form-control input-field verification-upsell-modal-input", timeout=3):
                        page.ele(".form-control input-field verification-upsell-modal-input").input(email)
                        page.ele(".modal-button verification-upsell-btn btn-cta-md btn-min-width").click()
                except dp_errors.ElementNotFoundError:
                    pass

                # Poll for verification email
                print_progress(x + 1, count, 80, "Waiting for verification email")
                link = None
                for _attempt in range(30):
                    try:
                        messages = lib.fetchVerification(email, email_password, emailID)
                        if messages and len(messages) > 0:
                            msg = messages[0]
                            body = getattr(msg, 'text', None)
                            if not body and hasattr(msg, 'html') and msg.html and len(msg.html) > 0:
                                body = msg.html[0]
                            if body:
                                match = re.search(r'https://www\.roblox\.com/account/settings/verify-email\?ticket=[^\s)"]+', body)
                                if match:
                                    link = match.group(0)
                                    break
                    except Exception:
                        pass
                    await asyncio.sleep(5)

                if link:
                    print_progress(x + 1, count, 85, "Clicking verification link")
                    page.get(link)
                    result["verified"] = True

            # Extract cookies
            print_progress(x + 1, count, 90, "Extracting cookies")
            for cookie_item in page.cookies():
                if cookie_item["name"] == ".ROBLOSECURITY":
                    result["cookie"] = cookie_item["value"]
                    break

            if result["cookie"]:
                save_generated_account(
                    result["username"], password,
                    result["email"], result["email_password"],
                    result["cookie"], result["verified"]
                )

            print_progress(x + 1, count, 100, "Complete")
            print()

        except Exception as e:
            result["error"] = str(e) or type(e).__name__
            print_progress(x + 1, count, 100, "Failed")
            print()

        finally:
            try:
                if chrome:
                    chrome.quit()
            except Exception:
                pass

        results.append(result)



def _show_generation_results(results):
    show_header()

    if not results:
        print(f"  {G}No accounts were generated.{RST}")
        input(f"\n  {G}Press Enter to go back...{RST}")
        return

    success = sum(1 for r in results if r["cookie"])
    failed = len(results) - success

    print(f"  {W}Generation Complete{RST}\n")
    print(f"  {G}{'=' * 50}{RST}")
    print(f"  {GR}Successfully created: {success}/{len(results)}{RST}    {R if failed else G}Failed: {failed}/{len(results)}{RST}")
    print(f"  {G}{'=' * 50}{RST}\n")

    print(f"  {W}#   Username          Email                     Status{RST}")
    print(f"  {G}{'─' * 55}{RST}")

    for i, r in enumerate(results):
        num = str(i + 1)
        if r["cookie"]:
            uname = (r["username"] or "Unknown")[:16]
            em = (r["email"] or "--")[:24]
            status = f"{GR}Verified{RST}" if r["verified"] else f"{C}Created{RST}"
            print(f"  {W}{num:<4}{RST}{C}{uname:<18}{RST}{G}{em:<26}{RST}{status}")
        else:
            err = r.get("error") or "Unknown error"
            print(f"  {W}{num:<4}{RST}{R}{'FAILED':<18}{RST}{R}{err[:50]}{RST}")

    if success > 0:
        print(f"\n  {G}Accounts saved to history.{RST}")

    print(f"\n  {W}[1]{RST} Import all to Account Manager")
    print(f"  {W}[2]{RST} Copy all cookies")
    print(f"  {W}[Enter]{RST} Go back\n")

    choice = input(f"  {W}Select {G}>{RST} ").strip()

    cookies = [r["cookie"] for r in results if r["cookie"]]

    if choice == "1":
        for c in cookies:
            import_to_account_manager(c)
        input(f"\n  {G}Press Enter to go back...{RST}")
    elif choice == "2":
        if cookies:
            all_cookies = "\n".join(cookies)
            if copy_to_clipboard(all_cookies):
                print(f"\n  {GR}Copied {len(cookies)} cookie(s) to clipboard!{RST}")
            else:
                print(f"\n  {R}Failed to copy.{RST}")
        else:
            print(f"\n  {R}No cookies to copy.{RST}")
        input(f"\n  {G}Press Enter to go back...{RST}")
