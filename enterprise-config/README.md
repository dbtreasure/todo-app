# Enterprise Deployment Models

## Centralized Deployment
- Single IT team manages all Claude Code configuration
- Managed MCP policy pushed to all developers
- Consistent model access, tool permissions, and audit logging
- Best for: regulated industries, large organizations

## Team-Based Deployment
- Each team manages their own Claude Code configuration
- Shared plugins and MCP servers within team boundaries
- Teams choose their own models and tool permissions
- Best for: autonomous teams, startups, R&D organizations

## Hybrid Deployment
- Organization sets baseline policies (managed-mcp.json)
- Teams can extend but not override organizational rules
- Example: org blocks opus model for cost control, but teams choose between sonnet and haiku
- Best for: most enterprises balancing governance with autonomy

## Key Configuration Files
- `managed-mcp.json` — Organization-wide policies and MCP server config
- `.claude/settings.json` — Project-level settings (must comply with managed policies)
- `~/.claude/settings.json` — User-level settings (must comply with managed policies)
