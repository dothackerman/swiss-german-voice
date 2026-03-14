# Contributing

This project accepts incremental PRs, but adapter changes must preserve the channel-agnostic contract defined in [skill/swiss-german-voice/references/adapter-interface.md](skill/swiss-german-voice/references/adapter-interface.md).

## Adapter PR contract

- keep channel-specific API shapes inside the adapter layer
- map incoming events into the shared request envelope
- map core outcomes back into channel-native replies
- document any new adapter capability or limitation
- avoid adding core behavior that only one adapter can trigger unless the limitation is made explicit

## Tests expectation

For now, every PR that adds behavior should include tests proportional to the change:

- unit tests for envelope translation and adapter normalization
- at least one integration-style test for the core-to-adapter handoff when executable code exists
- updated docs when contracts, phases, or interfaces change

If a PR cannot include tests yet, explain why in the PR description. "Will add later" is not a contract; it is debt with lipstick.
