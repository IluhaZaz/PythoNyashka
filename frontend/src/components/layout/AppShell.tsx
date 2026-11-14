import { useEffect, useRef, useState } from 'react'
import { Link, NavLink, Outlet, useLocation, useNavigate } from 'react-router-dom'
import { USE_MOCKS } from '@/api'
import { useChats, useMatchHistory, useMockSync } from '@/api/hooks'
import { useAuth } from '@/state/auth'
import { useToast } from '@/state/toast'
import { cn } from '@/lib/cn'
import { mockReset } from '@/api/mock'
import { Avatar } from '@/components/MediaImage'
import { Icon, type IconName } from '@/components/ui/Icon'
import { Logo } from './Background'
import { NotificationBell } from './NotificationBell'

const NAV: { to: string; label: string; icon: IconName }[] = [
  { to: '/swipes', label: 'Свайпы', icon: 'cards' },
  { to: '/matches', label: 'Матчи', icon: 'heart' },
  { to: '/chats', label: 'Чаты', icon: 'chat' },
  { to: '/profile', label: 'Анкета', icon: 'user' },
]

export function AppShell() {
  useMockSync()
  const { profile, logout } = useAuth()
  const { push } = useToast()
  const navigate = useNavigate()
  const location = useLocation()
  const [menuOpen, setMenuOpen] = useState(false)
  const menuRef = useRef<HTMLDivElement>(null)

  const { data: matches } = useMatchHistory()
  const { data: chats } = useChats()

  const matchCount = matches?.filter((match) => match.status === 'accepted').length ?? 0
  const unreadChats = chats?.reduce((sum, chat) => sum + chat.unread, 0) ?? 0
  const pendingLikes =
    matches?.filter(
      (match) => match.status === 'noResponse' && match.targetProfileId === profile?.id,
    ).length ?? 0

  const counts: Record<string, number> = {
    '/matches': pendingLikes || matchCount,
    '/chats': unreadChats,
  }

  useEffect(() => setMenuOpen(false), [location.pathname])

  useEffect(() => {
    if (!menuOpen) return
    const onClick = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) setMenuOpen(false)
    }
    document.addEventListener('mousedown', onClick)
    return () => document.removeEventListener('mousedown', onClick)
  }, [menuOpen])

  const handleLogout = async () => {
    await logout()
    push({ tone: 'sky', emoji: '👋', title: 'Ты вышел', text: 'Сессия закрыта, токен отозван.' })
    navigate('/login')
  }

  const handleReset = () => {
    mockReset()
    push({ tone: 'sun', emoji: '🧪', title: 'Демо-данные сброшены', text: 'Перезагружаю приложение…' })
    window.setTimeout(() => window.location.reload(), 700)
  }

  return (
    <div className="flex min-h-dvh flex-col">
      <header className="sticky top-0 z-50 border-b border-line/70 bg-cream/80 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-[1400px] items-center gap-3 px-4 sm:px-6">
          <Link to="/swipes" className="flex items-center gap-2.5">
            <Logo />
            <span className="hidden leading-none sm:block">
              <span className="font-display block text-[15px] font-extrabold tracking-tight">
                PythoNyashka
              </span>
              <span className="font-mono text-[10.5px] text-dim">матчим по стеку</span>
            </span>
          </Link>

          <nav className="mx-auto hidden items-center gap-1 md:flex">
            {NAV.map((item) => (
              <NavLink
                key={item.to}
                to={item.to}
                className={({ isActive }) => cn('nav-link', isActive && 'nav-link-active')}
              >
                <Icon name={item.icon} size={17} />
                {item.label}
                {counts[item.to] > 0 && <span className="count-badge">{counts[item.to]}</span>}
              </NavLink>
            ))}
          </nav>

          <div className="ml-auto flex items-center gap-2 md:ml-0">
            {USE_MOCKS && (
              <span
                className="mono-badge hidden lg:inline-flex"
                title="Данные обслуживает встроенный мок, бэкенд не нужен"
              >
                demo · mocks on
              </span>
            )}
            <NotificationBell />
            <div className="relative" ref={menuRef}>
              <button
                type="button"
                onClick={() => setMenuOpen((value) => !value)}
                aria-label="Меню профиля"
                aria-expanded={menuOpen}
                className="flex items-center gap-2 rounded-full border border-line bg-surface py-1 pr-3 pl-1 transition hover:border-line-strong"
              >
                <Avatar
                  mediaId={profile?.avatar}
                  seed={profile?.id ?? 'me'}
                  name={profile?.name ?? 'Я'}
                  size={32}
                  online
                />
                <span className="hidden text-[13px] font-bold sm:block">{profile?.name ?? 'Я'}</span>
                <Icon name="chevron-down" size={14} className="text-dim" />
              </button>

              {menuOpen && (
                <div className="card animate-rise absolute right-0 z-50 mt-2 w-60 overflow-hidden p-1.5">
                  <div className="px-3 py-2">
                    <p className="font-display text-sm font-bold">
                      {profile?.name} {profile?.surname}
                    </p>
                    <p className="truncate font-mono text-[11px] text-dim">{profile?.email}</p>
                  </div>
                  <div className="my-1 h-px bg-line" />
                  {[
                    { to: '/profile', label: 'Моя анкета', icon: 'user' as IconName },
                    { to: '/settings', label: 'Настройки', icon: 'settings' as IconName },
                    { to: '/notifications', label: 'Уведомления', icon: 'bell' as IconName },
                  ].map((item) => (
                    <Link
                      key={item.to}
                      to={item.to}
                      className="flex items-center gap-2.5 rounded-2xl px-3 py-2 text-[13.5px] font-semibold text-sub transition hover:bg-cream-deep hover:text-ink"
                    >
                      <Icon name={item.icon} size={16} />
                      {item.label}
                    </Link>
                  ))}
                  {USE_MOCKS && (
                    <button
                      type="button"
                      onClick={handleReset}
                      className="flex w-full items-center gap-2.5 rounded-2xl px-3 py-2 text-[13.5px] font-semibold text-sub transition hover:bg-cream-deep hover:text-ink"
                    >
                      <Icon name="refresh" size={16} />
                      Сбросить демо-данные
                    </button>
                  )}
                  <div className="my-1 h-px bg-line" />
                  <button
                    type="button"
                    onClick={handleLogout}
                    className="flex w-full items-center gap-2.5 rounded-2xl px-3 py-2 text-[13.5px] font-bold text-coral-deep transition hover:bg-coral-soft"
                  >
                    <Icon name="logout" size={16} />
                    Выйти
                  </button>
                </div>
              )}
            </div>
          </div>
        </div>
      </header>

      <main className="mx-auto w-full max-w-[1400px] flex-1 px-4 pt-5 pb-28 sm:px-6 md:pb-10">
        <Outlet />
      </main>

      <nav className="fixed inset-x-0 bottom-0 z-50 border-t border-line bg-cream/95 backdrop-blur-xl md:hidden">
        <div className="flex items-stretch">
          {NAV.map((item) => (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                cn(
                  'relative flex flex-1 flex-col items-center gap-0.5 py-2.5 text-[11px] font-bold transition',
                  isActive ? 'text-coral-deep' : 'text-sub',
                )
              }
            >
              {({ isActive }) => (
                <>
                  <span
                    className={cn(
                      'grid h-8 w-12 place-items-center rounded-full transition',
                      isActive && 'bg-coral-soft',
                    )}
                  >
                    <Icon name={item.icon} size={19} />
                  </span>
                  {item.label}
                  {counts[item.to] > 0 && (
                    <span className="count-badge absolute top-1 right-[22%]">{counts[item.to]}</span>
                  )}
                </>
              )}
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  )
}
