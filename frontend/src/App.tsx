import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

import RootLayout from './layouts/RootLayout'
import Dashboard from './features/dashboard/Dashboard'
import Library from './features/library/Library'
import BookDetails from './features/library/BookDetails'
import QueryWorkspace from './features/query/QueryWorkspace'
import Settings from './features/settings/Settings'
import SystemStatus from './features/status/SystemStatus'
import NotFound from './features/404/NotFound'

// Initialize React Query Client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 5000,
    },
  },
})

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<RootLayout />}>
            <Route index element={<Navigate to="/dashboard" replace />} />
            <Route path="dashboard" element={<Dashboard />} />
            <Route path="library" element={<Library />} />
            <Route path="library/:bookId" element={<BookDetails />} />
            <Route path="queries" element={<QueryWorkspace />} />
            <Route path="settings" element={<Settings />} />
            <Route path="status" element={<SystemStatus />} />
            <Route path="*" element={<NotFound />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </QueryClientProvider>
  )
}
