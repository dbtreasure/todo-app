# Enterprise Deployment Models

## Centralized Deployment
- Single IT team manages all Claude Code configuration
- Managed MCP policy pushed to all developers
- Consistent tool permissions and environment settings
- Best for: regulated industries, large organizations

## Team-Based Deployment
- Each team manages their own Claude Code configuration
- Shared plugins and MCP servers within team boundaries
- Teams choose their own tool permissions
- Best for: autonomous teams, startups, R&D organizations

## Hybrid Deployment
- Organization sets baseline policies via managed config files
- Teams can extend but not override organizational rules
- Best for: most enterprises balancing governance with autonomy

## Key Configuration Files
- `managed-mcp.json` — Organization-wide MCP server configuration (just `mcpServers`)
- `managed-settings.json` — Enterprise policy: permissions (allow/deny patterns), default environment variables
- `.claude/settings.json` — Project-level settings
- `~/.claude/settings.json` — User-level settings
