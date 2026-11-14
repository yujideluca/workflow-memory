# Rules tagged git

Generated 2026-11-14 from 1094 events. Do not edit: record changes as events.

branches, commits, repos, GitHub

- [ci.required-jobs] Every CI job that checks a requirement must be a required check on main, and a push is done only when all its jobs are green, not just the required one. Lesson 2026-11-06: status-quo's windows job (SQ-36) stayed red from b701cda unnoticed because only gate was required. (#ea94f4)
- [git.no-force-push] Never force-push. (#932143)
- [pipeline-check.merge-block] Merges to main are blocked by the local pre-push check (pipeline-check --pre-push, hook in tools/hooks, enabled with git config core.hooksPath tools/hooks) because private repositories on the free GitHub plan cannot use branch protection; pipeline-check is public so CI needs no token (decided 2026-10-24). (#eba53a)
- [repos.public] Repos that need branch protection are public, because GitHub Free has no protection on private repos. german-quiz, remote-terminal, wiki, workflow-memory and processing-sketches were made public on 2026-10-25 after a clean secret scan. (#d52b3e)
- [repos.workflow-memory-unprotected] workflow-memory is intentionally without branch protection: its mem job pushes derived files to main with the built-in token and a required check rejects that push (simulation 2026-10-25). Local pre-push check stands in; pipeline-check.toml has protection_exception, so protecao-de-branch is an accepted aviso there, not a failure. (#b68bd7)
- [wiki.coauthor-trailer] wiki publish adds a Co-Authored-By line only from --co-author 'Name <email>' (or WIKI_CO_AUTHOR): pass the exact attribution line your own session was given, none if you have none. Never a fixed model name. (#3cb16b)
- [work.document-commits] Every commit message must document what was modified (files and why, requirements touched, anything changed outside the repo); split piled-up work into commits by area. Giovanni asked for this on 2026-11-01 and said it should always be done. (#bc4259)
- [work.github-standard] Every project has a versioned repository on GitHub (private unless it must be public); a folder in ~/dev without git and a remote is a gap to fix. (#e5c35f)
- [work.maintenance] Software projects follow the golden path: ADRs for structural decisions, requirements before code, one quality gate run by CI on every push, debt as GitHub Issues labelled debt/P1-P3, about one session in five on debt or prevention, monthly architecture review. New projects start from ~/dev/project-template. (#724cdb)
- [work.shared-tools] A tool used by more than one project lives once, in its own repository, and is consumed by pinned version, never copied (example: pipeline-check, github.com/yujideluca/pipeline-check). (#34b423)
- [work.single-branch] Keep every repository on one branch, main. Use a branch only briefly to get CI before promoting to main, then delete it (local and remote) and remove its worktree. Never leave parallel feature, session or draft branches; fold their work into main. (#f8fbd3)
