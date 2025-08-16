import { useToast } from "@/hooks/use-toast"
import {
  Toast,
  ToastClose,
  ToastDescription,
  ToastProvider,
  ToastTitle,
  ToastViewport,
} from "@/components/ui/toast"
import { useEffect, useState } from "react"

export function Toaster() {
  const { toasts } = useToast()

  return (
    <ToastProvider>
      {toasts.map(function ({ id, title, description, action, duration, ...props }) {
        return (
          <ToastWithProgress 
            key={id} 
            id={id}
            title={title}
            description={description}
            action={action}
            duration={duration || (props.variant === 'destructive' ? 4000 : 2000)}
            {...props}
          />
        )
      })}
      <ToastViewport />
    </ToastProvider>
  )
}

function ToastWithProgress({ 
  id, 
  title, 
  description, 
  action, 
  duration,
  ...props 
}: any) {
  const [progress, setProgress] = useState(100)

  useEffect(() => {
    if (duration === Infinity || duration === 0) return

    const startTime = Date.now()
    const interval = setInterval(() => {
      const elapsed = Date.now() - startTime
      const remaining = Math.max(0, (duration - elapsed) / duration * 100)
      setProgress(remaining)
      
      if (remaining <= 0) {
        clearInterval(interval)
      }
    }, 50) // Update every 50ms for smooth animation

    return () => clearInterval(interval)
  }, [duration])

  return (
    <Toast {...props}>
      <div className="grid gap-1 flex-1">
        {title && <ToastTitle>{title}</ToastTitle>}
        {description && (
          <ToastDescription>{description}</ToastDescription>
        )}
        {/* Progress bar */}
        {duration !== Infinity && duration !== 0 && (
          <div className="w-full bg-muted/20 rounded-full h-1 mt-2 overflow-hidden">
            <div 
              className="bg-primary/40 h-1 rounded-full transition-all duration-75 ease-linear"
              style={{ width: `${progress}%` }}
            />
          </div>
        )}
      </div>
      {action}
      <ToastClose />
    </Toast>
  )
}
