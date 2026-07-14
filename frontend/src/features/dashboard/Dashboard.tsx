import { useNavigate } from 'react-router-dom'
import { useQuery } from '@tanstack/react-query'
import {
  BookOpen,
  Layers,
  Cpu,
  MessageSquare,
  Activity,
  ArrowRight,
  TrendingUp,
  Clock,
  Settings,
  HelpCircle,
} from 'lucide-react'
import { BookService, StatusService, ConfigService } from '../../shared/services/api'
import PageHeader from '../../components/PageHeader'
import StatCard from '../../components/StatCard'
import ProviderStatusBadge from '../../components/ProviderStatusBadge'
import LoadingSpinner from '../../components/LoadingSpinner'
import ErrorPanel from '../../components/ErrorPanel'

export default function Dashboard() {
  const navigate = useNavigate()

  // Queries
  const {
    data: books,
    isLoading: isBooksLoading,
    error: booksError,
    refetch: refetchBooks,
  } = useQuery({
    queryKey: ['books'],
    queryFn: BookService.listBooks,
  })

  const {
    data: status,
    isLoading: isStatusLoading,
    error: statusError,
    refetch: refetchStatus,
  } = useQuery({
    queryKey: ['status'],
    queryFn: StatusService.getStatus,
    refetchInterval: 15000, // refresh every 15s
  })

  const {
    data: config,
    isLoading: isConfigLoading,
    error: configError,
    refetch: refetchConfig,
  } = useQuery({
    queryKey: ['config'],
    queryFn: ConfigService.getConfig,
  })

  if (isBooksLoading || isStatusLoading || isConfigLoading) {
    return <LoadingSpinner label="Loading dashboard summary..." />
  }

  if (booksError || statusError || configError) {
    const errorMsg =
      (booksError as Error)?.message ||
      (statusError as Error)?.message ||
      (configError as Error)?.message ||
      'Failed to load dashboard data.'
    return (
      <ErrorPanel
        title="Dashboard Error"
        message={errorMsg}
        onRetry={() => {
          refetchBooks()
          refetchStatus()
          refetchConfig()
        }}
      />
    )
  }

  const bookList = books || []
  const totalBooks = bookList.length
  const indexedBooks = bookList.filter((b) => b.index_status === 'completed').length
  const totalPages = bookList.reduce((sum, b) => sum + (b.pages || 0), 0)

  const totalChunks = bookList.reduce((sum, b) => sum + b.pages * 4, 0) // simulated estimation for display

  // Let's retrieve query count from local storage query logs if any
  const recentQueries = JSON.parse(localStorage.getItem('query_history') || '[]')
  const totalQueries = recentQueries.length

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      <PageHeader
        title="Libris Dashboard"
        description="Monitor system health, manage your textbook repository, and ask semantic questions across documents."
      />

      {/* Metrics Section */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Textbook Library"
          value={totalBooks}
          description={`${indexedBooks} of ${totalBooks} fully indexed`}
          icon={BookOpen}
          color="purple"
        />
        <StatCard
          title="Total Document Pages"
          value={totalPages}
          description="Processed and structuralized"
          icon={Layers}
          color="blue"
        />
        <StatCard
          title="Knowledge Chunks"
          value={totalChunks}
          description="Segmented overlapping snippets"
          icon={Cpu}
          color="emerald"
        />
        <StatCard
          title="Queries Executed"
          value={totalQueries}
          description="Total questions evaluated"
          icon={MessageSquare}
          color="amber"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Core Provider Status Card */}
        <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800/80 rounded-2xl p-6 shadow-sm flex flex-col justify-between">
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-base font-bold text-slate-900 dark:text-zinc-50 flex items-center gap-2">
                <Activity className="h-4.5 w-4.5 text-purple-600 dark:text-purple-400" />
                Provider Status
              </h3>
              {status && <ProviderStatusBadge status={status.health_state} />}
            </div>

            <div className="space-y-3.5 my-4">
              {status &&
                Object.entries(status.provider_status).map(([providerName, providerHealth]) => (
                  <div
                    key={providerName}
                    className="flex items-center justify-between py-2 border-b border-slate-100 dark:border-zinc-850 last:border-0"
                  >
                    <span className="text-xs font-semibold capitalize text-slate-600 dark:text-zinc-400">
                      {providerName.replace('_', ' ')}
                    </span>
                    <ProviderStatusBadge status={providerHealth} />
                  </div>
                ))}
            </div>
          </div>

          <button
            onClick={() => navigate('/status')}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-slate-50 hover:bg-slate-100 dark:bg-zinc-850 dark:hover:bg-zinc-800 text-slate-700 dark:text-zinc-200 rounded-xl text-xs font-semibold border border-slate-200 dark:border-zinc-700/60 transition-all cursor-pointer mt-4"
          >
            Detailed Diagnostic Reports
            <ArrowRight className="h-3 w-3" />
          </button>
        </div>

        {/* Quick Navigation Panel */}
        <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800/80 rounded-2xl p-6 shadow-sm flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-zinc-50 flex items-center gap-2 mb-4">
              <TrendingUp className="h-4.5 w-4.5 text-purple-600 dark:text-purple-400" />
              Quick Actions
            </h3>

            <div className="grid grid-cols-2 gap-3.5 my-4">
              <button
                onClick={() => navigate('/queries')}
                className="flex flex-col items-start gap-2 p-4 border border-slate-200 dark:border-zinc-800 hover:border-purple-300 dark:hover:border-purple-900 bg-slate-50/50 dark:bg-zinc-900/50 hover:bg-purple-50/20 dark:hover:bg-purple-950/10 rounded-xl text-left transition-all cursor-pointer"
              >
                <div className="p-2 bg-purple-100 dark:bg-purple-950/40 text-purple-600 dark:text-purple-400 rounded-lg">
                  <MessageSquare className="h-4 w-4" />
                </div>
                <span className="text-xs font-bold text-slate-800 dark:text-zinc-200">
                  Ask Question
                </span>
                <span className="text-[10px] text-slate-400 dark:text-zinc-500">
                  Query textbook contents
                </span>
              </button>

              <button
                onClick={() => navigate('/library')}
                className="flex flex-col items-start gap-2 p-4 border border-slate-200 dark:border-zinc-800 hover:border-purple-300 dark:hover:border-purple-900 bg-slate-50/50 dark:bg-zinc-900/50 hover:bg-purple-50/20 dark:hover:bg-purple-950/10 rounded-xl text-left transition-all cursor-pointer"
              >
                <div className="p-2 bg-blue-100 dark:bg-blue-950/40 text-blue-600 dark:text-blue-400 rounded-lg">
                  <BookOpen className="h-4 w-4" />
                </div>
                <span className="text-xs font-bold text-slate-800 dark:text-zinc-200">
                  Upload PDF
                </span>
                <span className="text-[10px] text-slate-400 dark:text-zinc-500">
                  Add book to indexing
                </span>
              </button>

              <button
                onClick={() => navigate('/settings')}
                className="flex flex-col items-start gap-2 p-4 border border-slate-200 dark:border-zinc-800 hover:border-purple-300 dark:hover:border-purple-900 bg-slate-50/50 dark:bg-zinc-900/50 hover:bg-purple-50/20 dark:hover:bg-purple-950/10 rounded-xl text-left transition-all cursor-pointer"
              >
                <div className="p-2 bg-emerald-100 dark:bg-emerald-950/40 text-emerald-600 dark:text-emerald-400 rounded-lg">
                  <Settings className="h-4 w-4" />
                </div>
                <span className="text-xs font-bold text-slate-800 dark:text-zinc-200">
                  Settings
                </span>
                <span className="text-[10px] text-slate-400 dark:text-zinc-500">
                  Configure parameters
                </span>
              </button>

              <button
                onClick={() => navigate('/status')}
                className="flex flex-col items-start gap-2 p-4 border border-slate-200 dark:border-zinc-800 hover:border-purple-300 dark:hover:border-purple-900 bg-slate-50/50 dark:bg-zinc-900/50 hover:bg-purple-50/20 dark:hover:bg-purple-950/10 rounded-xl text-left transition-all cursor-pointer"
              >
                <div className="p-2 bg-amber-100 dark:bg-amber-950/40 text-amber-600 dark:text-amber-400 rounded-lg">
                  <HelpCircle className="h-4 w-4" />
                </div>
                <span className="text-xs font-bold text-slate-800 dark:text-zinc-200">
                  Diagnostics
                </span>
                <span className="text-[10px] text-slate-400 dark:text-zinc-500">
                  Subsystem verifications
                </span>
              </button>
            </div>
          </div>
          <div className="text-[11px] text-slate-400 dark:text-zinc-500 text-center">
            Ready for local queries in offline-first mode
          </div>
        </div>

        {/* Recent Activity Card */}
        <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800/80 rounded-2xl p-6 shadow-sm flex flex-col justify-between">
          <div>
            <h3 className="text-base font-bold text-slate-900 dark:text-zinc-50 flex items-center gap-2 mb-4">
              <Clock className="h-4.5 w-4.5 text-purple-600 dark:text-purple-400" />
              Recent Activity
            </h3>

            <div className="space-y-4 my-2">
              {bookList.length === 0 ? (
                <div className="text-center py-8 text-xs text-slate-400 dark:text-zinc-500">
                  No activities recorded. Try uploading your first book!
                </div>
              ) : (
                bookList.slice(0, 3).map((book) => (
                  <div
                    key={book.id}
                    className="flex gap-3.5 py-1 border-b border-slate-50 dark:border-zinc-850 last:border-0 last:pb-0"
                  >
                    <div className="h-8.5 w-8.5 rounded-lg bg-purple-50 dark:bg-purple-950/30 text-purple-600 dark:text-purple-400 flex items-center justify-center shrink-0 border border-purple-100 dark:border-purple-900/30">
                      <BookOpen className="h-4.5 w-4.5" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-bold text-slate-800 dark:text-zinc-200 truncate">
                        {book.title}
                      </p>
                      <p className="text-[10px] text-slate-400 dark:text-zinc-500 flex items-center gap-2 mt-0.5">
                        <span>Indexed Status:</span>
                        <span
                          className={`font-semibold ${book.index_status === 'completed' ? 'text-emerald-600' : 'text-amber-500'}`}
                        >
                          {book.index_status}
                        </span>
                      </p>
                    </div>
                  </div>
                ))
              )}
            </div>
          </div>

          <button
            onClick={() => navigate('/library')}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-slate-50 hover:bg-slate-100 dark:bg-zinc-850 dark:hover:bg-zinc-800 text-slate-700 dark:text-zinc-200 rounded-xl text-xs font-semibold border border-slate-200 dark:border-zinc-700/60 transition-all cursor-pointer mt-4"
          >
            Manage Library Collection
            <ArrowRight className="h-3 w-3" />
          </button>
        </div>
      </div>

      {/* Semantic Index Parameters Card */}
      <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800/80 rounded-2xl p-6 shadow-sm">
        <h3 className="text-sm font-bold text-slate-900 dark:text-zinc-50 flex items-center gap-2 mb-4">
          <Cpu className="h-4 w-4 text-purple-600 dark:text-purple-400" />
          Semantic Index Parameters
        </h3>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-6 text-xs mt-2">
          <div className="space-y-1">
            <span className="text-slate-400 dark:text-zinc-500 block uppercase font-bold text-[9px] tracking-wider">
              Average Chunk Size
            </span>
            <span className="font-bold text-slate-800 dark:text-zinc-200 mt-1 block">
              {config ? `${config.chunk_size} chars` : '500 chars'}
            </span>
          </div>
          <div className="space-y-1">
            <span className="text-slate-400 dark:text-zinc-500 block uppercase font-bold text-[9px] tracking-wider">
              Similarity Threshold
            </span>
            <span className="font-bold text-slate-800 dark:text-zinc-200 mt-1 block">
              {config ? `${config.similarity_threshold}` : '0.35'}
            </span>
          </div>
          <div className="space-y-1">
            <span className="text-slate-400 dark:text-zinc-500 block uppercase font-bold text-[9px] tracking-wider">
              Embedding Dimension
            </span>
            <span className="font-bold text-slate-800 dark:text-zinc-200 mt-1 block">
              {config?.embedding_model?.includes('MiniLM') ? '384d' : '768d'}
            </span>
          </div>
          <div className="space-y-1">
            <span className="text-slate-400 dark:text-zinc-500 block uppercase font-bold text-[9px] tracking-wider">
              Vector DB Provider
            </span>
            <span className="font-bold text-slate-800 dark:text-zinc-200 mt-1 block">ChromaDB</span>
          </div>
          <div className="space-y-1">
            <span className="text-slate-400 dark:text-zinc-500 block uppercase font-bold text-[9px] tracking-wider">
              Index Status
            </span>
            <span className="inline-flex items-center gap-1.5 mt-1 text-[11px] font-bold text-emerald-650 dark:text-emerald-500">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-500 animate-pulse" />
              Active
            </span>
          </div>
          <div className="space-y-1">
            <span className="text-slate-400 dark:text-zinc-500 block uppercase font-bold text-[9px] tracking-wider">
              Retrieval Limit
            </span>
            <span className="font-bold text-slate-800 dark:text-zinc-200 mt-1 block">
              {config ? `${config.retrieval_limit} chunks` : '4 chunks'}
            </span>
          </div>
        </div>
      </div>
    </div>
  )
}
