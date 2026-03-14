# Architecture

## Goal

Build `swiss-german-voice` so the core behavior is reusable across channels, while adapters stay thin and replaceable.

The trap to avoid is simple: if Telegram update types become the de facto domain model, the architecture is already compromised.

## System split

### Core

The core owns:

- normalized request and response shapes
- orchestration of voice-processing steps
- channel-agnostic business rules
- error categories that adapters can translate

The core must not know about:

- Telegram update payloads
- chat IDs, bot APIs, or webhook formats
- adapter-specific retry mechanics

### Adapters

Each adapter owns:

- intake from a channel-specific transport
- authentication or channel setup concerns
- translation from channel payloads into the shared core request envelope
- translation from core outcomes into channel-native replies

Adapters should be replaceable. If swapping Telegram for another channel requires changing core rules, the boundary was fake.

## Interface contract

The intended flow is:

1. adapter receives an external event
2. adapter normalizes it into a shared request envelope
3. core processes the request and returns a structured outcome
4. adapter renders or dispatches the outcome for that channel

See [skill/swiss-german-voice/references/adapter-interface.md](../skill/swiss-german-voice/references/adapter-interface.md) for the initial contract.

## Repository intent

This repo starts with documentation and interfaces before implementation. That is a constraint, not a delay tactic. The cost is slower day one progress. The benefit is that Phase C does not quietly dictate the entire project just because it shipped first.
