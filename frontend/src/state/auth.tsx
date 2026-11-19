import { createContext, useCallback, useContext, useEffect, useMemo, useState } from 'react'
import type { ReactNode } from 'react'
import { useQuery, useQueryClient } from '@tanstack/react-query'
import { ApiError, MODE, USE_MOCKS, api, tokenStore } from '@/api'
import type { Profile, ProfileCreateInput } from '@/api/types'
import { readJson, writeJson } from '@/lib/storage'
import { DEMO_EMAIL, ME_ID } from '@/api/mock/seed'
import { startAmbient } from '@/api/mock'

const DEMO_PASSWORD_VALUE = 'nyashka123'

interface AuthContextValue {
  authenticated: boolean
  booting: boolean
  profile: Profile | null
  profileLoading: boolean
  login(email: string, password: string): Promise<void>
  register(input: ProfileCreateInput): Promise<void>
  logout(): Promise<void>
  reloadProfile(): Promise<void>
}

const AuthContext = createContext<AuthContextValue | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const queryClient = useQueryClient()
  const [authenticated, setAuthenticated] = useState(() => Boolean(tokenStore.refresh()))
  const [booting, setBooting] = useState(true)

  useEffect(() => {
    let cancelled = false
    const boot = async () => {
      // В демо-режиме приложение открывается уже populated — без экрана входа.
      if (USE_MOCKS && !tokenStore.refresh() && !readJson('demo-dismissed', false)) {
        try {
          await api.login(DEMO_EMAIL, DEMO_PASSWORD_VALUE)
          if (!cancelled) setAuthenticated(true)
        } catch {
          /* покажем обычный экран входа */
        }
      }
      if (!cancelled) setBooting(false)
    }
    void boot()
    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    if (USE_MOCKS && authenticated) startAmbient()
  }, [authenticated])

  useEffect(() => {
    const unsubscribe = tokenStore.subscribe((isAuthed) => {
      if (!isAuthed) setAuthenticated(false)
    })
    return () => {
      unsubscribe()
    }
  }, [])

  const profileQuery = useQuery({
    queryKey: ['profile'],
    queryFn: () => api.getProfile(),
    enabled: authenticated,
    retry: (failureCount, error) =>
      !(error instanceof ApiError && error.status === 401) && failureCount < 2,
    staleTime: 30_000,
  })

  useEffect(() => {
    const error = profileQuery.error
    if (error instanceof ApiError && error.status === 401) {
      tokenStore.clear()
      setAuthenticated(false)
    }
  }, [profileQuery.error])

  const login = useCallback(
    async (email: string, password: string) => {
      await api.login(email, password)
      writeJson('demo-dismissed', true)
      queryClient.clear()
      setAuthenticated(true)
    },
    [queryClient],
  )

  const register = useCallback(
    async (input: ProfileCreateInput) => {
      await api.register(input)
      await api.login(input.email, input.password)
      writeJson('demo-dismissed', true)
      queryClient.clear()
      setAuthenticated(true)
    },
    [queryClient],
  )

  const logout = useCallback(async () => {
    writeJson('demo-dismissed', true)
    await api.logout()
    tokenStore.clear()
    setAuthenticated(false)
    queryClient.clear()
  }, [queryClient])

  const reloadProfile = useCallback(async () => {
    await queryClient.invalidateQueries({ queryKey: ['profile'] })
  }, [queryClient])

  const value = useMemo<AuthContextValue>(
    () => ({
      authenticated,
      booting,
      profile: profileQuery.data ?? null,
      profileLoading: profileQuery.isLoading && authenticated,
      login,
      register,
      logout,
      reloadProfile,
    }),
    [authenticated, booting, profileQuery.data, profileQuery.isLoading, login, register, logout, reloadProfile],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext)
  if (!context) throw new Error('useAuth должен вызываться внутри AuthProvider')
  return context
}

/**
 * В hybrid профиль живёт на BFF (реальный uuid), а мок-данные (мэтчи/чаты)
 * ключуются по сидированному ME_ID — сравнения «моё/чужое» берут его.
 */
export function useMyId(): string {
  const { profile } = useAuth()
  return MODE === 'hybrid' ? ME_ID : (profile?.id ?? '')
}
