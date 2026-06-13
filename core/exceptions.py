class ApiError(RuntimeError):
    def __init__(self, status_code: int, url: str, body: str) -> None:
        snippet = body[:200] + "…" if len(body) > 200 else body
        super().__init__(f"HTTP {status_code} — {url}\n{snippet}")
        self.status_code = status_code
        self.url = url
        self.body = body
