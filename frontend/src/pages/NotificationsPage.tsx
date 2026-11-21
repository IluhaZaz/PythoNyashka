import { useState } from 'react'
import { ApiError } from '@/api'
import { useMarkRead, useNotifications } from '@/api/hooks'
import { cn } from '@/lib/cn'
import { plural, timeAgo } from '@/lib/format'
import { useToast } from '@/state/toast'
import { Button } from '@/components/ui/Button'
import { EmptyState, ErrorState, SectionTitle, Skeleton } from '@/components/ui/Feedback'
import { Segmented } from '@/components/ui/Field'
import { Icon, type IconName } from '@/components/ui/Icon'

type Tab = 'all' | 'unread'

function iconFor(text: string): { icon: IconName; tone: string } {
  const lower = text.toLowerCase()
  if (lower.includes('мэтч') || lower.includes('взаимно'))
    return { icon: 'heart-fill', tone: 'bg-coral-soft text-coral-deep' }
  if (lower.includes('лайк')) return { icon: 'star', tone: 'bg-sun-soft text-sun-deep' }
  if (lower.includes('чат') || lower.includes('ответил'))
    return { icon: 'chat', tone: 'bg-sky-soft text-sky-deep' }
  return { icon: 'spark', tone: 'bg-mint-soft text-mint-deep' }
}

export function NotificationsPage() {
  const { data, isLoading, error, refetch } = useNotifications(50)
  const markRead = useMarkRead()
  const { push } = useToast()
  const [tab, setTab] = useState<Tab>('all')

  const list = data ?? []
  const unread = list.filter((item) => !item.is_read)
  const shown = tab === 'unread' ? unread : list

  const markAll = async () => {
    if (unread.length === 0) return
    try {
      await Promise.all(unread.map((item) => markRead.mutateAsync(item.id)))
      push({ tone: 'mint', emoji: '🧹', title: 'Все прочитаны' })
    } catch {
      push({ tone: 'coral', title: 'Часть уведомлений не обновилась' })
    }
  }

  return (
    <div className="mx-auto max-w-3xl">
      <SectionTitle
        eyebrow="события"
        title="Уведомления"
        action={
          <div className="flex flex-wrap items-center gap-2">
            <Segmented<Tab>
              value={tab}
              onChange={setTab}
              options={[
                { value: 'all', label: 'Все', count: list.length },
                { value: 'unread', label: 'Новые', count: unread.length },
              ]}
            />
            <Button
              variant="ghost"
              size="sm"
              icon="check"
              disabled={unread.length === 0 || markRead.isPending}
              onClick={() => void markAll()}
            >
              Прочитать все
            </Button>
          </div>
        }
      />

      {isLoading && (
        <div className="space-y-3">
          {[0, 1, 2, 3].map((index) => (
            <Skeleton key={index} className="h-20 w-full rounded-3xl" />
          ))}
        </div>
      )}

      {error && (
        <ErrorState
          message={error instanceof ApiError ? error.message : 'Уведомления недоступны'}
          onRetry={() => void refetch()}
        />
      )}

      {!isLoading && !error && shown.length === 0 && (
        <EmptyState
          emoji={tab === 'unread' ? '✅' : '🔔'}
          title={tab === 'unread' ? 'Новых нет' : 'Пока тихо'}
          text="Здесь появятся лайки, мэтчи и ответы в чатах. Мы обязательно пинганём."
        />
      )}

      <div className="space-y-2.5">
        {shown.map((item) => {
          const visual = iconFor(item.text)
          return (
            <button
              key={item.id}
              type="button"
              onClick={() => !item.is_read && markRead.mutate(item.id)}
              className={cn(
                'card flex w-full items-start gap-3.5 p-4 text-left transition hover:-translate-y-0.5',
                !item.is_read && 'border-coral/40 bg-coral-soft/35',
              )}
            >
              <span className={cn('grid h-10 w-10 shrink-0 place-items-center rounded-2xl', visual.tone)}>
                <Icon name={visual.icon} size={18} />
              </span>
              <span className="min-w-0 flex-1">
                <span className="block text-[14px] leading-relaxed text-ink/90">{item.text}</span>
                <span className="mt-1 block font-mono text-[11px] text-dim">
                  {timeAgo(item.created_at)}
                  {!item.is_read && <span className="ml-2 text-coral-deep">· новое</span>}
                </span>
              </span>
              {!item.is_read && <span className="mt-1 h-2.5 w-2.5 shrink-0 rounded-full bg-coral" />}
            </button>
          )
        })}
      </div>

      {list.length > 0 && (
        <p className="hint mt-5 text-center">
          {list.length} {plural(list.length, 'событие', 'события', 'событий')} · непрочитанных:{' '}
          {unread.length}
        </p>
      )}
    </div>
  )
}
