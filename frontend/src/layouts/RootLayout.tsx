import { useEffect, useState } from 'react'
import { NavLink, Outlet, useLocation } from 'react-router-dom'
import {
  LayoutDashboard,
  BookOpen,
  MessageSquare,
  Settings as SettingsIcon,
  Activity,
  Sun,
  Moon,
  Menu,
  X,
  Server,
} from 'lucide-react'
import { StatusService } from '../shared/services/api'
import { Toaster } from 'sonner'

export default function RootLayout() {
  const [darkMode, setDarkMode] = useState<boolean>(() => {
    return (
      localStorage.getItem('theme') === 'dark' ||
      (!localStorage.getItem('theme') && window.matchMedia('(prefers-color-scheme: dark)').matches)
    )
  })

  const [isSidebarOpen, setIsSidebarOpen] = useState(false)
  const [isSystemHealthy, setIsSystemHealthy] = useState<boolean | null>(null)
  const location = useLocation()

  // Handle Theme
  useEffect(() => {
    const root = window.document.documentElement
    if (darkMode) {
      root.classList.add('dark')
      localStorage.setItem('theme', 'dark')
    } else {
      root.classList.remove('dark')
      localStorage.setItem('theme', 'light')
    }
  }, [darkMode])

  // Check Health Periodically
  useEffect(() => {
    const checkHealth = async () => {
      const healthy = await StatusService.getHealth()
      setIsSystemHealthy(healthy)
    }

    checkHealth()
    const interval = setInterval(checkHealth, 10000) // check every 10 seconds
    return () => clearInterval(interval)
  }, [])

  // Close sidebar on navigation (mobile)
  useEffect(() => {
    setIsSidebarOpen(false)
  }, [location.pathname])

  const navItems = [
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/library', label: 'Library', icon: BookOpen },
    { to: '/queries', label: 'Ask Questions', icon: MessageSquare },
    { to: '/status', label: 'System Status', icon: Activity },
    { to: '/settings', label: 'Settings', icon: SettingsIcon },
  ]

  return (
    <div className="min-h-screen bg-slate-50 dark:bg-zinc-950 text-slate-900 dark:text-zinc-100 flex flex-col md:flex-row transition-colors duration-200">
      <Toaster position="top-right" richColors />

      {/* Mobile Header */}
      <header className="md:hidden flex items-center justify-between px-6 py-4 bg-white/70 dark:bg-zinc-900/70 backdrop-blur-md border-b border-slate-200 dark:border-zinc-800 sticky top-0 z-30">
        <div className="flex items-center gap-2">
          <Server className="h-6 w-6 text-purple-600 dark:text-purple-400" />
          <span className="font-bold text-lg bg-gradient-to-r from-purple-600 to-indigo-600 dark:from-purple-400 dark:to-indigo-400 bg-clip-text text-transparent">
            Libris
          </span>
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={() => setDarkMode(!darkMode)}
            className="p-2 rounded-lg text-slate-500 hover:text-slate-900 dark:text-zinc-400 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-zinc-800 transition-colors"
            aria-label="Toggle Dark Mode"
          >
            {darkMode ? <Sun className="h-5 w-5" /> : <Moon className="h-5 w-5" />}
          </button>
          <button
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            className="p-2 rounded-lg text-slate-500 hover:text-slate-900 dark:text-zinc-400 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-zinc-800 transition-colors"
            aria-label="Toggle Sidebar"
          >
            {isSidebarOpen ? <X className="h-6 w-6" /> : <Menu className="h-6 w-6" />}
          </button>
        </div>
      </header>

      {/* Sidebar - Desktop and Mobile Drawer */}
      <aside
        className={`
        fixed inset-y-0 left-0 z-40 w-64 bg-white/80 dark:bg-zinc-900/80 backdrop-blur-lg border-r border-slate-200 dark:border-zinc-800 flex flex-col justify-between p-6 transform transition-transform duration-300 ease-in-out md:translate-x-0 md:static md:h-screen
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full'}
      `}
      >
        <div className="flex flex-col gap-8">
          {/* Logo */}
          <div className="hidden md:flex items-center gap-2.5 px-2">
            <Server className="h-7 w-7 text-purple-600 dark:text-purple-400" />
            <span className="font-extrabold text-xl bg-gradient-to-r from-purple-600 to-indigo-600 dark:from-purple-400 dark:to-indigo-400 bg-clip-text text-transparent">
              Libris
            </span>
          </div>

          {/* Navigation Links */}
          <nav className="flex flex-col gap-1.5">
            {navItems.map((item) => {
              const Icon = item.icon
              return (
                <NavLink
                  key={item.to}
                  to={item.to}
                  className={({ isActive }) => `
                    flex items-center gap-3 px-4 py-3 rounded-xl font-medium text-sm transition-all duration-200 group
                    ${
                      isActive
                        ? 'bg-purple-600 text-white shadow-lg shadow-purple-500/25 dark:shadow-purple-500/10'
                        : 'text-slate-600 hover:text-slate-900 dark:text-zinc-400 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-zinc-800/60'
                    }
                  `}
                >
                  <Icon className="h-4.5 w-4.5 shrink-0" />
                  {item.label}
                </NavLink>
              )
            })}
          </nav>
        </div>

        {/* Sidebar Footer */}
        <div className="flex flex-col gap-4 border-t border-slate-100 dark:border-zinc-800/80 pt-6">
          {/* Health status */}
          <div className="flex items-center justify-between px-2 text-xs">
            <span className="text-slate-500 dark:text-zinc-500 font-medium">Server Health:</span>
            <div className="flex items-center gap-1.5">
              <span
                className={`h-2 w-2 rounded-full ${
                  isSystemHealthy === null
                    ? 'bg-amber-400 animate-pulse'
                    : isSystemHealthy
                      ? 'bg-emerald-500'
                      : 'bg-rose-500'
                }`}
              />
              <span
                className={`font-semibold capitalize ${
                  isSystemHealthy === null
                    ? 'text-amber-500'
                    : isSystemHealthy
                      ? 'text-emerald-600 dark:text-emerald-500'
                      : 'text-rose-600 dark:text-rose-500'
                }`}
              >
                {isSystemHealthy === null ? 'checking' : isSystemHealthy ? 'healthy' : 'offline'}
              </span>
            </div>
          </div>

          {/* Theme Selector (Desktop only, mobile has it in header) */}
          <div className="hidden md:flex items-center justify-between px-2">
            <span className="text-slate-500 dark:text-zinc-500 text-xs font-medium">
              Appearance:
            </span>
            <button
              onClick={() => setDarkMode(!darkMode)}
              className="flex items-center gap-1.5 p-1 bg-slate-100 dark:bg-zinc-800 rounded-lg border border-slate-200 dark:border-zinc-700/80 cursor-pointer"
            >
              <span
                className={`p-1 rounded ${!darkMode ? 'bg-white shadow-xs text-amber-500' : 'text-slate-400'}`}
              >
                <Sun className="h-3.5 w-3.5" />
              </span>
              <span
                className={`p-1 rounded ${darkMode ? 'bg-zinc-700 shadow-xs text-indigo-400' : 'text-slate-400'}`}
              >
                <Moon className="h-3.5 w-3.5" />
              </span>
            </button>
          </div>
        </div>
      </aside>

      {/* Overlay for mobile sidebar */}
      {isSidebarOpen && (
        <div
          onClick={() => setIsSidebarOpen(false)}
          className="fixed inset-0 bg-slate-900/40 dark:bg-black/60 backdrop-blur-xs z-30 md:hidden"
        />
      )}

      {/* Main Content Area */}
      <main className="flex-1 flex flex-col min-w-0 md:h-screen overflow-y-auto">
        <div className="flex-1 p-6 md:p-8 max-w-7xl w-full mx-auto">
          <Outlet />
        </div>
      </main>
    </div>
  )
}
