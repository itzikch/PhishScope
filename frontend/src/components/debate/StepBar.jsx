import { Check, Loader2 } from 'lucide-react'

/**
 * StepBar - Progress indicator for debate analysis
 * 
 * Shows 6 steps:
 * 1. Scraping
 * 2. Prosecutor Round 1
 * 3. Defense Round 1
 * 4. Prosecutor Round 2
 * 5. Defense Round 2
 * 6. Judge's Ruling
 * 
 * @param {Object} props
 * @param {number} props.currentStep - Current step (0-5)
 */
function StepBar({ currentStep = 0 }) {
  const steps = [
    { label: 'Scraping', short: 'Scrape' },
    { label: 'Prosecutor R1', short: 'P1' },
    { label: 'Defense R1', short: 'D1' },
    { label: 'Prosecutor R2', short: 'P2' },
    { label: 'Defense R2', short: 'D2' },
    { label: 'Judge', short: 'Judge' },
  ]

  return (
    <div className="w-full py-6">
      <div className="flex items-center justify-between relative">
        {/* Progress Line */}
        <div className="absolute top-5 left-0 right-0 h-0.5 bg-gray-200 dark:bg-gray-700">
          <div
            className="h-full bg-primary-500 transition-all duration-500 ease-out"
            style={{ width: `${(currentStep / (steps.length - 1)) * 100}%` }}
          />
        </div>

        {/* Steps */}
        {steps.map((step, index) => {
          const isCompleted = index < currentStep
          const isCurrent = index === currentStep
          const isPending = index > currentStep

          return (
            <div key={index} className="relative flex flex-col items-center z-10">
              {/* Circle */}
              <div
                className={`
                  w-10 h-10 rounded-full flex items-center justify-center
                  transition-all duration-300 border-2
                  ${isCompleted
                    ? 'bg-primary-500 border-primary-500 text-white'
                    : isCurrent
                    ? 'bg-white dark:bg-dark-card border-primary-500 text-primary-600'
                    : 'bg-white dark:bg-dark-card border-gray-300 dark:border-gray-600 text-gray-400'
                  }
                  ${isCurrent ? 'scale-110 shadow-lg' : ''}
                `}
              >
                {isCompleted ? (
                  <Check className="w-5 h-5" aria-hidden="true" />
                ) : isCurrent ? (
                  <Loader2 className="w-5 h-5 animate-spin" aria-hidden="true" />
                ) : (
                  <span className="text-sm font-semibold">{index + 1}</span>
                )}
              </div>

              {/* Label */}
              <div className="mt-2 text-center">
                <div
                  className={`
                    text-xs font-medium transition-colors
                    ${isCurrent
                      ? 'text-primary-600 dark:text-primary-400'
                      : isCompleted
                      ? 'text-gray-700 dark:text-gray-300'
                      : 'text-gray-400 dark:text-gray-500'
                    }
                  `}
                >
                  {/* Show full label on larger screens, short on mobile */}
                  <span className="hidden sm:inline">{step.label}</span>
                  <span className="sm:hidden">{step.short}</span>
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default StepBar

// Made with Bob
