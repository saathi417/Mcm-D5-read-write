# CLAUDE.md

Guidance for AI assistants (Claude Code and others) working in this repository.

## Repository status

This repository is in a **pre-code / bootstrap state**. As of this writing it
contains only:

- `README.md` — a placeholder (`# Mcm-D5-read-write` / `Flash`)
- `LICENSE` — Apache License 2.0
- `CLAUDE.md` — this file

There is **no source code, build system, dependency manifest, test suite, or
CI configuration yet**. Do not assume any language, framework, or tooling is in
place — none has been chosen. Verify the current state with `ls` and `git
status` before acting on assumptions; this file may lag behind the repo.

### Keep this file current

Because the project is just starting, this document will go stale quickly. When
you add real structure (a language, package manager, build/test commands, a
source layout), **update this file in the same change** so it reflects reality.
Treat sections below marked _(to be defined)_ as TODOs to fill in as the
codebase grows.

## Project intent

The repository name is `Mcm-D5-read-write`, suggesting a read/write component
("D5"). The actual scope, language, and architecture have not been established
in code. If the task you are working on clarifies the intent, capture it here.

- **Purpose:** _(to be defined)_
- **Language / runtime:** _(to be defined)_
- **Key dependencies:** _(to be defined)_

## Development workflow

### Branching

- The default branch is `main`.
- Do all work on a feature branch; do not commit directly to `main`.
- Branch names in this project use the form `claude/<short-description>-<id>`
  (e.g. `claude/claude-md-documentation-08lrtx`).

### Commits

- Write clear, imperative, descriptive commit messages
  (e.g. "Add read/write module skeleton").
- Keep commits focused and scoped to a single logical change.

### Pushing

- Push with `git push -u origin <branch-name>`.
- On network failures, retry with exponential backoff (2s, 4s, 8s, 16s).
- **Do not open a pull request unless explicitly asked.**

## Build / test / lint commands

None exist yet. _(to be defined)_

Once tooling is added, document the canonical commands here, for example:

```
# install dependencies
# build
# run tests
# lint / format
```

Until then, do not invent or run build/test commands that the repository does
not define.

## Conventions for AI assistants

- **Don't fabricate structure.** This repo is nearly empty; only describe and
  rely on what actually exists. Inspect the tree before making claims.
- **Match what you find.** When code is added, mirror its existing style,
  naming, and layout rather than imposing a new convention.
- **Smallest viable change.** Prefer minimal, well-scoped edits over broad
  scaffolding unless the task explicitly calls for it.
- **License headers.** The project is Apache-2.0. Follow whatever header
  convention is established once source files appear; don't add headers
  preemptively without a pattern to follow.
- **Update this file** whenever you introduce something future contributors (or
  future AI sessions) would need to know to work effectively here.
