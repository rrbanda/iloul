#!/bin/bash
# Spec-Kit Integration for v1
SPEC_KIT_PATH="$(dirname $(dirname $(dirname $(realpath $0))))/spec-kit"

echo "🛠️ Using spec-kit from: $SPEC_KIT_PATH"
echo "📍 Current specs directory: $(pwd)"

case "$1" in
  "clarify")
    $SPEC_KIT_PATH/clarify $2
    ;;
  "plan")
    $SPEC_KIT_PATH/plan $2
    ;;
  "tasks")
    $SPEC_KIT_PATH/tasks $2
    ;;
  *)
    echo "Usage: ./use-spec-kit.sh [clarify|plan|tasks] <spec-file>"
    echo "Example: ./use-spec-kit.sh clarify agents.md"
    ;;
esac
