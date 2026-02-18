/**
 * First Agent with Error Handling (TypeScript)
 *
 * Demonstrates proper error handling and logging.
 *
 * Usage:
 *   npx tsx src/first-agent-with-error-handling.ts
 */

import "dotenv/config";
import {
  ClaudeCodeAgent,
  AgentError,
  AuthenticationError,
  RateLimitError,
} from "@anthropic-ai/claude-code-sdk";

async function main() {
  console.log("[INFO] Starting agent...");

  try {
    const agent = new ClaudeCodeAgent({
      model: "sonnet",
      permissionMode: "read-only",
      maxTurns: 5,
    });

    const result = await agent.run(
      "Read src/lib/actions.ts and explain what each server action does."
    );

    console.log(
      `[INFO] Agent completed. Tokens: ${result.usage.inputTokens} in, ${result.usage.outputTokens} out`
    );
    console.log(result.text);
  } catch (error) {
    if (error instanceof AuthenticationError) {
      console.error("[ERROR] Authentication failed. Check your ANTHROPIC_API_KEY.");
      process.exit(1);
    }
    if (error instanceof RateLimitError) {
      console.error("[ERROR] Rate limited. Wait and try again.");
      process.exit(1);
    }
    if (error instanceof AgentError) {
      console.error(`[ERROR] Agent error: ${error.message}`);
      process.exit(1);
    }
    throw error;
  }
}

main();
