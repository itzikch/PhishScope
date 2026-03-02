import { AlertCircle, CheckCircle, Info, XCircle, X } from 'lucide-react'

const variants = {
  info: {
    container: 'bg-blue-50 border-blue-200 text-blue-900',
    icon: 'text-blue-600',
    IconComponent: Info,
  },
  success: {
    container: 'bg-green-50 border-green-200 text-green-900',
    icon: 'text-green-600',
    IconComponent: CheckCircle,
  },
  warning: {
    container: 'bg-yellow-50 border-yellow-200 text-yellow-900',
    icon: 'text-yellow-600',
    IconComponent: AlertCircle,
  },
  error: {
    container: 'bg-red-50 border-red-200 text-red-900',
    icon: 'text-red-600',
    IconComponent: XCircle,
  },
}

const Alert = ({ 
  children, 
  variant = 'info',
  title,
  onClose,
  className = '',
  ...props 
}) => {
  const { container, icon, IconComponent } = variants[variant]
  
  return (
    <div
      role="alert"
      className={`relative flex gap-3 p-4 rounded-lg border ${container} ${className}`}
      {...props}
    >
      <IconComponent className={`flex-shrink-0 w-5 h-5 ${icon}`} aria-hidden="true" />
      <div className="flex-1 min-w-0">
        {title && (
          <h4 className="font-semibold mb-1">
            {title}
          </h4>
        )}
        <div className="text-sm">
          {children}
        </div>
      </div>
      {onClose && (
        <button
          onClick={onClose}
          className="flex-shrink-0 p-1 rounded-md hover:bg-black/5 transition-colors"
          aria-label="Close alert"
        >
          <X className="w-4 h-4" />
        </button>
      )}
    </div>
  )
}

export default Alert