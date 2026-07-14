import { useState, useEffect, useRef, type FormEvent } from 'react'
import { useLocation } from 'react-router-dom'
import { useMutation } from '@tanstack/react-query'
import {
  MessageSquare,
  Send,
  Copy,
  Check,
  Bookmark,
  Loader2,
  History,
  FileText,
  Cpu,
  Layers,
} from 'lucide-react'
import { BookService, QueryService } from '../../shared/services/api'
import type { BookSummary, VerifiedResponse } from '../../shared/services/types'
import PageHeader from '../../components/PageHeader'
import ErrorPanel from '../../components/ErrorPanel'
import EmptyState from '../../components/EmptyState'
import { toast } from 'sonner'

interface QueryHistoryItem {
  query: string
  timestamp: string
  response: VerifiedResponse
}

export default function QueryWorkspace() {
  const location = useLocation()
  const [question, setQuestion] = useState('')
  const [similarityThreshold, setSimilarityThreshold] = useState<number>(0.35)
  const [retrievalLimit, setRetrievalLimit] = useState<number>(4)
  const [copied, setCopied] = useState(false)
  const [citationsCopied, setCitationsCopied] = useState(false)
  const [activeExcerptIdx, setActiveExcerptIdx] = useState<number | null>(null)

  // Pipeline simulation state during query execution
  const [queryPipelineStep, setQueryPipelineStep] = useState<number>(0)
  const [isQuerying, setIsQuerying] = useState(false)

  // Local storage query history
  const [history, setHistory] = useState<QueryHistoryItem[]>(() => {
    return JSON.parse(localStorage.getItem('query_history') || '[]')
  })

  const [activeResponse, setActiveResponse] = useState<VerifiedResponse | null>(null)

  const queryInputRef = useRef<HTMLInputElement>(null)

  // Keyboard shortcut Ctrl+K to focus search input
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault()
        queryInputRef.current?.focus()
      }
    }
    window.addEventListener('keydown', handleKeyDown)
    return () => window.removeEventListener('keydown', handleKeyDown)
  }, [])

  const [books, setBooks] = useState<BookSummary[]>([])
  const [selectedBookId, setSelectedBookId] = useState<string>('')

  // Load books list on mount
  useEffect(() => {
    BookService.listBooks()
      .then((data) => {
        setBooks(data)
      })
      .catch((err) => {
        console.error('Failed to load books for dropdown:', err)
      })
  }, [])

  // Load selected book from route state if redirected from details
  useEffect(() => {
    if (location.state && (location.state as any).selectedBookId) {
      setSelectedBookId((location.state as any).selectedBookId)
      toast.info('Selected book from library.')
    }
  }, [location.state])

  // Query Mutation
  const queryMutation = useMutation({
    mutationFn: QueryService.submitQuery,
    onSuccess: (data) => {
      // Advance to final steps
      setQueryPipelineStep(6)
      setTimeout(() => {
        setIsQuerying(false)
        setQueryPipelineStep(0)
        setActiveResponse(data)
        setActiveExcerptIdx(0)

        // Add to history
        const newHistoryItem: QueryHistoryItem = {
          query: question,
          timestamp: new Date().toISOString(),
          response: data,
        }
        const updated = [newHistoryItem, ...history.slice(0, 9)] // keep last 10
        setHistory(updated)
        localStorage.setItem('query_history', JSON.stringify(updated))

        toast.success('Response compiled and verified against sources!')
      }, 1200)
    },
    onError: (err: any) => {
      setIsQuerying(false)
      setQueryPipelineStep(0)
      toast.error(err?.message || 'Failed to evaluate query.')
    },
  })

  // Query Pipeline steps timer simulation
  useEffect(() => {
    if (!isQuerying) return

    const timer1 = setTimeout(() => setQueryPipelineStep(1), 400) // Retrieving Evidence
    const timer2 = setTimeout(() => setQueryPipelineStep(2), 900) // Building Prompt
    const timer3 = setTimeout(() => setQueryPipelineStep(3), 1500) // Generating Answer
    const timer4 = setTimeout(() => setQueryPipelineStep(4), 2200) // Verifying Citations
    const timer5 = setTimeout(() => setQueryPipelineStep(5), 3000) // Completed

    return () => {
      clearTimeout(timer1)
      clearTimeout(timer2)
      clearTimeout(timer3)
      clearTimeout(timer4)
      clearTimeout(timer5)
    }
  }, [isQuerying])

  const handleQuerySubmit = (e: FormEvent) => {
    e.preventDefault()
    if (!question.trim() || isQuerying) return

    setIsQuerying(true)
    setQueryPipelineStep(0)
    setActiveResponse(null)

    queryMutation.mutate({
      query_text: question,
      similarity_threshold: similarityThreshold,
      limit: retrievalLimit,
      book_id: selectedBookId || undefined,
    })
  }

  const handleCopy = () => {
    const activeItem = activeResponse?.items?.[0]
    if (!activeItem) return

    navigator.clipboard.writeText(activeItem.answer_text)
    setCopied(true)
    toast.success('Answer copied to clipboard!')
    setTimeout(() => setCopied(false), 2000)
  }

  const handleCopyCitations = () => {
    const activeItem = activeResponse?.items?.[0]
    if (!activeItem || activeItem.supporting_citations.length === 0) return

    const citationText = activeItem.supporting_citations
      .map((cit, idx) => {
        return `[${idx + 1}] Book: ${cit.book_title}, Page: ${cit.page_number}, Chapter: ${cit.chapter || 'N/A'}`
      })
      .join('\n')

    navigator.clipboard.writeText(citationText)
    setCitationsCopied(true)
    toast.success('Citations list copied!')
    setTimeout(() => setCitationsCopied(false), 2000)
  }

  const loadHistoryItem = (item: QueryHistoryItem) => {
    setQuestion(item.query)
    setActiveResponse(item.response)
    setActiveExcerptIdx(0)
  }

  const activeItem = activeResponse?.items?.[0]

  const scrollToAndHighlightExcerpt = (idx: number) => {
    setActiveExcerptIdx(idx)
    setTimeout(() => {
      const element = document.getElementById(`evidence-card-${idx}`)
      if (element) {
        element.scrollIntoView({ behavior: 'smooth', block: 'center' })
        element.classList.add('ring-4', 'ring-purple-500/50', 'border-purple-500', 'scale-[1.01]')
        setTimeout(() => {
          element.classList.remove(
            'ring-4',
            'ring-purple-500/50',
            'border-purple-500',
            'scale-[1.01]'
          )
        }, 2000)
      }
    }, 100)
  }

  const renderAnswerWithClickableCitations = (text: string) => {
    if (!activeItem) return text
    const lines = text.split('\n')

    return lines.map((line, lineIdx) => {
      const tokens: { type: 'text' | 'bold' | 'citation'; content: string; num?: number }[] = []
      let tempIndex = 0
      const lineRegex = /(\*\*[^*]+\*\*|\[\d+\])/g
      let match

      while ((match = lineRegex.exec(line)) !== null) {
        if (match.index > tempIndex) {
          tokens.push({ type: 'text', content: line.substring(tempIndex, match.index) })
        }

        const tokenText = match[0]
        if (tokenText.startsWith('**') && tokenText.endsWith('**')) {
          tokens.push({ type: 'bold', content: tokenText.slice(2, -2) })
        } else if (tokenText.startsWith('[') && tokenText.endsWith(']')) {
          const num = parseInt(tokenText.slice(1, -1))
          tokens.push({ type: 'citation', content: tokenText, num })
        }

        tempIndex = lineRegex.lastIndex
      }

      if (tempIndex < line.length) {
        tokens.push({ type: 'text', content: line.substring(tempIndex) })
      }

      const lineContent =
        tokens.length === 0
          ? line
          : tokens.map((t, tIdx) => {
              if (t.type === 'bold') {
                return (
                  <strong key={tIdx} className="font-bold text-slate-900 dark:text-zinc-100">
                    {t.content}
                  </strong>
                )
              } else if (t.type === 'citation' && t.num) {
                const citationIdx = t.num - 1
                if (citationIdx >= 0 && citationIdx < activeItem.supporting_citations.length) {
                  return (
                    <button
                      key={tIdx}
                      type="button"
                      onClick={() => scrollToAndHighlightExcerpt(citationIdx)}
                      className="inline-flex items-center justify-center px-1.5 py-0.5 mx-0.5 text-[10px] font-bold text-white bg-purple-600 hover:bg-purple-700 active:scale-95 rounded-md cursor-pointer transition-transform hover:scale-105"
                      title={`View evidence chunk #${t.num} from page ${activeItem.supporting_citations[citationIdx].page_number}`}
                    >
                      [{t.num}]
                    </button>
                  )
                }
                return t.content
              }
              return t.content
            })

      // Check if it's a numbered list item
      const listMatch = line.match(/^(\d+)\.\s(.*)/)
      if (listMatch) {
        const remainingTokens: {
          type: 'text' | 'bold' | 'citation'
          content: string
          num?: number
        }[] = []
        let subTempIndex = 0
        const subLine = listMatch[2]
        let subMatch

        while ((subMatch = lineRegex.exec(subLine)) !== null) {
          if (subMatch.index > subTempIndex) {
            remainingTokens.push({
              type: 'text',
              content: subLine.substring(subTempIndex, subMatch.index),
            })
          }

          const tokenText = subMatch[0]
          if (tokenText.startsWith('**') && tokenText.endsWith('**')) {
            remainingTokens.push({ type: 'bold', content: tokenText.slice(2, -2) })
          } else if (tokenText.startsWith('[') && tokenText.endsWith(']')) {
            const num = parseInt(tokenText.slice(1, -1))
            remainingTokens.push({ type: 'citation', content: tokenText, num })
          }

          subTempIndex = lineRegex.lastIndex
        }

        if (subTempIndex < subLine.length) {
          remainingTokens.push({ type: 'text', content: subLine.substring(subTempIndex) })
        }

        const subLineContent =
          remainingTokens.length === 0
            ? subLine
            : remainingTokens.map((t, tIdx) => {
                if (t.type === 'bold') {
                  return (
                    <strong key={tIdx} className="font-bold text-slate-900 dark:text-zinc-100">
                      {t.content}
                    </strong>
                  )
                } else if (t.type === 'citation' && t.num) {
                  const citationIdx = t.num - 1
                  if (citationIdx >= 0 && citationIdx < activeItem.supporting_citations.length) {
                    return (
                      <button
                        key={tIdx}
                        type="button"
                        onClick={() => scrollToAndHighlightExcerpt(citationIdx)}
                        className="inline-flex items-center justify-center px-1.5 py-0.5 mx-0.5 text-[10px] font-bold text-white bg-purple-600 hover:bg-purple-700 active:scale-95 rounded-md cursor-pointer transition-transform hover:scale-105"
                        title={`View evidence chunk #${t.num} from page ${activeItem.supporting_citations[citationIdx].page_number}`}
                      >
                        [{t.num}]
                      </button>
                    )
                  }
                  return t.content
                }
                return t.content
              })

        return (
          <div key={lineIdx} className="pl-4 py-1.5 flex gap-2 text-slate-700 dark:text-zinc-300">
            <span className="font-bold text-purple-600 dark:text-purple-400 shrink-0">
              {listMatch[1]}.
            </span>
            <div className="flex-1">{subLineContent}</div>
          </div>
        )
      }

      return (
        <p
          key={lineIdx}
          className={line.trim() === '' ? 'h-3' : 'py-1 text-slate-750 dark:text-zinc-300'}
        >
          {lineContent}
        </p>
      )
    })
  }

  const pipelineSteps = [
    { label: 'Question Submitted', desc: 'Validating and embedding incoming query text' },
    { label: 'Retrieving Evidence', desc: 'Executing vector similarity search in local database' },
    {
      label: 'Building Prompt',
      desc: 'Assembling relevant context structure and metadata boundaries',
    },
    {
      label: 'Generating Answer',
      desc: 'Generating structured response utilizing deep inference model',
    },
    {
      label: 'Verifying Citations',
      desc: 'Reconciling outputs against actual retrieval source offsets',
    },
    { label: 'Completed', desc: 'Response verified, citation offsets resolved and ready' },
  ]

  return (
    <div className="space-y-8 animate-in fade-in duration-300">
      <PageHeader
        title="Query Workspace"
        description="Ask question across all ingested textbooks. The engine returns compiled responses with inline citations and similarity indexes."
      />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        {/* Left Side Settings / History Panel */}
        <div className="space-y-6 lg:col-span-1">
          {/* Query Parameters Panel */}
          <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800/80 rounded-2xl p-5 shadow-sm space-y-4">
            <h3 className="text-xs font-bold text-slate-800 dark:text-zinc-300 uppercase tracking-wider border-b border-slate-100 dark:border-zinc-850 pb-2">
              Parameters
            </h3>

            <div className="space-y-3">
              <div>
                <label className="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-wider flex justify-between">
                  <span>Scope Textbook</span>
                </label>
                <select
                  value={selectedBookId}
                  onChange={(e) => setSelectedBookId(e.target.value)}
                  className="w-full bg-slate-50 dark:bg-zinc-850/60 border border-slate-200 dark:border-zinc-800 rounded-lg text-xs p-2 text-slate-700 dark:text-zinc-300 mt-2 outline-none focus:border-purple-500 transition-colors cursor-pointer"
                >
                  <option value="">All / Latest Uploaded</option>
                  {books.map((book) => (
                    <option key={book.id} value={book.id}>
                      {book.title} {book.edition ? `(${book.edition})` : ''}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-wider flex justify-between">
                  <span>Similarity Cutoff</span>
                  <span>{similarityThreshold}</span>
                </label>
                <input
                  type="range"
                  min="0.10"
                  max="0.80"
                  step="0.05"
                  value={similarityThreshold}
                  onChange={(e) => setSimilarityThreshold(parseFloat(e.target.value))}
                  className="w-full h-1 bg-slate-200 dark:bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-purple-600 mt-2"
                />
              </div>

              <div>
                <label className="text-[10px] font-bold text-slate-400 dark:text-zinc-500 uppercase tracking-wider flex justify-between">
                  <span>Retrieval Limit</span>
                  <span>{retrievalLimit} chunks</span>
                </label>
                <input
                  type="range"
                  min="1"
                  max="10"
                  step="1"
                  value={retrievalLimit}
                  onChange={(e) => setRetrievalLimit(parseInt(e.target.value))}
                  className="w-full h-1 bg-slate-200 dark:bg-zinc-800 rounded-lg appearance-none cursor-pointer accent-purple-600 mt-2"
                />
              </div>
            </div>
          </div>

          {/* History Panel */}
          <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800/80 rounded-2xl p-5 shadow-sm flex flex-col max-h-[400px]">
            <div className="flex items-center justify-between border-b border-slate-100 dark:border-zinc-850 pb-2">
              <h3 className="text-xs font-bold text-slate-800 dark:text-zinc-300 uppercase tracking-wider flex items-center gap-1.5">
                <History className="h-3.5 w-3.5 text-slate-400" />
                Recent Queries
              </h3>
              {history.length > 0 && (
                <button
                  type="button"
                  onClick={() => {
                    setHistory([])
                    localStorage.removeItem('query_history')
                    toast.success('Query history cleared.')
                  }}
                  className="text-[10px] font-semibold text-rose-600 hover:text-rose-700 dark:text-rose-455 hover:underline cursor-pointer"
                >
                  Clear All
                </button>
              )}
            </div>

            <div className="overflow-y-auto space-y-2 mt-3 flex-1">
              {history.length === 0 ? (
                <p className="text-[11px] text-slate-400 dark:text-zinc-500 text-center py-4">
                  No query history in this workspace session.
                </p>
              ) : (
                history.map((item, idx) => (
                  <button
                    key={idx}
                    type="button"
                    onClick={() => loadHistoryItem(item)}
                    className="w-full text-left p-2.5 rounded-lg text-xs hover:bg-slate-50 dark:hover:bg-zinc-850/60 border border-transparent hover:border-slate-100 dark:hover:border-zinc-855 transition-all text-slate-600 dark:text-zinc-400 font-medium flex flex-col gap-1 cursor-pointer"
                  >
                    <span className="line-clamp-2">{item.query}</span>
                    <span className="text-[9px] text-slate-400 dark:text-zinc-500 font-normal">
                      {new Date(item.timestamp).toLocaleTimeString([], {
                        hour: '2-digit',
                        minute: '2-digit',
                      })}
                    </span>
                  </button>
                ))
              )}
            </div>
          </div>
        </div>

        {/* Right Main Question Input & Output Area */}
        <div className="lg:col-span-3 space-y-6">
          {/* Question Form */}
          <form
            onSubmit={handleQuerySubmit}
            className="relative bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800/80 rounded-2xl p-4 shadow-sm"
          >
            <div className="flex items-center gap-3">
              <MessageSquare className="h-5 w-5 text-slate-400 dark:text-zinc-500 shrink-0" />
              <input
                ref={queryInputRef}
                type="text"
                placeholder="Ask an academic question (e.g., 'What is standard cell library characterization?')..."
                value={question}
                onChange={(e) => setQuestion(e.target.value)}
                disabled={isQuerying}
                className="flex-1 bg-transparent text-sm text-slate-900 dark:text-zinc-100 outline-none placeholder-slate-400 dark:placeholder-zinc-500"
              />
              <div className="hidden md:flex items-center gap-1 bg-slate-100 dark:bg-zinc-800/80 text-[10px] text-slate-400 dark:text-zinc-500 font-bold px-1.5 py-0.5 rounded border border-slate-200 dark:border-zinc-700/60 shrink-0 select-none">
                <kbd>Ctrl</kbd>+<kbd>K</kbd>
              </div>
              <button
                type="submit"
                disabled={!question.trim() || isQuerying}
                className={`
                  p-2.5 rounded-xl cursor-pointer transition-all shrink-0 active:scale-95
                  ${
                    question.trim() && !isQuerying
                      ? 'bg-purple-600 hover:bg-purple-700 text-white shadow-md shadow-purple-500/20'
                      : 'bg-slate-150 dark:bg-zinc-850 text-slate-400 dark:text-zinc-600 cursor-not-allowed'
                  }
                `}
                aria-label="Send Query"
              >
                {isQuerying ? (
                  <Loader2 className="h-4 w-4 animate-spin" />
                ) : (
                  <Send className="h-4 w-4" />
                )}
              </button>
            </div>
          </form>

          {/* Processing Visualizer Steps */}
          {isQuerying && (
            <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800/80 rounded-2xl p-6 shadow-sm space-y-5 animate-pulse">
              <div className="flex items-center justify-between">
                <span className="text-xs font-bold text-slate-700 dark:text-zinc-300">
                  Retrieving and generating verified responses...
                </span>
                <Loader2 className="h-4 w-4 animate-spin text-purple-600 dark:text-purple-400" />
              </div>

              <div className="space-y-3">
                {pipelineSteps.map((step, idx) => {
                  const isFinished = queryPipelineStep > idx
                  const isActive = queryPipelineStep === idx

                  return (
                    <div
                      key={step.label}
                      className={`
                        flex items-start gap-3.5 p-3 rounded-xl border text-xs transition-all duration-300
                        ${
                          isFinished
                            ? 'bg-emerald-50/40 dark:bg-emerald-950/10 border-emerald-250 dark:border-emerald-900/40 text-emerald-850 dark:text-emerald-400'
                            : isActive
                              ? 'bg-purple-50/50 dark:bg-purple-950/10 border-purple-250 dark:border-purple-900/40 text-purple-800 dark:text-purple-400 font-semibold'
                              : 'bg-slate-50/20 dark:bg-zinc-900/20 border-slate-150 dark:border-zinc-850 text-slate-400 dark:text-zinc-500'
                        }
                      `}
                    >
                      <span className="shrink-0 flex items-center justify-center h-5 w-5 rounded-full border border-current font-bold text-[10px]">
                        {idx + 1}
                      </span>
                      <div className="space-y-0.5">
                        <p className="font-bold">{step.label}</p>
                        <p className="text-[10px] opacity-80 leading-relaxed">{step.desc}</p>
                      </div>
                    </div>
                  )
                })}
              </div>
            </div>
          )}

          {/* Query Error State */}
          {queryMutation.isError && (
            <ErrorPanel
              title="Execution Failure"
              message={queryMutation.error.message || 'An error occurred during query evaluation.'}
              onRetry={() =>
                queryMutation.mutate({
                  query_text: question,
                  similarity_threshold: similarityThreshold,
                  limit: retrievalLimit,
                })
              }
            />
          )}

          {/* Compiled Output response view */}
          {activeResponse && activeItem && (
            <div className="space-y-6 animate-in fade-in slide-in-from-bottom duration-300">
              {/* Answer Box */}
              <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800/80 rounded-2xl p-6 shadow-sm space-y-4">
                <div className="flex items-center justify-between border-b border-slate-100 dark:border-zinc-850 pb-3">
                  <h3 className="text-sm font-bold text-slate-800 dark:text-zinc-200 flex items-center gap-2">
                    <FileText className="h-4.5 w-4.5 text-purple-600 dark:text-purple-400" />
                    Verified Answer
                  </h3>
                  <button
                    onClick={handleCopy}
                    className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-50 hover:bg-slate-100 dark:bg-zinc-850 dark:hover:bg-zinc-800 text-slate-600 dark:text-zinc-300 rounded-lg text-xs font-semibold cursor-pointer transition-colors border border-slate-200 dark:border-zinc-700/60 active:scale-95"
                  >
                    {copied ? (
                      <Check className="h-3.5 w-3.5 text-emerald-500" />
                    ) : (
                      <Copy className="h-3.5 w-3.5" />
                    )}
                    {copied ? 'Copied' : 'Copy Answer'}
                  </button>
                </div>

                <div className="text-sm text-slate-800 dark:text-zinc-200 leading-relaxed font-normal whitespace-pre-wrap">
                  {renderAnswerWithClickableCitations(activeItem.answer_text)}
                </div>
              </div>

              {/* Citations list */}
              {activeItem.supporting_citations.length > 0 && (
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <h3 className="text-xs font-bold text-slate-800 dark:text-zinc-400 uppercase tracking-wider flex items-center gap-2">
                      <Bookmark className="h-4 w-4" />
                      Supporting Evidence Citations
                    </h3>
                    <button
                      onClick={handleCopyCitations}
                      className="flex items-center gap-1 px-2.5 py-1 bg-slate-50 hover:bg-slate-100 dark:bg-zinc-850 dark:hover:bg-zinc-800 text-slate-550 dark:text-zinc-300 rounded-lg text-[10px] font-bold cursor-pointer transition-colors border border-slate-200 dark:border-zinc-700/60 active:scale-95 shrink-0"
                    >
                      {citationsCopied ? (
                        <Check className="h-3 w-3 text-emerald-500" />
                      ) : (
                        <Copy className="h-3 w-3" />
                      )}
                      {citationsCopied ? 'Copied Citations' : 'Copy Citations'}
                    </button>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4">
                    {activeItem.supporting_citations.map((citation, idx) => (
                      <button
                        key={citation.citation_id || idx}
                        onClick={() => scrollToAndHighlightExcerpt(idx)}
                        className={`
                          p-4 rounded-xl border text-left cursor-pointer transition-all flex flex-col justify-between
                          ${
                            activeExcerptIdx === idx
                              ? 'bg-purple-50/60 dark:bg-purple-950/15 border-purple-300 dark:border-purple-900 shadow-sm'
                              : 'bg-white dark:bg-zinc-900 border-slate-200 dark:border-zinc-800 hover:border-slate-350 dark:hover:border-zinc-700'
                          }
                        `}
                      >
                        <div>
                          <div className="flex items-center justify-between gap-2 mb-2">
                            <span className="text-[10px] uppercase font-bold text-slate-400 dark:text-zinc-500">
                              Citation #{idx + 1}
                            </span>
                            <span className="text-[10px] font-semibold text-emerald-600 bg-emerald-50 dark:bg-emerald-950/20 px-2 py-0.5 rounded-full">
                              Score:{' '}
                              {citation.similarity_score !== null
                                ? (citation.similarity_score * 100).toFixed(0)
                                : '0'}
                              %
                            </span>
                          </div>
                          <h4 className="text-xs font-bold text-slate-900 dark:text-zinc-100 line-clamp-1">
                            {citation.book_title}
                          </h4>
                        </div>
                        <div className="flex items-center justify-between text-[10px] mt-4 pt-2 border-t border-slate-100 dark:border-zinc-850 text-slate-500 dark:text-zinc-400">
                          <span>Page {citation.page_number}</span>
                          <span>Rank #{citation.retrieval_rank || idx + 1}</span>
                        </div>
                      </button>
                    ))}
                  </div>
                </div>
              )}

              {/* Retrieved Evidence Chunks Panel */}
              {activeItem.supporting_citations.length > 0 && (
                <div className="space-y-4">
                  <h3 className="text-xs font-bold text-slate-800 dark:text-zinc-400 uppercase tracking-wider flex items-center gap-2">
                    <Layers className="h-4 w-4 text-purple-600 dark:text-purple-400" />
                    Retrieved Evidence Chunks
                  </h3>
                  <div className="space-y-4">
                    {activeItem.supporting_citations.map((citation, idx) => {
                      const excerpt = activeItem.supporting_excerpts[idx] || ''
                      const isFocused = activeExcerptIdx === idx
                      return (
                        <div
                          key={citation.citation_id || idx}
                          id={`evidence-card-${idx}`}
                          className={`
                            p-5 bg-white dark:bg-zinc-900 border rounded-2xl shadow-sm transition-all duration-300 space-y-3
                            ${
                              isFocused
                                ? 'bg-purple-50/25 dark:bg-purple-950/10 border-purple-400 dark:border-purple-900 ring-2 ring-purple-500/20'
                                : 'border-slate-250 dark:border-zinc-800/80 hover:border-slate-350 dark:hover:border-zinc-700'
                            }
                          `}
                        >
                          <div className="flex items-center justify-between flex-wrap gap-2 border-b border-slate-100 dark:border-zinc-850 pb-2.5">
                            <div className="flex items-center gap-2.5">
                              <span className="h-5 w-5 rounded-full bg-purple-100 dark:bg-purple-950/60 text-purple-700 dark:text-purple-400 flex items-center justify-center font-bold text-[10px]">
                                {idx + 1}
                              </span>
                              <h4 className="text-xs font-bold text-slate-900 dark:text-zinc-150 max-w-[200px] sm:max-w-md truncate">
                                {citation.book_title}
                              </h4>
                            </div>
                            <div className="flex items-center gap-2">
                              <span className="text-[10px] font-semibold text-emerald-650 bg-emerald-50 dark:bg-emerald-950/20 px-2 py-0.5 rounded-full">
                                Similarity:{' '}
                                {citation.similarity_score !== null
                                  ? (citation.similarity_score * 100).toFixed(0)
                                  : '0'}
                                %
                              </span>
                              <span className="text-[10px] font-semibold text-slate-550 bg-slate-100 dark:bg-zinc-850 px-2 py-0.5 rounded-full">
                                Page {citation.page_number}
                              </span>
                            </div>
                          </div>
                          <div className="p-4 bg-slate-50/50 dark:bg-zinc-950 border border-slate-150/70 dark:border-zinc-850 rounded-xl text-xs text-slate-700 dark:text-zinc-300 leading-relaxed font-mono whitespace-pre-wrap max-h-52 overflow-y-auto">
                            {excerpt}
                          </div>
                          <div className="flex justify-between items-center text-[10px] text-slate-400 dark:text-zinc-550">
                            <span>Rank: #{citation.retrieval_rank || idx + 1}</span>
                            <button
                              onClick={() => {
                                navigator.clipboard.writeText(excerpt)
                                toast.success('Excerpt copied to clipboard!')
                              }}
                              className="flex items-center gap-1 hover:text-purple-600 dark:hover:text-purple-400 cursor-pointer font-semibold"
                            >
                              <Copy className="h-3 w-3" />
                              Copy Excerpt
                            </button>
                          </div>
                        </div>
                      )
                    })}
                  </div>
                </div>
              )}

              {/* Execution statistics */}
              <div className="bg-white dark:bg-zinc-900 border border-slate-200 dark:border-zinc-800/80 rounded-2xl p-6 shadow-sm">
                <h3 className="text-xs font-bold text-slate-800 dark:text-zinc-400 uppercase tracking-wider border-b border-slate-150 dark:border-zinc-850 pb-2 mb-4 flex items-center gap-2">
                  <Cpu className="h-4.5 w-4.5 text-slate-400" />
                  RAG Execution Diagnostics
                </h3>

                <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-xs">
                  <div>
                    <span className="text-slate-400 dark:text-zinc-500 block">
                      Processing Duration
                    </span>
                    <span className="font-bold text-slate-900 dark:text-zinc-100">
                      {activeResponse.statistics?.processing_duration
                        ? `${(activeResponse.statistics.processing_duration * 1000).toFixed(0)} ms`
                        : 'N/A'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 dark:text-zinc-500 block">
                      Total Retrieved Chunks
                    </span>
                    <span className="font-bold text-slate-900 dark:text-zinc-100">
                      {activeItem.supporting_citations.length}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 dark:text-zinc-500 block">Embedding Model</span>
                    <span className="font-bold text-slate-900 dark:text-zinc-100 truncate block max-w-xs">
                      {activeResponse.metadata?.model || 'SentenceTransformer'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 dark:text-zinc-500 block">
                      Generation Source
                    </span>
                    <span
                      className={`font-bold block truncate max-w-xs ${
                        activeResponse.metadata?.generation_source === 'Gemini'
                          ? 'text-purple-600 dark:text-purple-400'
                          : 'text-amber-600 dark:text-amber-500'
                      }`}
                    >
                      {activeResponse.metadata?.generation_source || 'Gemini'}
                    </span>
                  </div>
                  <div>
                    <span className="text-slate-400 dark:text-zinc-500 block">
                      Verification Timestamp
                    </span>
                    <span className="font-bold text-slate-900 dark:text-zinc-100">
                      {new Date(activeItem.verification_timestamp).toLocaleTimeString()}
                    </span>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Ask Workspace Empty State */}
          {!activeResponse && !isQuerying && (
            <div className="py-12">
              <EmptyState
                title="Query Workspace Ready"
                description="Ask an academic question above to search across the knowledge index. The pipeline will retrieve evidence, compile a prompt, generate an answer, and verify citations."
                icon={MessageSquare}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
