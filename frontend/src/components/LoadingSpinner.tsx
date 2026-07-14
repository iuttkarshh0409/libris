import { Loader2 } from 'lucide-react'

interface LoadingSpinnerProps {
  label?: string
  size?: 'sm' | 'md' | 'lg'
}

export default function LoadingSpinner({
  label = 'Loading contents...',
  size = 'md',
}: LoadingSpinnerProps) {
  const sizeMap = {
    sm: 'h-5 w-5 border-2',
    md: 'h-8 w-8 border-3',
    lg: 'h-12 w-12 border-4',
  }

  return (
    <div className="flex flex-col items-center justify-center py-12 px-6 text-center space-y-4">
      <Loader2 className={`animate-spin text-purple-600 dark:text-purple-400 ${sizeMap[size]}`} />
      {label && (
        <p className="text-sm font-medium text-slate-500 dark:text-zinc-400/90 animate-pulse">
          {label}
        </p>
      )}
    </div>
  )
}
