import type { NyashkaApi } from './contract'
import { ApiError, request, requestBlob } from './http'
import { tokenStore } from './tokens'
import type {
  AuthTokens,
  ChatMessages,
  ChatSummary,
  Match,
  NotificationItem,
  Profile,
  ProfileCreateInput,
  ProfileUpdateInput,
  SwipeDecision,
} from './types'

function profileForm(input: ProfileCreateInput | ProfileUpdateInput): FormData {
  const form = new FormData()
  for (const [key, value] of Object.entries(input)) {
    if (value === undefined || value === null) continue
    if (key === 'tags') {
      // OpenAPI: style=form, explode=true — каждый тег отдельным полем.
      for (const tag of value as string[]) form.append('tags', tag)
    } else if (key === 'avatar') {
      form.append('avatar', value as File)
    } else {
      form.append(key, String(value))
    }
  }
  return form
}

const notImplemented = (what: string) =>
  new ApiError(501, `${what} ещё не реализован в BFF — включи VITE_USE_MOCKS=true`)

export const liveApi: NyashkaApi = {
  mode: 'live',

  async login(email, password) {
    const tokens = await request<AuthTokens>('/auth/login', {
      method: 'POST',
      json: { email, password },
      auth: false,
    })
    tokenStore.set(tokens)
    return tokens
  },

  register(input) {
    return request<{ id: string }>('/profiles', {
      method: 'POST',
      form: profileForm(input),
      auth: false,
    })
  },

  async logout() {
    const refresh_token = tokenStore.refresh()
    try {
      if (refresh_token) {
        await request<void>('/auth/logout', { method: 'POST', json: { refresh_token } })
      }
    } finally {
      tokenStore.clear()
    }
  },

  async changePassword(oldPassword, newPassword) {
    await request<void>('/auth/password/change', {
      method: 'POST',
      json: { old_password: oldPassword, new_password: newPassword },
    })
    tokenStore.clear()
  },

  async getProfile() {
    const data = await request<{ profile: Profile }>('/profiles')
    return data.profile
  },

  updateProfile(input) {
    return request<void>('/profiles', { method: 'PATCH', form: profileForm(input) })
  },

  mediaBlob(mediaId, signal) {
    return requestBlob(`/media/${mediaId}`, signal)
  },

  async notifications(limit, offset) {
    const data = await request<{ notifications: NotificationItem[] }>(
      `/notifications?limit=${limit}&offset=${offset}`,
    )
    return data.notifications
  },

  markNotificationRead(id) {
    return request<void>(`/notifications/${id}/read`, { method: 'POST' })
  },

  feed() {
    return Promise.reject(notImplemented('Эндпоинт ленты'))
  },

  swipe() {
    return Promise.reject(notImplemented('Свайп по анкете'))
  },

  undoSwipe() {
    return Promise.reject(notImplemented('Отмена свайпа'))
  },

  publicProfile() {
    return Promise.resolve(null)
  },

  currentMatch() {
    return request<Match>('/matches').catch((error: unknown) => {
      if (error instanceof ApiError && error.status === 404) return null
      throw error
    })
  },

  async matchHistory(limit, offset) {
    const data = await request<{ matches: Match[] }>(
      `/matches/history?limit=${limit}&offset=${offset}`,
    )
    return data.matches ?? []
  },

  answerMatch(matchId, decision: SwipeDecision) {
    return request<void>(`/matches/${matchId}/swipe`, { method: 'POST', json: decision })
  },

  async chats() {
    const data = await request<{ chatIds: string[] }>('/chats')
    // Контракт отдаёт только id: участников и превью пока неоткуда взять.
    return (data.chatIds ?? []).map<ChatSummary>((id) => ({
      id,
      contact: null,
      lastMessage: null,
      unread: 0,
    }))
  },

  createChat(contactIds) {
    return request<{ id: string }>('/chats', { method: 'POST', json: { contactIds } })
  },

  messages(chatId, limit, offset) {
    return request<ChatMessages>(`/chats/${chatId}/messages?limit=${limit}&offset=${offset}`)
  },

  sendMessage(chatId, text, media) {
    const form = new FormData()
    form.append('text', text)
    for (const file of media) form.append('media', file)
    return request<void>(`/chats/${chatId}/message`, { method: 'POST', form })
  },
}
