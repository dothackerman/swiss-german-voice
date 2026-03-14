# swiss-german-voice

Use this skill when handling Swiss German voice workflows for `swiss-german-voice`.

Start small:

1. read `references/phases.md` for current project phase and scope
2. read `references/adapter-interface.md` before touching adapter logic
3. stay inside the core-versus-adapter boundary from `docs/ARCHITECTURE.md`

## Current intent

- channel-agnostic skill design
- Telegram adapter first
- documentation-led implementation until runtime contracts are proven

## Working rules

- keep Telegram details in adapter code or adapter docs
- treat normalized request and response shapes as the durable surface
- prefer extending references over inventing behavior in the skill file

If a task needs deeper context, open the reference docs rather than expanding this file into a novel.
