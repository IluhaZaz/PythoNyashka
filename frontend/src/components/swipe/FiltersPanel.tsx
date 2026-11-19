import { DEFAULT_FILTERS, type FeedFilters } from '@/api/types'
import { cn } from '@/lib/cn'
import { stickerClass } from '@/lib/tags'
import { Button } from '@/components/ui/Button'
import { Toggle } from '@/components/ui/Field'
import { Icon } from '@/components/ui/Icon'

const POPULAR = [
  'python',
  'javascript',
  'typescript',
  'go',
  'rust',
  'backend',
  'frontend',
  'devops',
  'gamedev',
  'machine-learning',
  'cybersecurity',
  'ui-ux',
  'react',
  'fastapi',
  'docker',
  'ctf',
]

export function FiltersPanel({
  filters,
  onChange,
  onReset,
  remaining,
  total,
}: {
  filters: FeedFilters
  onChange: (patch: Partial<FeedFilters>) => void
  onReset: () => void
  remaining: number
  total: number
}) {
  const dirty = JSON.stringify(filters) !== JSON.stringify(DEFAULT_FILTERS)

  const toggleTag = (tag: string) => {
    onChange({
      tags: filters.tags.includes(tag)
        ? filters.tags.filter((item) => item !== tag)
        : [...filters.tags, tag],
    })
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between gap-2">
        <p className="panel-title">фильтры ленты</p>
        <span className="mono-badge">
          {remaining}/{total}
        </span>
      </div>

      <div>
        <div className="mb-2 flex items-baseline justify-between">
          <label className="label mb-0" htmlFor="filter-distance">
            Расстояние
          </label>
          <span className="font-mono text-[12px] font-bold text-coral-deep">
            до {filters.maxDistanceKm} км
          </span>
        </div>
        <input
          id="filter-distance"
          type="range"
          className="range"
          min={1}
          max={100}
          step={1}
          value={filters.maxDistanceKm}
          onChange={(event) => onChange({ maxDistanceKm: Number(event.target.value) })}
        />
      </div>

      <div>
        <div className="mb-2 flex items-baseline justify-between">
          <span className="label mb-0">Возраст</span>
          <span className="font-mono text-[12px] font-bold text-coral-deep">
            {filters.ageMin}–{filters.ageMax}
          </span>
        </div>
        <div className="space-y-2">
          <input
            type="range"
            aria-label="Минимальный возраст"
            className="range"
            min={18}
            max={60}
            value={filters.ageMin}
            onChange={(event) =>
              onChange({ ageMin: Math.min(Number(event.target.value), filters.ageMax) })
            }
          />
          <input
            type="range"
            aria-label="Максимальный возраст"
            className="range"
            min={18}
            max={60}
            value={filters.ageMax}
            onChange={(event) =>
              onChange({ ageMax: Math.max(Number(event.target.value), filters.ageMin) })
            }
          />
        </div>
      </div>

      <div className="rounded-2xl border border-line bg-surface px-4 py-3">
        <Toggle
          checked={filters.onlineOnly}
          onChange={(value) => onChange({ onlineOnly: value })}
          label="Только в сети"
          hint="Отвечают прямо сейчас"
        />
      </div>

      <div>
        <p className="label">Обязательные теги</p>
        <div className="flex flex-wrap gap-1.5">
          {POPULAR.map((tag) => {
            const active = filters.tags.includes(tag)
            return (
              <button
                key={tag}
                type="button"
                onClick={() => toggleTag(tag)}
                aria-pressed={active}
                className={cn(
                  'sticker cursor-pointer border transition',
                  active
                    ? cn(stickerClass(tag), 'border-transparent ring-2 ring-ink/70')
                    : 'border-line bg-surface text-sub hover:border-line-strong hover:text-ink',
                )}
              >
                {active && <Icon name="check" size={11} />}
                {tag}
              </button>
            )
          })}
        </div>
        {filters.tags.length > 0 && (
          <p className="hint mt-2">Анкета должна содержать все выбранные теги.</p>
        )}
      </div>

      <Button variant="ghost" size="sm" icon="refresh" onClick={onReset} disabled={!dirty} className="w-full">
        Сбросить фильтры
      </Button>
    </div>
  )
}
