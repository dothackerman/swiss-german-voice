# Roadmap

This roadmap is intentionally phased so the project can earn complexity instead of assuming it.

## Phase A: Scaffold and Contracts

- establish repository structure and public documentation
- define the core versus adapter boundary
- write the first OpenClaw skill scaffold and reference docs
- keep runtime code out until interfaces are stable

Exit criteria:

- scaffold is committed on `main`
- adapter contract is explicit
- future contributors can tell where core logic belongs

## Phase B: Core Runtime Slice

- implement a minimal core request/response contract
- define voice-processing pipeline boundaries
- add local tests for normalization and orchestration
- keep execution path channel-agnostic

Exit criteria:

- core can accept a normalized request and produce a deterministic outcome
- tests validate the contract without requiring Telegram

## Phase C: Telegram Adapter

- implement Telegram event intake and message normalization
- translate Telegram voice inputs into the shared core contract
- send channel-native replies based on core outcomes
- add adapter-focused tests and operational notes

Exit criteria:

- Telegram can exercise the core without leaking Telegram update shapes into it
- adapter failure cases are documented

## Phase D: Additional Channels and Operations

- add at least one non-Telegram adapter using the same contract
- document deployment, observability, and support playbooks
- tighten contribution and release workflows
- validate that the core contract survives multi-channel pressure

Exit criteria:

- second adapter reuses the core without architectural exceptions
- operations guidance exists for public maintenance
