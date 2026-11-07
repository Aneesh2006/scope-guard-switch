"""Checks scope-guard.template.yaml beyond "it parses": what Switch needs to create it,
and the product rule that the client never sees an agent.
Usage: python scripts/check-template.py [path]"""
import re
import sys

import yaml

path = sys.argv[1] if len(sys.argv) > 1 else "scope-guard.template.yaml"
with open(path, encoding="utf-8") as f:
    t = yaml.safe_load(f)

params = set(t.get("params", {}))
agents = {a["name"]: a for a in t["agents"]}
rooms = {r["name"]: r for r in t["rooms"]}
errors = []

for name, a in agents.items():
    for key in ("provider", "directory", "instructions"):
        if not a.get(key):
            errors.append(f"agent {name}: missing {key}")
    if not (a.get("machine") or a.get("location")):
        errors.append(f"agent {name}: missing machine or location")
    if "{team}" not in str(a.get("directory", "")):
        errors.append(f"agent {name}: directory must include {{team}}, or every client shares one ledger")
    used = params & set(re.findall(r"\{(\w+)\}", a.get("instructions", "")))
    if used:
        errors.append(f"agent {name}: instructions use template params {sorted(used)}; refer to rooms and agents by name suffix")

for name, r in rooms.items():
    for a in r.get("agents", []):
        if a not in agents:
            errors.append(f"room {name}: unknown agent {a}")
    if name.endswith("-client") and any(not a.endswith("-watch") for a in r.get("agents", [])):
        errors.append(f"room {name}: only Scope Watch may be in the client room")
    if name.endswith("-client") and r.get("kickoff"):
        errors.append(f"room {name}: no kickoff in the client room; the client would see it")
    if r.get("users", []) != ["{$creator}"]:
        errors.append(f"room {name}: the template adds only the vendor; the client is invited by hand to the client room")

for link in t.get("links", []):
    for end in (link["from"], link["to"]):
        if end not in rooms:
            errors.append(f"link: unknown room {end}")

# A {placeholder} that names no param is left as written, so a typo would create "{clinet}" channels.
known = params | {"$creator", "$creator_email", "$date", "$timestamp", "$agents_dir", "agent"}
outside_instructions = yaml.safe_dump({k: v for k, v in t.items() if k not in ("params", "agents")})
for name in sorted(set(re.findall(r"\{(\$?\w+)\}", outside_instructions)) - known):
    errors.append(f"unknown placeholder {{{name}}} in rooms, group or links")

for e in errors:
    print(f"::error file={path}::{e}")
print(f"{path}: {len(agents)} agents, {len(rooms)} rooms, {len(errors)} problems")
sys.exit(1 if errors else 0)
