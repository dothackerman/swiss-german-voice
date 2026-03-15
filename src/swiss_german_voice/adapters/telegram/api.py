from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen


class TelegramApiError(RuntimeError):
    """Raised for Telegram Bot API transport or payload failures."""


class TelegramBotApi:
    def __init__(self, token: str, timeout_seconds: int = 30) -> None:
        self.token = token
        self.timeout_seconds = timeout_seconds
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.file_base_url = f"https://api.telegram.org/file/bot{token}"

    def get_updates(self, offset: int | None = None, timeout: int = 25) -> list[dict[str, Any]]:
        params: dict[str, Any] = {"timeout": timeout}
        if offset is not None:
            params["offset"] = offset
        payload = self._request_json("GET", f"/getUpdates?{urlencode(params)}")
        return payload.get("result", [])

    def get_file_path(self, file_id: str) -> str:
        payload = self._request_json("GET", f"/getFile?{urlencode({'file_id': file_id})}")
        result = payload.get("result", {})
        file_path = result.get("file_path")
        if not file_path:
            raise TelegramApiError(f"file path missing for file_id={file_id}")
        return str(file_path)

    def download_file(self, file_path: str, destination: str) -> str:
        output = Path(destination)
        output.parent.mkdir(parents=True, exist_ok=True)
        file_url = f"{self.file_base_url}/{file_path}"

        request = Request(file_url, method="GET")
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:  # noqa: S310
                output.write_bytes(response.read())
        except Exception as exc:  # pragma: no cover - external transport
            raise TelegramApiError(f"failed to download telegram file: {exc}") from exc
        return str(output)

    def send_message(self, chat_id: str, text: str) -> None:
        body = json.dumps({"chat_id": chat_id, "text": text}).encode("utf-8")
        self._request_json("POST", "/sendMessage", data=body, headers={"Content-Type": "application/json"})

    def _request_json(
        self,
        method: str,
        path: str,
        data: bytes | None = None,
        headers: dict[str, str] | None = None,
    ) -> dict[str, Any]:
        request = Request(
            url=f"{self.base_url}{path}",
            method=method,
            data=data,
            headers=headers or {},
        )
        try:
            with urlopen(request, timeout=self.timeout_seconds) as response:  # noqa: S310
                payload = json.loads(response.read().decode("utf-8"))
        except Exception as exc:  # pragma: no cover - external transport
            raise TelegramApiError(f"telegram api request failed: {exc}") from exc

        if not payload.get("ok"):
            raise TelegramApiError(f"telegram api error: {payload}")
        return payload
