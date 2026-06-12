class ApiError(RuntimeError):
    def __init__(self, status_code: int, url: str, body: str) -> None:
        super().__init__(f"HTTP {status_code} — {url}")
        self.status_code = status_code
        self.url = url
        self.body = body
