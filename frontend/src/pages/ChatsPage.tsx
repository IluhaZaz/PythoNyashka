import { useEffect, useMemo, useRef, useState } from 'react'
import type { ChangeEvent, KeyboardEvent } from 'react'
import { useQueryClient } from '@tanstack/react-query'
import { useNavigate, useParams } from 'react-router-dom'
import { ApiError } from '@/api'
import type { ChatSummary, Message, PublicProfile } from '@/api/types'
import {
  keys,
  useChats,
  useChatTyping,
  useMessages,
  useSendMessage,
} from '@/api/hooks'
import { cn } from '@/lib/cn'
import { clockTime, dayLabel, shortAgo, timeAgo } from '@/lib/format'
import { useAuth } from '@/state/auth'
import { useToast } from '@/state/toast'
import { Avatar, MediaImage } from '@/components/MediaImage'
import { PersonModal } from '@/components/PersonModal'
import { Button } from '@/components/ui/Button'
import { EmptyState, ErrorState, Skeleton } from '@/components/ui/Feedback'
import { Icon } from '@/components/ui/Icon'
import { StickerRow } from '@/components/ui/Sticker'

const ICE_BREAKERS = [
  'Привет! Что сейчас пилишь?',
  'Твой стек — огонь. Какой редактор?',
  'Табы или пробелы? Важный вопрос 🙂',
]

const mediaIdOf = (value: string) => value.replace(/^\/?api\/media\//, '').replace(/^\/media\//, '')

function ChatListItem({
  chat,
  active,
  meId,
  onClick,
}: {
  chat: ChatSummary
  active: boolean
  meId: string
  onClick: () => void
}) {
  const contact = chat.contact
  const preview = chat.lastMessage
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'flex w-full items-center gap-3 rounded-3xl border px-3 py-3 text-left transition',
        active
          ? 'border-coral/50 bg-coral-soft/60'
          : 'border-transparent hover:border-line hover:bg-cream-deep/60',
      )}
    >
      <Avatar
        mediaId={contact?.avatar}
        seed={contact?.id ?? chat.id}
        name={contact?.name ?? 'Чат'}
        size={48}
        online={contact?.online}
      />
      <span className="min-w-0 flex-1">
        <span className="flex items-baseline gap-2">
          <span className="font-display truncate text-[14.5px] font-bold">
            {contact ? `${contact.name} ${contact.surname}` : `Чат ${chat.id.slice(0, 8)}`}
          </span>
          {preview && (
            <span className="ml-auto shrink-0 font-mono text-[10.5px] text-dim">
              {shortAgo(preview.sentAt)}
            </span>
          )}
        </span>
        <span className="mt-0.5 flex items-center gap-2">
          <span className="truncate text-[12.5px] text-sub">
            {preview
              ? `${preview.senderId === meId ? 'Ты: ' : ''}${preview.text || '📎 вложение'}`
              : 'Чат создан — напиши первым'}
          </span>
          {chat.unread > 0 && <span className="count-badge ml-auto shrink-0">{chat.unread}</span>}
        </span>
      </span>
    </button>
  )
}

function MessageGroup({
  messages,
  meId,
  contact,
}: {
  messages: Message[]
  meId: string
  contact: PublicProfile | null
}) {
  let lastDay = ''
  return (
    <>
      {messages.map((message) => {
        const day = dayLabel(message.sentAt)
        const showDay = day !== lastDay
        lastDay = day
        const mine = message.senderId === meId
        return (
          <div key={message.id}>
            {showDay && (
              <div className="my-4 flex items-center gap-3">
                <span className="h-px flex-1 bg-line" />
                <span className="mono-badge">{day}</span>
                <span className="h-px flex-1 bg-line" />
              </div>
            )}
            <div className={cn('mb-2.5 flex items-end gap-2', mine && 'flex-row-reverse')}>
              {!mine && (
                <Avatar
                  mediaId={contact?.avatar}
                  seed={contact?.id ?? message.senderId}
                  name={contact?.name ?? 'Собеседник'}
                  size={28}
                />
              )}
              <div className={cn('bubble', mine ? 'bubble-out' : 'bubble-in')}>
                {message.text && <p className="whitespace-pre-wrap">{message.text}</p>}
                {message.media.length > 0 && (
                  <div className={cn('grid gap-2', message.text && 'mt-2')}>
                    {message.media.map((media) => (
                      <MediaImage
                        key={media}
                        mediaId={mediaIdOf(media)}
                        seed={media}
                        alt="Вложение"
                        className="max-h-56 w-full rounded-2xl"
                      />
                    ))}
                  </div>
                )}
                <p
                  className={cn(
                    'mt-1 text-right font-mono text-[10px]',
                    mine ? 'text-white/95' : 'text-dim',
                  )}
                >
                  {clockTime(message.sentAt)}
                </p>
              </div>
            </div>
          </div>
        )
      })}
    </>
  )
}

export function ChatsPage() {
  const { chatId } = useParams<{ chatId: string }>()
  const navigate = useNavigate()
  const { profile } = useAuth()
  const { push } = useToast()
  const queryClient = useQueryClient()
  const chats = useChats()
  const messages = useMessages(chatId ?? null)
  const typing = useChatTyping(chatId ?? null)

  const [search, setSearch] = useState('')
  const [text, setText] = useState('')
  const [files, setFiles] = useState<File[]>([])
  const [opened, setOpened] = useState<PublicProfile | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)
  const fileRef = useRef<HTMLInputElement>(null)
  const composerRef = useRef<HTMLTextAreaElement>(null)

  const meId = profile?.id ?? ''
  const list = chats.data ?? []
  const active = list.find((chat) => chat.id === chatId) ?? null
  const contact = active?.contact ?? null
  const send = useSendMessage(chatId ?? '')

  const filtered = useMemo(() => {
    const query = search.trim().toLowerCase()
    if (!query) return list
    return list.filter((chat) => {
      const name = chat.contact ? `${chat.contact.name} ${chat.contact.surname}` : chat.id
      return (
        name.toLowerCase().includes(query) ||
        (chat.lastMessage?.text ?? '').toLowerCase().includes(query) ||
        (chat.contact?.tags ?? []).some((tag) => tag.includes(query))
      )
    })
  }, [list, search])

  useEffect(() => {
    setText('')
    setFiles([])
  }, [chatId])

  useEffect(() => {
    if (!chatId && list.length > 0 && window.matchMedia('(min-width: 1024px)').matches) {
      navigate(`/chats/${list[0].id}`, { replace: true })
    }
  }, [chatId, list, navigate])

  useEffect(() => {
    if (messages.data) void queryClient.invalidateQueries({ queryKey: keys.chats })
  }, [messages.data, queryClient])

  useEffect(() => {
    const node = scrollRef.current
    if (node) node.scrollTop = node.scrollHeight
  }, [messages.data, typing, chatId])

  const submit = async () => {
    if (!chatId || (!text.trim() && files.length === 0) || send.isPending) return
    const payload = { text: text.trim(), media: files }
    setText('')
    setFiles([])
    try {
      await send.mutateAsync(payload)
      composerRef.current?.focus()
    } catch (error) {
      setText(payload.text)
      setFiles(payload.media)
      push({
        tone: 'coral',
        emoji: '📡',
        title: 'Сообщение не отправилось',
        text: error instanceof ApiError ? error.message : 'Попробуй ещё раз.',
      })
    }
  }

  const onKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === 'Enter' && !event.shiftKey) {
      event.preventDefault()
      void submit()
    }
  }

  const pickFiles = (event: ChangeEvent<HTMLInputElement>) => {
    const picked = Array.from(event.target.files ?? []).filter((file) =>
      file.type.startsWith('image/'),
    )
    if (picked.length) setFiles((current) => [...current, ...picked].slice(0, 4))
    event.target.value = ''
  }

  const thread = (
    <div className="card flex h-full min-h-0 flex-col overflow-hidden p-0">
      {!active ? (
        <div className="grid flex-1 place-items-center p-6">
          <EmptyState
            className="border-0 bg-transparent shadow-none"
            emoji="💬"
            title="Выбери чат"
            text="Слева — все диалоги. Взаимный лайк создаёт чат автоматически."
          />
        </div>
      ) : (
        <>
          <header className="flex items-center gap-3 border-b border-line px-4 py-3">
            <button
              type="button"
              onClick={() => navigate('/chats')}
              aria-label="Назад к списку"
              className="btn btn-ghost btn-icon h-9 w-9 lg:hidden"
            >
              <Icon name="arrow-left" size={17} />
            </button>
            <Avatar
              mediaId={contact?.avatar}
              seed={contact?.id ?? active.id}
              name={contact?.name ?? 'Чат'}
              size={42}
              online={contact?.online}
            />
            <div className="min-w-0 flex-1">
              <p className="font-display truncate text-[15px] font-bold">
                {contact ? `${contact.name} ${contact.surname}` : `Чат ${active.id.slice(0, 8)}`}
              </p>
              <p className="truncate text-[12px] text-sub">
                {typing ? (
                  <span className="font-semibold text-coral-deep">печатает…</span>
                ) : contact?.online ? (
                  'в сети'
                ) : contact ? (
                  `была ${timeAgo(contact.lastSeen)}`
                ) : (
                  'профиль недоступен'
                )}
              </p>
            </div>
            {contact && (
              <Button variant="ghost" size="sm" icon="user" onClick={() => setOpened(contact)}>
                <span className="hidden sm:inline">Анкета</span>
              </Button>
            )}
          </header>

          <div ref={scrollRef} className="min-h-0 flex-1 overflow-y-auto px-4 py-4">
            {messages.isLoading && (
              <div className="space-y-3">
                <Skeleton className="h-12 w-2/3" />
                <Skeleton className="ml-auto h-10 w-1/2" />
                <Skeleton className="h-14 w-3/5" />
              </div>
            )}
            {messages.error && (
              <ErrorState
                message={
                  messages.error instanceof ApiError ? messages.error.message : 'Чат недоступен'
                }
                onRetry={() => void messages.refetch()}
              />
            )}
            {messages.data && messages.data.messages.length === 0 && (
              <div className="py-8 text-center">
                <p className="animate-wiggle text-4xl">👋</p>
                <p className="font-display mt-2 text-lg font-bold">Начни разговор</p>
                <p className="hint mx-auto mt-1 max-w-xs">
                  Общие теги — лучший повод. Вот несколько заходов:
                </p>
                <div className="mt-4 flex flex-wrap justify-center gap-2">
                  {ICE_BREAKERS.map((line) => (
                    <button
                      key={line}
                      type="button"
                      onClick={() => {
                        setText(line)
                        composerRef.current?.focus()
                      }}
                      className="sticker st-sky cursor-pointer border border-line bg-surface transition hover:border-sky"
                    >
                      {line}
                    </button>
                  ))}
                </div>
                {contact && (
                  <div className="mt-6">
                    <p className="panel-title mb-2">её стек</p>
                    <StickerRow tags={contact.tags} className="justify-center" />
                  </div>
                )}
              </div>
            )}
            {messages.data && (
              <MessageGroup messages={messages.data.messages} meId={meId} contact={contact} />
            )}
            {typing && (
              <div className="mb-2 flex items-end gap-2">
                <Avatar
                  mediaId={contact?.avatar}
                  seed={contact?.id ?? 'contact'}
                  name={contact?.name ?? 'Собеседник'}
                  size={28}
                />
                <div className="bubble bubble-in flex items-center gap-1 py-3">
                  {[0, 1, 2].map((index) => (
                    <span
                      key={index}
                      className="h-1.5 w-1.5 animate-bounce rounded-full bg-dim"
                      style={{ animationDelay: `${index * 0.12}s` }}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>

          <footer className="border-t border-line bg-surface-2 px-3 py-3">
            {files.length > 0 && (
              <div className="mb-2 flex flex-wrap gap-2">
                {files.map((file, index) => (
                  <span
                    key={`${file.name}-${index}`}
                    className="inline-flex items-center gap-2 rounded-full border border-line bg-surface px-3 py-1.5 font-mono text-[11px]"
                  >
                    <Icon name="image" size={13} className="text-coral-deep" />
                    <span className="max-w-32 truncate">{file.name}</span>
                    <button
                      type="button"
                      aria-label={`Убрать ${file.name}`}
                      onClick={() => setFiles((current) => current.filter((_, i) => i !== index))}
                      className="text-dim transition hover:text-coral-deep"
                    >
                      <Icon name="close" size={12} />
                    </button>
                  </span>
                ))}
              </div>
            )}
            <div className="flex items-end gap-2">
              <input
                ref={fileRef}
                type="file"
                accept="image/*"
                multiple
                className="hidden"
                onChange={pickFiles}
              />
              <button
                type="button"
                aria-label="Прикрепить картинку"
                onClick={() => fileRef.current?.click()}
                className="btn btn-ghost btn-icon h-11 w-11 shrink-0"
              >
                <Icon name="clip" size={19} />
              </button>
              <textarea
                ref={composerRef}
                rows={1}
                value={text}
                onChange={(event) => setText(event.target.value)}
                onKeyDown={onKeyDown}
                placeholder="Напиши что-нибудь няшное… (Enter — отправить)"
                className="field max-h-32 min-h-11 flex-1 resize-none py-3 leading-snug"
              />
              <Button
                size="icon"
                className="h-11 w-11 shrink-0"
                aria-label="Отправить"
                loading={send.isPending}
                disabled={!text.trim() && files.length === 0}
                onClick={() => void submit()}
              >
                {!send.isPending && <Icon name="send" size={19} />}
              </Button>
            </div>
          </footer>
        </>
      )}
    </div>
  )

  return (
    <div className="grid gap-5 lg:h-[calc(100dvh-9rem)] lg:grid-cols-[320px_minmax(0,1fr)]">
      <aside className={cn('card flex min-h-0 flex-col p-3', chatId && 'hidden lg:flex')}>
        <div className="px-2 pt-1 pb-3">
          <div className="flex items-baseline justify-between">
            <h1 className="text-xl">Чаты</h1>
            <span className="mono-badge">{list.length}</span>
          </div>
          <div className="relative mt-3">
            <Icon
              name="search"
              size={16}
              className="pointer-events-none absolute top-1/2 left-3.5 -translate-y-1/2 text-dim"
            />
            <input
              className="field pl-10"
              placeholder="имя, тег или текст…"
              value={search}
              onChange={(event) => setSearch(event.target.value)}
              aria-label="Поиск по чатам"
            />
          </div>
        </div>

        <div className="min-h-0 flex-1 space-y-1 overflow-y-auto">
          {chats.isLoading &&
            [0, 1, 2].map((index) => (
              <div key={index} className="flex items-center gap-3 px-3 py-3">
                <Skeleton className="h-12 w-12 rounded-2xl" />
                <div className="flex-1 space-y-2">
                  <Skeleton className="h-3.5 w-2/3" />
                  <Skeleton className="h-3 w-4/5" />
                </div>
              </div>
            ))}
          {chats.error && (
            <ErrorState
              message={chats.error instanceof ApiError ? chats.error.message : 'Чаты недоступны'}
              onRetry={() => void chats.refetch()}
            />
          )}
          {!chats.isLoading && filtered.length === 0 && (
            <div className="px-4 py-10 text-center">
              <p className="text-3xl">🗨️</p>
              <p className="font-display mt-2 text-[15px] font-bold">
                {list.length === 0 ? 'Чатов пока нет' : 'Ничего не нашлось'}
              </p>
              <p className="hint mt-1">
                {list.length === 0
                  ? 'Поставь лайк в ленте — при взаимности чат появится сам.'
                  : 'Попробуй другой запрос.'}
              </p>
              {list.length === 0 && (
                <Button className="mt-4" size="sm" icon="cards" onClick={() => navigate('/swipes')}>
                  В ленту
                </Button>
              )}
            </div>
          )}
          {filtered.map((chat) => (
            <ChatListItem
              key={chat.id}
              chat={chat}
              meId={meId}
              active={chat.id === chatId}
              onClick={() => navigate(`/chats/${chat.id}`)}
            />
          ))}
        </div>
      </aside>

      <section className={cn('min-h-0 h-[calc(100dvh-13rem)] lg:h-auto', !chatId && 'hidden lg:block')}>
        {thread}
      </section>

      <PersonModal person={opened} myTags={profile?.tags ?? []} onClose={() => setOpened(null)} />
    </div>
  )
}
