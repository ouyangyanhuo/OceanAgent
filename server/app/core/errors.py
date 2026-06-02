"""业务异常定义。

路由层不直接拼错误响应，而是抛出这些异常，由 main.py 注册的异常处理器统一转换。
"""


class AppError(Exception):
    """业务异常基类。

    detail 面向开发者和前端排查，code 面向前端判断错误类型。
    """

    code = "APP_ERROR"

    def __init__(self, detail: str, code: str | None = None) -> None:
        super().__init__(detail)
        self.detail = detail
        if code:
            self.code = code


class NotFoundError(AppError):
    """资源不存在，例如节点、边、快照文件不存在。"""

    code = "NOT_FOUND"


class ValidationError(AppError):
    """业务输入或 LLM 候选结果不符合约束。"""

    code = "VALIDATION_ERROR"


class LLMError(AppError):
    """LLM 调用失败或返回无法解析。"""

    code = "LLM_ERROR"


class GraphWriteError(AppError):
    """图谱写入失败。当前暂未细分使用，预留给后续持久化错误处理。"""

    code = "GRAPH_WRITE_ERROR"
