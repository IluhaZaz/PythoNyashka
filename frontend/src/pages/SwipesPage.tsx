import { useCallback, useEffect, useMemo, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ApiError } from '@/api'
import { DEFAULT_FILTERS, type FeedFilters, type PublicProfile } from '@/api/types'
import { useFeed, useMatchHistory, useSwipe, useUndoSwipe } from '@/api/hooks'
import { cn } from '@/lib/cn'
import { plural } from '@/lib/format'
import { readJson, writeJson } from '@/lib/storage'
import { useAuth } from '@/state/auth'
import { useToast } from '@/state/toast'
import { PersonModal } from '@/components/PersonModal'
import { FiltersPanel } from '@/components/swipe/FiltersPanel'
import { MatchOverlay } from '@/components/swipe/MatchOverlay'
import { SwipeCard } from '@/components/swipe/SwipeCard'
import { Button } from '@/components/ui/Button'
import { EmptyState, ErrorState, SectionTitle, Skeleton } from '@/components/ui/Feedback'
import { Icon } from '@/components/ui/Icon'
import { Modal } from '@/components/ui/Modal'

interface LastAction {
  id: string
  name: string
  decision: 'like' | 'dislike'
}

export function SwipesPage() {
  const { profile } = useAuth()
  const { push } = useToast()
  const navigate = useNavigate()
  const swipe = useSwipe()
  const undo = useUndoSwipe()
  const { data: matches } = useMatchHistory()

  const [filters, setFilters] = useState<FeedFilters>(() => readJson('feed-filters', DEFAULT_FILTERS))
  const [dismissed, setDismissed] = useState<string[]>([])
  const [history, setHistory] = useState<LastAction[]>([])
  const [flying, setFlying] = useState<'like' | 'dislike' | null>(null)
  const [matched, setMatched] = useState<{ person: PublicProfile; chatId: string } | null>(null)
  const [opened, setOpened] = useState<PublicProfile | null>(null)
  const [filtersOpen, setFiltersOpen] = useState(false)
  const busy = useRef(false)
  const timer = useRef<number | null>(null)

  const feed = useFeed(filters)
  const myTags = profile?.tags ?? []

  useEffect(() => writeJson('feed-filters', filters), [filters])
  useEffect(
    () => () => {
      if (timer.current) window.clearTimeout(timer.current)
    },
    [],
  )

  const visible = useMemo(
    () => (feed.data?.candidates ?? []).filter((person) => !dismissed.includes(person.id)),
    [feed.data, dismissed],
  )
  const top = visible[0] ?? null

  const decide = useCallback(
    (decision: 'like' | 'dislike') => {
      if (!top || busy.current) return
      busy.current = true
      const person = top
      setFlying(decision)
      timer.current = window.setTimeout(() => {
        setFlying(null)
        setDismissed((list) => [...list, person.id])
        setHistory((list) => [...list, { id: person.id, name: person.name, decision }])
        swipe
          .mutateAsync({ profileId: person.id, decision })
          .then((result) => {
            if (result.matched && result.chatId) {
              setMatched({ person, chatId: result.chatId })
            } else if (decision === 'like') {
              push({
                tone: 'sun',
                emoji: '💌',
                title: 'Лайк отправлен',
                text: `Ждём ответ от ${person.name}.`,
              })
            }
          })
          .catch((error: unknown) => {
            setDismissed((list) => list.filter((id) => id !== person.id))
            setHistory((list) => list.slice(0, -1))
            push({
              tone: 'coral',
              emoji: '🙈',
              title: 'Свайп не прошёл',
              text: error instanceof ApiError ? error.message : 'Попробуй ещё раз.',
            })
          })
          .finally(() => {
            busy.current = false
          })
      }, 260)
    },
    [top, swipe, push],
  )

  const undoLast = useCallback(() => {
    const last = history.at(-1)
    if (!last || busy.current) return
    busy.current = true
    undo
      .mutateAsync(last.id)
      .then(() => {
        setHistory((list) => list.slice(0, -1))
        setDismissed((list) => list.filter((id) => id !== last.id))
        push({ tone: 'sky', emoji: '↩️', title: 'Свайп отменён', text: `${last.name} снова в ленте.` })
      })
      .catch(() => push({ tone: 'coral', title: 'Не получилось отменить' }))
      .finally(() => {
        busy.current = false
      })
  }, [history, undo, push])

  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      const target = event.target as HTMLElement | null
      if (target && /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName)) return
      if (matched || opened || filtersOpen) return
      if (event.key === 'ArrowRight') {
        event.preventDefault()
        decide('like')
      } else if (event.key === 'ArrowLeft') {
        event.preventDefault()
        decide('dislike')
      } else if (event.key.toLowerCase() === 'z' || event.key === 'Backspace') {
        event.preventDefault()
        undoLast()
      }
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [decide, undoLast, matched, opened, filtersOpen])

  const resetFilters = () => {
    setFilters(DEFAULT_FILTERS)
    push({ tone: 'sky', emoji: '🧹', title: 'Фильтры сброшены' })
  }

  const liked = history.filter((item) => item.decision === 'like').length
  const accepted = matches?.filter((item) => item.status === 'accepted').length ?? 0

  const panel = (
    <FiltersPanel
      filters={filters}
      onChange={(patch) => setFilters((value) => ({ ...value, ...patch }))}
      onReset={resetFilters}
      remaining={visible.length}
      total={feed.data?.total ?? 0}
    />
  )

  return (
    <>
      <SectionTitle
        eyebrow="лента"
        title="Кто тебе подходит"
        action={
          <div className="flex items-center gap-2">
            <span className="mono-badge hidden sm:inline-flex">
              {visible.length} {plural(visible.length, 'анкета', 'анкеты', 'анкет')}
            </span>
            <Button
              variant="ghost"
              size="sm"
              icon="filter"
              className="lg:hidden"
              onClick={() => setFiltersOpen(true)}
            >
              Фильтры
            </Button>
          </div>
        }
      />

      <div className="grid gap-6 lg:grid-cols-[250px_minmax(0,1fr)] xl:grid-cols-[250px_minmax(0,1fr)_270px]">
        <aside className="hidden lg:block">
          <div className="card sticky top-24 p-5">{panel}</div>
        </aside>

        <section className="flex flex-col items-center">
          <div className="relative mx-auto h-[560px] w-full max-w-[390px] sm:h-[600px]">
            {feed.isLoading && (
              <div className="card absolute inset-0 overflow-hidden p-0">
                <Skeleton className="h-[46%] w-full rounded-none" />
                <div className="space-y-3 p-5">
                  <Skeleton className="h-5 w-2/3" />
                  <Skeleton className="h-4 w-full" />
                  <Skeleton className="h-4 w-5/6" />
                  <div className="flex gap-2 pt-2">
                    <Skeleton className="h-7 w-20 rounded-full" />
                    <Skeleton className="h-7 w-24 rounded-full" />
                    <Skeleton className="h-7 w-16 rounded-full" />
                  </div>
                </div>
              </div>
            )}

            {feed.error && (
              <ErrorState
                className="absolute inset-x-0 top-0"
                message={feed.error instanceof ApiError ? feed.error.message : 'Лента недоступна'}
                onRetry={() => void feed.refetch()}
              />
            )}

            {!feed.isLoading && !feed.error && visible.length === 0 && (
              <EmptyState
                className="absolute inset-0 justify-center"
                emoji="🌵"
                title="Анкеты закончились"
                text="Ты просмотрел всё, что подходит под фильтры. Ослабь условия или верни последние свайпы."
                action={
                  <>
                    <Button variant="sun" icon="refresh" onClick={resetFilters}>
                      Сбросить фильтры
                    </Button>
                    {history.length > 0 && (
                      <Button variant="ghost" icon="undo" onClick={undoLast}>
                        Вернуть последнюю
                      </Button>
                    )}
                  </>
                }
              />
            )}

            {visible
              .slice(0, 3)
              .map((person, index) => (
                <SwipeCard
                  key={person.id}
                  person={person}
                  myTags={myTags}
                  depth={index}
                  interactive={index === 0 && !flying}
                  flying={index === 0 ? flying : null}
                  onDecide={decide}
                  onOpen={() => setOpened(person)}
                />
              ))
              .reverse()}
          </div>

          <div className="mt-6 flex items-center justify-center gap-3">
            <button
              type="button"
              aria-label="Пропустить"
              disabled={!top || Boolean(flying)}
              onClick={() => decide('dislike')}
              className="grid h-14 w-14 place-items-center rounded-full border border-line bg-surface text-coral-deep shadow-[var(--shadow-soft)] transition hover:-translate-y-0.5 hover:border-coral disabled:opacity-40 disabled:hover:translate-y-0"
            >
              <Icon name="close" size={24} />
            </button>
            <button
              type="button"
              aria-label="Отменить последний свайп"
              disabled={history.length === 0}
              onClick={undoLast}
              className="grid h-11 w-11 place-items-center rounded-full border border-line bg-surface text-sky-deep shadow-[var(--shadow-soft)] transition hover:-translate-y-0.5 hover:border-sky disabled:opacity-40 disabled:hover:translate-y-0"
            >
              <Icon name="undo" size={19} />
            </button>
            <button
              type="button"
              aria-label="Открыть анкету"
              disabled={!top}
              onClick={() => top && setOpened(top)}
              className="grid h-11 w-11 place-items-center rounded-full border border-line bg-surface text-grape-deep shadow-[var(--shadow-soft)] transition hover:-translate-y-0.5 hover:border-grape disabled:opacity-40 disabled:hover:translate-y-0"
            >
              <Icon name="info" size={19} />
            </button>
            <button
              type="button"
              aria-label="Нравится"
              disabled={!top || Boolean(flying)}
              onClick={() => decide('like')}
              className="grid h-16 w-16 place-items-center rounded-full bg-[image:var(--grad-warm)] text-white shadow-[var(--shadow-pop)] transition hover:-translate-y-0.5 disabled:opacity-40 disabled:hover:translate-y-0"
            >
              <Icon name="heart-fill" size={28} />
            </button>
          </div>

          <p className="mt-4 hidden items-center gap-2 font-mono text-[11.5px] text-dim sm:flex">
            <kbd className="rounded-md border border-line bg-surface px-1.5 py-0.5">←</kbd> мимо
            <kbd className="ml-2 rounded-md border border-line bg-surface px-1.5 py-0.5">→</kbd> няшка
            <kbd className="ml-2 rounded-md border border-line bg-surface px-1.5 py-0.5">Z</kbd> отменить
            <span className="ml-2">или тяни карточку мышью</span>
          </p>
        </section>

        <aside className="hidden xl:block">
          <div className="sticky top-24 space-y-4">
            <div className="card p-5">
              <p className="panel-title mb-3">твоя сессия</p>
              <div className="grid grid-cols-3 gap-2 text-center">
                {[
                  { value: visible.length, label: 'в ленте', tone: 'text-ink' },
                  { value: liked, label: 'лайков', tone: 'text-coral-deep' },
                  { value: accepted, label: 'мэтчей', tone: 'text-mint-deep' },
                ].map((item) => (
                  <div key={item.label} className="rounded-2xl bg-cream-deep/70 px-2 py-3">
                    <p className={cn('font-display text-xl font-extrabold', item.tone)}>{item.value}</p>
                    <p className="text-[11px] text-sub">{item.label}</p>
                  </div>
                ))}
              </div>
            </div>

            <div className="card-flat p-5">
              <p className="panel-title mb-2">как считается мэтч</p>
              <p className="text-[13px] leading-relaxed text-sub">
                Процент — это пересечение твоих тегов со стеком анкеты плюс близость по расстоянию.
                Взаимный лайк сразу открывает чат.
              </p>
              <div className="mt-3 rounded-2xl bg-surface p-3 font-mono text-[11.5px] text-dim">
                score = |A ∩ B| / |A ∪ B|
              </div>
            </div>

            {history.length > 0 && (
              <div className="card p-5">
                <p className="panel-title mb-3">последние решения</p>
                <ul className="space-y-2">
                  {history
                    .slice(-5)
                    .reverse()
                    .map((item) => (
                      <li key={item.id} className="flex items-center gap-2 text-[13px]">
                        <span
                          className={cn(
                            'grid h-6 w-6 shrink-0 place-items-center rounded-full',
                            item.decision === 'like'
                              ? 'bg-coral-soft text-coral-deep'
                              : 'bg-cream-deep text-dim',
                          )}
                        >
                          <Icon name={item.decision === 'like' ? 'heart-fill' : 'close'} size={12} />
                        </span>
                        <span className="truncate font-semibold">{item.name}</span>
                      </li>
                    ))}
                </ul>
              </div>
            )}
          </div>
        </aside>
      </div>

      <Modal open={filtersOpen} onClose={() => setFiltersOpen(false)} title="Фильтры ленты">
        {panel}
      </Modal>

      <PersonModal
        person={opened}
        myTags={myTags}
        onClose={() => setOpened(null)}
        footer={
          opened && (
            <>
              <Button
                variant="ghost"
                icon="close"
                onClick={() => {
                  setOpened(null)
                  decide('dislike')
                }}
              >
                Мимо
              </Button>
              <Button
                icon="heart-fill"
                onClick={() => {
                  setOpened(null)
                  decide('like')
                }}
              >
                Няшка
              </Button>
            </>
          )
        }
      />

      {matched && profile && (
        <MatchOverlay
          person={matched.person}
          me={{ id: profile.id, name: profile.name, avatar: profile.avatar }}
          myTags={myTags}
          onClose={() => setMatched(null)}
          onWrite={() => navigate(`/chats/${matched.chatId}`)}
        />
      )}
    </>
  )
}
