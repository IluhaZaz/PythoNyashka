import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import { liveApi } from '@/api/live'
import { DEFAULT_FILTERS } from '@/api/types'

vi.hoisted(() => vi.stubEnv('VITE_API_BASE', '/api'))

const fetchMock = vi.fn<typeof fetch>()
beforeEach(() => vi.stubGlobal('fetch', fetchMock))
afterEach(() => {
  fetchMock.mockReset()
  vi.unstubAllGlobals()
})

it('submits registration as multipart with repeated tag fields and the original avatar bytes', async () => {
  const avatar = new File([Uint8Array.of(1, 2, 3)], 'avatar.png', { type: 'image/png' })
  fetchMock.mockResolvedValueOnce(Response.json({ id: 'new-profile' }, { status: 201 }))

  await expect(liveApi.register({
    email: 'ada@example.com', password: 'example-password', name: 'Ada',
    surname: 'Lovelace', age: 28, gender: 'female', bio: 'Writes code',
    tags: ['python', 'sql'], avatar,
  })).resolves.toEqual({ id: 'new-profile' })

  const [[url, options]] = fetchMock.mock.calls
  expect([url, options?.method]).toEqual(['/api/profiles', 'POST'])
  expect(new Headers(options?.headers).has('content-type')).toBe(false)
  expect(new Headers(options?.headers).has('authorization')).toBe(false)
  const form = options?.body as FormData
  expect(form.getAll('tags')).toEqual(['python', 'sql'])
  expect(form.get('age')).toBe('28')
  const uploadedAvatar = form.get('avatar') as File
  expect([uploadedAvatar.name, uploadedAvatar.type]).toEqual(['avatar.png', 'image/png'])
  expect(new Uint8Array(await uploadedAvatar.arrayBuffer())).toEqual(Uint8Array.of(1, 2, 3))
})

it('maps the candidate profile to the match ID and sends the swipe as a JSON scalar', async () => {
  fetchMock
    .mockResolvedValueOnce(Response.json({ id: 'match-id', targetProfileId: 'profile-id' }))
    .mockResolvedValueOnce(Response.json({
      profile: { id: 'profile-id', name: 'Ada', tags: ['python'] },
    }))
    .mockResolvedValueOnce(new Response(null, { status: 204 }))

  await expect(liveApi.feed(DEFAULT_FILTERS)).resolves.toMatchObject({
    candidates: [expect.objectContaining({ id: 'profile-id', name: 'Ada' })],
  })
  await expect(liveApi.swipe('profile-id', 'like')).resolves.toMatchObject({ decision: 'like' })

  expect(fetchMock.mock.calls.map(([url]) => url)).toEqual([
    '/api/matches', '/api/profiles/profile-id/public', '/api/matches/match-id/swipe',
  ])
  expect(fetchMock.mock.calls[2][1]).toMatchObject({
    method: 'POST', headers: { 'Content-Type': 'application/json' }, body: '"like"',
  })
})

it('keeps chat contact IDs and converts history to chronological order for display', async () => {
  fetchMock
    .mockResolvedValueOnce(Response.json({
      chatIds: ['chat-one', 'chat-two'], chats: [{ id: 'chat-one', contactId: 'other-profile' }],
    }))
    .mockResolvedValueOnce(Response.json({
      chatId: 'chat-one', messages: [{ id: 'newer' }, { id: 'older' }],
    }))

  await expect(liveApi.chats()).resolves.toMatchObject([
    { id: 'chat-one', contactId: 'other-profile' }, { id: 'chat-two', contactId: null },
  ])
  await expect(liveApi.messages('chat-one', 2, 0)).resolves.toEqual({
    chatId: 'chat-one', messages: [{ id: 'older' }, { id: 'newer' }],
  })
  expect(fetchMock.mock.calls[1][0]).toBe('/api/chats/chat-one/messages?limit=2&offset=0')
})
