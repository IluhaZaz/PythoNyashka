import { ApiError } from '@/api/http'
import { tokenStore } from '@/api/tokens'
import type { NyashkaApi } from '@/api/contract'
import type {
  AuthTokens,
  ChatMessages,
  ChatSummary,
  FeedFilters,
  FeedPage,
  Match,
  Profile,
  SwipeDecision,
  SwipeResult,
} from '@/api/types'
import { avatarSvg } from '@/lib/avatar'
import {
  db,
  emitBackground,
  newId,
  nowIso,
  openChat,
  otherParty,
  personById,
  pushNotification,
  resetDb,
  save,
  subscribe,
} from './db'
import { CHAT_REPLIES, DEMO_EMAIL, ME_ID, pid } from './seed'

const wait = (ms: number) => new Promise((resolve) => setTimeout(resolve, ms))
const latency = () => wait(120 + Math.random() * 220)

export const mockTyping = new Set<string>()
export const mockSubscribe = subscribe
export const mockReset = resetDb

/**
 * В hybrid-режиме мок обслуживает ленту/мэтчи/чаты без своего логина,
 * а real-JWT сессия не пишет db.sessionProfileId — подкладываем демо-профиль.
 */
export function ensureMockSession(): void {
  if (!db.sessionProfileId) {
    db.sessionProfileId = ME_ID
    save()
  }
}

function currentProfileId(): string {
  if (!db.sessionProfileId) throw new ApiError(401, 'Сессия истекла — войди заново')
  return db.sessionProfileId
}

function makeTokens(profileId: string): AuthTokens {
  const tokens: AuthTokens = {
    access_token: `mock-access.${profileId}.${Date.now()}`,
    refresh_token: `mock-refresh.${profileId}.${Date.now()}`,
    token_type: 'Bearer',
    expires_in: 900,
  }
  db.sessionProfileId = profileId
  tokenStore.set(tokens)
  save()
  return tokens
}

function fileToDataUrl(file: File): Promise<string> {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result))
    reader.onerror = () => reject(new ApiError(400, 'Не удалось прочитать файл'))
    reader.readAsDataURL(file)
  })
}

/** Автоматическая «няшка» на другом конце провода. */
function scheduleReply(chatId: string, contactId: string): void {
  const chat = db.chats.find((item) => item.id === chatId)
  if (!chat) return

  window.setTimeout(() => {
    mockTyping.add(chatId)
    emitBackground()
  }, 700)

  window.setTimeout(
    () => {
      mockTyping.delete(chatId)
      const person = personById(contactId)
      const text = CHAT_REPLIES[Math.floor(Math.random() * CHAT_REPLIES.length)]
      chat.messages.push({
        id: newId(),
        senderId: contactId,
        text,
        media: [],
        sentAt: nowIso(),
      })
      chat.unread += 1
      pushNotification(`${person?.name ?? 'Собеседник'} ответила в чате: «${text}»`)
      save()
      emitBackground()
    },
    2200 + Math.random() * 1600,
  )
}

let ambientStarted = false

/** Один срежиссированный входящий лайк, чтобы приложение жило само. */
export function startAmbient(): void {
  if (ambientStarted) return
  ambientStarted = true

  window.setTimeout(() => {
    const admirerId = pid(6)
    if (!db.sessionProfileId) return
    if (db.matches.some((match) => otherParty(match, db.sessionProfileId!) === admirerId)) return

    const person = personById(admirerId)
    db.matches.unshift({
      id: newId(),
      initiatorProfileId: admirerId,
      targetProfileId: db.sessionProfileId,
      status: 'noResponse',
      createdAt: nowIso(),
    })
    delete db.swipes[admirerId]
    pushNotification(`${person?.name ?? 'Кто-то'} лайкнула твою анкету. Ответь, чтобы получить мэтч.`)
    save()
    emitBackground()
  }, 32_000)
}

function acceptMatch(match: Match): { chatId: string } {
  match.status = 'accepted'
  const contactId = otherParty(match, currentProfileId())
  const chat = openChat(contactId)
  const person = personById(contactId)
  pushNotification(`Новый мэтч: ${person?.name ?? 'кто-то'} ${person?.surname ?? ''}. Напиши первым.`)
  return { chatId: chat.id }
}

export const mockApi: NyashkaApi = {
  mode: 'mock',

  async login(email, password) {
    await latency()
    const account = db.accounts.find(
      (item) => item.email.toLowerCase() === email.trim().toLowerCase(),
    )
    if (!account || account.password !== password) {
      throw new ApiError(401, 'Неверная почта или пароль')
    }
    return makeTokens(account.profileId)
  },

  async register(input) {
    await latency()
    const email = input.email.trim().toLowerCase()
    if (db.accounts.some((item) => item.email.toLowerCase() === email)) {
      throw new ApiError(409, 'Профиль с такой почтой уже существует')
    }
    const id = newId()
    let avatar: string | null = null
    if (input.avatar) {
      avatar = newId()
      db.media[avatar] = await fileToDataUrl(input.avatar)
    }
    const profile: Profile = {
      id,
      name: input.name,
      surname: input.surname,
      age: input.age,
      bio: input.bio,
      gender: input.gender,
      tags: input.tags,
      created_at: nowIso(),
      updated_at: nowIso(),
      email,
      avatar,
    }
    db.profiles[id] = profile
    db.accounts.push({ email, password: input.password, profileId: id })
    pushNotification('Добро пожаловать в PythoNyashka 🐍 Первые анкеты уже ждут.')
    save()
    return { id }
  },

  async logout() {
    await wait(80)
    db.sessionProfileId = null
    tokenStore.clear()
    save()
  },

  async changePassword(oldPassword, newPassword) {
    await latency()
    const id = currentProfileId()
    const account = db.accounts.find((item) => item.profileId === id)
    if (!account || account.password !== oldPassword) {
      throw new ApiError(400, 'Текущий пароль неверный')
    }
    account.password = newPassword
    db.sessionProfileId = null
    tokenStore.clear()
    save()
  },

  async getProfile() {
    await latency()
    const id = currentProfileId()
    const profile = db.profiles[id]
    if (!profile) throw new ApiError(404, 'Анкета не найдена')
    return { ...profile }
  },

  async updateProfile(input) {
    await latency()
    const id = currentProfileId()
    const profile = db.profiles[id]
    if (!profile) throw new ApiError(404, 'Анкета не найдена')

    if (input.avatar) {
      const mediaId = newId()
      db.media[mediaId] = await fileToDataUrl(input.avatar)
      profile.avatar = mediaId
    }
    if (input.name !== undefined) profile.name = input.name
    if (input.surname !== undefined) profile.surname = input.surname
    if (input.age !== undefined) profile.age = input.age
    if (input.bio !== undefined) profile.bio = input.bio
    if (input.gender !== undefined) profile.gender = input.gender
    if (input.tags !== undefined) profile.tags = [...input.tags]
    profile.updated_at = nowIso()
    save()
  },

  async mediaBlob(mediaId) {
    const stored = db.media[mediaId]
    const svg = stored ?? `data:image/svg+xml;charset=utf-8,${encodeURIComponent(avatarSvg(mediaId))}`
    const response = await fetch(svg)
    return response.blob()
  },

  async notifications(limit, offset) {
    await wait(90)
    return [...db.notifications]
      .sort((a, b) => b.created_at.localeCompare(a.created_at))
      .slice(offset, offset + limit)
      .map((item) => ({ ...item }))
  },

  async markNotificationRead(id) {
    await wait(60)
    const item = db.notifications.find((entry) => entry.id === id)
    if (!item) throw new ApiError(404, 'Уведомление не найдено')
    item.is_read = true
    save()
  },

  async feed(filters: FeedFilters) {
    await latency()
    const meId = currentProfileId()
    const blocked = new Set(
      db.matches.map((match) => otherParty(match, meId)),
    )
    const candidates = db.people
      .filter((person) => !db.swipes[person.id] && !blocked.has(person.id))
      .filter((person) => person.distanceKm <= filters.maxDistanceKm)
      .filter((person) => person.age >= filters.ageMin && person.age <= filters.ageMax)
      .filter((person) => !filters.onlineOnly || person.online)
      .filter(
        (person) =>
          filters.tags.length === 0 ||
          filters.tags.every((tag) => person.tags.includes(tag)),
      )
      .sort((a, b) => b.matchScore - a.matchScore)

    return {
      candidates: candidates.map((person) => ({ ...person })),
      total: db.people.length,
      remaining: candidates.length,
    } satisfies FeedPage
  },

  async swipe(profileId, decision: SwipeDecision) {
    await wait(160)
    const meId = currentProfileId()
    const person = personById(profileId)
    if (!person) throw new ApiError(404, 'Анкета не найдена')

    const pending = db.matches.find(
      (match) => match.status === 'noResponse' && otherParty(match, meId) === profileId,
    )

    let match: Match | null = null
    let chatId: string | null = null

    if (decision === 'like') {
      if (pending && pending.initiatorProfileId === profileId) {
        match = pending
        chatId = acceptMatch(pending).chatId
      } else if (person.matchScore >= 0.85) {
        match = {
          id: newId(),
          initiatorProfileId: meId,
          targetProfileId: profileId,
          status: 'accepted',
          createdAt: nowIso(),
        }
        db.matches.unshift(match)
        chatId = openChat(profileId).id
        pushNotification(`Взаимно! ${person.name} ${person.surname} тоже считает тебя няшкой.`)
      } else {
        match = {
          id: newId(),
          initiatorProfileId: meId,
          targetProfileId: profileId,
          status: 'noResponse',
          createdAt: nowIso(),
        }
        db.matches.unshift(match)
      }
    }

    db.swipes[profileId] = {
      decision,
      at: nowIso(),
      matchId: match?.id ?? null,
      chatId,
    }
    save()

    return {
      decision,
      matched: match?.status === 'accepted',
      match,
      chatId,
    } satisfies SwipeResult
  },

  async undoSwipe(profileId) {
    await wait(80)
    const record = db.swipes[profileId]
    if (!record) return
    if (record.matchId) {
      db.matches = db.matches.filter((match) => match.id !== record.matchId)
    }
    if (record.chatId) {
      const chat = db.chats.find((item) => item.id === record.chatId)
      if (chat && chat.messages.length === 0) {
        db.chats = db.chats.filter((item) => item.id !== record.chatId)
      }
    }
    delete db.swipes[profileId]
    save()
  },

  async publicProfile(id) {
    await wait(80)
    const person = personById(id)
    return person ? { ...person } : null
  },

  async currentMatch() {
    await wait(90)
    const meId = currentProfileId()
    return (
      db.matches.find((match) => match.status === 'noResponse' && match.targetProfileId === meId) ??
      null
    )
  },

  async matchHistory(limit, offset) {
    await wait(90)
    return [...db.matches]
      .sort((a, b) => b.createdAt.localeCompare(a.createdAt))
      .slice(offset, offset + limit)
      .map((match) => ({ ...match }))
  },

  async answerMatch(matchId, decision) {
    await wait(140)
    const match = db.matches.find((item) => item.id === matchId)
    if (!match) throw new ApiError(404, 'Мэтч не найден')
    if (decision === 'like') {
      acceptMatch(match)
    } else {
      match.status = 'rejected'
      db.swipes[otherParty(match, currentProfileId())] = {
        decision: 'dislike',
        at: nowIso(),
        matchId: match.id,
        chatId: null,
      }
    }
    save()
  },

  async chats() {
    await wait(110)
    return db.chats
      .map<ChatSummary>((chat) => ({
        id: chat.id,
        contact: personById(chat.contactId),
        lastMessage: chat.messages.at(-1) ?? null,
        unread: chat.unread,
      }))
      .sort((a, b) =>
        (b.lastMessage?.sentAt ?? '').localeCompare(a.lastMessage?.sentAt ?? ''),
      )
  },

  async createChat(contactIds) {
    await wait(120)
    const contactId = contactIds[0]
    if (!contactId) throw new ApiError(400, 'Не выбран собеседник')
    const chat = openChat(contactId)
    save()
    return { id: chat.id }
  },

  async messages(chatId, limit, offset) {
    await wait(120)
    const chat = db.chats.find((item) => item.id === chatId)
    if (!chat) throw new ApiError(404, 'Чат не найден')
    chat.unread = 0
    save()
    const ordered = [...chat.messages].sort((a, b) => a.sentAt.localeCompare(b.sentAt))
    const end = Math.max(ordered.length - offset, 0)
    return {
      chatId,
      messages: ordered.slice(Math.max(end - limit, 0), end),
    } satisfies ChatMessages
  },

  async sendMessage(chatId, text, media) {
    await wait(180)
    const chat = db.chats.find((item) => item.id === chatId)
    if (!chat) throw new ApiError(404, 'Чат не найден')
    const attachments: string[] = []
    for (const file of media) {
      const mediaId = newId()
      db.media[mediaId] = await fileToDataUrl(file)
      attachments.push(`/api/media/${mediaId}`)
    }
    chat.messages.push({
      id: newId(),
      senderId: currentProfileId(),
      text,
      media: attachments,
      sentAt: nowIso(),
    })
    save()
    scheduleReply(chatId, chat.contactId)
  },
}

export { ME_ID, DEMO_EMAIL }
