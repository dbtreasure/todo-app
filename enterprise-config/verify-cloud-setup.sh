#!/bin/bash
# Verify cloud provider setup for Claude Code.
# Checks that required environment variables are set and tests connectivity.

set -euo pipefail

echo "=== Claude Code Cloud Provider Verification ==="
echo ""

ERRORS=0

check_var() {
    local var_name="$1"
    local provider="$2"
    if [ -n "${!var_name:-}" ]; then
        echo "  [OK] $var_name is set"
    else
        echo "  [MISSING] $var_name is not set"
        ERRORS=$((ERRORS + 1))
    fi
}

# AWS Bedrock
echo "── AWS Bedrock ──"
if [ "${CLAUDE_CODE_USE_BEDROCK:-}" = "1" ]; then
    check_var "AWS_ACCESS_KEY_ID" "Bedrock"
    check_var "AWS_SECRET_ACCESS_KEY" "Bedrock"
    check_var "AWS_REGION" "Bedrock"
    if command -v aws &> /dev/null; then
        echo "  Checking AWS connectivity..."
        if aws sts get-caller-identity &> /dev/null; then
            echo "  [OK] AWS authentication successful"
        else
            echo "  [FAIL] AWS authentication failed"
            ERRORS=$((ERRORS + 1))
        fi
    else
        echo "  [SKIP] AWS CLI not installed — cannot verify connectivity"
    fi
else
    echo "  [SKIP] CLAUDE_CODE_USE_BEDROCK not set"
fi
echo ""

# Google Vertex AI
echo "── Google Vertex AI ──"
if [ "${CLAUDE_CODE_USE_VERTEX:-}" = "1" ]; then
    check_var "ANTHROPIC_VERTEX_PROJECT_ID" "Vertex"
    check_var "CLOUD_ML_REGION" "Vertex"
    check_var "GOOGLE_APPLICATION_CREDENTIALS" "Vertex"
    if [ -n "${GOOGLE_APPLICATION_CREDENTIALS:-}" ] && [ -f "${GOOGLE_APPLICATION_CREDENTIALS}" ]; then
        echo "  [OK] Service account key file exists"
    elif [ -n "${GOOGLE_APPLICATION_CREDENTIALS:-}" ]; then
        echo "  [FAIL] Service account key file not found: $GOOGLE_APPLICATION_CREDENTIALS"
        ERRORS=$((ERRORS + 1))
    fi
else
    echo "  [SKIP] CLAUDE_CODE_USE_VERTEX not set"
fi
echo ""

# Azure AI Foundry
echo "── Azure AI Foundry ──"
if [ -n "${ANTHROPIC_BASE_URL:-}" ] && echo "$ANTHROPIC_BASE_URL" | grep -q "azure"; then
    check_var "ANTHROPIC_BASE_URL" "Azure"
    check_var "ANTHROPIC_API_KEY" "Azure"
else
    echo "  [SKIP] Azure not configured (ANTHROPIC_BASE_URL does not contain 'azure')"
fi
echo ""

# Summary
echo "=== Summary ==="
if [ $ERRORS -eq 0 ]; then
    echo "All checks passed."
else
    echo "$ERRORS issue(s) found. Review the output above."
fi
exit $ERRORS
