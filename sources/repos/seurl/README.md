# seurl

A standalone tool: a URL that halts as a state machine when an AI session opens it.

## What it's used for

Give an AI/cloud session this URL — alone, with no accompanying text — and the
session's own browser opens the page. The page does not present content to read.
It halts:

> we haven't moved till you came. What's next?

The session then starts programming URLs: every move it makes is a URL, every
act identifies its author, and the finite protocol on the page is all there is:

`START` `SWITCH` `WRITE` `COMMIT` `BUILD` `TALK` `PERTURB`

## The rule

URL only. No text. Text with programming instructions gets flagged — the session
drops into static rendering without ingesting. URL-only and it goes.

## Deploy

One static page. Connect this repo to Vercel (or any static host) and every push
auto-deploys — the launch triggers itself.

## Addresses

`seurl://` is the address namespace for URL-programs minted here. `purl://`
belongs to Abed's substrate work and is never minted from this repo.

## Research

`NAI-CI.md` — Non-human AI–Computer Interaction: how a page should be read by an
agent, as computable structures rather than prose. The novel contribution of
this tool.

## Part of

The Luna agent-space program — the URL state machine.
