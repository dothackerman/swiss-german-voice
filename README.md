# swiss-german-voice

`swiss-german-voice` is a public OpenClaw skill scaffold for building a channel-agnostic Swiss German voice workflow, with Telegram as the first adapter rather than the defining interface.

This repository is intentionally governance-first. The first commit sets the contract for future implementation work:

- core behavior lives behind a stable adapter interface
- adapters translate channel payloads into that core contract
- documentation leads code until the real execution paths are clear

## What is in this scaffold

- [docs/ROADMAP.md](docs/ROADMAP.md): phased delivery plan for A/B/C/D
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md): core versus adapters boundary
- [skill/swiss-german-voice/SKILL.md](skill/swiss-german-voice/SKILL.md): initial OpenClaw skill entrypoint
- [skill/swiss-german-voice/references/adapter-interface.md](skill/swiss-german-voice/references/adapter-interface.md): adapter contract
- [skill/swiss-german-voice/references/phases.md](skill/swiss-german-voice/references/phases.md): roadmap summary for agent context
- [CONTRIBUTING.md](CONTRIBUTING.md): adapter PR expectations

## Design intent

The project is channel-agnostic by default.

That sounds obvious, but it is where many bot projects cheat: they let Telegram update shapes leak into the business flow and then call the result "portable." This scaffold blocks that mistake early. Adapters should be thin, boring translators.

## Scope of this first commit

This commit does not include runtime code, deployment code, or message-handling logic. It provides the structure and contracts needed to add those deliberately in later phases.

## Initial layout

```text
docs/
  ARCHITECTURE.md
  ROADMAP.md
scripts/
  README.md
skill/
  swiss-german-voice/
    SKILL.md
    references/
      adapter-interface.md
      phases.md
```

## License

MIT. See [LICENSE](LICENSE).
