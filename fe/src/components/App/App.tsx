import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import './App.css'
import { CredentialLoader } from '../CredentialLoader/CredentialLoader'
import { UserSignUp } from '../UserSignUp/UserSignUp'

const queryClient = new QueryClient()

export function App() {
  return (
    
    <QueryClientProvider client={queryClient}>
      <h1>Hello World</h1>
      <UserSignUp />
      <CredentialLoader >
        CredentialLoader body is here
      </CredentialLoader>
    </QueryClientProvider>
  )
}

