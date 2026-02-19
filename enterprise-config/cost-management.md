# Cost Management Guide

## Model Tiers

| Model | Input (per 1M tokens) | Output (per 1M tokens) | Use For |
|-------|----------------------|------------------------|---------|
| **Haiku 4.5** | $1.00 | $5.00 | Simple tasks, fast iteration — linting, formatting, simple Q&A |
| **Sonnet 4.6** | $3.00 | $15.00 | General development — code review, feature implementation, debugging |
| **Opus 4.6** | $5.00 | $25.00 | Complex reasoning — architecture decisions, security audits, system design |

## Cost Optimization Strategies

### 1. Match Model to Task Complexity
- Use haiku for agents that do simple, repetitive work (linting, formatting)
- Use sonnet for general development (default for most work)
- Reserve opus for tasks requiring deep reasoning (architecture, security)

### 2. Context Window Management
- Enable `autoCompact` in settings to automatically compress context when it grows large
- Use `/compact` command to manually compress when you notice slowdown
- Keep CLAUDE.md lean — only include information Claude needs
- Scope agents with `maxTurns` to prevent runaway sessions

### 3. Budget Controls
- Set `max_turns` in Agent SDK scripts to prevent runaway sessions
- Monitor per-user and per-project spending
- Set up alerts at 80% and 100% of budget thresholds
- Review weekly cost reports to identify optimization opportunities

### 4. Token Efficiency
- Write specific, focused prompts (reduces input tokens)
- Use agents with restricted tool sets (reduces unnecessary exploration)
- Leverage skills for repetitive tasks (consistent, predictable token usage)
- Use read-only permission mode when writes aren't needed

## Budget Formula
```
Monthly Cost = Sum of (Input Tokens x Input Price + Output Tokens x Output Price)

Current per-model pricing (as of early 2026):
- Haiku 4.5:  $1.00/M input,  $5.00/M output
- Sonnet 4.6: $3.00/M input,  $15.00/M output
- Opus 4.6:   $5.00/M input,  $25.00/M output
```
