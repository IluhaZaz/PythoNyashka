import { useEffect } from 'react'
import { createPortal } from 'react-dom'
import type { PublicProfile } from '@/api/types'
import { Avatar } from '@/components/MediaImage'
import { Button } from '@/components/ui/Button'
import { Icon } from '@/components/ui/Icon'
import { StickerRow } from '@/components/ui/Sticker'

const HEARTS = [
  { left: '8%', delay: '0s', size: 22 },
  { left: '22%', delay: '.25s', size: 16 },
  { left: '38%', delay: '.5s', size: 26 },
  { left: '54%', delay: '.15s', size: 18 },
  { left: '70%', delay: '.4s', size: 24 },
  { left: '86%', delay: '.65s', size: 15 },
]

export function MatchOverlay({
  person,
  me,
  myTags,
  onWrite,
  onClose,
}: {
  person: PublicProfile
  me: { id: string; name: string; avatar?: string | null }
  myTags: string[]
  onWrite: () => void
  onClose: () => void
}) {
  useEffect(() => {
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', onKey)
    return () => document.removeEventListener('keydown', onKey)
  }, [onClose])

  const shared = myTags.filter((tag) => person.tags.includes(tag))

  return createPortal(
    <div className="fixed inset-0 z-[95] grid place-items-center overflow-hidden p-5">
      <button
        type="button"
        aria-label="Закрыть"
        onClick={onClose}
        className="absolute inset-0 bg-[#4A3B38]/45 backdrop-blur-[5px]"
      />
      {HEARTS.map((heart) => (
        <span
          key={heart.left}
          aria-hidden="true"
          className="animate-heart-burst pointer-events-none absolute bottom-0 text-coral"
          style={{ left: heart.left, animationDelay: heart.delay, fontSize: heart.size }}
        >
          ♥
        </span>
      ))}

      <div className="card animate-pop-in relative w-full max-w-md p-7 text-center">
        <p className="panel-title">взаимный лайк</p>
        <h2 className="font-display mt-1 text-[32px] leading-none font-extrabold text-coral-deep">
          Это мэтч!
        </h2>
        <p className="mt-2 text-[14px] text-sub">
          {person.name} тоже считает тебя няшкой. Чат уже открыт — не тяни с первым сообщением.
        </p>

        <div className="mt-6 flex items-center justify-center gap-3">
          <Avatar mediaId={me.avatar} seed={me.id} name={me.name} size={92} className="rotate-[-6deg]" />
          <span className="grid h-12 w-12 shrink-0 place-items-center rounded-full bg-coral-deep text-white shadow-[var(--shadow-pop)]">
            <Icon name="heart-fill" size={24} />
          </span>
          <Avatar
            mediaId={person.avatar}
            seed={person.id}
            name={person.name}
            size={92}
            className="rotate-[6deg]"
          />
        </div>

        <p className="mt-4 font-mono text-[12px] text-dim">
          match_score = {person.matchScore.toFixed(2)}
        </p>

        {shared.length > 0 && (
          <div className="mt-4">
            <p className="panel-title mb-2">общий стек</p>
            <StickerRow tags={shared} className="justify-center" />
          </div>
        )}

        <div className="mt-6 flex flex-col gap-2">
          <Button size="lg" icon="send" onClick={onWrite}>
            Написать {person.name}
          </Button>
          <Button variant="ghost" onClick={onClose}>
            Свайпать дальше
          </Button>
        </div>
      </div>
    </div>,
    document.body,
  )
}
