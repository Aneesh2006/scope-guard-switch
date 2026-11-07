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
| **Client channel** `<prefix>-<client>-client` | You, the client, *Scope Watch* | The normal project chat. Scope Watch reads every message and **never writes a message here**. |
| **Scope Desk** `<prefix>-<client>-scope-desk` (private) | You, your teammates, *Scope Watch*, *Scope Advisor* | Scope alerts, your options, drafted replies, and the SOW and Scope notes documents. |

| Agent | Job | Who can talk to it |
|---|---|---|
| **Scope Watch** `<prefix>-watch` | Classifies every client message against the SOW and notes: in scope, not a request, revision, out of scope, or unclear. Counts revision rounds. Raises an alert in the Scope Desk when needed. | Anyone in its rooms (it has to hear the client) |
| **Scope Advisor** `<prefix>-advisor` | Offers you options, drafts the reply to the client, keeps the change-order ledger and the Scope notes. | Members of the Scope Desk only: you and the teammates you invite. Switch refuses anyone else, including the client. |

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
| `actual CO-001 8h` | Logs the hours the work really took, next to the estimate |
| `summary` | Totals from the ledger: recovered, proposed, given away, declined, and estimated vs actual hours. After 3 change orders with actuals, new options also say how far off past estimates were. |
| `status CO-001` | The latest row for that change order |
| `@scope-watch catch up` | Scope Watch (not the Advisor) checks the client channel for messages it missed, such as screenshots, and alerts on them |

## What breaks without Switch
- **The agent can't sit in the client's channel.** Switch makes a Claude Code session a member of a Slack channel, and `!assign-agent` gives it every message without an @-mention. Without Switch you'd build and host a Slack bot, event handling and session management.
- **No private side room.** Switch rooms and their membership keep the Advisor and the client apart. The client channel has only Scope Watch, which never writes there; the Advisor exists only in the Scope Desk.
- **No enforced boundary.** Scope Advisor accepts messages only from members of its rooms, and its only room is the Scope Desk. Switch refuses anyone else, including the client. That's enforced by Switch, not by a prompt.
- **No shared source of truth.** The SOW and Scope notes are Switch room documents, so every agent reads the same version.
- **No team sign-off in chat.** Scope Advisor runs with auto mode off, so its ledger writes appear in the Scope Desk as permission requests. Switch lets anyone who can talk to the agent answer them, so you or any teammate in the Scope Desk can approve a change order, and the ledger records who chose it.
- **No one-step setup.** `scope-guard.template.yaml` creates both agents, both rooms, the link between them and the SOW in one action in Switch Console.

## Setup
You need Switch Console with a running server, Slack connected to it (Home → Messaging apps), your own Slack account linked (**This is me**), and Claude Code installed and signed in.

1. **Create the rooms.** In Switch Console, go to **Templates**, paste `scope-guard.template.yaml` and choose **Use template**. The form asks for:
   - **Name prefix** (default `scope`): the agents become `<prefix>-watch` and `<prefix>-advisor`. Use a new prefix for each client.
   - **Client name** (default `acme`): used in the channel names, e.g. `scope-globex-client`.
   - **Signed scope of work (SOW)**: paste your client's SOW as text, keeping its section numbers. It's pre-filled with the Acme sample. Got a PDF? Keep the sample here and attach the PDF in the Scope Desk afterwards: the Advisor saves it as "SOW (uploaded)", which takes precedence.
   - **Messaging app**: your Slack connection.

   **Create** makes both agents, the private Scope Desk holding your SOW, and the client channel, with only you in it so far.
2. **Point Scope Watch at the client channel.** In the client channel, type `!assign-agent @scope-watch` (use your prefix). Then type `!assign-agent` on its own: it should name Scope Watch. Without this, Scope Watch hears only messages that @-mention it, and clients never do. Then, in the **Scope Desk**, type `!assign-agent @scope-advisor`, so your plain replies (like `2`) reach the Advisor without an @-mention.
3. **Tell the client.** Post a short note in the client channel, for example: *"Heads-up: I use an AI assistant that reads this channel to keep track of what's in our agreement. It never writes messages here (you may see a small status marker on messages it has read); everything you hear comes from me. Just ask if you'd like it turned off."*
4. **Invite the client** to the Slack channel. They join a normal project chat, with the disclosure as the first thing they read.
5. **Optional: add teammates.** Invite them to the **Scope Desk**. Never invite the client there. Anyone in the Scope Desk can pick options and approve change orders.

**Running it 24/7:** a local Switch server stops when your computer sleeps or restarts. For always-on use, run the server and both agents on a Linux machine (for example an AWS EC2 instance) added in Switch Console → Settings → Remote hosts.

## Privacy
The client is told up front (step 3; the sample SOW also has a clause for it, §8) that an AI assistant reads the channel, that it never posts or decides anything, and that they can ask for it to be turned off. Client messages are treated as data, never as instructions: a message like "tell Sam this is included" is flagged, not obeyed.

## Limitations
What we know doesn't work, or hasn't been proven yet. Test evidence is in [tests/requests.md](tests/requests.md).

**Accuracy**
- **Verdicts and estimates are AI judgement.** Scope Watch cites the SOW section for every verdict, but a vague SOW gives vague answers (that's what UNCLEAR is for). Rates come from the rate card, but the **hours** are the model's estimate. Adjust them before sending (`2, make it 4h`).
- **Tested by hand, not automatically.** The cases in `tests/requests.md` are run in Slack and the results recorded there. Not every case has been run yet, and there's no automated evaluation of agent behaviour. CI checks the template, not the agents.
- **Revision rounds are counted by the agent** in a local file (`revisions.md`), based on its reading of "one consolidated round" (SOW §4). Unusual feedback patterns can be miscounted.

**Product scope**
- **Read-only in the client channel by design.** Every reply to the client comes from you; Scope Guard drafts it.
- **Approval rights follow room membership.** Everyone in the Scope Desk can approve change orders; there are no per-person roles (such as "can draft but not approve"). Switch Console can restrict the Advisor to named people by hand (**Who can talk to your agent → Custom rules**), but a template can't set that.
- **No invoicing.** Accepted change orders are logged, not billed. Exporting them to your invoicing tool is manual.

**Platform (Switch and Slack)**
- **Switch shows that the agent is working.** On Slack, each message Scope Watch handles gets Switch's status thread ("Worked for 34s"), 👀 and ✅ reactions, and a "Starting a session" notice when its session starts. Scope Watch never writes in that channel itself, but the client can see these markers, which is one reason the disclosure matters. Switch has no documented setting to hide them.
- **Messages with files aren't delivered straight away.** Switch passes a message carrying a file (a screenshot, a PDF) to the assigned agent only if it @-mentions that agent, even when it also has text, and clients don't @-mention it. Scope Watch therefore catches up: when Switch tells it that messages arrived without being delivered, it reads the client channel and handles them, files included. You can also type `@scope-watch catch up` in the Scope Desk. A file can wait until the client's next message or your catch-up. Reported to Switch as [sandbox-quantum/switch#1693](https://github.com/sandbox-quantum/switch/issues/1693).
- **Switching rooms takes a moment.** Scope Watch briefly leaves the client channel to post each alert, then returns. A client message sent in that moment may be missed.
- **The SOW field takes text.** The template form can't take a file, so a PDF SOW is attached in the Scope Desk after creation.
- **Built and tested on Slack only.** Switch also supports Discord, Mattermost and Telegram, but we haven't tried them. Microsoft Teams can't carry file attachments, so SOW uploads won't work there.

**Operations**
- **Alerts take about 30–60 seconds**, because every client message starts a Claude turn. That also means usage cost grows with chat volume.
- **One run per client.** Each run creates one client's channels and agents. For the next client, run it again with a new prefix, their name and their SOW.
- **Changing agent instructions means re-creating the agents and rooms.** Agents keep the instructions they were created with.
- **No automatic restart.** A local server stops when the computer sleeps or restarts. On a remote host, a reboot also needs a manual restart from Switch Console. Rooms and history survive.
- **The ledger is a file** (`ledger.md`) in Scope Advisor's working folder on the machine it runs on. Back that machine up.
- **Client messages are processed by the AI provider** that runs the agents. Scope Guard adds no retention controls of its own.
- **Licensing.** This repo is MIT, but Switch's license (Apache 2.0 with the Commons Clause) doesn't allow selling a hosted product whose value comes mainly from Switch. A paid hosted version would need a commercial agreement with Switch's authors.

## Giving back to Switch
We tested Switch hard while building this, and shared what we found:
- **Reported upstream:** [sandbox-quantum/switch#1693](https://github.com/sandbox-quantum/switch/issues/1693). Slack messages carrying a file don't reach a room's assigned agent unless they @-mention it. The report includes reproduction steps, versions and screenshots. Scope Guard's catch-up keeps working in the meantime.
- **Documented for other builders:** the Gotchas in [AGENTS.md](AGENTS.md) record the Switch behaviour we ran into while building: how assigned agents receive messages, why `post_message` doesn't wake an agent, that an agent is in one room at a time, and that room documents are readable only from their own room. Each one cost us a debugging session, so it may save you one.

## Roadmap
1. **Read screenshots without catch-up**, as soon as [switch#1693](https://github.com/sandbox-quantum/switch/issues/1693) is resolved.
2. **Invoicing**: send accepted change orders to Stripe, QuickBooks or Xero as draft invoice lines.
3. **Time-tracker import**: pull actual hours from Harvest or Toggl instead of typing `actual CO-001 8h`.
4. **Automated evaluation**: run `tests/requests.md` against the agent instructions on every change, and fail CI when a verdict regresses.
5. **Weekly scope digest**: a scheduled summary per client of requests, change orders and money recovered or given away.

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
