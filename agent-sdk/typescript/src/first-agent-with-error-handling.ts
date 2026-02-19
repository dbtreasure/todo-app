/**
 * First Agent with Error Handling (TypeScript)
 *
 * Demonstrates proper error handling and logging using the
 * Claude Agent SDK.
 *
 * Usage:
 *   npx tsx src/first-agent-with-error-handling.ts
 */

import "dotenv/config";
import {
  query,
  type Options,
  type SDKAssistantMessage,
  type SDKResultMessage,
} from "@anthropic-ai/claude-agent-sdk";

async function main() {
  console.log("[INFO] Starting agent...");

  try {
    const options: Options = {
      permissionMode: "bypassPermissions",
      model: "claude-sonnet-4-5",
      maxTurns: 5,
    };

    const response = query({
      prompt:
        "Read src/lib/actions.ts and explain what each server action does.",
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
        console.log(
          `[INFO] Agent completed. Cost: $${message.total_cost_usd.toFixed(4)}, Duration: ${message.duration_ms}ms`
        );
        console.log(`[INFO] Session ID: ${message.session_id}`);
      }
    }
  } catch (error) {
    if (error instanceof Error) {
      console.error(`[ERROR] ${error.name}: ${error.message}`);
    } else {
      console.error("[ERROR] Unknown error:", error);
    }
    process.exit(1);
  }
}

main();
