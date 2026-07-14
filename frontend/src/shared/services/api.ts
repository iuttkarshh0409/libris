import type {
  BookSummary,
  ConfigurationResponse,
  QueryRequest,
  StandardApiResponse,
  StatusResponse,
  VerifiedResponse,
} from './types'

// Helper to handle response and extract data or throw error
async function handleResponse<T>(response: Response): Promise<T> {
  const contentType = response.headers.get('content-type')
  let payload: StandardApiResponse<T> | null = null

  if (contentType && contentType.includes('application/json')) {
    try {
      payload = await response.json()
    } catch {
      // JSON parsing failed
    }
  }

  if (!response.ok) {
    const errorMsg = payload?.errors?.[0] || `HTTP error! status: ${response.status}`
    throw new Error(errorMsg)
  }

  if (payload && payload.success && payload.data !== null) {
    return payload.data
  }

  throw new Error('API returned success: false or empty payload data.')
}

export const BookService = {
  async listBooks(): Promise<BookSummary[]> {
    const res = await fetch('/api/v1/books')
    return handleResponse<BookSummary[]>(res)
  },

  async getBook(id: string): Promise<BookSummary> {
    const res = await fetch(`/api/v1/books/${encodeURIComponent(id)}`)
    return handleResponse<BookSummary>(res)
  },

  async uploadBook(file: File): Promise<BookSummary> {
    const formData = new FormData()
    formData.append('file', file)

    const res = await fetch('/api/v1/books', {
      method: 'POST',
      body: formData,
    })
    return handleResponse<BookSummary>(res)
  },

  async deleteBook(id: string): Promise<void> {
    const res = await fetch(`/api/v1/books/${encodeURIComponent(id)}`, {
      method: 'DELETE',
    })
    const payload = await res.json()
    if (!res.ok || !payload.success) {
      throw new Error(payload?.errors?.[0] || 'Failed to delete book.')
    }
  },
}

export const QueryService = {
  async submitQuery(request: QueryRequest): Promise<VerifiedResponse> {
    const res = await fetch('/api/v1/queries', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(request),
    })
    return handleResponse<VerifiedResponse>(res)
  },
}

export const ConfigService = {
  async getConfig(): Promise<ConfigurationResponse> {
    const res = await fetch('/api/v1/config')
    return handleResponse<ConfigurationResponse>(res)
  },
}

export const StatusService = {
  async getStatus(): Promise<StatusResponse> {
    const res = await fetch('/api/v1/status')
    return handleResponse<StatusResponse>(res)
  },

  async getHealth(): Promise<boolean> {
    try {
      const res = await fetch('/health')
      if (!res.ok) return false
      const data = await res.json()
      return data?.status === 'healthy'
    } catch {
      return false
    }
  },
}
