import { readJson, writeJson } from '@/lib/storage'
import type { Match, NotificationItem, Profile, PublicProfile } from '@/api/types'
import {
  DEMO_EMAIL,
  DEMO_PASSWORD,
  DEMO_PROFILE,
  ME_ID,
  PEOPLE,
  pid,
  seedChats,
  seedMatches,
  seedNotifications,
  type MockChat,
} from './seed'

const VERSION = 5
const KEY = 'mock-db'

export interface MockAccount {
  email: string
  password: string
  profileId: string
}

export interface SwipeRecord {
  decision: 'like' | 'dislike'
  at: string
  matchId: string | null
  chatId: string | null
}

export interface MockDb {
  version: number
  seq: number
  sessionProfileId: string | null
  accounts: MockAccount[]
  profiles: Record<string, Profile>
  people: PublicProfile[]
  swipes: Record<string, SwipeRecord>
  matches: Match[]
  chats: MockChat[]
  notifications: NotificationItem[]
  media: Record<string, string>
}

function fresh(): MockDb {
  return {
    version: VERSION,
    seq: 20000,
    sessionProfileId: null,
    accounts: [{ email: DEMO_EMAIL, password: DEMO_PASSWORD, profileId: ME_ID }],
    profiles: { [ME_ID]: { ...DEMO_PROFILE } },
    people: PEOPLE.map((person) => ({ ...person })),
    swipes: {},
    matches: seedMatches(),
    chats: seedChats(),
    notifications: seedNotifications(),
    media: {},
  }
}

function load(): MockDb {
  const stored = readJson<MockDb | null>(KEY, null)
  if (!stored || stored.version !== VERSION) return fresh()
  return stored
}

export const db: MockDb = load()

export function save(): void {
  writeJson(KEY, db)
}

export function resetDb(): MockDb {
  const next = fresh()
  Object.assign(db, next)
  save()
  return db
}

/* Мок-транспорт зовёт подписчиков только на фоновых событиях (автоответ,
   входящий лайк), чтобы интерфейс оживал сам, без ручного обновления. */
type Listener = () => void
const listeners = new Set<Listener>()

export function subscribe(listener: Listener): () => void {
  listeners.add(listener)
  return () => listeners.delete(listener)
}

export function emitBackground(): void {
  listeners.forEach((fn) => fn())
}

export const newId = (): string => pid((db.seq += 1))

export function nowIso(): string {
  return new Date().toISOString()
}

export function pushNotification(text: string): NotificationItem {
  const item: NotificationItem = {
    id: newId(),
    profile_id: db.sessionProfileId ?? ME_ID,
    text,
    is_read: false,
    is_sent: true,
    created_at: nowIso(),
  }
  db.notifications.unshift(item)
  return item
}

export function personById(id: string): PublicProfile | null {
  const found = db.people.find((person) => person.id === id)
  if (found) return found
  const profile = db.profiles[id]
  if (!profile) return null
  return {
    id: profile.id,
    name: profile.name,
    surname: profile.surname,
    age: profile.age,
    gender: profile.gender,
    bio: profile.bio,
    tags: profile.tags,
    role: 'участник PythoNyashka',
    city: 'Москва',
    distanceKm: 0,
    online: true,
    lastSeen: nowIso(),
    matchScore: 1,
    avatar: profile.avatar ?? null,
    prompts: [],
    lookingFor: 'Пока не заполнено',
  }
}

export function otherParty(match: Match, meId: string): string {
  return match.initiatorProfileId === meId ? match.targetProfileId : match.initiatorProfileId
}

export function chatWith(contactId: string): MockChat | undefined {
  return db.chats.find((chat) => chat.contactId === contactId)
}

export function openChat(contactId: string): MockChat {
  const existing = chatWith(contactId)
  if (existing) return existing
  const chat: MockChat = { id: newId(), contactId, unread: 0, messages: [] }
  db.chats.unshift(chat)
  return chat
}
