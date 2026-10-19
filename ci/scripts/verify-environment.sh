#!/usr/bin/env bash
# Prints and checks the build toolchain so a failed build shows at a glance
# whether the agent itself is misconfigured. Safe to run locally too.
set -euo pipefail

required_java=21

echo "== Agent =="
echo "user: $(id -un) ($(id -u))  host: $(hostname)  workspace: $(pwd)"

echo "== Git =="
git --version
echo "commit: $(git rev-parse --verify -q HEAD || echo "none (not a git checkout or no commits)")"

echo "== Java =="
# The Maven wrapper prefers $JAVA_HOME over PATH, so check the JDK Maven will use.
if [ -n "${JAVA_HOME:-}" ]; then
    java_cmd="$JAVA_HOME/bin/java"
    echo "JAVA_HOME=$JAVA_HOME"
else
    java_cmd=$(command -v java || true)
fi
if [ -z "$java_cmd" ] || [ ! -x "$java_cmd" ]; then
    echo "ERROR: no Java found (JAVA_HOME unset and java not on PATH). Install JDK ${required_java}; see docs/installation/jenkins-on-azure-vm.md." >&2
    exit 1
fi
"$java_cmd" -version 2>&1
java_major=$("$java_cmd" -XshowSettings:properties -version 2>&1 | awk -F'= ' '/java.specification.version/ {print $2}')
java_major=${java_major#1.}   # Java 8 reports "1.8"
if [ "${java_major%%.*}" -lt "$required_java" ]; then
    echo "ERROR: Java ${required_java}+ required, but ${java_cmd} is Java ${java_major}." >&2
    echo "Fix JAVA_HOME for the Jenkins agent (Manage Jenkins > Nodes > Built-In Node > Environment variables)." >&2
    exit 1
fi

echo "== Maven (wrapper) =="
(cd application && ./mvnw -B -ntp --version)

echo "Environment OK"
