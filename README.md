# HYDROXIDE - Cookie Refresher

**Website:** [hydroxide.solutions](https://hydroxide.solutions) | **Discord:** [discord.gg/fnpNyCsG4u](https://discord.gg/fnpNyCsG4u)

A CLI tool for refreshing Roblox `.ROBLOSECURITY` cookies and generating new accounts with automatic captcha solving.

https://github.com/user-attachments/assets/c49a5a49-70e0-4771-abb3-32be0b32f4e6

## Features

- **Cookie Refresh** - Generate a new `.ROBLOSECURITY` cookie from an existing one
- **Stella Integration** - Queries Stella for in-game build info (class, race, edict, artifacts, etc.)
- **Account Generation** - Create new Roblox accounts with optional email verification
- **Captcha Solving** - Automatic FunCaptcha solving via NopeCHA extension
- **Account History** - Tracks all refreshed accounts with deduplication
- **Clipboard Copy** - Copy any cookie to clipboard instantly
- **Account Manager Import** - Import cookies directly into Roblox Account Manager

## Requirements

- Python 3.10+
- [Chromium](https://www.chromium.org/) browser (required for account generation with captcha solving)

### Python Dependencies

```
pip install requests
```

DrissionPage and pymailtm are auto-installed on first use if missing.

### Installing Chromium (macOS)

```
brew install --cask chromium
xattr -cr /Applications/Chromium.app
```

Chromium is needed because Google Chrome 137+ removed `--load-extension` support from branded builds. Chromium (open-source) still supports loading extensions like NopeCHA directly.

## Usage

```
python CookieMain.py
```

### Menu Options

| Option | Description |
|--------|-------------|
| `1` | Refresh a cookie |
| `2` | View account history |
| `3` | Generate accounts |
| `q` | Quit |

### Cookie Refresh

Paste an existing `.ROBLOSECURITY` cookie to generate a fresh one. Shows account info, creation date, and Stella build info (class, race, artifacts, server status, etc.).

### Account Generation

Creates new Roblox accounts automatically:

1. Choose how many accounts to generate
2. Choose whether to verify with email (recommended)
3. Enter a NopeCHA API key (or press Enter for the default key)

The generator:
- Opens Chromium with the NopeCHA extension loaded
- Fills the Roblox signup form (handles both classic and new React page layouts)
- NopeCHA automatically solves the FunCaptcha
- Retries up to 3 times if the captcha fails
- Optionally verifies the account via temp email
- Saves the `.ROBLOSECURITY` cookie to history

#### NopeCHA

[NopeCHA](https://nopecha.com/) is used for automatic captcha solving. Get a free API key at https://nopecha.com/manage (200 free solves/day on the Starter plan).

### Account Manager Integration

After refreshing a cookie or generating accounts, you can import directly into [Roblox Account Manager](https://github.com/ic3w0lf22/Roblox-Account-Manager):

1. Open Account Manager
2. Click the **Settings** cog
3. Go to the **Developer** tab
4. Enable **Web Server** and set the port to `7963`

## Project Structure

```
CookieMain.py           - Entry point: menu, cookie refresh, main loop
modules/
  config.py             - Constants, colors, paths
  bypass.py             - Cookie refresh via auth ticket redemption
  helpers.py            - UI utilities + Roblox API lookups
  history.py            - History CRUD + display
  generator.py          - Account generation with browser automation
```

## Data Storage

| Platform | Path |
|----------|------|
| macOS | `~/Library/Application Support/HYDROXIDE/processed/` |
| Windows | `%LOCALAPPDATA%\HYDROXIDE\processed\` |

## Credits

- [roblox-auto-signup](https://github.com/qing762/roblox-auto-signup) by Qing762

## License

Licensed under the GNU General Public License v3.0. See [LICENSE](LICENSE) for details.
