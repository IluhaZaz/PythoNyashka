import { useMemo, useState } from 'react'
import { useQueries } from '@tanstack/react-query'
import { useNavigate } from 'react-router-dom'
import { ApiError, api } from '@/api'
import type { Match, PublicProfile } from '@/api/types'
import { keys, useAnswerMatch, useCreateChat, useMatchHistory } from '@/api/hooks'
import { avatarGradient } from '@/lib/avatar'
import { cn } from '@/lib/cn'
import { plural, timeAgo } from '@/lib/format'
import { useAuth, useMyId } from '@/state/auth'
import { useToast } from '@/state/toast'
import { Avatar, MediaImage } from '@/components/MediaImage'
import { PersonModal } from '@/components/PersonModal'
import { Button } from '@/components/ui/Button'
import { EmptyState, ErrorState, SectionTitle, Skeleton } from '@/components/ui/Feedback'
import { Segmented } from '@/components/ui/Field'
import { Icon } from '@/components/ui/Icon'
import { StickerRow } from '@/components/ui/Sticker'

type Tab = 'incoming' | 'matched' | 'history'

export function MatchesPage() {
  const { profile } = useAuth()
  const { push } = useToast()
  const navigate = useNavigate()
  const history = useMatchHistory()
  const createChat = useCreateChat()
  const answer = useAnswerMatch()
  const [tab, setTab] = useState<Tab>('incoming')
  const [opened, setOpened] = useState<PublicProfile | null>(null)
  const [pendingId, setPendingId] = useState<string | null>(null)

  const meId = useMyId()
  const rows = history.data ?? []

  const otherId = (match: Match) =>
    match.initiatorProfileId === meId ? match.targetProfileId : match.initiatorProfileId

  const ids = useMemo(() => Array.from(new Set(rows.map(otherId))), [rows, meId])

  const people = useQueries({
    queries: ids.map((id) => ({
      queryKey: keys.person(id),
      queryFn: () => api.publicProfile(id),
      staleTime: 60_000,
    })),
  })

  const personById = useMemo(() => {
    const map = new Map<string, PublicProfile | null>()
    ids.forEach((id, index) => map.set(id, people[index]?.data ?? null))
    return map
  }, [ids, people])

  const incoming = rows.filter(
    (match) => match.status === 'noResponse' && match.targetProfileId === meId,
  )
  const matched = rows.filter((match) => match.status === 'accepted')
  const shown = tab === 'incoming' ? incoming : tab === 'matched' ? matched : rows

  const openChat = async (match: Match) => {
    if (createChat.isPending) return
    try {
      const { id } = await createChat.mutateAsync([otherId(match)])
      navigate(`/chats/${id}`)
    } catch (error) {
      push({
        tone: 'coral',
        title: 'Не получилось открыть чат',
        text: error instanceof ApiError ? error.message : undefined,
      })
    }
  }

  const respond = async (match: Match, decision: 'like' | 'dislike') => {
    setPendingId(match.id)
    try {
      await answer.mutateAsync({ id: match.id, decision })
      if (decision === 'like') {
        push({
          tone: 'mint',
          emoji: '💞',
          title: 'Взаимно!',
          action: { label: 'Написать', onClick: () => void openChat(match) },
        })
      } else {
        push({ tone: 'sky', emoji: '🫥', title: 'Отклонено', text: 'Анкета больше не появится.' })
      }
    } catch (error) {
      push({
        tone: 'coral',
        title: 'Не получилось ответить',
        text: error instanceof ApiError ? error.message : undefined,
      })
    } finally {
      setPendingId(null)
    }
  }


  return (
    <>
      <SectionTitle
        eyebrow="симпатии"
        title="Мэтчи и лайки"
        action={
          <Segmented<Tab>
            value={tab}
            onChange={setTab}
            options={[
              { value: 'incoming', label: 'Тебя лайкнули', count: incoming.length },
              { value: 'matched', label: 'Мэтчи', count: matched.length },
              { value: 'history', label: 'История', count: rows.length },
            ]}
          />
        }
      />

      {incoming.length > 0 && tab !== 'incoming' && (
        <button
          type="button"
          onClick={() => setTab('incoming')}
          className="mb-5 flex w-full items-center gap-3 rounded-3xl border border-coral/40 bg-coral-soft px-5 py-3.5 text-left transition hover:border-coral"
        >
          <span className="animate-wiggle text-2xl">💌</span>
          <span className="flex-1">
            <span className="font-display block text-[14px] font-bold text-coral-deep">
              {incoming.length} {plural(incoming.length, 'анкета ждёт', 'анкеты ждут', 'анкет ждут')}{' '}
              ответа
            </span>
            <span className="text-[13px] text-ink/70">Ответь взаимностью — и чат откроется сразу.</span>
          </span>
          <Icon name="chevron-right" size={18} className="text-coral-deep" />
        </button>
      )}

      {history.isLoading && (
        <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
          {[0, 1, 2, 3, 4, 5].map((index) => (
            <div key={index} className="card space-y-3 p-5">
              <div className="flex gap-3">
                <Skeleton className="h-14 w-14 rounded-2xl" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-4 w-2/3" />
                  <Skeleton className="h-3 w-1/2" />
                </div>
              </div>
              <Skeleton className="h-10 w-full" />
            </div>
          ))}
        </div>
      )}

      {history.error && (
        <ErrorState
          message={history.error instanceof ApiError ? history.error.message : 'Мэтчи недоступны'}
          onRetry={() => void history.refetch()}
        />
      )}

      {!history.isLoading && !history.error && shown.length === 0 && (
        <EmptyState
          emoji={tab === 'incoming' ? '🕊️' : tab === 'matched' ? '🫶' : '🗂️'}
          title={
            tab === 'incoming'
              ? 'Пока никто не лайкнул'
              : tab === 'matched'
                ? 'Мэтчей ещё нет'
                : 'История пустая'
          }
          text="Загляни в ленту — там уже подобраны анкеты по твоему стеку. Взаимный лайк открывает чат."
          action={
            <Button icon="cards" onClick={() => navigate('/swipes')}>
              Открыть ленту
            </Button>
          }
        />
      )}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {shown.map((match) => {
          const person = personById.get(otherId(match))
          const isIncoming = match.status === 'noResponse' && match.targetProfileId === meId
          const isOutgoing = match.status === 'noResponse' && match.initiatorProfileId === meId
          const loading = pendingId === match.id

          return (
            <article key={match.id} className="card animate-rise flex flex-col overflow-hidden p-0">
              <div
                className="relative h-24"
                style={{ background: person ? avatarGradient(person.id) : 'var(--color-cream-deep)' }}
              >
                {person && (
                  <MediaImage
                    mediaId={person.avatar}
                    seed={person.id}
                    alt={person.name}
                    className="h-full w-full opacity-90"
                  />
                )}
                <span
                  className={cn(
                    'absolute top-3 right-3 rounded-full px-2.5 py-1 text-[11px] font-extrabold backdrop-blur',
                    match.status === 'accepted' && 'bg-mint-soft text-mint-deep',
                    isIncoming && 'bg-coral-deep text-white',
                    isOutgoing && 'bg-surface/92 text-sub',
                    match.status === 'rejected' && 'bg-surface/92 text-dim',
                  )}
                >
                  {match.status === 'accepted'
                    ? 'мэтч'
                    : isIncoming
                      ? 'ждёт ответа'
                      : isOutgoing
                        ? 'лайк отправлен'
                        : 'отклонено'}
                </span>
              </div>

              <div className="-mt-8 flex flex-1 flex-col px-5 pb-5">
                <Avatar
                  mediaId={person?.avatar}
                  seed={otherId(match)}
                  name={person?.name ?? 'Анкета'}
                  size={64}
                  online={person?.online}
                  className="[&>img]:border-4 [&>img]:border-surface"
                />
                <p className="font-display mt-2.5 text-[17px] font-extrabold">
                  {person ? `${person.name} ${person.surname}` : `Анкета ${otherId(match).slice(0, 8)}`}
                  {person && <span className="font-body font-semibold text-sub">, {person.age}</span>}
                </p>
                <p className="font-mono text-[11.5px] text-dim">
                  {person?.role ?? 'профиль скрыт контрактом'} · {timeAgo(match.createdAt)}
                </p>

                {person && (
                  <>
                    <p className="mt-3 line-clamp-2 text-[13.5px] leading-relaxed text-sub">
                      {person.bio}
                    </p>
                    <StickerRow tags={person.tags} limit={4} className="mt-3" />
                  </>
                )}

                <div className="mt-auto flex flex-wrap gap-2 pt-4">
                  {isIncoming && (
                    <>
                      <Button
                        size="sm"
                        icon="heart-fill"
                        loading={loading}
                        onClick={() => void respond(match, 'like')}
                      >
                        Взаимно
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        icon="close"
                        disabled={loading}
                        onClick={() => void respond(match, 'dislike')}
                      >
                        Мимо
                      </Button>
                    </>
                  )}
                  {match.status === 'accepted' && (
                    <Button
                      size="sm"
                      icon="send"
                      disabled={createChat.isPending}
                      loading={createChat.isPending && createChat.variables?.[0] === otherId(match)}
                      onClick={() => void openChat(match)}
                    >
                      Написать
                    </Button>
                  )}
                  {person && (
                    <Button size="sm" variant="quiet" icon="user" onClick={() => setOpened(person)}>
                      Анкета
                    </Button>
                  )}
                </div>
              </div>
            </article>
          )
        })}
      </div>

      <PersonModal
        person={opened}
        myTags={profile?.tags ?? []}
        onClose={() => setOpened(null)}
      />
    </>
  )
}
