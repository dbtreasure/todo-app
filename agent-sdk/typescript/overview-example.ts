/**
 * Minimal Claude Code Agent SDK Example (TypeScript)
 *
 * Demonstrates the simplest possible agent: create a session, send a message,
 * and print the response.
 *
 * Usage:
 *   npx tsx agent-sdk/typescript/overview-example.ts
 */

import { ClaudeCodeAgent, AgentConfig } from "@anthropic-ai/claude-code-sdk";

async function main() {
  const agent = new ClaudeCodeAgent({
    model: "sonnet",
    permissionMode: "read-only",
    maxTurns: 3,
  });

  const result = await agent.run(
    "List all TypeScript files in src/ and summarize the project structure."
  );

  console.log("Agent response:");
  console.log(result.text);
  console.log(
    `\nTokens used: ${result.usage.inputTokens} in, ${result.usage.outputTokens} out`
  );
}

main().catch(console.error);
