import { createFileRoute } from '@tanstack/react-router'
import { UserSignUp } from '../components/SignUp/SignUp'

export const Route = createFileRoute('/signup')({
  component: UserSignUp,
})

