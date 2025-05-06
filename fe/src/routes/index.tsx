import { createFileRoute, Link } from '@tanstack/react-router'

export const Route = createFileRoute('/')({
  component: Index,
})

function Index() {
  return (
    <div className="p-2">
    <Link to="/signup" className="[&.active]:font-bold">
      Sign Up
    </Link>
    <br />
    <Link to="/signin" className="[&.active]:font-bold">
      Sign In
    </Link>
    </div>
  )
}