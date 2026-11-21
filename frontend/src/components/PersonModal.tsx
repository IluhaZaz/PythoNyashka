import type { ReactNode } from 'react'
import { MOCK_FEATURES } from '@/api'
import type { PublicProfile } from '@/api/types'
import { avatarGradient } from '@/lib/avatar'
import { km, timeAgo } from '@/lib/format'
import { MediaImage } from '@/components/MediaImage'
import { Modal } from '@/components/ui/Modal'
import { Icon } from '@/components/ui/Icon'
import { StickerRow } from '@/components/ui/Sticker'

export function PersonModal({
  person,
  myTags,
  onClose,
  footer,
}: {
  person: PublicProfile | null
  myTags: string[]
  onClose: () => void
  footer?: ReactNode
}) {
  if (!person) return null
  const shared = myTags.filter((tag) => person.tags.includes(tag))

  return (
    <Modal open onClose={onClose} title={`${person.name} ${person.surname}`} footer={footer} wide>
      <div
        className="relative -mx-1 h-52 overflow-hidden rounded-3xl"
        style={{ background: avatarGradient(person.id) }}
      >
        <MediaImage
          mediaId={person.avatar}
          seed={person.id}
          alt={person.name}
          className="h-full w-full"
        />
        {MOCK_FEATURES && (
          <span className="absolute top-3 left-3 rounded-full bg-surface/92 px-3 py-1.5 font-mono text-[11.5px] font-bold text-coral-deep backdrop-blur">
            {Math.round(person.matchScore * 100)}% совпадение
          </span>
        )}
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-x-3 gap-y-1">
        <p className="font-display text-xl font-extrabold">
          {person.name}, <span className="font-body font-semibold text-sub">{person.age}</span>
        </p>
        {person.role && <span className="mono-badge">{person.role}</span>}
        {person.online ? (
          <span className="inline-flex items-center gap-1.5 text-[12px] font-bold text-mint-deep">
            <span className="h-2 w-2 rounded-full bg-mint" />в сети
          </span>
        ) : person.lastSeen && (
          <span className="hint">была {timeAgo(person.lastSeen)}</span>
        )}
      </div>

      {person.city && (
        <p className="mt-1 inline-flex items-center gap-1.5 font-mono text-[11.5px] text-dim">
          <Icon name="pin" size={13} />
          {person.city} · {km(person.distanceKm)} от тебя
        </p>
      )}

      <p className="mt-4 text-[14px] leading-relaxed text-ink/85">{person.bio}</p>

      <div className="mt-5">
        <p className="panel-title mb-2">стек</p>
        <StickerRow tags={person.tags} />
      </div>

      {shared.length > 0 && (
        <p className="mt-3 rounded-2xl bg-mint-soft px-3.5 py-2.5 text-[12.5px] font-semibold text-mint-deep">
          Пересечение с твоим стеком: {shared.join(', ')}
        </p>
      )}

      <div className="mt-5 space-y-3">
        {person.prompts.map((prompt) => (
          <div key={prompt.question} className="quote-block">
            <p className="font-mono text-[11px] text-coral-deep">{prompt.question}</p>
            <p className="mt-1.5 text-[13.5px] leading-relaxed text-ink/85">{prompt.answer}</p>
          </div>
        ))}
      </div>

      {person.lookingFor && (
        <p className="mt-5 text-[13.5px] text-sub">
          <span className="font-bold text-ink">Ищет:</span> {person.lookingFor}
        </p>
      )}
    </Modal>
  )
}
