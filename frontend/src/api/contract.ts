import type {
  AuthTokens,
  ChatMessages,
  ChatSummary,
  FeedFilters,
  FeedPage,
  Match,
  NotificationItem,
  Profile,
  ProfileCreateInput,
  ProfileUpdateInput,
  PublicProfile,
  SwipeDecision,
  SwipeResult,
} from './types'

export type ApiMode = 'mock' | 'live' | 'hybrid'

export interface NyashkaApi {
  readonly mode: ApiMode

  login(email: string, password: string): Promise<AuthTokens>
  register(input: ProfileCreateInput): Promise<{ id: string }>
  logout(): Promise<void>
  changePassword(oldPassword: string, newPassword: string): Promise<void>

  getProfile(): Promise<Profile>
  updateProfile(input: ProfileUpdateInput): Promise<void>
  mediaBlob(mediaId: string, signal?: AbortSignal): Promise<Blob>

  notifications(limit: number, offset: number): Promise<NotificationItem[]>
  markNotificationRead(id: string): Promise<void>

  feed(filters: FeedFilters): Promise<FeedPage>
  swipe(profileId: string, decision: SwipeDecision): Promise<SwipeResult>
  undoSwipe(profileId: string): Promise<void>
  publicProfile(id: string): Promise<PublicProfile | null>

  currentMatch(): Promise<Match | null>
  matchHistory(limit: number, offset: number): Promise<Match[]>
  answerMatch(matchId: string, decision: SwipeDecision): Promise<void>

  chats(): Promise<ChatSummary[]>
  createChat(contactIds: string[]): Promise<{ id: string }>
  messages(chatId: string, limit: number, offset: number): Promise<ChatMessages>
  sendMessage(chatId: string, text: string, media: File[]): Promise<void>
}
