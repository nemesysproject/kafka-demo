#!/usr/bin/env bash
# ==============================================================================
# Helper Script to Generate KRaft Cluster ID and Format Storage for Kafka
# ==============================================================================

set -euo pipefail

echo "=================================================="
echo " Generating Kafka KRaft Cluster UUID..."
echo "=================================================="

# Check if docker is running
if ! docker info >/dev/null 2>&1; then
  echo "Error: Docker daemon is not running. Please start Docker first." >&2
  exit 1
fi

# Run a temporary kafka container to generate a cluster ID
CLUSTER_ID=$(docker run --rm apache/kafka:3.8.0 /opt/kafka/bin/kafka-storage.sh random-uuid)

echo "Generated KRaft Cluster ID: ${CLUSTER_ID}"
echo ""
echo "You can set this in your docker-compose.yml under CLUSTER_ID:"
echo "CLUSTER_ID: \"${CLUSTER_ID}\""
echo "=================================================="
