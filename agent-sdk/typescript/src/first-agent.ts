/**
 * First Agent — Basic Claude Code SDK Usage (TypeScript)
 *
 * Creates an agent, sends a task, and prints the result.
 *
 * Usage:
 *   npx tsx src/first-agent.ts
 */

import "dotenv/config";
import { ClaudeCodeAgent } from "@anthropic-ai/claude-code-sdk";

async function main() {
  const agent = new ClaudeCodeAgent({
    model: "sonnet",
    permissionMode: "read-only",
    maxTurns: 5,
  });

  const result = await agent.run(
    "Read src/lib/actions.ts and explain what each server action does, " +
      "including its parameters and return type."
  );

  console.log(result.text);
}

main().catch(console.error);
