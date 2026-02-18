'use server'

import { revalidatePath } from 'next/cache'
import connectDB from './mongodb'
import Todo from './models/todo'

export async function getTodos() {
  await connectDB()
  const todos = await Todo.find({}).sort({ createdAt: -1 }).lean()
  return todos.map((todo) => ({
    _id: String(todo._id),
    title: todo.title as string,
    desc: (todo.desc as string) || '',
    createdAt: (todo.createdAt as Date).toISOString(),
    updatedAt: (todo.updatedAt as Date).toISOString(),
  }))
}

export async function createTodo(formData: FormData) {
  await connectDB()
  const title = formData.get('title') as string
  const desc = formData.get('desc') as string

  if (!title || !title.trim()) {
    throw new Error('Title is required')
  }

  await Todo.create({ title: title.trim(), desc: desc?.trim() || '' })
  revalidatePath('/')
}

export async function updateTodo(id: string, formData: FormData) {
  await connectDB()
  const title = formData.get('title') as string
  const desc = formData.get('desc') as string

  if (!title || !title.trim()) {
    throw new Error('Title is required')
  }

  await Todo.findByIdAndUpdate(id, { title: title.trim(), desc: desc?.trim() || '' })
  revalidatePath('/')
}

export async function deleteTodo(id: string) {
  await connectDB()
  await Todo.findByIdAndDelete(id)
  revalidatePath('/')
}
