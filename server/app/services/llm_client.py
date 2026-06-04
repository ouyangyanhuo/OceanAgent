"""OpenAI 兼容 LLM 客户端。

使用 httpx 调用 OpenAI 兼容的 /chat/completions 接口。
支持 JSON、纯文本和流式三种输出模式，带重试和超时处理。
"""

import json
import logging
from collections.abc import Generator
from typing import Any

import httpx

from app.core.errors import LLMError

logger = logging.getLogger(__name__)

# 默认系统提示，约束 LLM 行为。
_DEFAULT_SYSTEM = "你是一个海洋知识图谱分析助手。请严格按照要求输出。"


class LLMClient:
    """OpenAI 兼容 LLM 客户端，使用 httpx 同步调用。"""

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        timeout: int = 60,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.model = model
        self.timeout = timeout

    def chat_json(
        self,
        user_prompt: str,
        system_prompt: str = _DEFAULT_SYSTEM,
        temperature: float = 0.2,
    ) -> dict[str, Any]:
        """调用 chat/completions，强制 JSON 输出，返回解析后的 dict。

        使用 response_format=json_object 确保 LLM 输出合法 JSON。
        解析失败时自动重试一次，将错误信息反馈给 LLM。
        """
        body: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "response_format": {"type": "json_object"},
        }

        # 第一次尝试
        raw = self._call_completions(body)
        result = self._parse_json_response(raw)
        if result is not None:
            return result

        # 解析失败，用错误信息重试一次
        logger.warning("LLM JSON 解析失败，重试中。原始响应: %s", raw[:500])
        body["messages"].append({"role": "assistant", "content": raw})
        body["messages"].append({
            "role": "user",
            "content": "你的上一条回复不是合法 JSON。请严格只输出一个 JSON 对象，不要包含任何其他文字。",
        })
        raw = self._call_completions(body)
        result = self._parse_json_response(raw)
        if result is not None:
            return result

        raise LLMError(
            f"LLM 返回的内容无法解析为 JSON。原始响应: {raw[:300]}",
            code="LLM_JSON_PARSE_ERROR",
        )

    def chat_text(
        self,
        user_prompt: str,
        system_prompt: str = _DEFAULT_SYSTEM,
        temperature: float = 0.5,
    ) -> str:
        """调用 chat/completions，返回纯文本。"""
        body: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
        }
        raw = self._call_completions(body)
        if not raw:
            raise LLMError("LLM 返回空内容", code="LLM_EMPTY_RESPONSE")
        return raw

    def chat_text_stream(
        self,
        user_prompt: str,
        system_prompt: str = _DEFAULT_SYSTEM,
        temperature: float = 0.5,
    ) -> Generator[str, None, None]:
        """调用 chat/completions 流式接口，逐块 yield content 文本。

        使用 stream=True 参数，OpenAI 兼容接口会返回 SSE 格式的增量内容。
        每行格式为 data: {json}，最后一个 data: [DONE] 标记结束。
        """
        body: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "stream": True,
        }
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                with client.stream("POST", url, json=body, headers=headers) as resp:
                    resp.raise_for_status()
                    for line in resp.iter_lines():
                        if not line or not line.startswith("data: "):
                            continue
                        data_str = line[6:]  # 去掉 "data: " 前缀
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except (json.JSONDecodeError, IndexError, KeyError):
                            continue
        except httpx.TimeoutException:
            raise LLMError(
                f"LLM 流式请求超时 ({self.timeout}s)",
                code="LLM_TIMEOUT",
            )
        except httpx.HTTPStatusError as exc:
            raise LLMError(
                f"LLM HTTP 错误: {exc.response.status_code} - {exc.response.text[:300]}",
                code="LLM_HTTP_ERROR",
            )
        except httpx.RequestError as exc:
            raise LLMError(
                f"LLM 请求失败: {exc}",
                code="LLM_REQUEST_ERROR",
            )

    def _call_completions(self, body: dict[str, Any]) -> str:
        """发送 HTTP 请求到 /chat/completions 并返回 content 文本。"""
        url = f"{self.base_url}/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        try:
            with httpx.Client(timeout=self.timeout) as client:
                resp = client.post(url, json=body, headers=headers)
                resp.raise_for_status()
        except httpx.TimeoutException:
            raise LLMError(
                f"LLM 请求超时 ({self.timeout}s)",
                code="LLM_TIMEOUT",
            )
        except httpx.HTTPStatusError as exc:
            raise LLMError(
                f"LLM HTTP 错误: {exc.response.status_code} - {exc.response.text[:300]}",
                code="LLM_HTTP_ERROR",
            )
        except httpx.RequestError as exc:
            raise LLMError(
                f"LLM 请求失败: {exc}",
                code="LLM_REQUEST_ERROR",
            )

        try:
            data = resp.json()
        except ValueError:
            raise LLMError(
                f"LLM 返回非 JSON 响应: {resp.text[:300]}",
                code="LLM_INVALID_RESPONSE",
            )

        # 标准 OpenAI 响应结构
        choices = data.get("choices", [])
        if not choices:
            raise LLMError("LLM 响应中无 choices", code="LLM_NO_CHOICES")

        return choices[0].get("message", {}).get("content", "")

    @staticmethod
    def _parse_json_response(text: str) -> dict[str, Any] | None:
        """尝试将 LLM 输出解析为 JSON。

        支持处理 LLM 偶尔输出的 ```json ... ``` 包裹格式。
        解析失败返回 None。
        """
        if not text:
            return None

        cleaned = text.strip()

        # 去掉可能的 ```json ... ``` 包裹
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            # 去掉首尾的 ``` 行
            if lines[0].startswith("```"):
                lines = lines[1:]
            if lines and lines[-1].strip() == "```":
                lines = lines[:-1]
            cleaned = "\n".join(lines).strip()

        try:
            result = json.loads(cleaned)
            if isinstance(result, dict):
                return result
            return None
        except (json.JSONDecodeError, ValueError):
            return None
