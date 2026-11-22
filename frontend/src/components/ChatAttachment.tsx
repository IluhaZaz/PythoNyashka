import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/api'
import { Icon } from '@/components/ui/Icon'

const UUID = /^[a-f0-9]{8}(?:-[a-f0-9]{4}){3}-[a-f0-9]{12}$/i
const sizeUnits = ['Б', 'КБ', 'МБ', 'ГБ']
const sizeFormat = new Intl.NumberFormat('ru-RU', { maximumFractionDigits: 1 })

function mediaIdOf(reference: string): string | null {
  const value = reference.trim()
  if (UUID.test(value)) return value.toLowerCase()
  try {
    // Only use the ID. The actual request must go through the configured BFF.
    const path = new URL(value, 'http://localhost').pathname
    const id = /\/media\/([^/]+)\/?$/.exec(path)?.[1]
    return id && UUID.test(id) ? id.toLowerCase() : null
  } catch {
    return null
  }
}

function fileSize(bytes: number): string {
  const unit = bytes < 1024 ? 0 : Math.min(Math.floor(Math.log2(bytes) / 10), sizeUnits.length - 1)
  return sizeFormat.format(bytes / 1024 ** unit) + ' ' + sizeUnits[unit]
}

export function ChatAttachment({ media }: { media: string }) {
  const mediaId = mediaIdOf(media)
  const { data, isError } = useQuery({
    queryKey: ['attachment', mediaId],
    queryFn: ({ signal }) => api.attachment(mediaId!, signal),
    enabled: mediaId !== null,
    staleTime: 5 * 60_000,
    gcTime: 10 * 60_000,
    retry: false,
  })
  const blob = data?.blob
  const [objectUrl, setObjectUrl] = useState<{ blob: Blob; url: string } | null>(null)
  const [failedPreview, setFailedPreview] = useState<string | null>(null)

  useEffect(() => {
    if (!blob) return
    const url = URL.createObjectURL(blob)
    setObjectUrl({ blob, url })
    return () => URL.revokeObjectURL(url)
  }, [blob])

  const url = objectUrl?.blob === blob ? objectUrl?.url : undefined
  if (!mediaId || isError || !data || !url) {
    return (
      <span className="flex items-center gap-2 rounded-xl bg-surface/95 px-3 py-2 text-xs text-sub">
        <Icon name="clip" size={16} className="shrink-0" />
        {mediaId && !isError ? 'Загрузка вложения…' : 'Вложение недоступно'}
      </span>
    )
  }

  const name = data.fileName ?? 'Вложение'
  const showImage = data.blob.type.startsWith('image/') && failedPreview !== url
  return (
    <a
      href={url}
      download={data.fileName ?? ''}
      aria-label={'Скачать ' + name}
      className="block min-w-0 overflow-hidden rounded-xl border border-line bg-surface/95 text-ink transition hover:border-coral focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-coral"
    >
      {showImage && (
        <img
          src={url}
          alt={name}
          className="max-h-64 w-full bg-surface-2 object-contain"
          onError={() => setFailedPreview(url)}
        />
      )}
      <span className="flex min-w-0 items-center gap-2.5 px-3 py-2">
        {!showImage && <Icon name="file" size={19} className="shrink-0 text-coral-deep" />}
        <span className="min-w-0 flex-1">
          <span className="block truncate text-sm font-semibold" title={name}>{name}</span>
          <span className="block font-mono text-[11px] text-sub">{fileSize(data.blob.size)}</span>
        </span>
        <Icon name="download" size={18} className="shrink-0 text-coral-deep" />
      </span>
    </a>
  )
}
