// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import { App } from '@/App'
import { tokenStore } from '@/api/tokens'

vi.hoisted(() => {
  vi.stubEnv('VITE_USE_MOCKS', 'false')
  vi.stubEnv('VITE_API_BASE', '/api')
})

const fetchMock = vi.fn<typeof fetch>()

beforeEach(() => {
  localStorage.clear()
  tokenStore.clear()
  vi.stubGlobal('fetch', fetchMock)
  vi.spyOn(window, 'scrollTo').mockImplementation(() => {})
})

afterEach(() => {
  cleanup()
  tokenStore.clear()
  fetchMock.mockReset()
  vi.unstubAllGlobals()
  vi.restoreAllMocks()
})

function enterCredentials() {
  fireEvent.change(screen.getByLabelText('Почта'), { target: { value: 'ada@example.com' } })
  fireEvent.change(screen.getByLabelText('Пароль'), { target: { value: 'test-password' } })
  fireEvent.click(screen.getByRole('button', { name: 'Войти' }))
}

it('redirects a guest away from a protected page without contacting the API', async () => {
  window.history.replaceState(null, '', '/profile')
  render(<App />)

  expect(await screen.findByRole('heading', { name: 'Рады видеть снова' })).toBeTruthy()
  expect(window.location.pathname).toBe('/login')
  expect(fetchMock).not.toHaveBeenCalled()
})

it('shows a local validation error before sending an incomplete form', () => {
  window.history.replaceState(null, '', '/login')
  render(<App />)

  fireEvent.click(screen.getByRole('button', { name: 'Войти' }))

  expect(screen.getByText('Укажи почту')).toBeTruthy()
  expect(screen.getByText('Введи пароль')).toBeTruthy()
  expect(fetchMock).not.toHaveBeenCalled()
})

it('submits credentials, saves the session and opens the feed after a successful login', async () => {
  window.history.replaceState(null, '', '/login')
  fetchMock.mockImplementation(async (url) => {
    if (url === '/api/auth/login') return Response.json({
      access_token: 'access-from-bff', refresh_token: 'refresh-from-bff', token_type: 'Bearer',
    })
    if (url === '/api/profiles') return Response.json({
      profile: { id: 'profile-id', name: 'Ada', surname: 'Lovelace', tags: ['python'] },
    })
    if (url === '/api/matches') return new Response(null, { status: 404 })
    if (String(url).startsWith('/api/notifications?')) return Response.json({ notifications: [] })
    throw new Error('Unexpected API request: ' + url)
  })
  render(<App />)

  enterCredentials()

  await waitFor(() => expect(window.location.pathname).toBe('/swipes'))
  expect(fetchMock).toHaveBeenCalledWith('/api/auth/login', expect.objectContaining({
    method: 'POST', body: JSON.stringify({ email: 'ada@example.com', password: 'test-password' }),
  }))
  await waitFor(() => expect(fetchMock).toHaveBeenCalledWith('/api/matches', expect.objectContaining({
    headers: { Authorization: 'Bearer access-from-bff' },
  })))
  expect(await screen.findByText('Анкеты закончились')).toBeTruthy()
  expect(tokenStore.refresh()).toBe('refresh-from-bff')
})
