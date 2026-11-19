import type { SVGProps } from 'react'

export type IconName =
  | 'heart'
  | 'heart-fill'
  | 'close'
  | 'star'
  | 'bell'
  | 'chat'
  | 'user'
  | 'spark'
  | 'filter'
  | 'arrow-left'
  | 'arrow-right'
  | 'send'
  | 'clip'
  | 'logout'
  | 'lock'
  | 'search'
  | 'check'
  | 'undo'
  | 'code'
  | 'mail'
  | 'eye'
  | 'eye-off'
  | 'plus'
  | 'image'
  | 'settings'
  | 'refresh'
  | 'pin'
  | 'clock'
  | 'chevron-down'
  | 'chevron-right'
  | 'trash'
  | 'edit'
  | 'camera'
  | 'cards'
  | 'info'

const PATHS: Record<IconName, string> = {
  heart: 'M12 20.3C6.5 16.4 3.5 13.2 3.5 9.6A4.6 4.6 0 0 1 12 7a4.6 4.6 0 0 1 8.5 2.6c0 3.6-3 6.8-8.5 10.7Z',
  'heart-fill':
    'M12 20.3C6.5 16.4 3.5 13.2 3.5 9.6A4.6 4.6 0 0 1 12 7a4.6 4.6 0 0 1 8.5 2.6c0 3.6-3 6.8-8.5 10.7Z',
  close: 'M6 6l12 12M18 6L6 18',
  star: 'M12 3.6l2.6 5.4 5.9.8-4.3 4.1 1 5.9-5.2-2.8-5.2 2.8 1-5.9L3.5 9.8l5.9-.8L12 3.6Z',
  bell: 'M18 9a6 6 0 1 0-12 0c0 5-2 6-2 6h16s-2-1-2-6M10.3 19a2 2 0 0 0 3.4 0',
  chat: 'M20.5 12c0 4.1-3.8 7.4-8.5 7.4-1 0-2-.15-2.9-.43L4 20.5l1.6-3.9A7 7 0 0 1 3.5 12C3.5 7.9 7.3 4.6 12 4.6s8.5 3.3 8.5 7.4Z',
  user: 'M20 20.5v-1.8a4.2 4.2 0 0 0-4.2-4.2H8.2A4.2 4.2 0 0 0 4 18.7v1.8M16 7.5a4 4 0 1 1-8 0 4 4 0 0 1 8 0Z',
  spark: 'M12 3l1.9 5.1L19 10l-5.1 1.9L12 17l-1.9-5.1L5 10l5.1-1.9L12 3ZM18.5 15.5l.8 2.2 2.2.8-2.2.8-.8 2.2-.8-2.2-2.2-.8 2.2-.8.8-2.2Z',
  filter: 'M4 6h16M7 12h10M10 18h4',
  'arrow-left': 'M19 12H5M11 18l-6-6 6-6',
  'arrow-right': 'M5 12h14M13 6l6 6-6 6',
  send: 'M21 3L10.5 13.5M21 3l-6.8 18-3.7-7.5L3 9.8 21 3Z',
  clip: 'M20.4 11.5l-8.5 8.5a5 5 0 0 1-7.1-7.1l8.5-8.5a3.3 3.3 0 1 1 4.7 4.7l-8.4 8.4a1.7 1.7 0 1 1-2.4-2.4l7.8-7.7',
  logout: 'M9 20H5.5A1.5 1.5 0 0 1 4 18.5v-13A1.5 1.5 0 0 1 5.5 4H9M15.5 16.5L20 12l-4.5-4.5M20 12H9.5',
  lock: 'M6.5 10.5h11a1.5 1.5 0 0 1 1.5 1.5v7a1.5 1.5 0 0 1-1.5 1.5h-11A1.5 1.5 0 0 1 5 19v-7a1.5 1.5 0 0 1 1.5-1.5ZM8 10.5V7.8a4 4 0 1 1 8 0v2.7',
  search: 'M20 20l-4.2-4.2M17 11a6 6 0 1 1-12 0 6 6 0 0 1 12 0Z',
  check: 'M5 12.5l4.5 4.5L19 7.5',
  undo: 'M4 9h10a5.5 5.5 0 0 1 0 11H9M4 9l4-4M4 9l4 4',
  code: 'M9 17l-5-5 5-5M15 7l5 5-5 5',
  mail: 'M4 6.5h16v11H4zM4 7l8 6 8-6',
  eye: 'M2.5 12S6 5.5 12 5.5 21.5 12 21.5 12 18 18.5 12 18.5 2.5 12 2.5 12ZM15 12a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z',
  'eye-off': 'M4 4l16 16M10 5.9a8.6 8.6 0 0 1 2-.4c6 0 9.5 6.5 9.5 6.5a17 17 0 0 1-3.3 4.1M6.4 7.9A16.6 16.6 0 0 0 2.5 12S6 18.5 12 18.5c1.2 0 2.3-.2 3.3-.6M9.9 9.9a3 3 0 0 0 4.2 4.2',
  plus: 'M12 5v14M5 12h14',
  image: 'M4 5.5h16v13H4zM4 15l4.5-4.5 4 4L16 11l4 4M9.5 9.5a1 1 0 1 1-2 0 1 1 0 0 1 2 0Z',
  settings:
    'M12 15.2a3.2 3.2 0 1 0 0-6.4 3.2 3.2 0 0 0 0 6.4ZM19.4 15a1.6 1.6 0 0 0 .3 1.8l.1.1a2 2 0 1 1-2.8 2.8l-.1-.1a1.6 1.6 0 0 0-2.7 1.1v.3a2 2 0 1 1-4 0v-.2a1.6 1.6 0 0 0-2.8-1.1l-.1.1a2 2 0 1 1-2.8-2.8l.1-.1A1.6 1.6 0 0 0 3.5 14H3a2 2 0 1 1 0-4h.2A1.6 1.6 0 0 0 4.3 7.2l-.1-.1a2 2 0 1 1 2.8-2.8l.1.1A1.6 1.6 0 0 0 10 3.5V3a2 2 0 1 1 4 0v.2a1.6 1.6 0 0 0 2.7 1.1l.1-.1a2 2 0 1 1 2.8 2.8l-.1.1a1.6 1.6 0 0 0 1.1 2.7h.4a2 2 0 1 1 0 4h-.2a1.6 1.6 0 0 0-1.4 1.2Z',
  refresh: 'M20 11a8 8 0 1 0-.7 4.5M20 5v6h-6',
  pin: 'M19 10.5c0 5-7 11-7 11s-7-6-7-11a7 7 0 1 1 14 0ZM14.5 10.5a2.5 2.5 0 1 1-5 0 2.5 2.5 0 0 1 5 0Z',
  clock: 'M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0ZM12 7v5.2l3.4 2',
  'chevron-down': 'M6 9.5l6 6 6-6',
  'chevron-right': 'M9.5 6l6 6-6 6',
  trash: 'M4.5 7h15M9.5 7V5.2A1.2 1.2 0 0 1 10.7 4h2.6a1.2 1.2 0 0 1 1.2 1.2V7M6.5 7l.9 12.1A1.5 1.5 0 0 0 8.9 20.5h6.2a1.5 1.5 0 0 0 1.5-1.4L17.5 7M10.5 11v5.5M13.5 11v5.5',
  edit: 'M4 20h4L19 9a2.5 2.5 0 0 0-3.5-3.5L4.5 16.5 4 20ZM14.5 6.5L17.5 9.5',
  camera:
    'M4 8.5h3l1.5-2.5h7L17 8.5h3a1 1 0 0 1 1 1v9a1 1 0 0 1-1 1H4a1 1 0 0 1-1-1v-9a1 1 0 0 1 1-1ZM15.5 13.5a3.5 3.5 0 1 1-7 0 3.5 3.5 0 0 1 7 0Z',
  cards: 'M8 4.5h9a2 2 0 0 1 2 2v11a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2v-11a2 2 0 0 1 2-2ZM3.5 7v10',
  info: 'M21 12a9 9 0 1 1-18 0 9 9 0 0 1 18 0ZM12 11v5.5M12 7.6v.6',
}

const FILLED: IconName[] = ['heart-fill', 'star']

interface IconProps extends Omit<SVGProps<SVGSVGElement>, 'name'> {
  name: IconName
  size?: number
}

export function Icon({ name, size = 20, ...rest }: IconProps) {
  const filled = FILLED.includes(name) || rest.fill === 'currentColor'
  return (
    <svg
      viewBox="0 0 24 24"
      width={size}
      height={size}
      fill={filled ? 'currentColor' : 'none'}
      stroke="currentColor"
      strokeWidth={1.9}
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
      {...rest}
    >
      <path d={PATHS[name]} />
    </svg>
  )
}
