/**
 * First Agent -- Basic Claude Agent SDK Usage (TypeScript)
 *
 * Sends a prompt using query(), iterates over streamed messages,
 * and prints the result.
 *
 * Usage:
 *   npx tsx src/first-agent.ts
 */

import "dotenv/config";
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
    maxTurns: 5,
  };

  const response = query({
    prompt:
      "Read src/lib/actions.ts and explain what each server action does, " +
      "including its parameters and return type.",
    options,
  });

  for await (const message of response) {
    if (message.type === "assistant") {
      for (const block of message.content) {
        if (block.type === "text") {
          console.log(block.text);
        }
      }
    } else if (message.type === "result") {
      console.log(`\nCost: $${message.costUsd.toFixed(4)}`);
      console.log(`Duration: ${message.durationMs}ms`);
    }
  }
}

main().catch(console.error);
