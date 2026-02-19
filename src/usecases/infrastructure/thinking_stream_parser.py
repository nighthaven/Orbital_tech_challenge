from fastapi import WebSocket


class ThinkingStreamParser:
    """Stateful parser that splits streamed text into thinking vs. answer events.
    Handles <thinking>...</thinking> tags that may span across multiple deltas.
    Sends WebSocket events as soon as content is available.
    """

    def __init__(self, ws: WebSocket) -> None:
        self._ws = ws
        self._buffer = ""
        self._inside_thinking = False

    async def feed(self, delta: str) -> None:
        self._buffer += delta

        while self._buffer:
            if self._inside_thinking:
                end_idx = self._buffer.find("</thinking>")
                if end_idx == -1:
                    if self._could_be_partial_tag(self._buffer, "</thinking>"):
                        break
                    await self._emit("thinking", self._buffer)
                    self._buffer = ""
                else:
                    thinking_content = self._buffer[:end_idx]
                    if thinking_content:
                        await self._emit("thinking", thinking_content)
                    self._buffer = self._buffer[end_idx + len("</thinking>") :]
                    self._inside_thinking = False
            else:
                start_idx = self._buffer.find("<thinking>")
                if start_idx == -1:
                    if self._could_be_partial_tag(self._buffer, "<thinking>"):
                        safe_end = len(self._buffer) - len("<thinking>")
                        if safe_end > 0:
                            await self._emit("text_delta", self._buffer[:safe_end])
                            self._buffer = self._buffer[safe_end:]
                        break
                    await self._emit("text_delta", self._buffer)
                    self._buffer = ""
                else:
                    text_before = self._buffer[:start_idx]
                    if text_before:
                        await self._emit("text_delta", text_before)
                    self._buffer = self._buffer[start_idx + len("<thinking>") :]
                    self._inside_thinking = True

    async def flush(self) -> None:
        """Flush any remaining buffer content."""
        if self._buffer:
            event_type = "thinking" if self._inside_thinking else "text_delta"
            await self._emit(event_type, self._buffer)
            self._buffer = ""

    async def _emit(self, event_type: str, content: str) -> None:
        stripped = content.strip()
        if stripped:
            ws_type = "text" if event_type == "text_delta" else event_type
            await self._ws.send_json({"type": ws_type, "content": stripped})

    @staticmethod
    def _could_be_partial_tag(text: str, tag: str) -> bool:
        """Check if the end of text could be the start of a partial tag."""
        for i in range(1, len(tag)):
            if text.endswith(tag[:i]):
                return True
        return False
