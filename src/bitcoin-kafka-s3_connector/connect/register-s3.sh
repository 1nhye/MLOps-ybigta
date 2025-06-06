#!/usr/bin/env bash
set -e

echo "🔄  Waiting for Kafka Connect REST ..."
for i in {1..60}; do
  if curl -s http://connect:8083/connectors >/dev/null 2>&1; then
    echo "✅  Kafka Connect REST is ready!"
    break
  fi
  echo "⏳  Not yet... ($i)"
  sleep 5
done

if ! curl -s http://connect:8083/connectors >/dev/null 2>&1; then
  echo "❌  Kafka Connect REST never became ready"
  exit 1
fi


echo "🗑️  Removing existing S3 connector if it exists..."
curl -s -X DELETE http://connect:8083/connectors/s3-sink || echo "s3-sink not found (OK)"


sleep 2

echo "⚡  Registering S3 Sink"
curl -s -X POST -H "Content-Type: application/json" \
     --data @/connectors/s3-link.json \
     http://connect:8083/connectors

echo ""
echo "✅  S3 Sink Connector registered successfully!" 