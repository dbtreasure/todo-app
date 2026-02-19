# Claude Agent SDK

## CLI vs SDK: When to Use Each

### Use the CLI When:
- Interactive development (you're at the terminal)
- One-off tasks and explorations
- Quick code generation, refactoring, or debugging
- You want the full built-in tool set (Read, Edit, Bash, etc.)
- Headless mode covers your CI/CD needs

### Use the SDK When:
- Building automated pipelines (code review bots, deployment agents)
- Creating multi-agent workflows (planner + reviewer + executor)
- Embedding Claude into existing applications (web apps, Slack bots)
- You need programmatic control over permissions, sessions, and tools
- Custom tools beyond what the CLI provides
- Long-running background agents with session persistence

### Quick Decision Tree
```
Need interactive terminal experience? → CLI
Need automation/integration?          → SDK
Need multi-agent coordination?        → SDK
Need custom tool definitions?         → SDK
Need session persistence?             → SDK
CI/CD pipeline?                       → CLI (headless) or SDK
```

## Getting Started

### Python
```bash
uv add claude-agent-sdk python-dotenv
```

### TypeScript
```bash
npm install @anthropic-ai/claude-agent-sdk
```

Set `ANTHROPIC_API_KEY` in your environment or `.env` file.

## Python Usage

```python
from claude_agent_sdk import query, ClaudeAgentOptions, AssistantMessage, TextBlock, ResultMessage

async def main():
    options = ClaudeAgentOptions(
        permission_mode="bypassPermissions",
        model="claude-sonnet-4-5",
        max_turns=3,
    )
    async for message in query(prompt="Your task here", options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(block.text)
        elif isinstance(message, ResultMessage):
            print(f"Cost: ${message.cost_usd:.4f}")
```

## TypeScript Usage

```typescript
import { query, type Options } from "@anthropic-ai/claude-agent-sdk";

const options: Options = {
  permissionMode: "bypassPermissions",
  model: "claude-sonnet-4-5",
  maxTurns: 3,
};
const response = query({ prompt: "Your task here", options });
for await (const message of response) {
  if (message.type === "assistant") {
    for (const block of message.content) {
      if (block.type === "text") {
        console.log(block.text);
      }
    }
  } else if (message.type === "result") {
    console.log(`Cost: $${message.costUsd.toFixed(4)}`);
  }
}
```
