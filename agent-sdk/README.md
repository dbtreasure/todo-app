# Claude Code Agent SDK

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
uv add claude-code-sdk python-dotenv
```

### TypeScript
```bash
npm install @anthropic-ai/claude-code-sdk
```

Set `ANTHROPIC_API_KEY` in your environment or `.env` file.
