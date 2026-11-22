import { afterEach, beforeEach, describe, expect, it, vi } from 'vitest'
import { request } from '@/api/http'
import { tokenStore } from '@/api/tokens'
import type { AuthTokens } from '@/api/types'

vi.hoisted(() => vi.stubEnv('VITE_API_BASE', '/api'))

const original: AuthTokens = {
  access_token: 'original-access', refresh_token: 'original-refresh', token_type: 'Bearer',
}
const renewed: AuthTokens = {
  access_token: 'renewed-access', refresh_token: 'renewed-refresh', token_type: 'Bearer',
}
const fetchMock = vi.fn<typeof fetch>()

beforeEach(() => {
  const storage = new Map<string, string>()
  vi.stubGlobal('localStorage', {
    getItem: (key: string) => storage.get(key) ?? null,
    setItem: (key: string, value: string) => storage.set(key, value),
    removeItem: (key: string) => storage.delete(key),
  })
  vi.stubGlobal('fetch', fetchMock)
  tokenStore.set(original)
})

afterEach(() => {
  tokenStore.clear()
  fetchMock.mockReset()
  vi.unstubAllGlobals()
})

describe('HTTP client', () => {
  it('shares one refresh between two protected requests and retries both with the fresh token', async () => {
    const refresh = Promise.withResolvers<Response>()
    fetchMock.mockImplementation(async (url, options) => {
      if (url === '/api/auth/refresh') return refresh.promise
      const authorization = new Headers(options?.headers).get('authorization')
      if (authorization === 'Bearer original-access') return new Response(null, { status: 401 })
      expect(authorization).toBe('Bearer renewed-access')
      return Response.json({ path: url })
    })

    const requests = Promise.all([request('/profiles'), request('/chats')])
    await vi.waitFor(() => expect(fetchMock).toHaveBeenCalledTimes(3))
    refresh.resolve(Response.json(renewed))

    await expect(requests).resolves.toEqual([{ path: '/api/profiles' }, { path: '/api/chats' }])
    const refreshCalls = fetchMock.mock.calls.filter(([url]) => url === '/api/auth/refresh')
    expect(refreshCalls).toEqual([[
      '/api/auth/refresh',
      expect.objectContaining({
        method: 'POST',
        body: JSON.stringify({ refresh_token: original.refresh_token }),
      }),
    ]])
    expect(fetchMock).toHaveBeenCalledTimes(5)
    expect(tokenStore.refresh()).toBe(renewed.refresh_token)
  })

  it('clears rejected sessions and leaves the original request unretried', async () => {
    fetchMock.mockImplementation(async () => new Response(null, { status: 401 }))

    await expect(request('/profiles')).rejects.toMatchObject({ status: 401 })

    expect(fetchMock.mock.calls.map(([url]) => url)).toEqual([
      '/api/profiles', '/api/auth/refresh',
    ])
    expect(tokenStore.access()).toBeNull()
    expect(tokenStore.refresh()).toBeNull()
  })

  it('builds field errors from a FastAPI validation response', async () => {
    fetchMock.mockResolvedValueOnce(Response.json({
      detail: [{ loc: ['body', 'age'], msg: 'Must be greater than 0' }],
    }, { status: 422 }))

    await expect(request('/profiles', { method: 'PATCH', json: { age: 0 } }))
      .rejects.toMatchObject({
        status: 422,
        fieldErrors: { age: 'Возраст: Must be greater than 0' },
      })
  })
})
