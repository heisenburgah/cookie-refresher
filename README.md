# HYDROXIDE - Cookie Refresher

A CLI tool for refreshing Roblox `.ROBLOSECURITY` cookies via authentication ticket redemption.

## Features

- **Cookie Refresh** - Generate a new `.ROBLOSECURITY` cookie from an existing one
- **Account Lookup** - View account info, creation date, and Rogue Lineage badges from a cookie
- **Account History** - Tracks all refreshed accounts with deduplication (one entry per account)
- **Clipboard Copy** - Copy any cookie to clipboard instantly
- **Account Manager Import** - Import refreshed cookies directly into Roblox Account Manager via its local web API

## Requirements

```
pip install requests
```

## Usage

```
python cookie.py
```

### Menu Options

| Option | Description |
|--------|-------------|
| `1` | Refresh a cookie |
| `2` | View account history |
| `3` | Account lookup |
| `q` | Quit |

### Account Manager Integration

After refreshing a cookie, you can import it directly into [Roblox Account Manager](https://github.com/ic3w0lf22/Roblox-Account-Manager) by selecting `[1] Import to Account Manager`.

Requires the Account Manager web server to be enabled:

1. Open Account Manager
2. Click the **Settings** cog
3. Go to the **Developer** tab
4. Enable **Web Server** and set the port to `7963`

## History

Refresh history is stored locally at:

```
%LOCALAPPDATA%\HYDROXIDE\processed\history.json
```
