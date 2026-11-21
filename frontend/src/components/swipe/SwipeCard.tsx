import { useRef, useState } from 'react'
import type { PointerEvent as ReactPointerEvent } from 'react'
import { MOCK_FEATURES } from '@/api'
import type { PublicProfile } from '@/api/types'
import { avatarGradient } from '@/lib/avatar'
import { cn } from '@/lib/cn'
import { km } from '@/lib/format'
import { MediaImage } from '@/components/MediaImage'
import { Icon } from '@/components/ui/Icon'
import { StickerRow } from '@/components/ui/Sticker'

export interface SwipeCardProps {
  person: PublicProfile
  myTags: string[]
  depth: number
  interactive: boolean
  flying: 'like' | 'dislike' | null
  onDecide: (decision: 'like' | 'dislike') => void
  onOpen: () => void
}

const THRESHOLD = 110

export function SwipeCard({
  person,
  myTags,
  depth,
  interactive,
  flying,
  onDecide,
  onOpen,
}: SwipeCardProps) {
  const [offset, setOffset] = useState({ x: 0, y: 0 })
  const [dragging, setDragging] = useState(false)
  const start = useRef({ x: 0, y: 0 })
  const locked = useRef<'none' | 'x' | 'y'>('none')

  const shared = myTags.filter((tag) => person.tags.includes(tag))
  const progress = Math.min(Math.abs(offset.x) / THRESHOLD, 1)
  const intent: 'like' | 'dislike' | null =
    flying ?? (offset.x > 24 ? 'like' : offset.x < -24 ? 'dislike' : null)

  const onPointerDown = (event: ReactPointerEvent<HTMLDivElement>) => {
    if (!interactive || event.button !== 0) return
    if ((event.target as HTMLElement).closest('[data-no-drag]')) return
    start.current = { x: event.clientX, y: event.clientY }
    locked.current = 'none'
    setDragging(true)
  }

  const onPointerMove = (event: ReactPointerEvent<HTMLDivElement>) => {
    if (!dragging) return
    const dx = event.clientX - start.current.x
    const dy = event.clientY - start.current.y

    if (locked.current === 'none') {
      if (Math.abs(dx) > 8 && Math.abs(dx) > Math.abs(dy)) {
        locked.current = 'x'
        event.currentTarget.setPointerCapture(event.pointerId)
      } else if (Math.abs(dy) > 10) {
        locked.current = 'y'
        setDragging(false)
        return
      } else {
        return
      }
    }
    if (locked.current !== 'x') return
    setOffset({ x: dx, y: dy * 0.25 })
  }

  const finish = () => {
    if (!dragging) return
    setDragging(false)
    if (locked.current === 'x' && Math.abs(offset.x) > THRESHOLD) {
      onDecide(offset.x > 0 ? 'like' : 'dislike')
    }
    locked.current = 'none'
    setOffset({ x: 0, y: 0 })
  }

  const flyX = flying === 'like' ? 620 : flying === 'dislike' ? -620 : 0
  const translateX = flying ? flyX : offset.x
  const translateY = flying ? -40 : offset.y + depth * 12
  const rotate = flying ? (flying === 'like' ? 18 : -18) : offset.x / 22
  const scale = flying ? 0.94 : 1 - depth * 0.04

  return (
    <div
      className="swipe-card absolute inset-0"
      style={{
        transform: `translate3d(${translateX}px, ${translateY}px, 0) rotate(${rotate}deg) scale(${scale})`,
        transition: dragging ? 'none' : 'transform .34s cubic-bezier(.2,.9,.3,1.2), opacity .3s',
        opacity: flying ? 0 : 1,
        zIndex: 10 - depth,
        pointerEvents: interactive ? 'auto' : 'none',
      }}
      onPointerDown={onPointerDown}
      onPointerMove={onPointerMove}
      onPointerUp={finish}
      onPointerCancel={finish}
    >
      <article className="card flex h-full flex-col overflow-hidden p-0 select-none">
        <div
          className="relative h-[46%] min-h-56 shrink-0"
          style={{ background: avatarGradient(person.id) }}
        >
          <MediaImage
            mediaId={person.avatar}
            seed={person.id}
            alt={`${person.name} ${person.surname}`}
            className="h-full w-full"
          />
          <div className="pointer-events-none absolute inset-0 bg-[linear-gradient(to_top,rgba(74,59,56,.82),rgba(74,59,56,.15)_46%,transparent_70%)]" />

          <div className="absolute top-3.5 left-3.5 flex items-center gap-2">
            {MOCK_FEATURES && (
              <span className="inline-flex items-center gap-1.5 rounded-full bg-surface/92 px-3 py-1.5 font-mono text-[11.5px] font-bold text-coral-deep backdrop-blur">
                <Icon name="spark" size={13} />
                {Math.round(person.matchScore * 100)}% мэтч
              </span>
            )}
            {person.online && (
              <span className="inline-flex items-center gap-1.5 rounded-full bg-surface/92 px-2.5 py-1.5 text-[11px] font-extrabold text-mint-deep backdrop-blur">
                <span className="h-1.5 w-1.5 rounded-full bg-mint" />в сети
              </span>
            )}
          </div>

          <button
            type="button"
            data-no-drag
            onClick={onOpen}
            aria-label="Открыть анкету целиком"
            className="absolute top-3.5 right-3.5 grid h-9 w-9 place-items-center rounded-full bg-surface/92 text-ink backdrop-blur transition hover:bg-surface"
          >
            <Icon name="info" size={17} />
          </button>

          <div className="absolute inset-x-4 bottom-3.5 text-white">
            <h2 className="font-display text-[26px] leading-tight font-extrabold drop-shadow">
              {person.name}, <span className="font-body font-semibold">{person.age}</span>
            </h2>
            {person.role && <p className="text-[13px] font-semibold text-white/85">{person.role}</p>}
          </div>

          <span
            className="swipe-stamp left-5 -rotate-12 text-coral-deep"
            style={{ opacity: intent === 'dislike' ? progress : 0 }}
          >
            мимо
          </span>
          <span
            className="swipe-stamp right-5 rotate-12 text-mint-deep"
            style={{ opacity: intent === 'like' ? progress : 0 }}
          >
            няшка
          </span>
        </div>

        <div className="min-h-0 flex-1 overflow-y-auto px-5 py-4">
          {MOCK_FEATURES && (
            <div className="flex flex-wrap items-center gap-x-3 gap-y-1 font-mono text-[11.5px] text-dim">
              <span className="inline-flex items-center gap-1">
                <Icon name="pin" size={13} />
                {person.city} · {km(person.distanceKm)}
              </span>
              {!person.online && (
                <span className="inline-flex items-center gap-1">
                  <Icon name="clock" size={13} />
                  была недавно
                </span>
              )}
            </div>
          )}

          <p className="mt-3 text-[14px] leading-relaxed text-ink/85">{person.bio}</p>

          <div className="mt-4">
            <p className="panel-title mb-2">стек</p>
            <StickerRow tags={person.tags} limit={10} />
          </div>

          {shared.length > 0 && (
            <p className="mt-3 rounded-2xl bg-mint-soft px-3.5 py-2.5 text-[12.5px] font-semibold text-mint-deep">
              Общие теги: {shared.join(', ')}
            </p>
          )}

          <div className="mt-4 space-y-3">
            {person.prompts.map((prompt) => (
              <div key={prompt.question} className="quote-block">
                <p className="font-mono text-[11px] text-coral-deep">{prompt.question}</p>
                <p className="mt-1.5 text-[13.5px] leading-relaxed text-ink/85">{prompt.answer}</p>
              </div>
            ))}
          </div>

          <p className="mt-4 text-[13px] text-sub">
            <span className="font-bold text-ink">Ищет:</span> {person.lookingFor}
          </p>
        </div>
      </article>

      <div
        className={cn(
          'pointer-events-none absolute inset-0 rounded-[28px] ring-4 transition',
          intent === 'like' && 'ring-mint/50',
          intent === 'dislike' && 'ring-coral/50',
          !intent && 'ring-transparent',
        )}
      />
    </div>
  )
}
