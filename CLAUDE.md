# Todo App

## Overview

A full-stack CRUD todo application built with Next.js 15 (App Router), React 19, Tailwind CSS 4, and MongoDB. The UI is built entirely with Catalyst components from the Tailwind CSS team.

This project was originally an Express.js 4 / EJS server-rendered app and was rewritten from scratch to use a modern React stack while keeping the same MongoDB database and collection.

## Tech Stack

- **Framework:** Next.js 15 with App Router
- **Language:** TypeScript (strict mode)
- **UI Components:** Catalyst UI Kit (Tailwind CSS team's React component library)
- **Styling:** Tailwind CSS 4 via `@tailwindcss/postcss`, Inter font
- **Headless UI:** Headless UI v2 (peer dependency of Catalyst)
- **Database:** MongoDB via Mongoose 8
- **Runtime:** Node.js

## Project Structure

```
src/
  app/
    layout.tsx          # Root layout - imports Tailwind CSS, loads Inter font, sets metadata
    page.tsx            # Server component - fetches todos from DB, passes to TodoList
    todo-list.tsx       # Client component - table rendering, dialog state management, CRUD UI
  components/           # Catalyst UI components (copied from the kit, not installed via npm)
    button.tsx          # Button with solid/outline/plain variants, 20+ color options
    table.tsx           # Table, TableHead, TableBody, TableRow, TableHeader, TableCell
    input.tsx           # Input with InputGroup for icon positioning
    textarea.tsx        # Textarea with optional resize
    dialog.tsx          # Dialog, DialogTitle, DialogDescription, DialogBody, DialogActions
    fieldset.tsx        # Fieldset, Field, Label, Description, ErrorMessage, FieldGroup, Legend
    heading.tsx         # Heading (h1-h6) and Subheading
    text.tsx            # Text, TextLink, Strong, Code
    link.tsx            # Link wrapper integrating Headless UI DataInteractive with Next.js Link
    badge.tsx           # Badge and BadgeButton with color variants
    divider.tsx         # Horizontal rule divider with soft option
  lib/
    actions.ts          # Server Actions: getTodos, createTodo, updateTodo, deleteTodo
    mongodb.ts          # MongoDB connection singleton with global caching for HMR
    models/
      todo.ts           # Mongoose schema: { title: String (required), desc: String, timestamps }
  styles/
    tailwind.css        # Tailwind CSS entry point with Inter font theme config
```

## Architecture

### Data Flow

1. `page.tsx` is a **server component** that calls `getTodos()` server action at request time (`force-dynamic`)
2. Todos are serialized (ObjectIds to strings, Dates to ISO strings) and passed as props to `TodoList`
3. `todo-list.tsx` is a **client component** that renders the Catalyst Table and manages dialog state
4. Create/Edit/Delete operations call server actions directly, which run on the server, mutate MongoDB, and call `revalidatePath('/')` to refresh the page data

### Catalyst Components

The Catalyst components in `src/components/` are **source code copies** from the Catalyst UI Kit (`/Users/dan/Downloads/catalyst-ui-kit/typescript/`). They are not an npm package. The only modification from the kit is `link.tsx`, which was updated to use Next.js `<Link>` instead of a plain `<a>` tag.

These components depend on:
- `@headlessui/react` - for accessible primitives (Dialog, Button, Input, Textarea, Field, Label, etc.)
- `clsx` - for conditional class composition
- `tailwindcss` v4 - for styling via utility classes and CSS custom properties

If updating Catalyst components, copy the new versions from the kit and re-apply the Next.js Link integration in `link.tsx`.

### MongoDB Connection

`src/lib/mongodb.ts` caches the Mongoose connection on `globalThis` to survive Next.js HMR reloads in development. The connection string comes from `MONGODB_URI` in `.env`.

### Database

- **Database:** `todoDb`
- **Collection:** `todos` (Mongoose model name `todo` pluralizes to `todos`)
- **Schema fields:** `title` (String, required), `desc` (String, optional), `createdAt`, `updatedAt` (auto-managed by Mongoose timestamps)

This is the same database and collection the original Express app used, so existing data carries over.

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `MONGODB_URI` | MongoDB connection string | `mongodb://localhost:27017/todoDb` |

Defined in `.env` (gitignored via `.env.local` pattern, but `.env` itself is committed for this project).

## Running the App

```bash
npm install
npm run dev     # starts on http://localhost:3000
```

Requires MongoDB running locally on port 27017.

## Available Scripts

| Script | Command | Description |
|--------|---------|-------------|
| `dev` | `next dev` | Start development server with HMR |
| `build` | `next build` | Production build |
| `start` | `next start` | Serve production build |
| `lint` | `next lint` | Run Next.js ESLint |

## Path Aliases

TypeScript path alias `@/*` maps to `./src/*`. Use `@/components/button` instead of relative paths.

## Key Patterns

- **No separate API routes.** All database operations go through Next.js Server Actions in `src/lib/actions.ts`. No REST API, no route handlers.
- **Dialog-based UX.** Create, edit, and delete operations all use Catalyst Dialog modals instead of navigating to separate pages.
- **Server component data fetching.** The page fetches data on the server and passes it down. The client component only manages UI state (which dialog is open, which todo is selected).
- **Todos are sorted newest-first** by `createdAt` descending.

## Claude Agent SDK Demo Branches

This repo doubles as the demo project for Stormwind Studios' Claude Agent SDK video series (Section 17 + 18.1). Each video has a dedicated branch containing SDK example code in `agent-sdk/python/` and/or `agent-sdk/typescript/`. The todo-app source code on `main` is the real codebase that the SDK agents analyze.

### Branch List

| Branch | Video | What It Demonstrates |
|--------|-------|---------------------|
| `17.1-agent-sdk-overview` | SDK Overview | Minimal `query()` call, Python + TypeScript side-by-side |
| `17.2-python-sdk-setup` | Python Setup | First agent with error handling |
| `17.3-typescript-sdk-setup` | TypeScript Setup | First agent with error handling (TS) |
| `17.4-streaming-input-and-output` | Streaming | Real-time output iteration + large file input assembly |
| `17.5-handling-permissions` | Permissions | Permission callbacks, human approval, role-based access |
| `17.6-session-management` | Sessions | Session resumption, forking, multi-session workflows |
| `17.7-custom-tools-in-the-sdk` | Custom Tools | FastMCP tool server + agent integration |
| `17.8-mcp-in-the-sdk` | MCP Integration | Multiple MCP servers (Postgres, GitHub) |
| `17.9-subagents-in-the-sdk` | Subagents | AgentDefinition for parallel code review |
| `17.10-hosting-and-deployment` | Deployment | Production patterns, health checks, graceful shutdown |
| `18.1-best-practices-for-effective-use` | Best Practices | Plan-review-execute + read-only-then-write patterns |

### SDK Code Conventions

All agent scripts across all branches follow these patterns:

**`cwd` goes inside the options object, not on `query()`:**

```python
# Python — CORRECT
options = ClaudeAgentOptions(
    cwd="/tmp/work",            # MUST be inside options
    model="claude-sonnet-4-5",
    permission_mode="bypassPermissions",
    max_turns=5,
)
async for message in query(prompt="...", options=options):
    ...
```

```typescript
// TypeScript — CORRECT
const options: Options = {
    cwd: "/tmp/work",           // MUST be inside options
    permissionMode: "bypassPermissions",
    model: "claude-sonnet-4-5",
    maxTurns: 5,
};
const response = query({ prompt: "...", options });
```

**Result message fields use snake_case in both languages:**
- `message.total_cost_usd` (not `cost_usd` or `costUsd`)
- `message.duration_ms` (not `durationMs`)
- `message.session_id` (not `sessionId`)

**TypeScript assistant message content is nested:**
- `message.message.content` (not `message.content`) — `SDKAssistantMessage` wraps `APIAssistantMessage`

## E2E Test Infrastructure

The `e2e/` directory contains a Docker-based testing environment for verifying SDK demo code before recording.

### Directory Layout

```
e2e/
  .devcontainer/
    devcontainer.json       # VS Code Dev Container config
  .env                      # ANTHROPIC_API_KEY (gitignored — create manually)
  Dockerfile                # Ubuntu 24.04 + Node 22 + uv + Claude Code CLI
  docker-compose.yml        # Automated test runner (mounts repo read-only at /repo)
  docker-compose.interactive.yml  # Overrides for interactive dev container use
  run-tests.sh              # Automated E2E test runner (T1/T2/T3 tiers)
  setup-workspace.sh        # Interactive workspace setup (clones branch into /tmp/work)
  format-log.py             # Formats Claude Code JSON logs for debugging
  logs/                     # Claude Code session logs (gitignored)
```

### Test Tiers

| Tier | What It Tests | Needs API Key? | Run Time |
|------|--------------|----------------|----------|
| **T1: Parse** | Python `ast.parse()`, TypeScript `tsc --noEmit` | No | ~5s |
| **T2: Import** | `uv run python -c "from claude_agent_sdk import ..."`, `node -e "require(...)"` | No | ~15s |
| **T3: Execute** | Actually run the agent scripts against the real Claude API | Yes | ~60s |

### Running Automated Tests

```bash
# From the host machine (Mac or Windows with Docker):
cd todo-app/e2e
export ANTHROPIC_API_KEY=sk-ant-...

# Run T2 (import check) on branch 17.1:
BRANCH=17.1-agent-sdk-overview TIER=T2 docker compose up --build

# Run T3 (full execution) on branch 17.4:
BRANCH=17.4-streaming-input-and-output TIER=T3 docker compose up --build
```

### Interactive Dev Container (for recording demos)

1. Open `todo-app/e2e` in VS Code
2. VS Code prompts "Reopen in Container" — accept
3. In the container terminal:

```bash
# Clone a specific branch into /tmp/work:
BRANCH=17.3-typescript-sdk-setup bash /setup-workspace.sh

# Set your API key:
export ANTHROPIC_API_KEY=sk-ant-...

# Follow the printed instructions to install deps and run scripts
```

The setup script:
- Wipes and re-clones `/tmp/work` on every run (safe to re-run for branch switching)
- Auto-opens `/tmp/work` in VS Code
- Dynamically discovers Python/TypeScript files and prints correct run commands
- Detects extra dependencies from `requirements.txt`

### Environment

The Docker image (Ubuntu 24.04) includes:
- Node.js 22 LTS
- Python 3 + uv
- Claude Code CLI (`@anthropic-ai/claude-code`)
- git, build-essential

The entire todo-app repo is mounted read-only at `/repo`. The setup script clones from `/repo` into `/tmp/work` so you get a writable copy of whichever branch you need.

### API Key Storage

Create `e2e/.env` with your key:
```
ANTHROPIC_API_KEY=sk-ant-...
```

This file is **not** gitignored by default — add `e2e/.env` to `.gitignore` if you commit from this repo. The docker-compose.yml reads `ANTHROPIC_API_KEY` from the environment, and the `.env` file is auto-loaded by Docker Compose.
