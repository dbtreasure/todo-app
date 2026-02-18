# Cost Management Guide

## Model Tiers

| Model | Cost | Use For | Examples |
|-------|------|---------|----------|
| **Haiku** | $ | Simple tasks, fast iteration | Linting, formatting, simple Q&A, file search |
| **Sonnet** | $$ | General development work | Code review, feature implementation, debugging |
| **Opus** | $$$$ | Complex reasoning | Architecture decisions, security audits, system design |

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
- Set `maxTurnsPerSession` in managed policies
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

Approximate per-model pricing (check current rates):
- Haiku:  ~$0.25/M input,  ~$1.25/M output
- Sonnet: ~$3/M input,     ~$15/M output
- Opus:   ~$15/M input,    ~$75/M output
```
