import { useEffect, useState } from 'react'
import { useQuery } from '@tanstack/react-query'
import { api } from '@/api'
import { avatarDataUrl } from '@/lib/avatar'
import { cn } from '@/lib/cn'

interface MediaImageProps {
  mediaId?: string | null
  seed: string
  alt: string
  className?: string
}

export function MediaImage({ mediaId, seed, alt, className }: MediaImageProps) {
  const query = useQuery({
    queryKey: ['media', mediaId],
    queryFn: ({ signal }) => api.mediaBlob(mediaId!, signal),
    enabled: Boolean(mediaId),
    staleTime: 5 * 60_000,
    gcTime: 10 * 60_000,
    retry: 1,
  })

  const [objectUrl, setObjectUrl] = useState<string | null>(null)

  useEffect(() => {
    if (!query.data) return
    const url = URL.createObjectURL(query.data)
    setObjectUrl(url)
    return () => {
      URL.revokeObjectURL(url)
      setObjectUrl(null)
    }
  }, [query.data])

  const src = objectUrl ?? avatarDataUrl(seed)

  return (
    <img
      src={src}
      alt={alt}
      loading="lazy"
      draggable={false}
      className={cn('object-cover', className)}
    />
  )
}

export function Avatar({
  mediaId,
  seed,
  name,
  size = 44,
  online,
  className,
}: {
  mediaId?: string | null
  seed: string
  name: string
  size?: number
  online?: boolean
  className?: string
}) {
  return (
    <span
      className={cn('relative inline-block shrink-0', className)}
      style={{ width: size, height: size }}
    >
      <MediaImage
        mediaId={mediaId}
        seed={seed}
        alt={name}
        className="h-full w-full rounded-2xl border border-line"
      />
      {online && (
        <span
          className="absolute -right-0.5 -bottom-0.5 rounded-full border-2 border-surface bg-mint"
          style={{ width: size * 0.28, height: size * 0.28 }}
          aria-label="В сети"
        />
      )}
    </span>
  )
}
