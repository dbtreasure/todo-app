#!/bin/bash
# Network audit script — verifies connectivity and security configuration.

set -euo pipefail

echo "=== Network Audit ==="
echo ""

# Proxy configuration
echo "── Proxy Configuration ──"
echo "HTTP_PROXY:  ${HTTP_PROXY:-not set}"
echo "HTTPS_PROXY: ${HTTPS_PROXY:-not set}"
echo "NO_PROXY:    ${NO_PROXY:-not set}"
echo ""

# DNS resolution
echo "── DNS Resolution ──"
for host in api.anthropic.com github.com; do
    if nslookup "$host" &> /dev/null; then
        echo "  [OK] $host resolves"
    else
        echo "  [FAIL] $host does not resolve"
    fi
done
echo ""

# TLS handshake
echo "── TLS Handshake ──"
for host in api.anthropic.com:443; do
    if echo | openssl s_client -connect "$host" -servername "${host%%:*}" 2>/dev/null | grep -q "Verify return code: 0"; then
        echo "  [OK] $host — TLS handshake successful, certificate valid"
    else
        echo "  [WARN] $host — TLS handshake issue (check CA certificates)"
    fi
done
echo ""

# Custom CA certificate
echo "── CA Certificates ──"
if [ -n "${NODE_EXTRA_CA_CERTS:-}" ]; then
    if [ -f "$NODE_EXTRA_CA_CERTS" ]; then
        echo "  [OK] NODE_EXTRA_CA_CERTS file exists: $NODE_EXTRA_CA_CERTS"
        openssl x509 -in "$NODE_EXTRA_CA_CERTS" -noout -subject -dates 2>/dev/null || echo "  [WARN] Could not parse certificate"
    else
        echo "  [FAIL] NODE_EXTRA_CA_CERTS file not found: $NODE_EXTRA_CA_CERTS"
    fi
else
    echo "  [SKIP] NODE_EXTRA_CA_CERTS not set"
fi
echo ""

# mTLS client certificate
echo "── mTLS Client Certificate ──"
if [ -n "${CLAUDE_CODE_CLIENT_CERT:-}" ] && [ -f "${CLAUDE_CODE_CLIENT_CERT:-}" ]; then
    echo "  [OK] Client cert exists: $CLAUDE_CODE_CLIENT_CERT"
    openssl x509 -in "$CLAUDE_CODE_CLIENT_CERT" -noout -subject -dates 2>/dev/null || true
else
    echo "  [SKIP] CLAUDE_CODE_CLIENT_CERT not set or file not found"
fi
echo ""

echo "=== Audit Complete ==="
