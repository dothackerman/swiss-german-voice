# swiss-german-voice

Use this skill when handling Swiss German voice workflows for `swiss-german-voice`.

OpenClaw usage pattern:

1. Trigger this skill when Sil receives a voice memo from OG via Telegram/OpenClaw inbound media.
2. OpenClaw provides a local media path; pass that path directly to the adapter.
3. Use `OpenClawVoiceAdapter` at `swiss_german_voice.adapters.openclaw.adapter`.
4. Call `process_voice_memo(audio_path, user_ref=..., conversation_ref=..., language_hint="de")`.
5. Send `reply_text` through the OpenClaw message tool.

Keep adapters thin:

- normalize channel input to the shared core request envelope
- keep channel transport details out of `src/swiss_german_voice/core/`
- keep standalone Telegram polling adapter as reference, not as runtime dependency for OpenClaw
