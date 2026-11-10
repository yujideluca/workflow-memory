# Rules tagged quiz

Generated 2026-11-10 from 1035 events. Do not edit: record changes as events.

QuizApp and QuizWeb

- [project.quizapp] QuizApp lives in ~/dev/QuizApp (Kotlin, GitHub remote yujideluca/german-quiz): a German B2 quiz with 3 modes and Anki-style scheduling, tested on the phone over adb. (#d368f5)
- [quiz.signing-key-backup] QuizApp signing key backup: german-quiz-release.jks is in Giovanni's Google Drive (My Drive root), uploaded 2026-10-22; original in ~/.android. Passwords are kept by Giovanni, not on Drive. (#8c714a)
- [quiz.web-standalone-release] QuizWeb may ship a standalone maintenance release when it contains relevant changes, without waiting for another Android release. Ports of unreleased Android features still follow app promotion. (#3a001b)
- [release.pool-promote] Question-pool updates (tools/data, i18n) that pass the automated pipeline (gate + mutation check, then beta) may be promoted to the stable app and the web version without asking again; app code releases still need Giovanni's go-ahead (2026-10-25). (#8c704c)
