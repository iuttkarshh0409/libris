import { useNavigate } from 'react-router-dom'
import { HelpCircle, ArrowLeft } from 'lucide-react'

export default function NotFound() {
  const navigate = useNavigate()

  return (
    <div className="min-h-[70vh] flex flex-col items-center justify-center text-center p-6">
      <div className="p-4 bg-purple-50 dark:bg-purple-950/20 text-purple-600 dark:text-purple-400 rounded-full mb-6 border border-purple-100 dark:border-purple-900/30">
        <HelpCircle className="h-12 w-12" />
      </div>
      <h1 className="text-4xl font-extrabold text-slate-900 dark:text-zinc-55 mb-2">404</h1>
      <h2 className="text-lg font-bold text-slate-800 dark:text-zinc-200 mb-3">Page Not Found</h2>
      <p className="text-sm text-slate-500 dark:text-zinc-400 max-w-md mb-8">
        The route you are trying to access does not exist on this platform. If you expect a textbook
        collection details view, verify the book ID is correct.
      </p>

      <button
        onClick={() => navigate('/dashboard')}
        className="flex items-center gap-2 px-5 py-2.5 bg-purple-600 hover:bg-purple-700 text-white rounded-xl text-sm font-semibold transition-all shadow-md shadow-purple-500/20 active:scale-95 cursor-pointer"
      >
        <ArrowLeft className="h-4 w-4" />
        Return to Dashboard
      </button>
    </div>
  )
}
