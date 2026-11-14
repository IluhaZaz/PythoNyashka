import { useMemo, useState } from 'react'
import { cn } from '@/lib/cn'
import { PROFILE_TAGS, TAG_GROUPS, stickerClass, type ProfileTag } from '@/lib/tags'
import { Icon } from '@/components/ui/Icon'
import { Sticker } from '@/components/ui/Sticker'

export function TagPicker({
  value,
  onChange,
  max = 12,
}: {
  value: ProfileTag[]
  onChange: (tags: ProfileTag[]) => void
  max?: number
}) {
  const [search, setSearch] = useState('')
  const query = search.trim().toLowerCase()

  const groups = useMemo(
    () =>
      TAG_GROUPS.map((group) => ({
        ...group,
        tags: group.tags.filter((tag) => !query || tag.includes(query)),
      })).filter((group) => group.tags.length > 0),
    [query],
  )

  const toggle = (tag: ProfileTag) => {
    if (value.includes(tag)) {
      onChange(value.filter((item) => item !== tag))
    } else if (value.length < max) {
      onChange([...value, tag])
    }
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center gap-3">
        <div className="relative min-w-52 flex-1">
          <Icon
            name="search"
            size={17}
            className="pointer-events-none absolute top-1/2 left-3.5 -translate-y-1/2 text-dim"
          />
          <input
            className="field pl-10"
            placeholder="найти тег: python, ctf, rust…"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            aria-label="Поиск по тегам"
          />
        </div>
        <span className="mono-badge">
          {value.length}/{max}
        </span>
      </div>

      {value.length > 0 && (
        <div className="card-flat flex flex-wrap gap-2 p-3">
          {value.map((tag) => (
            <Sticker key={tag} tag={tag} onRemove={() => toggle(tag)} />
          ))}
        </div>
      )}

      <div className="max-h-80 space-y-4 overflow-y-auto pr-1">
        {groups.map((group) => (
          <div key={group.title}>
            <p className="panel-title mb-2">
              {group.emoji} {group.title}
            </p>
            <div className="flex flex-wrap gap-2">
              {group.tags.map((tag) => {
                const active = value.includes(tag)
                const disabled = !active && value.length >= max
                return (
                  <button
                    key={tag}
                    type="button"
                    disabled={disabled}
                    onClick={() => toggle(tag)}
                    aria-pressed={active}
                    className={cn(
                      'sticker cursor-pointer border transition',
                      active
                        ? cn(stickerClass(tag), 'border-transparent ring-2 ring-ink/70')
                        : 'border-line bg-surface text-sub hover:border-line-strong hover:text-ink',
                      disabled && 'cursor-not-allowed opacity-40',
                    )}
                  >
                    {active && <Icon name="check" size={12} />}
                    {tag}
                  </button>
                )
              })}
            </div>
          </div>
        ))}
        {groups.length === 0 && (
          <p className="hint py-6 text-center">
            Ничего не нашлось по «{search}». В словаре {PROFILE_TAGS.length} тегов.
          </p>
        )}
      </div>
    </div>
  )
}
