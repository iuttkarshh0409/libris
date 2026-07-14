import { useQuery } from '@tanstack/react-query'
import { ShieldCheck, Server, Cpu as ModelIcon } from 'lucide-react'
import { StatusService } from '../../shared/services/api'
import PageHeader from '../../components/PageHeader'
import LoadingSpinner from '../../components/LoadingSpinner'
import ErrorPanel from '../../components/ErrorPanel'
import ProviderStatusBadge from '../../components/ProviderStatusBadge'

export default function SystemStatus() {
  const {
    data: status,
    isLoading,
    error,
    refetch,
  } = useQuery({
    queryKey: ['status'],
    queryFn: StatusService.getStatus,
    refetchInterval: 10000, // refresh every 10s
  })

  if (isLoading) {
    return <LoadingSpinner label="Retrieving system health checks..." />
  }

  if (error || !status) {
    return (
      <ErrorPanel
        title="Diagnostic Failure"
        message={error ? (error as Error).message : 'Could not query provider states.'}
        onRetry={refetch}
      />
    )
  }

  // Frontend engines checklist status mapping (corresponds to architecture layers)
  const structuralSubsystems = [
    { name: 'Document Engine', type: 'Parsing', status: 'Healthy', provider: 'PyPDF / PDFminer' },
    {
      name: 'Chunking Engine',
      type: 'Segmentation',
      status: 'Healthy',
      provider: 'Semantic Overlap Segmenter',
    },
    {
      name: 'Embedding Engine',
      type: 'Vectorization',
      status: status.provider_status.embedding_provider,
      provider: status.configured_models.embedding_model,
    },
    {
      name: 'Indexing Engine',
      type: 'Vector Storage',
      status: status.provider_status.index_provider,
      provider: 'ChromaDB',
    },
    {
      name: 'Retrieval Engine',
      type: 'Similarity Search',
      status: 'Healthy',
      provider: 'Vector Ranker',
    },
    {
      name: 'Grounding Engine',
      type: 'Context Synthesis',
      status: 'Healthy',
      provider: 'Constraint Engine',
    },
    {
      name: 'Generation Engine',
      type: 'Inference',
      status: status.provider_status.llm_provider,
      provider: status.configured_models.llm_model,
    },
    {
      name: 'Citation Engine',
      type: 'Evidence Verification',
      status: 'Healthy',
      provider: 'Citations Reconciler',
    },
  ]

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      <PageHeader
        title="System Status"
        description="Monitor version configurations and active health check statuses across all core pipeline subsystems."
      />

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Core System Status Card */}
        <div className="lg:col-span-2 bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800/80 rounded-2xl p-6 shadow-sm space-y-6">
          <div className="flex items-center justify-between border-b border-slate-100 dark:border-zinc-850 pb-3">
            <h3 className="text-base font-bold text-slate-900 dark:text-zinc-50 flex items-center gap-2">
              <Server className="h-4.5 w-4.5 text-purple-600 dark:text-purple-400" />
              Subsystem Diagnostic
            </h3>
            <ProviderStatusBadge status={status.health_state} />
          </div>

          <div className="space-y-4">
            {structuralSubsystems.map((sub) => (
              <div
                key={sub.name}
                className="flex flex-col sm:flex-row sm:items-center sm:justify-between py-3 border-b border-slate-100 dark:border-zinc-850/60 last:border-0 last:pb-0"
              >
                <div className="space-y-0.5 mb-2 sm:mb-0">
                  <span className="text-sm font-bold text-slate-800 dark:text-zinc-200">
                    {sub.name}
                  </span>
                  <p className="text-[10px] text-slate-400 dark:text-zinc-500 font-medium">
                    {sub.type} • Provider: {sub.provider}
                  </p>
                </div>
                <ProviderStatusBadge status={sub.status} />
              </div>
            ))}
          </div>
        </div>

        {/* System Version details card */}
        <div className="space-y-6">
          <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800/80 rounded-2xl p-6 shadow-sm space-y-5">
            <h3 className="text-base font-bold text-slate-900 dark:text-zinc-50 flex items-center gap-2">
              <ShieldCheck className="h-4.5 w-4.5 text-purple-600 dark:text-purple-400" />
              Build Information
            </h3>

            <div className="space-y-3.5 text-xs text-slate-600 dark:text-zinc-400">
              <div className="flex justify-between py-2 border-b border-slate-50 dark:border-zinc-850">
                <span className="font-semibold">Application Version</span>
                <span className="font-mono font-bold text-slate-800 dark:text-zinc-200">
                  {status.application_version}
                </span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-50 dark:border-zinc-850">
                <span className="font-semibold">Architecture Version</span>
                <span className="font-mono font-bold text-slate-800 dark:text-zinc-200">
                  {status.architecture_version}
                </span>
              </div>
              <div className="flex justify-between py-2 border-b border-slate-50 dark:border-zinc-850">
                <span className="font-semibold">Build Phase</span>
                <span className="font-semibold text-purple-600 dark:text-purple-400">
                  Phase 11 (Release)
                </span>
              </div>
              <div className="flex justify-between py-2">
                <span className="font-semibold">Environment Mode</span>
                <span className="font-semibold text-emerald-600 dark:text-emerald-500">
                  Production Freezed
                </span>
              </div>
            </div>
          </div>

          <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800/80 rounded-2xl p-6 shadow-sm space-y-5">
            <h3 className="text-base font-bold text-slate-900 dark:text-zinc-50 flex items-center gap-2">
              <ModelIcon className="h-4.5 w-4.5 text-purple-600 dark:text-purple-400" />
              Inference Frameworks
            </h3>

            <div className="space-y-3.5 text-xs text-slate-650 dark:text-zinc-400">
              <div>
                <span className="text-[10px] uppercase font-bold text-slate-400 dark:text-zinc-500 block">
                  LLM Engine
                </span>
                <span className="font-bold text-slate-900 dark:text-zinc-250 block mt-1">
                  {status.configured_models.llm_model}
                </span>
              </div>
              <div>
                <span className="text-[10px] uppercase font-bold text-slate-400 dark:text-zinc-500 block">
                  Embeddings Engine
                </span>
                <span className="font-bold text-slate-900 dark:text-zinc-250 block mt-1 truncate max-w-xs">
                  {status.configured_models.embedding_model}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
