import { Routes, Route, Link, useLocation } from 'react-router-dom'
import { Shield, BarChart3, Github, Users } from 'lucide-react'
import { Toaster } from 'sonner'
import AnalysisPage from './pages/AnalysisPage'
import DashboardPage from './pages/DashboardPage'
import DebateAnalysisPage from './pages/DebateAnalysisPage'
import { ThemeToggle } from './components/ThemeToggle'

function App() {
  const location = useLocation()

  const isActive = (path) => location.pathname === path

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-dark-bg bg-gradient-mesh animate-fade-in transition-colors duration-300">
      <Toaster position="top-right" richColors />
      {/* Header */}
      <header className="sticky top-0 z-40 bg-white/70 dark:bg-dark-card/70 backdrop-blur-xl border-b border-white/20 dark:border-dark-border/20 shadow-sm relative transition-colors duration-300">
        <nav className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8" aria-label="Main navigation">
          <div className="flex justify-between items-center h-20">
            {/* Logo */}
            <Link
              to="/"
              className="flex items-center gap-3 group"
              aria-label="PhishScope home"
            >
              <div className="relative">
                <div className="absolute inset-0 bg-primary-500 blur-xl opacity-20 group-hover:opacity-40 transition-opacity duration-500 rounded-full" />
                <Shield className="relative w-8 h-8 text-primary-600 group-hover:scale-110 transition-transform duration-300" />
              </div>
              <div>
                <h1 className="text-2xl font-heading font-bold bg-gradient-to-r from-primary-600 to-indigo-600 bg-clip-text text-transparent">
                  PhishScope
                </h1>
                <p className="text-xs text-gray-500 font-medium tracking-wide">Evidence-Driven Analysis</p>
              </div>
            </Link>

            {/* Navigation Links */}
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-1 bg-gray-100/50 dark:bg-dark-card/50 p-1.5 rounded-xl backdrop-blur-sm border border-gray-200/50 dark:border-dark-border/50">
                <Link
                  to="/"
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${isActive('/')
                    ? 'bg-white dark:bg-dark-card text-primary-700 dark:text-primary-400 shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-200/50 dark:hover:bg-gray-700/50'
                    }`}
                  aria-current={isActive('/') ? 'page' : undefined}
                >
                  <span className="flex items-center gap-2">
                    <Shield className="w-4 h-4" aria-hidden="true" />
                    <span className="hidden sm:inline">Standard</span>
                  </span>
                </Link>

                <Link
                  to="/debate"
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${isActive('/debate')
                    ? 'bg-white dark:bg-dark-card text-primary-700 dark:text-primary-400 shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-200/50 dark:hover:bg-gray-700/50'
                    }`}
                  aria-current={isActive('/debate') ? 'page' : undefined}
                >
                  <span className="flex items-center gap-2">
                    <Users className="w-4 h-4" aria-hidden="true" />
                    <span className="hidden sm:inline">Debate</span>
                  </span>
                </Link>

                <Link
                  to="/dashboard"
                  className={`px-4 py-2 rounded-lg text-sm font-medium transition-all duration-300 ${isActive('/dashboard')
                    ? 'bg-white dark:bg-dark-card text-primary-700 dark:text-primary-400 shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200 hover:bg-gray-200/50 dark:hover:bg-gray-700/50'
                    }`}
                  aria-current={isActive('/dashboard') ? 'page' : undefined}
                >
                  <span className="flex items-center gap-2">
                    <BarChart3 className="w-4 h-4" aria-hidden="true" />
                    <span className="hidden sm:inline">Dashboard</span>
                  </span>
                </Link>
              </div>

              <a
                href="https://github.com/yourusername/phishscope"
                target="_blank"
                rel="noopener noreferrer"
                className="ml-4 p-2.5 text-gray-500 hover:text-gray-900 hover:bg-white/50 rounded-xl transition-all duration-300 border border-transparent hover:border-gray-200"
                aria-label="View on GitHub"
              >
                <Github className="w-5 h-5" aria-hidden="true" />
              </a>

              <ThemeToggle />
            </div>
          </div>
        </nav>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8 relative z-10">
        <Routes>
          <Route path="/" element={<AnalysisPage />} />
          <Route path="/debate" element={<DebateAnalysisPage />} />
          <Route path="/dashboard" element={<DashboardPage />} />
        </Routes>
      </main>

      {/* Footer */}
      <footer className="mt-auto border-t border-gray-200/50 bg-white/30 backdrop-blur-sm relative z-10">
        <div className="max-w-7xl mx-auto py-8 px-4 sm:px-6 lg:px-8">
          <div className="flex flex-col sm:flex-row justify-between items-center gap-4">
            <p className="text-sm text-gray-500">
              © 2024 PhishScope. Open source security analysis tool.
            </p>
            <div className="flex items-center gap-6 text-sm text-gray-500 font-medium">
              <a href="#" className="hover:text-primary-600 transition-colors">Documentation</a>
              <a href="#" className="hover:text-primary-600 transition-colors">API</a>
              <a href="#" className="hover:text-primary-600 transition-colors">Support</a>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}
export default App
