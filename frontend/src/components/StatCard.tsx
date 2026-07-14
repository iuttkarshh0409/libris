import type { LucideIcon } from 'lucide-react'

interface StatCardProps {
  title: string
  value: string | number
  description?: string
  icon: LucideIcon
  color?: 'purple' | 'blue' | 'emerald' | 'rose' | 'amber'
}

export default function StatCard({
  title,
  value,
  description,
  icon: Icon,
  color = 'purple',
}: StatCardProps) {
  const colorMap = {
    purple:
      'text-purple-600 bg-purple-100 dark:bg-purple-900/30 dark:text-purple-400 border-purple-200/55 dark:border-purple-800/30',
    blue: 'text-blue-600 bg-blue-100 dark:bg-blue-900/30 dark:text-blue-400 border-blue-200/55 dark:border-blue-800/30',
    emerald:
      'text-emerald-600 bg-emerald-100 dark:bg-emerald-900/30 dark:text-emerald-400 border-emerald-200/55 dark:border-emerald-800/30',
    rose: 'text-rose-600 bg-rose-100 dark:bg-rose-900/30 dark:text-rose-400 border-rose-200/55 dark:border-rose-800/30',
    amber:
      'text-amber-600 bg-amber-100 dark:bg-amber-900/30 dark:text-amber-400 border-amber-200/55 dark:border-amber-800/30',
  }

  return (
    <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800/80 rounded-2xl p-6 shadow-sm hover:shadow-md transition-all duration-200 flex items-start justify-between">
      <div className="flex flex-col gap-1">
        <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 dark:text-zinc-500">
          {title}
        </span>
        <span className="text-3xl font-extrabold tracking-tight text-slate-900 dark:text-zinc-50 mt-1">
          {value}
        </span>
        {description && (
          <span className="text-xs text-slate-400 dark:text-zinc-400/80 mt-1">{description}</span>
        )}
      </div>
      <div className={`p-3 rounded-xl border ${colorMap[color]} shrink-0`}>
        <Icon className="h-5 w-5" />
      </div>
    </div>
  )
}
