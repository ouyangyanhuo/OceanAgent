class AppError(Exception):
    code = "APP_ERROR"

    def __init__(self, detail: str, code: str | None = None) -> None:
        super().__init__(detail)
        self.detail = detail
        if code:
            self.code = code


class NotFoundError(AppError):
    code = "NOT_FOUND"


class ValidationError(AppError):
    code = "VALIDATION_ERROR"


class LLMError(AppError):
    code = "LLM_ERROR"


class GraphWriteError(AppError):
    code = "GRAPH_WRITE_ERROR"
