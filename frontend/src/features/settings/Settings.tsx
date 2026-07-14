import { useQuery } from '@tanstack/react-query'
import { ShieldAlert, Sliders } from 'lucide-react'
import { ConfigService } from '../../shared/services/api'
import PageHeader from '../../components/PageHeader'
import LoadingSpinner from '../../components/LoadingSpinner'
import ErrorPanel from '../../components/ErrorPanel'

export default function Settings() {
  const {
    data: config,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['config'],
    queryFn: ConfigService.getConfig,
  })

  if (isLoading) {
    return <LoadingSpinner label="Retrieving configuration..." />
  }

  if (error || !config) {
    return (
      <ErrorPanel
        title="Configuration Failure"
        message={error ? (error as Error).message : 'Could not read settings.'}
        onRetry={refetch}
      />
    )
  }

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      <PageHeader
        title="Platform Configuration"
        description="Review active infrastructure parameter settings for document parsing, segmentation, and semantic search thresholds."
      />

      <div className="max-w-3xl space-y-6">
        {/* Info/Warning Warning panel */}
        <div className="bg-amber-50/50 dark:bg-amber-950/10 border border-amber-200 dark:border-amber-900/60 rounded-2xl p-5 flex gap-4">
          <ShieldAlert className="h-5.5 w-5.5 text-amber-600 dark:text-amber-500 shrink-0 mt-0.5" />
          <div className="space-y-1">
            <h4 className="text-sm font-bold text-amber-800 dark:text-amber-400">
              Settings Are Read-Only
            </h4>
            <p className="text-xs text-amber-700 dark:text-amber-300/90 leading-relaxed">
              To preserve architectural integrity in Architecture v1.0.0, runtime mutation of
              configuration values has been restricted. Values are loaded from environment
              configurations or local system configuration files.
            </p>
          </div>
        </div>

        {/* Configuration grid */}
        <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800/80 rounded-2xl p-6 shadow-sm space-y-5">
          <h3 className="text-base font-bold text-slate-900 dark:text-zinc-50 flex items-center gap-2 border-b border-slate-100 dark:border-zinc-850 pb-3">
            <Sliders className="h-4.5 w-4.5 text-purple-600 dark:text-purple-400" />
            Parameter Configurations
          </h3>

          <div className="space-y-4">
            {/* Chunk Size */}
            <div className="flex items-center justify-between py-2 border-b border-slate-100 dark:border-zinc-850/60 last:border-0">
              <div className="space-y-0.5">
                <span className="text-sm font-bold text-slate-800 dark:text-zinc-200">
                  Semantic Chunk Size
                </span>
                <p className="text-[11px] text-slate-400 dark:text-zinc-500 leading-normal">
                  The target character length for segmented text blocks.
                </p>
              </div>
              <span className="font-mono text-sm font-bold px-3 py-1 bg-slate-100 dark:bg-zinc-800 text-slate-700 dark:text-zinc-300 rounded-lg">
                {config.chunk_size} chars
              </span>
            </div>

            {/* Chunk Overlap */}
            <div className="flex items-center justify-between py-2 border-b border-slate-100 dark:border-zinc-850/60 last:border-0">
              <div className="space-y-0.5">
                <span className="text-sm font-bold text-slate-800 dark:text-zinc-200">
                  Segment Overlap Boundary
                </span>
                <p className="text-[11px] text-slate-400 dark:text-zinc-500 leading-normal">
                  The overlap window size between contiguous text segments to preserve contextual
                  flow.
                </p>
              </div>
              <span className="font-mono text-sm font-bold px-3 py-1 bg-slate-100 dark:bg-zinc-800 text-slate-700 dark:text-zinc-300 rounded-lg">
                {config.chunk_overlap} chars
              </span>
            </div>

            {/* Similarity Cutoff */}
            <div className="flex items-center justify-between py-2 border-b border-slate-100 dark:border-zinc-850/60 last:border-0">
              <div className="space-y-0.5">
                <span className="text-sm font-bold text-slate-800 dark:text-zinc-200">
                  Default Similarity Cutoff
                </span>
                <p className="text-[11px] text-slate-400 dark:text-zinc-500 leading-normal">
                  The default cosine distance/similarity threshold filter applied to vector search
                  results.
                </p>
              </div>
              <span className="font-mono text-sm font-bold px-3 py-1 bg-slate-100 dark:bg-zinc-800 text-slate-700 dark:text-zinc-300 rounded-lg">
                {config.similarity_threshold}
              </span>
            </div>

            {/* Retrieval Limit */}
            <div className="flex items-center justify-between py-2 border-b border-slate-100 dark:border-zinc-850/60 last:border-0">
              <div className="space-y-0.5">
                <span className="text-sm font-bold text-slate-800 dark:text-zinc-200">
                  Retrieval Count Limit
                </span>
                <p className="text-[11px] text-slate-400 dark:text-zinc-500 leading-normal">
                  The maximum number of source chunks compiled into the LLM context wrapper.
                </p>
              </div>
              <span className="font-mono text-sm font-bold px-3 py-1 bg-slate-100 dark:bg-zinc-800 text-slate-700 dark:text-zinc-300 rounded-lg">
                {config.retrieval_limit} chunks
              </span>
            </div>

            {/* Embedding Model */}
            <div className="flex items-center justify-between py-2 last:border-0">
              <div className="space-y-0.5">
                <span className="text-sm font-bold text-slate-800 dark:text-zinc-200">
                  Embedding Model Identity
                </span>
                <p className="text-[11px] text-slate-400 dark:text-zinc-500 leading-normal">
                  Local Sentence Transformer model loaded in memory for text vectorizations.
                </p>
              </div>
              <span className="font-mono text-xs font-bold px-3 py-1.5 bg-purple-50 dark:bg-purple-950/20 text-purple-700 dark:text-purple-400 rounded-lg max-w-[200px] truncate">
                {config.embedding_model}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
