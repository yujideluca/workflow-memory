# Memory brief

Generated 2026-11-14 from 1084 events. Do not edit: record changes as events.

Memory sets defaults; it never authorizes. Precedence: current instruction > repo rules file > project memory > profile
Rules are modules loaded by kind of task; none is printed here. Your one standing order: for each message from Giovanni, first classify the task into the tags below (several can apply, none when nothing fits) and fetch `views/rules/TAG.md` from the repository (same tools as Recording) for every tag not loaded yet in this conversation. Do it as the very first step, before reading skills or files and before any other command; then follow their full wording. Classify again whenever the task changes. Tags:
- deploy (11): installing, releasing, changing system, service or tool configuration
- outward (8): acts others see or cannot undo: sending email or messages, purchases, publishing, deleting
- troubleshooting (8): debugging, testing, fixing findings, proving that it works
- coding (21): starting, designing or changing code; choosing tools
- reporting (9): how to answer, explain and report results or mistakes
- git (11): branches, commits, repos, GitHub
- docs-memory (15): wiki pages, memory entries, closing a task
- device (6): phone, adb, browser, Telegram
- quiz (4): QuizApp and QuizWeb
- radiology (38): radiology report matcher and crawler
- german (4): German exam practice and corrections
- status-quo (1): the Status Quo tray
- codex (10): work done by Codex

## Open items

Open items (shown in every chat until solved, archived or deleted):
- [open item radiology] Radiology design review 2026-11-14 (docs/r5-design-review.md): rule 'no case text in any model' costs about 7 points (naive classifier on tune half 83.5 % vs engine 77.0 %). Needs Giovanni's decision to allow training on the tuning half of cases and articles (test half and R10 stay held out; Radiopaedia licence decision before shipping). Also: label audit done (labels cost about 2 points), embedding model approved. | check: grep -n 'Data policy' ~/dev/radiology-crawler/docs/r5-design-review.md;… (since 2026-11-14, #e44546)
- [open item radiology] Radiology R5 (2026-11-14, English only): stage 1 engine built and pushed (tune-half top-3 48%, target 97%). Next: descriptor reader + rerank (stage 2), then R6 sufficiency, R7 questions. Needs Giovanni's decision: three-slot pair unit caps at 86%; score per case, per sentence, or user-marked target? Translators disabled and T2 DE/PT paused (see matcher.english-first). | check: python3 -I ~/dev/radiology-crawler/tools/analysis_status.py show | grep -E 'R5' (since 2026-11-14, #598a2f)
- [open item] Proactive Gmail watch for Giovanni's process (asked 2026-11-10): needs a durable daily check (not a session-only timer) that summarizes only emails changing the Hospitation/Approbation process; read-only. Study map (FSP + Kenntnisprüfung) exam map written at ~/Documents/09 Pacote Hospitation e Approbation/01_Mapa_das_provas_FSP_e_KP.md; next: Arztbrief lesson, then study plan, after Giovanni reads the map. Calendar events created for Hospitation, 8 March deadline, Quantiferon 22 March, Good Sta… (since 2026-11-10, #a58496)
- [open item] Hospitation/Approbation (2026-11-10 17:36 UTC): Giovanni SENT the Böhler quote request (10 PDFs): Group 1 (A1,A2,B1-B6) translated WITH apostille; Group 2 (Good Standing CRM-PR, PF certificate) translated WITHOUT apostille now, reissued + apostilled + translated again in FEBRUARY 2027 (their edit; I had written March). Waiting for Böhler quote and RP reply before contracting. | check: Gmail: reply from Böhler in thread 1a1c684df09d0528; RP Stuttgart reply in thread 1a1b6092055424d9 (since 2026-11-10, #905ea0)
- [open item] Hospitation/Approbation (2026-11-10): scope changed by Giovanni: quote ALL docs apostilled (A1,A2,B1-B6), excluding Good Standing CRM-PR and PF certificate (reissue+apostille+translate in March 2027). Böhler draft r3078633901294136714 NOT sent; Giovanni to send. Still wait for RP reply before contracting. | check: Gmail: reply from Böhler (new draft r3078633901294136714 sent by Giovanni?) and RP Stuttgart reply in thread 1a1b6092055424d9 (since 2026-11-10, #214fba)
- [open item] Heidelberg Hospitation + Approbation (2026-11-10): asked RP Stuttgart about apostille, sworn translator, docentes list, stapled copies, post vs digital. Pending: RP reply, sending Böhler quote draft, Giovanni submitting the two prefilled web forms. Package in ~/Documents/09 Pacote Hospitation e Approbation (checklist inside). Contract the translation once, only after the RP answers. | check: Gmail: reply from the RP Stuttgart Referat 98 in thread 1a1b6092055424d9 (sent 2026-11-07 and follow-up … (since 2026-11-10, #2bcfdb)
- [open item] Heidelberg Hospitation: visa question sent to Generalkonsulat São Paulo 2026-11-09 (does a 26-day Hospitation need a visa; best visa for Approbation/work). Waiting for reply. Also open: call labs for Quantiferon in English, dTpa confirmation, translator totals (Martineschen, Böhler, 6 pages). | check: Gmail: reply from Generalkonsulat São Paulo (sent via web form 2026-11-09, preferred language English); page https://claude.ai/artifact/NUjiWLN6FxzMukGhkXS21f (since 2026-11-10, checked 2026-11-10, #78b830)
- [open item] Heidelberg Hospitation (2026-11-09 night): docs complete except dTpa (pertussis) vaccine, Quantiferon (~1 week before 2027-04-03), choosing translator (2 of 6 quoted, scans of 5 vaccine pages sent to Martineschen and Böhler). Carta-convite request only after all docs ready. Giovanni to review corrected CV in 06_Curriculo. | check: Gmail: replies from translators (Orçamento de tradução juramentada); page https://claude.ai/artifact/NUjiWLN6FxzMukGhkXS21f (since 2026-11-10, checked 2026-11-10, #fbb4a7)
- [open item] Heidelberg Hospitation plan (2026-11-09): 6 translator quote emails sent 2026-11-09, no replies yet; Giovanni must save the 'A' vaccine PDF from Katja's 2026-08-03 email (I cannot download Gmail attachments); carta-convite request only when all docs ready except Quantiferon; CV needs fixes (ACLS expired, PHTLS date, Saarland); passport, birth/naturalization certificate, anti-HBs not found. | check: Gmail: search replies from the 6 translators (subject 'Orçamento de tradução juramentada'); page … (since 2026-11-09, checked 2026-11-10, #54c2e8)
- [open item radiology] Radiology T2 stopped by Giovanni 2026-11-09 08:2x: EN tags complete (morph-tags-sonnet-en-20261109.jsonl.gz, 55,226 findings kept, 874 articles with none). DE 129/7135 raw rows, PT not started. Resume only if Giovanni asks: systemd-run --user --unit morph-tags-full env LANGS='de pt' tools/morph_tags_full.sh, watchdog tools/t2_check.py. Or proceed to S1c with EN tags only (his call). | check: systemctl --user is-active morph-tags-full; wc -l ~/dev/radiology-crawler/data/analysis/morph/raw-sonnet… (since 2026-11-09, #3fc512)
- [open item radiology] Radiology finding assistant (2026-11-09): when T2 finding tags are done, Giovanni wants R1 (X-ray literature review, then R2..R10) started; estimate its token cost first. Docs: docs/assistant-problem-statement.md, ADR-0007, requirements draft. | check: python3 -I ~/dev/radiology-crawler/tools/analysis_status.py show | grep -E 'T2|R1' (since 2026-11-09, #5f73cf)
- [open item radiology] Radiology S1c (2026-11-09): V2t, V4t (cd7558f, ADR 0005) and V3t r2 (76c17ec, ADR 0006) merged on provisional EN tags; params in data/analysis/v{2,3,4}t-*. Audit top-10 EN tagged/no-tags: V2t chose tag weight 0 (61.3 %), V3t 59.5/58.8 %, V4t 18.4/17.2 % (unit-L1 normalization, design limit). Left after T2: V1t (AN-57..59), full-tag final reruns of all four, outer scoring; port codex_hooks=false into morph_tags.run_codex; 30-min retry fix needs Giovanni's OK. | check: python3 -I ~/dev/radiology-… (since 2026-11-09, #9ce5c9)
- [open item] Wiki globe selection: MP-10 implemented and deployed on main 96396cc; red/green CSS test, 99 Elixir and 193 Elm tests, local pipeline and branch CI passed; served assets match. Live desktop/phone gesture verification remains: CUA tab attachment, DOM snapshot, screenshot and evaluate all fail with Cannot read properties of undefined (reading timeoutMs), including explicit timeout and fresh tab. No authentication bypass attempted. | check: Use CUA browser to reload the live wiki and drag across g… (since 2026-11-08, #95f4d6)
- [open item] Translation check (2026-11-06): burn timer re-enabled by Giovanni; next fire 2026-11-12 13:38 -03 (24 h before weekly budget renews). Daily trickle still on. ~2,863 p1 reviews pending; fix --yes not run; wiki pages not written. | check: systemctl --user is-enabled translation-check-burn.timer (since 2026-11-06, #8132b8)
(5 more open item(s) did not fit: mem pending)

## Recording

Load the GitHub tools first (`get_file_contents`, `create_branch`, `create_or_update_file`). Then create ONE new
file on `main` of `yujideluca/workflow-memory`; never edit an existing one.

path: `events/YYYY/MM/YYYYMMDDTHHMMSSZ-app-xxxxxx.md` (UTC time, xxxxxx = 6 random characters)

```
---
type: pref          # pref, fact, decision, task
scope: global
key: short.topic    # the same key replaces the old rule
tags: deploy, git   # optional, kinds of task from mem/tags.toml (listed in the brief)
owner: user         # only for what the user said
instance: app
ts: 2026-01-31T12:00:00Z
---
The rule, in the user's words.
```

When you finish a task, report the entries that shaped your answer: a file with `type: use`,
`target: ref1, ref2` (the #codes) and one short line of text. For a wrong or outdated entry use
`type: feedback`, `target: ref`, `signal: wrong` (or stale, helpful, not_helpful).
Open items: `type: task`, text `what is open | check: how to verify it still applies`, optional `category: x`.
Verify: `type: use`, `target: ref`, a line on how. Solved: `type: done`; park: `type: archive` (`reopen`
undoes it); delete: `type: forget`; each with `target: ref`.
No secrets or contact data: such files are quarantined.

