#!/bin/bash
# Setup script for the platform-analytics cloud environment. Paste it into the environment's Setup script box.
# Runs as root on Ubuntu 24.04 before Claude Code starts. It must exit 0 and finish in about five minutes.
# Every host is on the default allowlist (archive.ubuntu.com, github.com, pypi.org). Unconfirmed: whether the GitHub
# proxy serves release downloads from repos the session does not attach (the Synthea jar, the uv tarball, CPython 3.12).
set -euo pipefail

SYNTHEA_URL=https://github.com/synthetichealth/synthea/releases/download/v4.0.0/synthea-with-dependencies.jar
SYNTHEA_SHA256=ed43c20ad40ba5c3bc724503a5af032715fe3c491620b766148e7c2361e6ecc1
SYNTHEA_DIR=/opt/synthea
UV_URL=https://github.com/astral-sh/uv/releases/download/0.13.10/uv-x86_64-unknown-linux-gnu.tar.gz
UV_SHA256=bf65ac1a0af10f92c522d91ac096c7c0a39657647b155577e7836c2cbbb4526c

# OpenJDK 17 matches the laptop build. The image ships OpenJDK 21, so point java at 17.
apt-get update -q
DEBIAN_FRONTEND=noninteractive apt-get install -y -q openjdk-17-jre-headless
update-alternatives --set java /usr/lib/jvm/java-17-openjdk-amd64/bin/java

# The image ships uv. Install a pinned release only if it is missing.
if ! command -v uv > /dev/null; then
  curl -fsSL "$UV_URL" -o /tmp/uv.tar.gz
  echo "$UV_SHA256  /tmp/uv.tar.gz" | sha256sum -c -
  tar -xzf /tmp/uv.tar.gz -C /usr/local/bin --strip-components=1
fi

# Keep the jar outside the clone: jobs/nightly.sh links it into vendor/ when the clone lacks it.
mkdir -p "$SYNTHEA_DIR"
if ! echo "$SYNTHEA_SHA256  $SYNTHEA_DIR/synthea-with-dependencies.jar" | sha256sum -c --status - 2> /dev/null; then
  curl -fsSL "$SYNTHEA_URL" -o "$SYNTHEA_DIR/synthea-with-dependencies.jar"
  echo "$SYNTHEA_SHA256  $SYNTHEA_DIR/synthea-with-dependencies.jar" | sha256sum -c -
fi

# Warm the uv cache so the first nightly run does not wait on PyPI. Skip if the clone is not the working directory.
uv python install 3.12
if repo=$(git rev-parse --show-toplevel 2> /dev/null) && [[ -f "$repo/uv.lock" ]]; then
  (cd "$repo" && uv sync --frozen)
else
  echo "setup: no repo at $PWD, skipping uv sync; uv run syncs on first use"
fi
