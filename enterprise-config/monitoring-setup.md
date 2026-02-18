# Monitoring and Analytics Setup

## Key Metrics to Track

### Usage Metrics
- **Tokens per session**: Input + output tokens consumed per session
- **Sessions per user per day**: Usage frequency across the team
- **Tool invocations by type**: Which tools are used most (Read, Edit, Bash, etc.)
- **Model distribution**: Percentage of requests to each model (haiku vs sonnet vs opus)

### Performance Metrics
- **Response latency (p50, p95, p99)**: Time from request to first token
- **Session duration**: How long interactive sessions last
- **Turns per session**: Average number of agent turns
- **Error rate**: Failed tool calls, API errors, timeouts

### Cost Metrics
- **Cost per session**: Total token cost per interactive session
- **Cost per user per month**: Aggregated spending by team member
- **Cost by model tier**: Spending breakdown by haiku/sonnet/opus
- **Cost by project**: Which repositories consume the most budget

## Alerting Rules

| Alert | Condition | Severity |
|-------|-----------|----------|
| High token usage | > 1M tokens/session | Warning |
| Excessive sessions | > 50 sessions/user/day | Warning |
| API errors spike | Error rate > 5% over 15 min | Critical |
| Budget threshold | Monthly spend > 80% of budget | Warning |
| Budget exceeded | Monthly spend > 100% of budget | Critical |
| Model policy violation | Denied model used | Critical |

## Dashboard Recommendations

### Executive Dashboard
- Total spend (MTD vs budget)
- Active users (DAU/WAU/MAU)
- Top 10 users by token consumption
- Cost trend (daily for last 30 days)

### Engineering Dashboard
- Tool usage heatmap (tool x time of day)
- Error rate by tool type
- Latency percentiles over time
- Sessions by project/repository

### Cost Management Dashboard
- Cost per model tier (stacked area chart)
- Cost per team (bar chart)
- Token efficiency (output tokens / input tokens ratio)
- Projected monthly spend

## OpenTelemetry Integration

Claude Code exports telemetry via OTLP. Set the following environment variables:

```bash
export OTEL_EXPORTER_OTLP_ENDPOINT=https://your-collector:4318
export OTEL_EXPORTER_OTLP_HEADERS="Authorization=Bearer token"
export OTEL_SERVICE_NAME=claude-code
```

Compatible collectors: Datadog, New Relic, Grafana, Honeycomb, Jaeger.
