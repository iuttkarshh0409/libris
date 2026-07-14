import { describe, it, expect, vi, beforeEach } from 'vitest'
import { BookService, QueryService, ConfigService, StatusService } from './api'

describe('Frontend Services Layer', () => {
  beforeEach(() => {
    vi.restoreAllMocks()
  })

  describe('BookService', () => {
    it('listBooks returns book summaries on success', async () => {
      const mockBooks = [
        { id: '1', title: 'Calculus', author: 'Stewart', pages: 1000, index_status: 'completed' },
      ]

      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        headers: { get: () => 'application/json' },
        json: async () => ({ success: true, data: mockBooks, errors: [] }),
      })
      vi.stubGlobal('fetch', mockFetch)

      const result = await BookService.listBooks()
      expect(mockFetch).toHaveBeenCalledWith('/api/v1/books')
      expect(result).toEqual(mockBooks)
    })

    it('uploadBook submits FormData and returns new book', async () => {
      const mockBook = {
        id: '2',
        title: 'Physics',
        author: 'Halliday',
        pages: 800,
        index_status: 'completed',
      }
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        headers: { get: () => 'application/json' },
        json: async () => ({ success: true, data: mockBook, errors: [] }),
      })
      vi.stubGlobal('fetch', mockFetch)

      const dummyFile = new File(['dummy'], 'physics.pdf', { type: 'application/pdf' })
      const result = await BookService.uploadBook(dummyFile)

      expect(mockFetch).toHaveBeenCalledWith('/api/v1/books', expect.any(Object))
      expect(result).toEqual(mockBook)
    })

    it('deleteBook sends DELETE request and returns void', async () => {
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ success: true, errors: [] }),
      })
      vi.stubGlobal('fetch', mockFetch)

      await expect(BookService.deleteBook('2')).resolves.not.toThrow()
      expect(mockFetch).toHaveBeenCalledWith('/api/v1/books/2', { method: 'DELETE' })
    })
  })

  describe('QueryService', () => {
    it('submitQuery sends POST query parameters and returns VerifiedResponse', async () => {
      const mockResponse = {
        book_id: 'all',
        items: [
          { answer_text: 'The answer is 42', supporting_citations: [], supporting_excerpts: [] },
        ],
        statistics: {},
        metadata: {},
      }

      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        headers: { get: () => 'application/json' },
        json: async () => ({ success: true, data: mockResponse, errors: [] }),
      })
      vi.stubGlobal('fetch', mockFetch)

      const result = await QueryService.submitQuery({ query_text: 'What is the answer?' })
      expect(mockFetch).toHaveBeenCalledWith(
        '/api/v1/queries',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify({ query_text: 'What is the answer?' }),
        })
      )
      expect(result).toEqual(mockResponse)
    })
  })

  describe('ConfigService', () => {
    it('getConfig returns active configuration', async () => {
      const mockConfig = {
        chunk_size: 500,
        chunk_overlap: 50,
        similarity_threshold: 0.35,
        retrieval_limit: 4,
        embedding_model: 'model-x',
      }
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        headers: { get: () => 'application/json' },
        json: async () => ({ success: true, data: mockConfig, errors: [] }),
      })
      vi.stubGlobal('fetch', mockFetch)

      const result = await ConfigService.getConfig()
      expect(mockFetch).toHaveBeenCalledWith('/api/v1/config')
      expect(result).toEqual(mockConfig)
    })
  })

  describe('StatusService', () => {
    it('getStatus returns healthy system state', async () => {
      const mockStatus = {
        application_version: '1.0.0',
        architecture_version: '1.0.0',
        provider_status: {},
        configured_models: {},
        health_state: 'healthy',
      }
      const mockFetch = vi.fn().mockResolvedValue({
        ok: true,
        headers: { get: () => 'application/json' },
        json: async () => ({ success: true, data: mockStatus, errors: [] }),
      })
      vi.stubGlobal('fetch', mockFetch)

      const result = await StatusService.getStatus()
      expect(mockFetch).toHaveBeenCalledWith('/api/v1/status')
      expect(result).toEqual(mockStatus)
    })
  })
})
