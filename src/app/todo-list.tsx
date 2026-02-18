'use client'

import { useState } from 'react'
import { createTodo, updateTodo, deleteTodo } from '@/lib/actions'
import { Button } from '@/components/button'
import { Dialog, DialogTitle, DialogDescription, DialogBody, DialogActions } from '@/components/dialog'
import { Field, Label } from '@/components/fieldset'
import { Heading } from '@/components/heading'
import { Input } from '@/components/input'
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/table'
import { Textarea } from '@/components/textarea'

type Todo = {
  _id: string
  title: string
  desc: string
  createdAt: string
  updatedAt: string
}

function formatDate(iso: string) {
  return new Date(iso).toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: 'numeric',
    minute: '2-digit',
  })
}

export function TodoList({ todos }: { todos: Todo[] }) {
  const [createOpen, setCreateOpen] = useState(false)
  const [editOpen, setEditOpen] = useState(false)
  const [deleteOpen, setDeleteOpen] = useState(false)
  const [selectedTodo, setSelectedTodo] = useState<Todo | null>(null)

  function openEdit(todo: Todo) {
    setSelectedTodo(todo)
    setEditOpen(true)
  }

  function openDelete(todo: Todo) {
    setSelectedTodo(todo)
    setDeleteOpen(true)
  }

  return (
    <div className="mx-auto max-w-6xl px-4 py-10 sm:px-6 lg:px-8">
      <div className="flex items-end justify-between gap-4">
        <Heading>Todos</Heading>
        <Button color="indigo" onClick={() => setCreateOpen(true)}>
          Add Todo
        </Button>
      </div>

      <div className="mt-8">
        {todos.length === 0 ? (
          <p className="py-12 text-center text-sm text-zinc-500 dark:text-zinc-400">
            No todos yet. Click &ldquo;Add Todo&rdquo; to create one.
          </p>
        ) : (
          <Table>
            <TableHead>
              <TableRow>
                <TableHeader>Title</TableHeader>
                <TableHeader>Description</TableHeader>
                <TableHeader>Created</TableHeader>
                <TableHeader>Updated</TableHeader>
                <TableHeader className="text-right">Actions</TableHeader>
              </TableRow>
            </TableHead>
            <TableBody>
              {todos.map((todo) => (
                <TableRow key={todo._id}>
                  <TableCell className="font-medium">{todo.title}</TableCell>
                  <TableCell className="max-w-xs truncate text-zinc-500 dark:text-zinc-400">
                    {todo.desc || '—'}
                  </TableCell>
                  <TableCell className="text-zinc-500 dark:text-zinc-400">
                    {formatDate(todo.createdAt)}
                  </TableCell>
                  <TableCell className="text-zinc-500 dark:text-zinc-400">
                    {formatDate(todo.updatedAt)}
                  </TableCell>
                  <TableCell className="text-right">
                    <div className="flex justify-end gap-2">
                      <Button plain onClick={() => openEdit(todo)}>
                        Edit
                      </Button>
                      <Button plain onClick={() => openDelete(todo)}>
                        Delete
                      </Button>
                    </div>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>

      {/* Create Dialog */}
      <Dialog open={createOpen} onClose={setCreateOpen} size="md">
        <DialogTitle>New Todo</DialogTitle>
        <DialogDescription>Add a new todo item.</DialogDescription>
        <form
          action={async (formData) => {
            await createTodo(formData)
            setCreateOpen(false)
          }}
        >
          <DialogBody className="space-y-4">
            <Field>
              <Label>Title</Label>
              <Input name="title" required autoFocus />
            </Field>
            <Field>
              <Label>Description</Label>
              <Textarea name="desc" rows={3} />
            </Field>
          </DialogBody>
          <DialogActions>
            <Button plain onClick={() => setCreateOpen(false)} type="button">
              Cancel
            </Button>
            <Button color="indigo" type="submit">
              Create
            </Button>
          </DialogActions>
        </form>
      </Dialog>

      {/* Edit Dialog */}
      <Dialog open={editOpen} onClose={setEditOpen} size="md">
        <DialogTitle>Edit Todo</DialogTitle>
        <DialogDescription>Update this todo item.</DialogDescription>
        {selectedTodo && (
          <form
            action={async (formData) => {
              await updateTodo(selectedTodo._id, formData)
              setEditOpen(false)
              setSelectedTodo(null)
            }}
          >
            <DialogBody className="space-y-4">
              <Field>
                <Label>Title</Label>
                <Input name="title" required defaultValue={selectedTodo.title} autoFocus />
              </Field>
              <Field>
                <Label>Description</Label>
                <Textarea name="desc" rows={3} defaultValue={selectedTodo.desc} />
              </Field>
            </DialogBody>
            <DialogActions>
              <Button plain onClick={() => setEditOpen(false)} type="button">
                Cancel
              </Button>
              <Button color="indigo" type="submit">
                Save
              </Button>
            </DialogActions>
          </form>
        )}
      </Dialog>

      {/* Delete Confirmation Dialog */}
      <Dialog open={deleteOpen} onClose={setDeleteOpen} size="sm">
        <DialogTitle>Delete Todo</DialogTitle>
        <DialogDescription>
          Are you sure you want to delete &ldquo;{selectedTodo?.title}&rdquo;? This action cannot be undone.
        </DialogDescription>
        <DialogActions>
          <Button plain onClick={() => setDeleteOpen(false)}>
            Cancel
          </Button>
          <Button
            color="red"
            onClick={async () => {
              if (selectedTodo) {
                await deleteTodo(selectedTodo._id)
              }
              setDeleteOpen(false)
              setSelectedTodo(null)
            }}
          >
            Delete
          </Button>
        </DialogActions>
      </Dialog>
    </div>
  )
}
