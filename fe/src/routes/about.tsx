import { createFileRoute } from '@tanstack/react-router'
import { UserBadge } from '../components/UserBadge/UserBadge'

export const Route = createFileRoute('/about')({
  component: About,
})

function About() {
  return (<div className="p-2">Hello from About!
            <UserBadge />
          </div>)
}