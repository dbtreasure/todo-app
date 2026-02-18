import { getTodos } from '@/lib/actions'
import { TodoList } from './todo-list'

export const dynamic = 'force-dynamic'

export default async function Home() {
  const todos = await getTodos()
  return <TodoList todos={todos} />
}
