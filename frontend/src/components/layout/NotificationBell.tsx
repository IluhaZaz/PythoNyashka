import { useEffect, useRef, useState } from 'react'
import { Link } from 'react-router-dom'
import { useMarkRead, useNotifications } from '@/api/hooks'
import { cn } from '@/lib/cn'
import { shortAgo } from '@/lib/format'
import { Icon } from '@/components/ui/Icon'
import { Spinner } from '@/components/ui/Button'

export function NotificationBell() {
  const [open, setOpen] = useState(false)
  const ref = useRef<HTMLDivElement>(null)
  const { data, isLoading } = useNotifications(8)
  const markRead = useMarkRead()

  const unread = data?.filter((item) => !item.is_read).length ?? 0

  useEffect(() => {
    if (!open) return
    const onClick = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) setOpen(false)
    }
    const onKey = (event: KeyboardEvent) => event.key === 'Escape' && setOpen(false)
    document.addEventListener('mousedown', onClick)
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('mousedown', onClick)
      document.removeEventListener('keydown', onKey)
    }
  }, [open])

  return (
    <div className="relative" ref={ref}>
      <button
        type="button"
        onClick={() => setOpen((value) => !value)}
        aria-label={`Уведомления${unread ? `, непрочитанных: ${unread}` : ''}`}
        aria-expanded={open}
        className="btn btn-ghost btn-icon relative"
      >
        <Icon name="bell" size={19} className={unread > 0 ? 'animate-ring' : undefined} />
        {unread > 0 && (
          <span className="count-badge absolute -top-1 -right-1 border-2 border-surface">{unread}</span>
        )}
      </button>

      {open && (
        <div className="card animate-rise absolute right-0 z-50 mt-2 w-[min(92vw,360px)] overflow-hidden p-0">
          <div className="flex items-center justify-between border-b border-line px-4 py-3">
            <p className="panel-title">Уведомления</p>
            <span className="mono-badge">{unread} новых</span>
          </div>

          <div className="max-h-[60vh] overflow-y-auto">
            {isLoading && (
              <div className="flex items-center gap-2 px-4 py-6 text-sub">
                <Spinner /> <span className="text-sm">Загружаем…</span>
              </div>
            )}
            {data?.length === 0 && (
              <p className="px-4 py-8 text-center text-sm text-sub">
                Пока тихо. Как кто-то лайкнет — узнаешь первой.
              </p>
            )}
            {data?.map((item) => (
              <button
                key={item.id}
                type="button"
                onClick={() => markRead.mutate(item.id)}
                className={cn(
                  'flex w-full gap-3 border-b border-line/60 px-4 py-3 text-left transition last:border-0 hover:bg-surface-2',
                  !item.is_read && 'bg-coral-soft/35',
                )}
              >
                <span
                  className={cn(
                    'mt-1.5 h-2 w-2 shrink-0 rounded-full',
                    item.is_read ? 'bg-line-strong' : 'bg-coral',
                  )}
                />
                <span className="min-w-0 flex-1">
                  <span className="block text-[13.5px] leading-snug">{item.text}</span>
                  <span className="mt-1 block font-mono text-[11px] text-dim">
                    {shortAgo(item.created_at)}
                  </span>
                </span>
              </button>
            ))}
          </div>

          <Link
            to="/notifications"
            onClick={() => setOpen(false)}
            className="block border-t border-line bg-surface-2 py-3 text-center text-[13px] font-bold text-coral-deep transition hover:bg-coral-soft"
          >
            Все уведомления
          </Link>
        </div>
      )}
    </div>
  )
}
