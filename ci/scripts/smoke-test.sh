#!/usr/bin/env bash
# Usage: smoke-test.sh <image:tag>
# Starts the image on a random localhost port, waits for readiness, checks the API
# answers and the process is not root, then removes the container.
set -euo pipefail

image="${1:?usage: smoke-test.sh <image:tag>}"
name="smoke-${BUILD_TAG:-local}-$$"
timeout_s=60

cleanup() {
    docker logs "$name" > smoke-test-container.log 2>&1 || true
    docker rm -f "$name" >/dev/null 2>&1 || true
}
trap cleanup EXIT

docker run -d --name "$name" -p 127.0.0.1::8080 "$image" >/dev/null
port=$(docker port "$name" 8080/tcp | head -n 1 | awk -F: '{print $NF}')
echo "Started $image as $name on 127.0.0.1:$port"

for ((i = 1; i <= timeout_s; i++)); do
    if curl -fsS "http://127.0.0.1:${port}/actuator/health/readiness" 2>/dev/null | grep -q '"UP"'; then
        echo "Readiness UP after ${i}s"
        break
    fi
    if ((i == timeout_s)); then
        echo "ERROR: not ready after ${timeout_s}s; container log in smoke-test-container.log" >&2
        exit 1
    fi
    sleep 1
done

curl -fsS "http://127.0.0.1:${port}/api/hello?name=smoke"; echo

uid=$(docker exec "$name" id -u)
if [[ "$uid" == "0" ]]; then
    echo "ERROR: container runs as root" >&2
    exit 1
fi
echo "Runs as uid $uid (non-root)"
