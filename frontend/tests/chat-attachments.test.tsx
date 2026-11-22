// @vitest-environment jsdom
import { cleanup, fireEvent, render, screen, waitFor } from '@testing-library/react'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { afterEach, expect, it, vi } from 'vitest'
import { tokenStore } from '@/api/tokens'
import { ChatsPage } from '@/pages/ChatsPage'
import { AuthProvider } from '@/state/auth'
import { ToastProvider } from '@/state/toast'

vi.hoisted(() => {
  vi.stubEnv('VITE_USE_MOCKS', 'false')
  vi.stubEnv('VITE_API_BASE', '/api')
})

afterEach(() => {
  cleanup()
  tokenStore.clear()
  vi.unstubAllGlobals()
})

it('loads the actual image, downloads a document by its name and can send that file type', async () => {
  const imageId = '00000000-0000-4000-8000-000000000011'
  const documentId = '00000000-0000-4000-8000-000000000012'
  const unavailableId = '00000000-0000-4000-8000-000000000013'
  const createObjectURL = vi.fn((blob: Blob) =>
    blob.type === 'image/png' ? 'blob:photo' : 'blob:document',
  )
  vi.stubGlobal('URL', class extends URL {
    static createObjectURL = createObjectURL
    static revokeObjectURL = vi.fn()
  })
  tokenStore.set({ access_token: 'chat-session', refresh_token: 'test-refresh', token_type: 'Bearer' })

  const fetchMock = vi.fn<typeof fetch>().mockImplementation(async (url) => {
    switch (url) {
      case '/api/profiles':
        return Response.json({ profile: { id: 'me' } })
      case '/api/chats':
        return Response.json({ chatIds: ['chat-one'] })
      case '/api/chats/chat-one/messages?limit=200&offset=0':
        return Response.json({
          chatId: 'chat-one',
          messages: [{
            id: 'message-one', senderId: 'me', sentAt: '2026-11-23T00:00:00Z', text: '',
            media: ['http://bff:8000/media/' + imageId, '/api/media/' + documentId, unavailableId],
          }],
        })
      case '/api/media/' + imageId:
        return new Response(Uint8Array.of(137, 80, 78, 71), { headers: {
          'Content-Type': 'image/png',
          'Content-Disposition': "inline; filename*=UTF-8''%D1%84%D0%BE%D1%82%D0%BE.png",
        } })
      case '/api/media/' + documentId:
        return new Response('%PDF', { headers: {
          'Content-Type': 'application/pdf',
          'Content-Disposition': 'inline; filename="report; draft.pdf"',
        } })
      case '/api/media/' + unavailableId:
        return new Response(null, { status: 404 })
      case '/api/chats/chat-one/message':
        return new Response(null, { status: 204 })
      default:
        throw new Error('Unexpected request: ' + url)
    }
  })
  vi.stubGlobal('fetch', fetchMock)
  const { container } = render(
    <QueryClientProvider client={new QueryClient({ defaultOptions: { queries: { retry: false } } })}>
      <MemoryRouter initialEntries={['/chats/chat-one']}>
        <AuthProvider>
          <ToastProvider>
            <Routes>
              <Route path="/chats/:chatId" element={<ChatsPage />} />
            </Routes>
          </ToastProvider>
        </AuthProvider>
      </MemoryRouter>
    </QueryClientProvider>,
  )

  const image = await screen.findByRole('img', { name: 'фото.png' })
  expect(image.getAttribute('src')).toBe('blob:photo')
  expect(fetchMock).toHaveBeenCalledWith('/api/media/' + imageId, expect.objectContaining({
    headers: { Authorization: 'Bearer chat-session' },
  }))
  const document = await screen.findByRole('link', { name: 'Скачать report; draft.pdf' })
  expect(document.getAttribute('download')).toBe('report; draft.pdf')
  expect(document.querySelector('img')).toBeNull()
  expect(await screen.findByText('Вложение недоступно')).toBeTruthy()
  const photoBlob = createObjectURL.mock.calls.find(([blob]) => blob.type === 'image/png')?.[0]
  expect(new Uint8Array(await photoBlob!.arrayBuffer())).toEqual(Uint8Array.of(137, 80, 78, 71))

  const picker = container.querySelector('input[type=file]')!
  expect(picker.hasAttribute('accept')).toBe(false)
  const file = new File(['%PDF'], 'new-report.pdf', { type: 'application/pdf' })
  fireEvent.change(picker, { target: { files: [file] } })
  expect(screen.getByText(file.name)).toBeTruthy()
  fireEvent.click(screen.getByRole('button', { name: 'Отправить' }))
  await waitFor(() => expect(fetchMock).toHaveBeenCalledWith(
    '/api/chats/chat-one/message', expect.objectContaining({ method: 'POST' }),
  ))
  const upload = fetchMock.mock.calls.find(([url]) => url === '/api/chats/chat-one/message')
  expect((upload?.[1]?.body as FormData).getAll('media')).toEqual([file])
})
