import os

# === DIRECTORIES ===
if os.name == "nt":
    HISTORY_DIR = os.path.join(os.environ.get("LOCALAPPDATA", os.path.expanduser("~")), "HYDROXIDE", "processed")
else:
    HISTORY_DIR = os.path.join(os.path.expanduser("~"), "Library", "Application Support", "HYDROXIDE", "processed")

SIGNUP_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "roblox-auto-signup-main")

# === BROWSER ===
# Chrome 137+ removed --load-extension for branded Chrome builds.
# Chromium (open-source) still supports it, so we use it to load NopeCHA.
_PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
if os.name == "nt":
    CHROMIUM_PATH = None  # TODO: download Ungoogled Chromium for Windows
else:
    CHROMIUM_PATH = "/Applications/Chromium.app/Contents/MacOS/Chromium"

NOPECHA_EXT_DIR = os.path.join(_PROJECT_DIR, "roblox-auto-signup-main", "lib", "NopeCHA")

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

# === ACCOUNT MANAGER ===
AM_PORT = 7963

# === ROGUE LINEAGE ===
ROGUE_PLACE_ID = 3016661674

ROGUE_BADGES = {
    2124634287: "Edict",
    2124634281: "Uber Class",
    2124634270: "Ultra Class",
    2124634267: "Super Class",
    2124503714: "World Traveller",
}
