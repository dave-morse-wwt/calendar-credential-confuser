import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { createRootRoute, Link, Outlet } from '@tanstack/react-router'
import { TanStackRouterDevtools } from '@tanstack/react-router-devtools'
import { AccessTokenProvider } from '../components/AccessTokenProvider/AccessTokenProvider';
import { UserBadge } from '../components/UserBadge/UserBadge';

const queryClient = new QueryClient()

const RootRoute = () => {
  return (<QueryClientProvider client={queryClient}>
            <AccessTokenProvider>
              <div className="p-2 flex gap-2">
                <Link to="/" className="[&.active]:font-bold">
                  Home
                </Link>{' '}
                <Link to="/about" className="[&.active]:font-bold">
                  About
                </Link>
                {' '}
                <UserBadge />
              </div>
              <hr />
              <Outlet />
              <TanStackRouterDevtools /> {/* TODO: Remove this in production */}
            </AccessTokenProvider >
          </QueryClientProvider>
  )}

export const Route = createRootRoute({component: RootRoute})