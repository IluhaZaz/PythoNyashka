import { readJson, removeKey, writeJson } from '@/lib/storage'
import type { AuthTokens } from './types'

const REFRESH_KEY = 'refresh-token'

let accessToken: string | null = null
const listeners = new Set<(authenticated: boolean) => void>()

export const tokenStore = {
  access: () => accessToken,
  refresh: () => readJson<string | null>(REFRESH_KEY, null),
  set(tokens: AuthTokens) {
    accessToken = tokens.access_token
    writeJson(REFRESH_KEY, tokens.refresh_token)
    listeners.forEach((fn) => fn(true))
  },
  clear() {
    accessToken = null
    removeKey(REFRESH_KEY)
    listeners.forEach((fn) => fn(false))
  },
  subscribe(fn: (authenticated: boolean) => void) {
    listeners.add(fn)
    return () => listeners.delete(fn)
  },
}
