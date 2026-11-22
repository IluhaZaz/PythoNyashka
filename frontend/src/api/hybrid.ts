import { ApiError } from './http'
import type { NyashkaApi } from './contract'
import { liveApi } from './live'
import { ensureMockSession, mockApi } from './mock'

function withMockSession<T>(fn: () => Promise<T>): Promise<T> {
  ensureMockSession()
  return fn()
}

/**
 * Гибрид: реализованное на BFF ходит вживую (auth, профиль, медиа, уведомления),
 * отсутствующее на бэке (лента/мэтчи/чаты) обслуживает сидированный мок.
 */
export const hybridApi: NyashkaApi = {
  mode: 'hybrid',

  login(email, password) {
    return liveApi.login(email, password)
  },
  register(input) {
    return liveApi.register(input)
  },
  logout() {
    return liveApi.logout()
  },
  changePassword(oldPassword, newPassword) {
    return liveApi.changePassword(oldPassword, newPassword)
  },
  getProfile() {
    return liveApi.getProfile()
  },
  updateProfile(input) {
    return liveApi.updateProfile(input)
  },

  // UUID моков неотличимы от uuid медиа-сервиса: сперва живой запрос,
  // при 404/0 — моковый dataURL/SVG из db.media.
  async mediaBlob(mediaId, signal) {
    try {
      return await liveApi.mediaBlob(mediaId, signal)
    } catch (error) {
      if (error instanceof ApiError) return mockApi.mediaBlob(mediaId, signal)
      throw error
    }
  },

  attachment(mediaId, signal) {
    return withMockSession(() => mockApi.attachment(mediaId, signal))
  },

  notifications(limit, offset) {
    return liveApi.notifications(limit, offset)
  },
  markNotificationRead(id) {
    return liveApi.markNotificationRead(id)
  },

  feed(filters) {
    return withMockSession(() => mockApi.feed(filters))
  },
  swipe(profileId, decision) {
    return withMockSession(() => mockApi.swipe(profileId, decision))
  },
  undoSwipe(profileId) {
    return withMockSession(() => mockApi.undoSwipe(profileId))
  },
  publicProfile(id) {
    return withMockSession(() => mockApi.publicProfile(id))
  },
  currentMatch() {
    return withMockSession(() => mockApi.currentMatch())
  },
  matchHistory(limit, offset) {
    return withMockSession(() => mockApi.matchHistory(limit, offset))
  },
  answerMatch(matchId, decision) {
    return withMockSession(() => mockApi.answerMatch(matchId, decision))
  },
  chats() {
    return withMockSession(() => mockApi.chats())
  },
  createChat(contactIds) {
    return withMockSession(() => mockApi.createChat(contactIds))
  },
  messages(chatId, limit, offset) {
    return withMockSession(() => mockApi.messages(chatId, limit, offset))
  },
  sendMessage(chatId, text, media) {
    return withMockSession(() => mockApi.sendMessage(chatId, text, media))
  },
}