import { cn } from '@/lib/cn'
import { stickerClass } from '@/lib/tags'
import { Icon } from './Icon'

export function Sticker({
  tag,
  tilt = true,
  onRemove,
  className,
}: {
  tag: string
  tilt?: boolean
  onRemove?: () => void
  className?: string
}) {
  return (
    <span className={cn('sticker', stickerClass(tag), tilt && 'sticker-tilt', className)}>
      {tag}
      {onRemove && (
        <button
          type="button"
          onClick={onRemove}
          aria-label={`Убрать тег ${tag}`}
          className="-mr-1 opacity-60 transition hover:opacity-100"
        >
          <Icon name="close" size={12} />
        </button>
      )}
    </span>
  )
}

export function StickerRow({
  tags,
  limit,
  tilt = true,
  className,
}: {
  tags: string[]
  limit?: number
  tilt?: boolean
  className?: string
}) {
  const shown = limit ? tags.slice(0, limit) : tags
  const rest = limit ? tags.length - shown.length : 0
  return (
    <div className={cn('flex flex-wrap gap-2', className)}>
      {shown.map((tag) => (
        <Sticker key={tag} tag={tag} tilt={tilt} />
      ))}
      {rest > 0 && <span className="sticker st-sky">+{rest}</span>}
    </div>
  )
}
