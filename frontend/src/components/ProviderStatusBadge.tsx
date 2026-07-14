interface ProviderStatusBadgeProps {
  status: string
}

export default function ProviderStatusBadge({ status }: ProviderStatusBadgeProps) {
  const normalized = status.toLowerCase()

  let isHealthy = normalized.includes('healthy')
  let isWarning =
    normalized.includes('busy') || normalized.includes('warning') || normalized.includes('queued')
  let isError =
    normalized.includes('unhealthy') ||
    normalized.includes('error') ||
    normalized.includes('failed')

  if (isHealthy) {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-emerald-50 dark:bg-emerald-950/20 text-emerald-700 dark:text-emerald-400 border border-emerald-200/60 dark:border-emerald-900/30">
        <span className="h-1.5 w-1.5 rounded-full bg-emerald-500" />
        {status}
      </span>
    )
  }

  if (isWarning) {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-amber-50 dark:bg-amber-950/20 text-amber-700 dark:text-amber-400 border border-amber-200/60 dark:border-amber-900/30">
        <span className="h-1.5 w-1.5 rounded-full bg-amber-500 animate-pulse" />
        {status}
      </span>
    )
  }

  if (isError) {
    return (
      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-rose-50 dark:bg-rose-950/20 text-rose-700 dark:text-rose-400 border border-rose-200/60 dark:border-rose-900/30">
        <span className="h-1.5 w-1.5 rounded-full bg-rose-500" />
        {status}
      </span>
    )
  }

  return (
    <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-md text-xs font-semibold bg-slate-50 dark:bg-zinc-800 text-slate-700 dark:text-zinc-300 border border-slate-200/60 dark:border-zinc-700/30">
      <span className="h-1.5 w-1.5 rounded-full bg-slate-400" />
      {status}
    </span>
  )
}
