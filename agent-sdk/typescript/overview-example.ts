/**
 * Minimal Claude Agent SDK Example (TypeScript)
 *
 * Demonstrates the simplest possible usage: send a prompt using query(),
 * iterate over streamed messages, and print the response.
 *
 * Usage:
 *   npx tsx agent-sdk/typescript/overview-example.ts
 */

import {
  query,
  type Options,
  type SDKAssistantMessage,
  type SDKResultMessage,
} from "@anthropic-ai/claude-agent-sdk";

async function main() {
  const options: Options = {
    permissionMode: "bypassPermissions",
    model: "claude-sonnet-4-5",
    maxTurns: 3,
  };

  console.log("Agent response:");
  const response = query({
    prompt:
      "List all TypeScript files in src/ and summarize the project structure.",
    options,
  });

  for await (const message of response) {
    if (message.type === "assistant") {
      for (const block of message.message.content) {
        if (block.type === "text") {
          console.log(block.text);
        }
      }
    } else if (message.type === "result") {
      console.log(`\nCost: $${message.total_cost_usd.toFixed(4)}`);
      console.log(`Duration: ${message.duration_ms}ms`);
      console.log(`Session ID: ${message.session_id}`);
    }
  }
}

main().catch(console.error);
