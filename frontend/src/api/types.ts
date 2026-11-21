import type { ProfileTag } from '@/lib/tags'

export type Gender = 'male' | 'female'
export type SwipeDecision = 'like' | 'dislike'
export type MatchStatus = 'noResponse' | 'accepted' | 'rejected'

/* ── Контракт BFF (openapi/bff/contract.yaml) ─────────────────────────── */

export interface AuthTokens {
  access_token: string
  refresh_token: string
  token_type: 'Bearer'
  expires_in?: number | null
}

export interface Profile {
  id: string
  name: string
  surname: string
  age: number
  bio: string
  gender: Gender
  tags: string[]
  created_at: string
  updated_at: string
  email?: string | null
  avatar?: string | null
}

export interface ProfileCreateInput {
  email: string
  password: string
  name: string
  surname: string
  age: number
  bio: string
  gender: Gender
  tags: ProfileTag[]
  avatar?: File | null
}

export type ProfileUpdateInput = Partial<Omit<ProfileCreateInput, 'email' | 'password'>>

export interface NotificationItem {
  id: string
  profile_id: string
  text: string
  is_read: boolean
  is_sent: boolean
  created_at: string
}

export interface Match {
  id: string
  initiatorProfileId: string
  targetProfileId: string
  status: MatchStatus
  createdAt: string
}

export interface Message {
  id: string
  senderId: string
  text: string
  media: string[]
  sentAt: string
}

export interface ChatMessages {
  chatId: string
  messages: Message[]
}

/* ── Модель приложения ──────────────────────────────────────────────────
   Дополнительные сведения о кандидатах заполняются в демо-режиме. */

export interface PublicProfile {
  id: string
  name: string
  surname: string
  age: number
  gender: Gender
  bio: string
  tags: string[]
  role: string
  city: string
  distanceKm: number
  online: boolean
  lastSeen: string
  matchScore: number
  avatar: string | null
  prompts: { question: string; answer: string }[]
  lookingFor: string
}

export interface ChatSummary {
  id: string
  contactId: string | null
  contact: PublicProfile | null
  lastMessage: Message | null
  unread: number
}

export interface FeedFilters {
  maxDistanceKm: number
  ageMin: number
  ageMax: number
  tags: string[]
  onlineOnly: boolean
}

export const DEFAULT_FILTERS: FeedFilters = {
  maxDistanceKm: 50,
  ageMin: 18,
  ageMax: 35,
  tags: [],
  onlineOnly: false,
}

export interface SwipeResult {
  decision: SwipeDecision
  matched: boolean
  match: Match | null
  chatId: string | null
}

export interface FeedPage {
  candidates: PublicProfile[]
  total: number
  remaining: number
}
