# Adapter Interface

This project uses a shared request and response envelope so channel integrations stay thin.

## Responsibilities

### Adapter input side

An adapter should:

- receive a channel event
- extract only the data needed by the core
- normalize that data into a shared request envelope
- attach adapter metadata separately from core business fields

## Shared request envelope

The runtime request envelope includes:

- `source_adapter`: adapter identifier such as `openclaw` or `telegram`
- `conversation_ref`: stable conversation or thread reference
- `user_ref`: stable user reference as known by the adapter
- `input_kind`: expected to support voice first, with room for text or commands later
- `payload`: normalized content or file reference needed by the core
- `metadata`: non-core details such as locale hints, timestamps, or adapter tracing fields

## Shared outcome envelope

The core should return a structured outcome that can be rendered by any adapter:

- `status`: success, retryable failure, or terminal failure
- `actions`: channel-agnostic instructions such as reply, store, or escalate
- `messages`: human-facing content ready for adapter rendering
- `artifacts`: optional generated outputs or references
- `errors`: categorized errors with enough detail for adapter-specific handling

## Invocation pattern (OpenClaw)

`swiss_german_voice.factory.build_adapter(...)` is the preferred entrypoint for OpenClaw integration. It wires:

- `FasterWhisperTranscriber`
- `SQLiteTranscriptionStore`
- `PersonalLexicon`
- `CoreRuntime`
- `OpenClawVoiceAdapter`

Then call `OpenClawVoiceAdapter.process_voice_memo(...)` per inbound media file.

## Non-goals

- exposing raw adapter payloads to the core
- encoding delivery details such as message IDs into core business logic
- letting one adapter add fields the contract cannot explain

If an adapter needs a special-case hole in the contract, that is usually architecture feedback, not a clever exception.
