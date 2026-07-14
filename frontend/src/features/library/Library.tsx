import { useState, useEffect, type ChangeEvent, type FormEvent } from 'react'
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import {
  BookOpen,
  Search,
  Trash2,
  Upload,
  Loader2,
  CheckCircle2,
  AlertCircle,
  Calendar,
  Layers,
  ArrowUpDown,
  BookMarked,
} from 'lucide-react'
import { BookService } from '../../shared/services/api'
import PageHeader from '../../components/PageHeader'
import EmptyState from '../../components/EmptyState'
import ErrorPanel from '../../components/ErrorPanel'
import ProviderStatusBadge from '../../components/ProviderStatusBadge'
import { toast } from 'sonner'

export default function Library() {
  const queryClient = useQueryClient()
  const [searchTerm, setSearchTerm] = useState('')
  const [sortBy, setSortBy] = useState<'title' | 'author' | 'pages' | 'date'>('date')
  const [filterStatus, setFilterStatus] = useState<string>('all')
  const [fileToUpload, setFileToUpload] = useState<File | null>(null)

  // Custom pipeline simulator state
  const [uploadPipelineStep, setUploadPipelineStep] = useState<number>(0)
  const [isUploading, setIsUploading] = useState(false)

  // Queries
  const {
    data: books,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['books'],
    queryFn: BookService.listBooks,
  })

  // Ingestion Mutation
  const uploadMutation = useMutation({
    mutationFn: BookService.uploadBook,
    onSuccess: (data) => {
      // Complete the pipeline simulation
      setUploadPipelineStep(6)
      setTimeout(() => {
        setIsUploading(false)
        setFileToUpload(null)
        setUploadPipelineStep(0)
        queryClient.invalidateQueries({ queryKey: ['books'] })
        toast.success(`Book "${data.title}" successfully ingested and indexed!`)
      }, 1500)
    },
    onError: (err: any) => {
      setIsUploading(false)
      setUploadPipelineStep(0)
      toast.error(err?.message || 'Failed to ingest book.')
    },
  })

  // Deletion Mutation
  const deleteMutation = useMutation({
    mutationFn: BookService.deleteBook,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['books'] })
      toast.success('Book deleted successfully from library and index.')
    },
    onError: (err: any) => {
      toast.error(err?.message || 'Failed to delete book.')
    },
  })

  // Pipeline simulation timer logic
  useEffect(() => {
    if (!isUploading) return

    // Simulate steps over time while API executes
    const timer1 = setTimeout(() => setUploadPipelineStep(1), 1500) // Creating Pages
    const timer2 = setTimeout(() => setUploadPipelineStep(2), 3000) // Chunk Generation
    const timer3 = setTimeout(() => setUploadPipelineStep(3), 5000) // Embedding Generation
    const timer4 = setTimeout(() => setUploadPipelineStep(4), 7500) // Knowledge Index
    const timer5 = setTimeout(() => setUploadPipelineStep(5), 10000) // Ready

    return () => {
      clearTimeout(timer1)
      clearTimeout(timer2)
      clearTimeout(timer3)
      clearTimeout(timer4)
      clearTimeout(timer5)
    }
  }, [isUploading])

  const handleFileChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      const file = e.target.files[0]
      if (file.type !== 'application/pdf') {
        toast.error('Only PDF files are supported.')
        return
      }
      setFileToUpload(file)
    }
  }

  const handleUploadSubmit = (e: FormEvent) => {
    e.preventDefault()
    if (!fileToUpload) return

    setIsUploading(true)
    setUploadPipelineStep(0)
    uploadMutation.mutate(fileToUpload)
  }

  const handleDelete = (id: string, title: string) => {
    if (
      window.confirm(
        `Are you sure you want to delete "${title}"? This will permanently wipe all its embeddings from the vector store.`
      )
    ) {
      deleteMutation.mutate(id)
    }
  }

  // Filter & Sort logic
  const filteredBooks = (books || [])
    .filter((book) => {
      const matchesSearch =
        book.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        book.author.toLowerCase().includes(searchTerm.toLowerCase()) ||
        book.subject.toLowerCase().includes(searchTerm.toLowerCase())

      const matchesFilter = filterStatus === 'all' || book.index_status === filterStatus

      return matchesSearch && matchesFilter
    })
    .sort((a, b) => {
      if (sortBy === 'title') return a.title.localeCompare(b.title)
      if (sortBy === 'author') return a.author.localeCompare(b.author)
      if (sortBy === 'pages') return b.pages - a.pages
      if (sortBy === 'date')
        return new Date(b.upload_timestamp).getTime() - new Date(a.upload_timestamp).getTime()
      return 0
    })

  const pipelineSteps = [
    { label: 'Parsing Document', desc: 'Extracting raw PDF text layout streams' },
    { label: 'Creating Pages', desc: 'Validating and mapping text boundaries to page offsets' },
    { label: 'Chunk Generation', desc: 'Tokenizing content into semantic context segments' },
    { label: 'Embedding Generation', desc: 'Computing dense floating-point vector dimensions' },
    { label: 'Knowledge Index', desc: 'Writing vectors to active ChromaDB search collection' },
    { label: 'Ready', desc: 'The textbook is fully indexed and ready for semantic queries' },
  ]

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      <PageHeader
        title="Document Library"
        description="Upload textbooks and index them. All content is processed locally and mapped into semantic search space."
      />

      {/* Upload Box Component */}
      <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800/80 rounded-2xl p-6 shadow-sm">
        <h3 className="text-base font-bold text-slate-900 dark:text-zinc-50 flex items-center gap-2 mb-4">
          <Upload className="h-4.5 w-4.5 text-purple-600 dark:text-purple-400" />
          Ingest New Textbook (PDF)
        </h3>

        {!isUploading ? (
          <form
            onSubmit={handleUploadSubmit}
            className="flex flex-col sm:flex-row gap-4 items-stretch sm:items-center"
          >
            <div className="flex-1 relative border-2 border-dashed border-slate-200 dark:border-zinc-800 rounded-xl hover:bg-slate-50 dark:hover:bg-zinc-900/50 transition-colors p-4 flex items-center justify-center">
              <input
                type="file"
                accept="application/pdf"
                onChange={handleFileChange}
                className="absolute inset-0 opacity-0 cursor-pointer"
                disabled={isUploading}
              />
              <div className="flex items-center gap-2 text-sm text-slate-500 dark:text-zinc-400">
                <BookMarked className="h-4 w-4 text-slate-400" />
                <span>{fileToUpload ? fileToUpload.name : 'Select or drop textbook PDF'}</span>
              </div>
            </div>
            <button
              type="submit"
              disabled={!fileToUpload || isUploading}
              className={`
                px-5 py-3 rounded-xl text-sm font-semibold transition-all cursor-pointer flex items-center justify-center gap-2 shadow-md
                ${
                  fileToUpload && !isUploading
                    ? 'bg-purple-600 hover:bg-purple-700 text-white shadow-purple-500/20 active:scale-95'
                    : 'bg-slate-100 dark:bg-zinc-800 text-slate-400 dark:text-zinc-500 shadow-none cursor-not-allowed'
                }
              `}
            >
              Start Ingestion Pipeline
            </button>
          </form>
        ) : (
          /* Active RAG Pipeline Visualizer */
          <div className="space-y-6 py-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-bold text-slate-700 dark:text-zinc-300">
                Ingestion Pipeline Active:{' '}
                <span className="text-purple-600 dark:text-purple-400">{fileToUpload?.name}</span>
              </span>
              <Loader2 className="h-4 w-4 animate-spin text-purple-600 dark:text-purple-400" />
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 relative">
              {pipelineSteps.map((step, idx) => {
                const isFinished = uploadPipelineStep > idx
                const isActive = uploadPipelineStep === idx

                return (
                  <div
                    key={step.label}
                    className={`
                      p-4 rounded-xl border transition-all duration-300 flex flex-col justify-between gap-1
                      ${
                        isFinished
                          ? 'bg-emerald-50/50 dark:bg-emerald-950/10 border-emerald-200 dark:border-emerald-900/40 text-emerald-800 dark:text-emerald-400'
                          : isActive
                            ? 'bg-purple-50/70 dark:bg-purple-950/10 border-purple-300 dark:border-purple-900/60 shadow-xs'
                            : 'bg-slate-50/40 dark:bg-zinc-900/40 border-slate-200 dark:border-zinc-800 text-slate-400 dark:text-zinc-500'
                      }
                    `}
                  >
                    <div className="flex items-center justify-between">
                      <span className="text-xs font-bold uppercase tracking-wider">
                        {idx + 1}. {step.label}
                      </span>
                      {isFinished ? (
                        <CheckCircle2 className="h-4 w-4 text-emerald-500 shrink-0" />
                      ) : isActive ? (
                        <Loader2 className="h-4 w-4 animate-spin text-purple-500 shrink-0" />
                      ) : (
                        <AlertCircle className="h-4 w-4 text-slate-300 dark:text-zinc-700 shrink-0" />
                      )}
                    </div>
                    <p
                      className={`text-[10px] mt-1.5 leading-relaxed ${isActive ? 'text-purple-700/80 dark:text-purple-400' : isFinished ? 'text-emerald-700/70 dark:text-emerald-500/80' : 'text-slate-400'}`}
                    >
                      {step.desc}
                    </p>
                  </div>
                )
              })}
            </div>
          </div>
        )}
      </div>

      {/* Search and Filters */}
      <div className="flex flex-col md:flex-row gap-4 justify-between items-stretch md:items-center">
        <div className="relative flex-1 max-w-md">
          <Search className="absolute left-3.5 top-1/2 -translate-y-1/2 h-4 w-4 text-slate-400 dark:text-zinc-500" />
          <input
            type="text"
            placeholder="Search books by title, author, or subject..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full pl-10 pr-4 py-2.5 bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl text-sm outline-none focus:border-purple-500 focus:ring-1 focus:ring-purple-500 transition-all"
          />
        </div>

        <div className="flex flex-wrap items-center gap-3">
          {/* Filter status */}
          <select
            value={filterStatus}
            onChange={(e) => setFilterStatus(e.target.value)}
            className="px-3.5 py-2.5 bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl text-xs font-semibold outline-none cursor-pointer hover:border-slate-300 dark:hover:border-zinc-700 transition-colors"
          >
            <option value="all">All Index Statuses</option>
            <option value="completed">Completed Only</option>
            <option value="processing">Processing Only</option>
            <option value="failed">Failed Only</option>
          </select>

          {/* Sort selection */}
          <div className="flex items-center gap-1.5 bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800 rounded-xl px-1.5 py-1">
            <span className="p-1.5 text-slate-400 dark:text-zinc-500">
              <ArrowUpDown className="h-3.5 w-3.5" />
            </span>
            {(
              [
                { key: 'date', label: 'Date' },
                { key: 'title', label: 'Title' },
                { key: 'author', label: 'Author' },
                { key: 'pages', label: 'Pages' },
              ] as const
            ).map((opt) => (
              <button
                key={opt.key}
                onClick={() => setSortBy(opt.key)}
                className={`
                  px-2.5 py-1.5 rounded-lg text-xs font-semibold cursor-pointer transition-colors
                  ${
                    sortBy === opt.key
                      ? 'bg-slate-100 dark:bg-zinc-800 text-slate-900 dark:text-zinc-100'
                      : 'text-slate-500 hover:text-slate-950 dark:text-zinc-400 dark:hover:text-white'
                  }
                `}
              >
                {opt.label}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Library Grid */}
      {isLoading ? (
        <div className="py-20 flex justify-center">
          <Loader2 className="h-10 w-10 animate-spin text-purple-600 dark:text-purple-400" />
        </div>
      ) : error ? (
        <ErrorPanel
          message={(error as Error)?.message || 'Failed to list library books.'}
          onRetry={refetch}
        />
      ) : filteredBooks.length === 0 ? (
        <EmptyState
          title={searchTerm ? 'No Match Found' : 'No Books Indexed'}
          description={
            searchTerm
              ? `No books match the search term "${searchTerm}". Try refining your search query or filters.`
              : 'Your Document Library is Empty. Upload your first textbook above to segment, embed, and index academic materials locally.'
          }
          icon={BookOpen}
        />
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredBooks.map((book) => (
            <div
              key={book.id}
              className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800/80 rounded-2xl p-6 shadow-xs hover:shadow-md transition-all flex flex-col justify-between group"
            >
              <div>
                <div className="flex items-start justify-between gap-4 mb-3">
                  <div className="p-2.5 bg-purple-50 dark:bg-purple-950/20 text-purple-600 dark:text-purple-400 rounded-xl border border-purple-100 dark:border-purple-900/20">
                    <BookOpen className="h-5 w-5" />
                  </div>
                  <ProviderStatusBadge status={book.index_status} />
                </div>

                <h4 className="text-base font-bold text-slate-900 dark:text-zinc-100 line-clamp-1 group-hover:text-purple-600 dark:group-hover:text-purple-400 transition-colors">
                  {book.title}
                </h4>
                <p className="text-xs text-slate-500 dark:text-zinc-400 mt-1">
                  by {book.author || 'Unknown Author'}
                </p>

                <div className="grid grid-cols-2 gap-3 mt-5 pt-4 border-t border-slate-100 dark:border-zinc-850 text-xs text-slate-600 dark:text-zinc-400">
                  <div className="flex items-center gap-1.5">
                    <Layers className="h-3.5 w-3.5 text-slate-400" />
                    <span>{book.pages} Pages</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Calendar className="h-3.5 w-3.5 text-slate-400" />
                    <span>{new Date(book.upload_timestamp).toLocaleDateString()}</span>
                  </div>
                  {book.subject && (
                    <div className="col-span-2 text-[10px] uppercase font-semibold tracking-wider text-slate-400 dark:text-zinc-500 mt-1">
                      Subject: {book.subject}
                    </div>
                  )}
                </div>
              </div>

              <div className="flex items-center gap-2 mt-6 pt-4 border-t border-slate-100 dark:border-zinc-850">
                <button
                  onClick={() => (window.location.href = `/library/${book.id}`)}
                  className="flex-1 px-3 py-2 bg-slate-50 hover:bg-slate-100 dark:bg-zinc-850 dark:hover:bg-zinc-850/70 border border-slate-200 dark:border-zinc-700/60 text-slate-700 dark:text-zinc-200 rounded-xl text-xs font-semibold transition-all text-center cursor-pointer"
                >
                  View Details
                </button>
                <button
                  onClick={() => handleDelete(book.id, book.title)}
                  className="p-2 border border-slate-200 dark:border-zinc-700/60 hover:bg-rose-50 hover:text-rose-600 dark:hover:bg-rose-950/20 text-slate-500 dark:text-zinc-400 rounded-xl transition-colors cursor-pointer"
                  aria-label="Delete Book"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
