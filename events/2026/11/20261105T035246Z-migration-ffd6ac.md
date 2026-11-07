---
type: pref
scope: global
key: release.pool-promote
instance: migration
owner: user
supersedes: 20261025T082149Z-code-de2122
tags: deploy, quiz
ts: 2026-11-05T03:52:46Z
---
Question-pool updates (tools/data, i18n) that pass the automated pipeline (gate + mutation check, then beta) may be promoted to the stable app and the web version without asking again; app code releases still need Giovanni's go-ahead (2026-10-25).
