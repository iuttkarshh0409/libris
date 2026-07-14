import { render, screen, waitFor } from '@testing-library/react'
import App from './App'
import { expect, test, vi, beforeEach } from 'vitest'

beforeEach(() => {
  vi.restoreAllMocks()

  // Mock window.matchMedia
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation((query) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  })
})

test('renders RootLayout and Dashboard with mocked service responses', async () => {
  // Mock fetch responses
  const mockBooks = [
    {
      id: '1',
      title: 'Calculus Textbook',
      author: 'Stewart',
      pages: 1000,
      index_status: 'completed',
      file_name: 'calc.pdf',
      upload_timestamp: new Date().toISOString(),
    },
  ]

  const mockStatus = {
    application_version: '1.0.0',
    architecture_version: '1.0.0',
    provider_status: { index_provider: 'healthy (version: 1.0)' },
    configured_models: { embedding_model: 'model-x', llm_model: 'gemini' },
    health_state: 'healthy',
  }

  const mockConfig = {
    chunk_size: 500,
    chunk_overlap: 50,
    similarity_threshold: 0.35,
    retrieval_limit: 4,
    embedding_model: 'all-MiniLM-L6-v2',
    llm_model: 'gemini-1.5-flash',
    embedding_device: 'cpu',
  }

  globalThis.fetch = vi.fn().mockImplementation((url: string) => {
    if (url.includes('/api/v1/books')) {
      return Promise.resolve({
        ok: true,
        headers: { get: () => 'application/json' },
        json: async () => ({ success: true, data: mockBooks, errors: [] }),
      })
    }
    if (url.includes('/api/v1/status')) {
      return Promise.resolve({
        ok: true,
        headers: { get: () => 'application/json' },
        json: async () => ({ success: true, data: mockStatus, errors: [] }),
      })
    }
    if (url.includes('/api/v1/config')) {
      return Promise.resolve({
        ok: true,
        headers: { get: () => 'application/json' },
        json: async () => ({ success: true, data: mockConfig, errors: [] }),
      })
    }
    if (url.includes('/health')) {
      return Promise.resolve({
        ok: true,
        json: async () => ({ status: 'healthy' }),
      })
    }
    return Promise.reject(new Error('Unknown url: ' + url))
  })

  render(<App />)

  // Wait for loading to finish and Dashboard title to render
  await waitFor(
    () => {
      expect(screen.getByText('Libris Dashboard')).toBeInTheDocument()
    },
    { timeout: 5000 }
  )

  // Verify dashboard metrics are rendered
  expect(screen.getByText('Textbook Library')).toBeInTheDocument()
  expect(screen.getByText('1')).toBeInTheDocument() // metric count for total books
})
