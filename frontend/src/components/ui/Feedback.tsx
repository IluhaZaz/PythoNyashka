import type { ReactNode } from 'react'
import { cn } from '@/lib/cn'

export function Skeleton({ className }: { className?: string }) {
  return <div className={cn('skeleton', className)} />
}

export function EmptyState({
  emoji,
  title,
  text,
  action,
  className,
}: {
  emoji: string
  title: string
  text: string
  action?: ReactNode
  className?: string
}) {
  return (
    <div className={cn('card flex flex-col items-center gap-3 px-6 py-12 text-center', className)}>
      <span className="animate-wiggle text-5xl">{emoji}</span>
      <h3 className="text-xl">{title}</h3>
      <p className="max-w-sm text-sm text-sub">{text}</p>
      {action && <div className="mt-2 flex flex-wrap justify-center gap-2">{action}</div>}
    </div>
  )
}

export function ErrorState({
  message,
  onRetry,
  className,
}: {
  message: string
  onRetry?: () => void
  className?: string
}) {
  return (
    <div className={cn('card border-coral/40 bg-coral-soft/50 px-5 py-6', className)}>
      <p className="font-display text-sm font-bold text-coral-deep">Что-то пошло не так</p>
      <p className="mt-1 text-sm text-ink/80">{message}</p>
      {onRetry && (
        <button type="button" className="btn btn-ghost btn-sm mt-3" onClick={onRetry}>
          Попробовать снова
        </button>
      )}
    </div>
  )
}

export function SectionTitle({
  eyebrow,
  title,
  action,
}: {
  eyebrow?: string
  title: string
  action?: ReactNode
}) {
  return (
    <div className="mb-4 flex flex-wrap items-end justify-between gap-3">
      <div>
        {eyebrow && <p className="panel-title mb-1">{eyebrow}</p>}
        <h1 className="text-2xl sm:text-3xl">{title}</h1>
      </div>
      {action}
    </div>
  )
}
