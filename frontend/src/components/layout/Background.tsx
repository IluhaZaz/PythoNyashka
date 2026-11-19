export function Background() {
  return (
    <>
      <div className="bg-stage" aria-hidden="true">
        <span className="blob blob-1" />
        <span className="blob blob-2" />
        <span className="blob blob-3" />
        <span className="blob blob-4" />
      </div>
      <div className="grain" aria-hidden="true" />
    </>
  )
}

export function Logo({ size = 38 }: { size?: number }) {
  return (
    <span
      className="grid shrink-0 place-items-center rounded-[14px] bg-gradient-to-br from-coral to-[#FF8A6B] shadow-[var(--shadow-pop)]"
      style={{ width: size, height: size }}
    >
      <svg viewBox="0 0 24 24" width={size * 0.6} height={size * 0.6} aria-hidden="true">
        <path
          d="M12 20.3C6.5 16.4 3.5 13.2 3.5 9.6A4.6 4.6 0 0 1 12 7a4.6 4.6 0 0 1 8.5 2.6c0 3.6-3 6.8-8.5 10.7Z"
          fill="#FFF6EC"
        />
        <circle cx="9.4" cy="10.2" r="1.05" fill="#FF5D73" />
        <circle cx="14.6" cy="10.2" r="1.05" fill="#FF5D73" />
      </svg>
    </span>
  )
}
