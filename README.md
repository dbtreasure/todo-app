# Todo App

A full-stack CRUD todo application built with Next.js 15, React 19, Tailwind CSS 4, and MongoDB. Uses the [Catalyst UI Kit](https://catalyst.tailwindui.com/) from the Tailwind CSS team for all interface components.

## Tech Stack

- **Next.js 15** (App Router, Server Actions)
- **React 19**
- **TypeScript**
- **Tailwind CSS 4** with `@tailwindcss/postcss`
- **Catalyst UI** (Headless UI + Tailwind component library)
- **MongoDB** with Mongoose 8

## Prerequisites

- Node.js 18+
- MongoDB running locally on port 27017

## Setup

```bash
git clone <repo-url>
cd todo-app
npm install
```

Create a `.env` file (or use the existing one):

```
MONGODB_URI=mongodb://localhost:27017/todoDb
```

## Usage

```bash
npm run dev       # Development server on http://localhost:3000
npm run build     # Production build
npm run start     # Serve production build
npm run lint      # Run ESLint
```

## Features

- Create, read, update, and delete todos
- Modal dialogs for all operations (no page navigation)
- Delete confirmation dialog
- Responsive table layout with Catalyst Table components
- Dark mode support
- Server-side data fetching with client-side interactivity
- Sorted newest-first

## Project Structure

```
src/
  app/
    layout.tsx        # Root layout with Tailwind CSS and Inter font
    page.tsx          # Server component - fetches todos from MongoDB
    todo-list.tsx     # Client component - table, dialogs, CRUD interactions
  components/         # Catalyst UI components (Button, Table, Dialog, Input, etc.)
  lib/
    actions.ts        # Server Actions for all CRUD operations
    mongodb.ts        # MongoDB connection singleton
    models/
      todo.ts         # Mongoose Todo schema
  styles/
    tailwind.css      # Tailwind CSS entry point
```

## License

MIT
