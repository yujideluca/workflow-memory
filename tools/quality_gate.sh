#!/usr/bin/env bash
# Quality gate: the unit tests of the memory plus the pipeline-check program's own tests and fitness checks.
# CI runs it through tools/pipeline-check (ADR-0004: the program measures and blocks).
set -euo pipefail
cd "$(dirname "$0")/.."
python3 -m unittest discover -s tests -t .
tools/pipeline-check.sh --measure-only
