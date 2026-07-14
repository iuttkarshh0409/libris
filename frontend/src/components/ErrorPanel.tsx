import { AlertCircle, RefreshCw } from 'lucide-react'

interface ErrorPanelProps {
  title?: string
  message: string
  onRetry?: () => void
}

export default function ErrorPanel({
  title = 'Operation Failed',
  message,
  onRetry,
}: ErrorPanelProps) {
  return (
    <div className="border border-rose-200 dark:border-rose-950/80 bg-rose-50/50 dark:bg-rose-950/10 rounded-2xl p-6 flex flex-col sm:flex-row items-start gap-4 max-w-2xl mx-auto my-8">
      <div className="p-2 bg-rose-100 dark:bg-rose-950/40 text-rose-600 dark:text-rose-400 rounded-xl shrink-0">
        <AlertCircle className="h-6 w-6" />
      </div>
      <div className="flex-1 space-y-1">
        <h4 className="text-base font-bold text-rose-800 dark:text-rose-400">{title}</h4>
        <p className="text-sm text-rose-700 dark:text-rose-300/90 leading-relaxed">{message}</p>
        <p className="text-xs text-rose-600/70 dark:text-rose-400/50 mt-2">
          Note: If this persists, verify your local server and database connection are active.
        </p>
      </div>
      {onRetry && (
        <button
          onClick={onRetry}
          className="flex items-center gap-2 px-4 py-2 bg-white dark:bg-zinc-900 hover:bg-rose-50 dark:hover:bg-rose-950/20 text-rose-700 dark:text-rose-300 border border-rose-200 dark:border-rose-900/60 rounded-xl text-sm font-semibold transition-all shrink-0 active:scale-95 cursor-pointer shadow-xs"
        >
          <RefreshCw className="h-3.5 w-3.5" />
          Retry
        </button>
      )}
    </div>
  )
}
