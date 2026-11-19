import { createContext, useCallback, useContext, useMemo, useRef, useState } from 'react'
import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'

export type ToastTone = 'coral' | 'mint' | 'sun' | 'sky'

export interface ToastAction {
  label: string
  onClick: () => void
}

export interface Toast {
  id: number
  tone: ToastTone
  title: string
  text?: string
  emoji?: string
  action?: ToastAction
}

interface ToastContextValue {
  push(toast: Omit<Toast, 'id'>): number
  dismiss(id: number): void
}

const ToastContext = createContext<ToastContextValue | null>(null)

const TONE_STYLES: Record<ToastTone, string> = {
  coral: 'border-coral/40 bg-coral-soft',
  mint: 'border-mint/40 bg-mint-soft',
  sun: 'border-sun/50 bg-sun-soft',
  sky: 'border-sky/40 bg-sky-soft',
}

const TONE_TEXT: Record<ToastTone, string> = {
  coral: 'text-coral-deep',
  mint: 'text-mint-deep',
  sun: 'text-sun-deep',
  sky: 'text-sky-deep',
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toasts, setToasts] = useState<Toast[]>([])
  const nextId = useRef(1)
  const timers = useRef(new Map<number, number>())

  const dismiss = useCallback((id: number) => {
    setToasts((list) => list.filter((toast) => toast.id !== id))
    const timer = timers.current.get(id)
    if (timer) {
      window.clearTimeout(timer)
      timers.current.delete(id)
    }
  }, [])

  const push = useCallback(
    (toast: Omit<Toast, 'id'>) => {
      const id = nextId.current++
      setToasts((list) => [...list.slice(-3), { ...toast, id }])
      timers.current.set(
        id,
        window.setTimeout(() => dismiss(id), toast.action ? 7000 : 4200),
      )
      return id
    },
    [dismiss],
  )

  const value = useMemo(() => ({ push, dismiss }), [push, dismiss])

  return (
    <ToastContext.Provider value={value}>
      {children}
      <div className="pointer-events-none fixed inset-x-3 bottom-3 z-[80] flex flex-col items-center gap-2 sm:inset-x-auto sm:right-6 sm:bottom-6 sm:items-end">
        {toasts.map((toast) => (
          <div
            key={toast.id}
            role="status"
            className={cn(
              'pointer-events-auto animate-rise flex w-full max-w-sm items-start gap-3 rounded-3xl border px-4 py-3 shadow-[var(--shadow-lift)] backdrop-blur-sm',
              TONE_STYLES[toast.tone],
            )}
          >
            {toast.emoji && <span className="text-xl leading-none">{toast.emoji}</span>}
            <div className="min-w-0 flex-1">
              <p className={cn('font-display text-[13px] font-bold', TONE_TEXT[toast.tone])}>
                {toast.title}
              </p>
              {toast.text && <p className="mt-0.5 text-[13px] text-ink/80">{toast.text}</p>}
              {toast.action && (
                <button
                  type="button"
                  className={cn('mt-1.5 text-[13px] font-extrabold underline', TONE_TEXT[toast.tone])}
                  onClick={() => {
                    toast.action?.onClick()
                    dismiss(toast.id)
                  }}
                >
                  {toast.action.label}
                </button>
              )}
            </div>
            <button
              type="button"
              aria-label="Закрыть уведомление"
              className="-mt-1 -mr-1 grid h-8 w-8 shrink-0 place-items-center rounded-full text-lg leading-none text-sub transition hover:bg-ink/8 hover:text-ink"
              onClick={() => dismiss(toast.id)}
            >
              ×
            </button>
          </div>
        ))}
      </div>
    </ToastContext.Provider>
  )
}

export function useToast(): ToastContextValue {
  const context = useContext(ToastContext)
  if (!context) throw new Error('useToast должен вызываться внутри ToastProvider')
  return context
}
