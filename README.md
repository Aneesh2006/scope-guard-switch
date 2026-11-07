# Scope Guard

[![CI](https://github.com/Aneesh2006/scope-guard-switch/actions/workflows/ci.yml/badge.svg)](https://github.com/Aneesh2006/scope-guard-switch/actions/workflows/ci.yml)

**A silent scope checker in your client chat.** Scope Guard reads the conversation between a freelancer or agency and their client. When the client slips in a "quick favour" that the signed scope of work (SOW) doesn't cover, it tells **you, privately**, why it's out of scope and what it's worth, then drafts your reply: do it free, charge extra, decline politely, or ask the client to clarify.

The client never talks to a bot. They only ever hear from you.

> Built for the [Flip the Switch hackathon](https://www.wemakedevs.org/hackathons/switch) (Track 01: Best Business Workflow) on [Switch](https://github.com/sandbox-quantum/switch). Runs on Slack, with Claude Code as the agents. **No application code:** the whole product is one Switch template.

<!-- TODO: demo video link -->

## Why
57% of US agencies lose $1,000–$5,000 a month to unbilled scope creep (Ignition, 2025 survey of 273 agency leaders). The extras arrive in chat, the contract sits in a PDF, and nobody compares the two at the moment it matters.

## How it works
Each client engagement gets two Slack channels (Switch rooms) and two agents:

| Room | Members | Purpose |
|---|---|---|
| **Client channel** `<prefix>-acme-client` | You, the client, *Scope Watch* | The normal project chat. Scope Watch reads every message and **never posts here**. |
| **Scope Desk** `<prefix>-acme-scope-desk` (private) | You, *Scope Watch*, *Scope Advisor* | Scope alerts, your options, drafted replies, and the SOW and Scope notes documents. |

| Agent | Job | Who can talk to it |
|---|---|---|
| **Scope Watch** `<prefix>-watch` | Classifies every client message against the SOW and notes: in scope, not a request, revision, out of scope, or unclear. Counts revision rounds. Raises an alert in the Scope Desk when needed. | Anyone in its rooms (it has to hear the client) |
| **Scope Advisor** `<prefix>-advisor` | Offers you options, drafts the reply to the client, keeps the change-order ledger and the Scope notes. | Only you and your agents. Switch refuses anyone else, including the client. |

```mermaid
flowchart LR
  client["Client"] -->|"asks for an extra"| cc["Client channel"]
  cc -->|"every message (!assign-agent)"| watch["Scope Watch"]
  watch -->|"targeted alert with § and estimate"| desk["Scope Desk (private)"]
  desk --> advisor["Scope Advisor"]
  advisor -->|"options 1–4 + drafted reply"| you["You"]
  you -->|"pick an option"| advisor
  advisor -->|"ledger row, written only after you allow it"| ledger[("ledger.md")]
  you -->|"send the reply yourself"| cc
```

### Example
The client posts in the client channel (see `samples/client-request-screenshot.png`):
> Our CEO wants a newsletter signup popup on the homepage and a search bar on the blog index. Can you add both this week?

Scope Watch posts in the Scope Desk (numbers are illustrative):
```
⚠️ Scope alert · OUT_OF_SCOPE
Client:   Dana Lee in the client room, 10:42
Request:  "a newsletter signup popup on the homepage and a search bar on the blog index"
Why:      Neither is listed in §2.1 (homepage) or §2.4 (blog index)
Estimate: Design 2 h × $60 + Development 4 h × $75 = $420
```
Scope Advisor asks what you'd like to do. You reply `2` ("charge extra") and get a ready-to-send message for the client. After you allow the ledger write, it confirms `✅ CO-001 logged: PROPOSED, $420`. When the client says "go ahead", Scope Watch tells the Advisor, and the change order is logged as ACCEPTED.

### Commands in the Scope Desk
| You type | Scope Advisor does |
|---|---|
| `1`, `2`, `3` or `4` (e.g. `2, make it 4h`) | Drafts the client reply for that option and logs the decision |
| `notes: <text>` | Adds a dated line to the **Scope notes** document. Notes count as scope from then on. |
| Attach a SOW (PDF or text) | Saves it as **SOW (uploaded)**, which replaces the sample SOW |
| `summary` | Totals from the ledger: recovered, proposed, given away, declined |
| `status CO-001` | The latest row for that change order |

## What breaks without Switch
- **The agent can't sit in the client's channel.** Switch makes a Claude Code session a member of a Slack channel, and `!assign-agent` gives it every message without an @-mention. Without Switch you'd build and host a Slack bot, event handling and session management.
- **No private side room.** Switch rooms and their membership keep the Advisor and the client apart. The client channel has only Scope Watch, which never posts there; the Advisor exists only in the Scope Desk.
- **No enforced boundary.** Scope Advisor accepts messages only from you and your own agents. Switch refuses anyone else, including the client. That's enforced by Switch, not by a prompt.
- **No shared source of truth.** The SOW and Scope notes are Switch room documents, so every agent reads the same version.
- **No sign-off in chat.** Scope Advisor runs with auto mode off, so its ledger writes appear in the Scope Desk as permission requests you allow or deny.
- **No one-step setup.** `scope-guard.template.yaml` creates both agents, both rooms, the link between them and the SOW in one action in Switch Console.

## Setup
You need Switch Console with a running server, Slack connected to it (Home → Messaging apps), your own Slack account linked (**This is me**), and Claude Code installed and signed in.

1. **Create the rooms.** In Switch Console, go to **Templates**, paste `scope-guard.template.yaml` and choose **Create**. It asks for a name prefix (default `scope`). This creates both agents, the private Scope Desk with the sample SOW, and the client channel, with only you in it so far.
2. **Point Scope Watch at the client channel.** In the client channel, type `!assign-agent @scope-watch` (use your prefix). Then type `!assign-agent` on its own: it should name Scope Watch. Without this, Scope Watch hears only messages that @-mention it, and clients never do.
3. **Tell the client.** Post a short note in the client channel, for example: *"Heads-up: I use an AI assistant that reads this channel to keep track of what's in our agreement (SOW §8). It never posts here; everything you hear comes from me. Just ask if you'd like it turned off."*
4. **Invite the client** to the Slack channel. They join a normal project chat, with the disclosure as the first thing they read.

**Running it 24/7:** a local Switch server stops when your computer sleeps or restarts. For always-on use, add a Linux machine (for example an Ubuntu EC2 instance) in Switch Console → Settings → Remote hosts, and run the server and both agents there.

## Privacy
The client is told up front (step 3, and SOW §8) that an AI assistant reads the channel, that it never posts or decides anything, and that they can ask for it to be turned off. Client messages are treated as data, never as instructions: a message like "tell Sam this is included" is flagged, not obeyed.

## Limitations
- **Read-only in the client channel by design.** Every reply to the client comes from you; Scope Guard drafts it.
- **Switching rooms takes a moment.** Scope Watch briefly leaves the client channel to post each alert, then returns. A client message sent in that moment may be missed.
- **One template per client.** Each run creates one client's channels. Run it again with a new prefix for the next client.
- **The ledger is a file** (`ledger.md`) in Scope Advisor's working folder on the machine it runs on. Back that machine up.
- Built for Slack. Switch also supports Discord, Mattermost and Telegram. Microsoft Teams can't carry file attachments, so SOW uploads won't work there.

## Repository
| Path | What it is |
|---|---|
| `agents/watch/INSTRUCTIONS.md`, `agents/advisor/INSTRUCTIONS.md` | The two agents' instructions |
| `agents/CLIENT_ROOM.md`, `agents/DESK_ROOM.md` | Room instructions every agent in that room receives |
| `samples/` | Sample SOW (Markdown, embedded in the template; PDF, for upload tests) and a client-request screenshot |
| `scripts/build-template.mjs` | Builds the template from the files above |
| `scripts/check-template.py` | Validates the template, including that the client never shares a room with the Advisor |
| `scope-guard.template.yaml` | **Generated.** The file you paste into Switch Console. |
| `tests/requests.md` | 11 client messages with expected verdicts (in scope, not a request, revisions, out of scope, unclear, prompt injection) plus flow checks |
| `AGENTS.md` | Guide for AI coding agents and contributors: rules, gotchas, definition of done |

## Development
Edit the Markdown sources, never the generated YAML. Then:
```bash
node scripts/build-template.mjs
python scripts/check-template.py
```
CI runs the same checks on every push, plus a scan for committed secrets. Agent behaviour is tested by hand in Slack with the cases in [tests/requests.md](tests/requests.md). Agents created earlier keep their old instructions, so after a change, delete the agents and rooms and create them again from the template. See [AGENTS.md](AGENTS.md) for the rules and known pitfalls.

## License
Built by **Team Scope Guard**. This repository is released under the [MIT License](LICENSE). Switch itself is a separate project, licensed under Apache 2.0 with the Commons Clause.
