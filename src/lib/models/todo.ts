import mongoose from 'mongoose'

const todoSchema = new mongoose.Schema(
  {
    title: { type: String, required: true },
    desc: String,
  },
  { timestamps: true }
)

const Todo = mongoose.models.todo || mongoose.model('todo', todoSchema)

export default Todo
