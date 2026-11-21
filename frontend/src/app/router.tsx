import { useEffect } from 'react'
import { Navigate, Route, Routes, useLocation } from 'react-router-dom'
import { AppShell } from '@/components/layout/AppShell'
import { Logo } from '@/components/layout/Background'
import { Spinner } from '@/components/ui/Button'
import { LoginPage } from '@/pages/auth/LoginPage'
import { RegisterPage } from '@/pages/auth/RegisterPage'
import { ChatsPage } from '@/pages/ChatsPage'
import { MatchesPage } from '@/pages/MatchesPage'
import { NotFoundPage } from '@/pages/NotFoundPage'
import { NotificationsPage } from '@/pages/NotificationsPage'
import { ProfilePage } from '@/pages/ProfilePage'
import { SettingsPage } from '@/pages/SettingsPage'
import { SwipesPage } from '@/pages/SwipesPage'
import { useAuth } from '@/state/auth'

function BootScreen() {
  return (
    <div className="flex min-h-dvh flex-col items-center justify-center gap-4">
      <Logo size={64} />
      <p className="font-display text-lg font-extrabold">PythoNyashka</p>
      <p className="flex items-center gap-2 font-mono text-[12px] text-dim">
        <Spinner size={14} />
        import nyashka…
      </p>
    </div>
  )
}

function RequireAuth() {
  const { authenticated, booting } = useAuth()
  const location = useLocation()

  if (booting) return <BootScreen />
  if (!authenticated) return <Navigate to="/login" replace state={{ from: location.pathname }} />
  return <AppShell />
}

function ScrollReset() {
  const { pathname } = useLocation()
  useEffect(() => {
    if (pathname.startsWith('/chats')) return
    window.scrollTo({ top: 0 })
  }, [pathname])
  return null
}

export function AppRoutes() {
  return (
    <>
      <ScrollReset />
      <Routes>
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        <Route element={<RequireAuth />}>
          <Route path="/" element={<Navigate to="/swipes" replace />} />
          <Route path="/swipes" element={<SwipesPage />} />
          <Route path="/matches" element={<MatchesPage />} />
          <Route path="/chats" element={<ChatsPage />} />
          <Route path="/chats/:chatId" element={<ChatsPage />} />
          <Route path="/profile" element={<ProfilePage />} />
          <Route path="/notifications" element={<NotificationsPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </>
  )
}
