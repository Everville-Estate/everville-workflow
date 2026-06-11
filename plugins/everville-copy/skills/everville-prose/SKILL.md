---
name: everville-prose
description: Use when writing or editing prose humans will read — marketing copy for roya.*, balicopter.com, everville.estate, bali.villas; PR bodies, commit messages, error messages, onboarding emails, UI copy, portal flash messages, investor updates. Applies Strunk's Elements of Style + Wikipedia's Signs of AI Writing patterns. Removes slop; adds voice.
---

<!--
  Adapted from softaworks/agent-toolkit — two MIT-licensed skills merged:
  (1) writing-clearly-and-concisely (@jessevincent — Strunk's Elements of Style)
  (2) humanizer (@blader — anti-AI-slop patterns based on Wikipedia's
      "Signs of AI writing" guide)
  See LICENSES/softaworks-MIT.txt for the original license text.
  Everville modifications: merged into one skill; description names specific
  Everville brands/surfaces; references organized into a single tree.
-->

# Everville Prose

Write with clarity and force for every Everville surface a human will read. Two disciplines, one skill:

1. **Strunk's Elements of Style** — what to do (clarity, concision, active voice)
2. **Anti-AI-slop patterns** — what to avoid (puffery, fake significance, em-dash spam)

## When to Use

Any time you're producing sentences humans will actually read:

- Marketing pages on roya.business, roya.gallery, balicopter.com, bali.villas, everville.estate, portal.everville.estate
- PR bodies (paired with `/explain-pr-changes`)
- Commit messages
- Error messages and UI copy (portal, eva, dashboards)
- Investor updates, onboarding emails, portal flash messages
- README files, technical explanations, spec documents

If you're writing a sentence a human will see, use this skill.

## Quick Checklist (the 80/20)

Before shipping any paragraph, check:

1. **Active voice** — "The dispatcher approved the booking" not "The booking was approved by the dispatcher"
2. **Positive form** — "Pending review" not "Not yet approved"
3. **Specific and concrete** — "214 investors" not "a large community"
4. **No needless words** — strike "in order to", "the fact that", "at this point in time"
5. **No puffery** — no "pivotal", "crucial", "vital", "testament", "enduring legacy", "seamless", "robust", "groundbreaking"
6. **No empty -ing phrases** — strike "ensuring reliability", "highlighting capabilities", "showcasing features"
7. **No em-dash spam** — at most one em dash per paragraph; comma or period usually works
8. **Has a voice** — if every sentence is the same length and structure, rewrite

## Two Disciplines

### A. Strunk's Elements of Style

Load the relevant section from `references/elements-of-style/` when editing. Most tasks only need `03-elementary-principles-of-composition.md`.

| Section | File | ~Tokens | When to load |
|---------|------|---------|--------------|
| Elementary rules of usage | `02-elementary-rules-of-usage.md` | 2,500 | Comma/grammar questions |
| Composition principles | `03-elementary-principles-of-composition.md` | 4,500 | **Default — most tasks** |
| Form (headings, quotes) | `04-a-few-matters-of-form.md` | 1,000 | Formatting decisions |
| Misused words | `05-words-and-expressions-commonly-misused.md` | 4,000 | Word-choice questions |

### B. Anti-AI-Slop

Load `references/signs-of-ai-writing.md` for the full catalog. The top patterns to strip:

| Pattern | Before | After |
|---------|--------|-------|
| Undue significance | "This represents a pivotal moment in the evolution of…" | "This is new." |
| Promotional adjectives | "seamless, robust, cutting-edge solution" | "it works" |
| Overused AI vocabulary | "delve, leverage, multifaceted, foster, realm, tapestry" | plain English |
| Empty -ing phrases | "ensuring reliability and showcasing features" | delete |
| Rule of three | "faster, stronger, smarter" | pick one |
| Negative parallelism | "not just X but Y" | just say Y |
| Excessive conjunctive phrases | "moreover, furthermore, additionally" | break the paragraph |

## Add a Voice

Avoiding slop is only half the job. Sterile, voiceless prose is just as obvious. Good writing has a human behind it.

- Vary rhythm: short punchy sentences. Then longer ones that take their time.
- Have opinions; don't just report facts.
- Use "I" when it fits. First person isn't unprofessional — it's honest.
- Acknowledge complexity: "this is impressive but also unsettling" beats "this is impressive".
- Be specific about feelings: not "concerning" but "unsettling to watch agents churn at 3am while nobody's watching".

## Subagent Copyedit Pass

For high-stakes surfaces (investor updates, marketing pages), a fresh-context editor catches what the author can't:

1. Write your draft using judgment
2. Dispatch a subagent with the draft + the one relevant reference file
3. Have the subagent copyedit and return the revision

A single reference section loads ~1,000-4,500 tokens instead of everything.

## Everville-specific gotchas

- **Don't use "everville.estate team" in copy aimed at operators** — use the brand the user is on (balicopter, roya, bali.villas)
- **Marketing voice for roya.*** is cinematic/intimate; **balicopter.com** is precise/aviation; **portal.everville.estate** is dry/functional. Don't mix.
- **Never put emoji in PR bodies, commit messages, or commit-authored content** unless the user explicitly asks. Global CLAUDE.md rule.
- **Never use em-dashes with spaces around them** — Everville house style is no-space em-dashes or comma/period

## References

- `references/elements-of-style/` — the four Strunk sections
- `references/signs-of-ai-writing.md` — Wikipedia's detailed AI-slop catalog
