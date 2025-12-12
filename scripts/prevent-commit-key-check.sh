#!/usr/bin/env bash
# Prevent committing private keys or .pem/.key files
set -e
EXIT_CODE=0
for FILE in $(git diff --cached --name-only); do
  if [[ -f "$FILE" ]]; then
    if grep -Iq "PRIVATE KEY" "$FILE" || grep -Iq "BEGIN RSA PRIVATE KEY" "$FILE" || [[ "$FILE" =~ (\.pem|\.key|id_ed25519)$ ]]; then
      echo "Error: Attempt to commit private key or PEM file: $FILE"
      EXIT_CODE=1
    fi
  fi
done
if [[ $EXIT_CODE -ne 0 ]]; then
  echo "Remove sensitive data before committing."
  exit 1
fi
exit 0
