export interface ResponseMetadata {
  timestamp: string
  request_id: string
  correlation_id: string
  api_version: string
  architecture_version: string
}

export interface StandardApiResponse<T> {
  success: boolean
  data: T | null
  errors: string[]
  metadata: ResponseMetadata
}

export interface BookSummary {
  id: string
  title: string
  author: string
  subject: string
  edition: string
  pages: number
  index_status: 'queued' | 'processing' | 'completed' | 'failed'
  file_name: string
  upload_timestamp: string
}

export interface StatusResponse {
  application_version: string
  architecture_version: string
  provider_status: Record<string, string>
  configured_models: Record<string, string>
  health_state: 'healthy' | 'unhealthy'
}

export interface ConfigurationResponse {
  chunk_size: number
  chunk_overlap: number
  similarity_threshold: number
  retrieval_limit: number
  embedding_model: string
}

export interface Citation {
  citation_id: string
  book_title: string
  page_number: number
  chapter: string | null
  section: string | null
  embedding_id: string | null
  retrieval_rank: number | null
  similarity_score: number | null
}

export interface VerifiedResponseItem {
  response_id: string
  query_id: string
  answer_text: string
  supporting_citations: Citation[]
  supporting_excerpts: string[]
  verification_timestamp: string
}

export interface VerifiedResponse {
  book_id: string
  items: VerifiedResponseItem[]
  statistics: Record<string, any>
  metadata: Record<string, any>
}

export interface QueryRequest {
  query_text: string
  similarity_threshold?: number
  limit?: number
  book_id?: string
}
