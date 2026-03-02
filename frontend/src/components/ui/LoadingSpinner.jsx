const LoadingSpinner = ({ 
  size = 'md', 
  className = '',
  text,
  fullScreen = false,
}) => {
  const sizes = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12',
    xl: 'w-16 h-16',
  }
  
  const spinner = (
    <div className={`flex flex-col items-center justify-center gap-3 ${className}`}>
      <div className="relative">
        <div className={`${sizes[size]} border-4 border-gray-200 rounded-full`}></div>
        <div 
          className={`${sizes[size]} border-4 border-primary-600 border-t-transparent rounded-full animate-spin absolute top-0 left-0`}
          role="status"
          aria-label="Loading"
        ></div>
      </div>
      {text && (
        <p className="text-sm text-gray-600 font-medium animate-pulse">
          {text}
        </p>
      )}
    </div>
  )
  
  if (fullScreen) {
    return (
      <div className="fixed inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center z-50">
        {spinner}
      </div>
    )
  }
  
  return spinner
}

export default LoadingSpinner