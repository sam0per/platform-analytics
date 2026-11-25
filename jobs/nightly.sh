#!/usr/bin/env bash
# Nightly job: refresh the raw tables, rebuild the models, retrain the churn model, check every signed-off number.
# Runs from anywhere inside the repo, on a laptop or in a cloud session. The first failing step stops the job with its exit code.
set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

step() {
  echo "== $1"
  shift
  "$@" || { rc=$?; echo "nightly: FAILED at: $*" >&2; exit "$rc"; }
}

echo "host: $(uname -sm), cloud session: ${CLAUDE_CODE_REMOTE:-false}"
# cloud/setup.sh keeps the Synthea jar outside the clone, because a cached environment can start from a fresh clone.
if [[ ! -e vendor/synthea-with-dependencies.jar && -e /opt/synthea/synthea-with-dependencies.jar ]]; then
  mkdir -p vendor && ln -s /opt/synthea/synthea-with-dependencies.jar vendor/
fi
step "refresh raw tables" uv run generate
step "rebuild models" uv run dbt build --quiet
step "retrain churn model (accuracy %)" uv run check accuracy_clean
step "check every number" uv run check all
echo "nightly: OK"
