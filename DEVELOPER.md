# Developer Guide

This document is for anyone contributing to this repository.

## About this repo

`test` is a public sandbox repository used for experimenting with GitHub
Copilot workflows and tooling. It is not a production project — there is no
build, no dependencies, and no CI pipeline. Content here is intentionally
lightweight (currently just recipes in the README) so it's easy to reason
about when testing automation.

## Working with this repo

- Clone it like any other repo: `git clone <repo-url>`.
- There's nothing to install or build — it's just Markdown.
- Create a branch per change, e.g. `git checkout -b my-change`.
- Open a pull request for review before merging to `main`.

## Conventions

- Keep changes small and focused; this repo is meant for quick, easy-to-review
  experiments.
- New recipes or content added to `README.md` should follow the existing
  format (`## Recipe: <Name>` with `### Ingredients` and `### Instructions`
  sections).
- Avoid introducing build tooling, dependencies, or CI unless the change
  specifically calls for testing that kind of workflow.

## Questions

If you're unsure whether a change fits the spirit of this repo, open a PR
and ask — it's a scratch space, so the bar for experimentation is low.
