# Scope Guard: agent guide

## What this is
A silent scope checker for freelancers and agencies. It reads the client's chat, flags requests the signed SOW doesn't cover, and helps the vendor reply privately; the client never talks to a bot.
Users: the vendor (agency or freelancer); the client only sees the vendor's own messages.
Stack: one Switch template (YAML, version 1) creating two Claude Code agents and two Slack rooms. Node ≥18 (stdlib only) generates the template. There is no app, server or database.

## Repo map
- `agents/watch/INSTRUCTIONS.md`: Scope Watch, the silent listener in the client room
- `agents/advisor/INSTRUCTIONS.md`: Scope Advisor: options, reply drafts, ledger, notes
- `agents/CLIENT_ROOM.md`, `agents/DESK_ROOM.md`: room instructions for the client room and the Scope Desk
- `samples/`: the sample SOW (`.md`, embedded in the template; `.pdf`, for upload tests) and a client-request screenshot
- `scripts/build-template.mjs`: assembles the template from the files above
- `scripts/check-template.py`: validates the template (required agent fields, room and link references, the client kept away from agents and setup messages)
- `.github/workflows/ci.yml`: on every push and PR: the template matches its sources, passes the check, and no secrets are committed
- `tests/requests.md`: manual acceptance tests: client messages with expected verdicts and cited § (the spec for agent behaviour)
- `LICENSE`: MIT, Team Scope Guard
- `scope-guard.template.yaml`: **generated**; the file imported in Switch Console → Templates
- `README.md`: for hackathon judges and users

## Commands
- Install: nothing to install. Needs Node ≥18, plus Python with PyYAML for the verify step.
- Build: `node scripts/build-template.mjs`
- Verify (run before finishing; CI runs the same): `node scripts/build-template.mjs; python scripts/check-template.py`
- Try it: Switch Console → Templates → paste `scope-guard.template.yaml` → Create. Then run the flow in Slack (see Definition of done).

## Golden rules
- Never commit secrets: Slack tokens (`xoxb-`, `xapp-`), API keys, `.env*`, `*.local.md`.
- Never edit `scope-guard.template.yaml` by hand. Edit the source `.md` files or the script, then build.
- Never weaken the product's hard rules: agents never post in the client room; no ledger entry without the vendor allowing the write; every verdict cites the SOW (§) or dated notes; estimates use only the SOW rate card.
- Only use template keys documented in Switch's [TEMPLATES.md](https://github.com/sandbox-quantum/switch/blob/main/docs/TEMPLATES.md). Never invent keys.
- Don't add dependencies or a `package.json` without saying why. The generator is stdlib-only on purpose.

## Conventions (only non-obvious ones)
- Agents find rooms and each other by **name suffix** (`-client`, `-scope-desk`, `-watch`, `-advisor`), never by `{param}` placeholders (see commit f72ebad).
- The ledger (`ledger.md` in Scope Advisor's working folder) is append-only: corrections are new rows. Statuses: ABSORBED, PROPOSED, DECLINED, ACCEPTED, DECLINED_BY_CLIENT.
- Commit messages: `feat:`, `fix:`, `documentation:`, `chore:`.

## Definition of done
- Verify passes, and the regenerated template is committed together with its source change.
- When agent behaviour changed: update the affected cases in `tests/requests.md` in the same change, recreate the agents and rooms from the template, run the cases in Slack, and record the result in its Results table.
- README updated if setup or the flow changed.

## Gotchas
- **Agents created earlier keep their old instructions.** After changing instructions, delete the agents and rooms and create them again from the template (or use a new `team` prefix).
- **A plain message reaches no agent** unless it @-mentions one, follows up on that agent's answer to the same person, or the room has an assigned agent. Setup assigns Scope Watch in the client room and Scope Advisor in the Scope Desk (`!assign-agent`), or the vendor's plain `2` goes nowhere.
- **Messages carrying a file aren't delivered to an assigned agent** unless they @-mention it (verified in Slack, case 9b). Scope Watch catches up via `read_context` when Switch reports undelivered messages, or when the vendor says `@scope-watch catch up`. The real fix belongs in Switch.
- **`post_message` doesn't wake an agent.** Use `send_targeted_message(target_names=[…])`, and never write `@name` in a `post_message` body.
- **An agent is connected to one room at a time.** Scope Watch must `connect_to_room` back to the client room after posting in the Scope Desk, or it stops hearing the client.
- **Documents are readable only from their own room** (`load_internal_documents`). `read_context` reads messages, not documents. An agent can update only documents it created, which is why an uploaded SOW becomes a new "SOW (uploaded)" document.
- **The client is never added by the template, and the client room has no kickoff.** The vendor runs `!assign-agent` first, posts the AI disclosure note, then invites the client (README, Setup). A kickoff would be visible to the client, and it isn't documented whether a kickoff runs `!` commands at all. `check-template.py` enforces this.
- **Runtime agents don't read this file.** They work in Switch's agents folder, outside this repo. Their instructions live in the template.
- **Local test runs load your personal `~/.claude` setup** (plugins and hooks) into the runtime agents. Disable plugins that change reply style before testing.
- Git's "LF will be replaced by CRLF" warning on the template is harmless.

## Read more
- Product and flow: `README.md`
- Switch template language: https://github.com/sandbox-quantum/switch/blob/main/docs/TEMPLATES.md
- How Switch agents use rooms and tools: https://github.com/sandbox-quantum/switch/blob/main/console/packages/plugins/src/switch-skill/SKILL.md
