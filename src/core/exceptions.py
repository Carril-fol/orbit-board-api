class DomainError(Exception):
    status_code: int = 400
    detail: str = "Bad request"

    def __init__(self, detail: str | None = None):
        if detail:
            self.detail = detail
        super().__init__(self.detail)


class DatabaseUnavailable(DomainError):
    status_code = 503
    detail = "Database unavailable"
