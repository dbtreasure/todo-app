#!/bin/bash
# Generate self-signed CA and client certificates for mTLS testing.
#
# This creates:
#   - ca.key / ca.crt — Certificate Authority
#   - client.key / client.crt — Client certificate signed by the CA
#
# Usage: ./enterprise-config/generate-client-cert.sh [output-dir]

set -euo pipefail

OUTPUT_DIR="${1:-./certs}"
mkdir -p "$OUTPUT_DIR"

echo "Generating certificates in $OUTPUT_DIR..."

# Generate CA private key and self-signed certificate
openssl genrsa -out "$OUTPUT_DIR/ca.key" 4096
openssl req -new -x509 -key "$OUTPUT_DIR/ca.key" -sha256 \
    -subj "/C=US/ST=CA/O=TestOrg/CN=TestCA" \
    -days 365 -out "$OUTPUT_DIR/ca.crt"

# Generate client private key and CSR
openssl genrsa -out "$OUTPUT_DIR/client.key" 4096
openssl req -new -key "$OUTPUT_DIR/client.key" \
    -subj "/C=US/ST=CA/O=TestOrg/CN=claude-code-client" \
    -out "$OUTPUT_DIR/client.csr"

# Sign client certificate with CA
openssl x509 -req -in "$OUTPUT_DIR/client.csr" \
    -CA "$OUTPUT_DIR/ca.crt" -CAkey "$OUTPUT_DIR/ca.key" \
    -CAcreateserial -sha256 -days 365 \
    -out "$OUTPUT_DIR/client.crt"

# Clean up CSR
rm -f "$OUTPUT_DIR/client.csr" "$OUTPUT_DIR/ca.srl"

echo ""
echo "Certificates generated:"
echo "  CA:     $OUTPUT_DIR/ca.crt"
echo "  Client: $OUTPUT_DIR/client.crt"
echo "  Key:    $OUTPUT_DIR/client.key"
echo ""
echo "Set these environment variables:"
echo "  export MTLS_CLIENT_CERT=$OUTPUT_DIR/client.crt"
echo "  export MTLS_CLIENT_KEY=$OUTPUT_DIR/client.key"
echo "  export NODE_EXTRA_CA_CERTS=$OUTPUT_DIR/ca.crt"
