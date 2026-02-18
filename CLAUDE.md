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


---

## Demo Environment: Headless Mode

This branch is configured for **Video 14.3: Headless Mode** in the Claude Code Enterprise Development course.

### Topic
Non-interactive Claude Code usage — dangerously-skip-permissions, tool whitelisting, JSON output, budget caps, and piping.

### Files Added
- `scripts/headless-examples.sh` — Documented headless usage examples
- `scripts/ci-automation.sh` — Complete CI/CD headless integration script

### Usage
Review the scripts for documented examples. Run individual examples with `bash scripts/headless-examples.sh`.
