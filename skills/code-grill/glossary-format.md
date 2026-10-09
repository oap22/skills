# GLOSSARY.md Format

Adapted from `domain-modeling` in https://github.com/mattpocock/skills (MIT, Copyright (c) 2026 Matt Pocock).

## Structure

```md
# {Context name}

{One or two sentences: what this context is and why it exists.}

## Language

**Order**:
A customer's request to buy one or more items.
_Avoid_: Purchase, transaction

**Customer**:
A person or organization that places orders.
_Avoid_: Client, buyer, account
```

## Rules

- **Be opinionated.** When several words name one concept, pick the best and list the others under `_Avoid_`.
- **Keep definitions tight.** One or two sentences. Define what it is, not what it does.
- **Project terms only.** General programming concepts (timeouts, error types, retries) do not belong, even if the project uses them a lot.
- **No implementation detail.** The glossary is not a spec, a scratch pad, or a decision log.
- **Group under subheadings** when clusters emerge; a flat list is fine otherwise.

## Single vs multiple contexts

- If `GLOSSARY-MAP.md` exists at the repo root, read it to find each context's `GLOSSARY.md` and use the one the change belongs to; ask if unclear.
- If only a root `GLOSSARY.md` exists, it is a single context.
- If neither exists, create a root `GLOSSARY.md` when the first term resolves.

A map lists contexts and how they relate:

```md
# Glossary Map

## Contexts

- [Ordering](./src/ordering/GLOSSARY.md): receives and tracks customer orders
- [Billing](./src/billing/GLOSSARY.md): generates invoices and takes payments

## Relationships

- **Ordering → Billing**: Ordering emits `OrderPlaced`; Billing consumes it to invoice
```
