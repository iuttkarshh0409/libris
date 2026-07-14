import type { LucideIcon } from 'lucide-react'

interface EmptyStateProps {
  title: string
  description: string
  icon: LucideIcon
  actionLabel?: string
  onAction?: () => void
}

export default function EmptyState({
  title,
  description,
  icon: Icon,
  actionLabel,
  onAction,
}: EmptyStateProps) {
  return (
    <div className="flex flex-col items-center justify-center text-center p-8 border border-dashed border-slate-300 dark:border-zinc-800 rounded-2xl bg-slate-50/50 dark:bg-zinc-900/30 max-w-xl mx-auto my-12">
      <div className="p-4 bg-slate-100 dark:bg-zinc-800/80 text-slate-400 dark:text-zinc-500 rounded-full mb-4">
        <Icon className="h-10 w-10" />
      </div>
      <h3 className="text-lg font-bold text-slate-900 dark:text-zinc-50 mb-1">{title}</h3>
      <p className="text-sm text-slate-500 dark:text-zinc-400/80 mb-6 max-w-md">{description}</p>
      {actionLabel && onAction && (
        <button
          onClick={onAction}
          className="px-5 py-2.5 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-sm font-semibold transition-all shadow-md shadow-purple-500/20 active:scale-95 cursor-pointer"
        >
          {actionLabel}
        </button>
      )}
    </div>
  )
}
