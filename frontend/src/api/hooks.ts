import { useEffect } from 'react'
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { MOCK_FEATURES, USE_MOCKS, api } from '@/api'
import type { FeedFilters, SwipeDecision } from '@/api/types'
import { mockSubscribe, mockTyping } from '@/api/mock'

export const keys = {
  profile: ['profile'] as const,
  notifications: ['notifications'] as const,
  matches: ['matches'] as const,
  currentMatch: ['matches', 'current'] as const,
  chats: ['chats'] as const,
  messages: (chatId: string) => ['chats', chatId, 'messages'] as const,
  feed: (filters: FeedFilters) => ['feed', filters] as const,
  person: (id: string) => ['person', id] as const,
}

/** Фоновые события мока (автоответ, входящий лайк) сами обновляют кэш. */
export function useMockSync(): void {
  const queryClient = useQueryClient()
  useEffect(() => {
    if (!MOCK_FEATURES) return
    return mockSubscribe(() => {
      void queryClient.invalidateQueries({ queryKey: keys.chats })
      void queryClient.invalidateQueries({ queryKey: keys.notifications })
      void queryClient.invalidateQueries({ queryKey: keys.matches })
      void queryClient.invalidateQueries({ queryKey: ['feed'] })
    })
  }, [queryClient])
}

export function useChatTyping(chatId: string | null): boolean {
  const queryClient = useQueryClient()
  const query = useQuery({
    queryKey: ['typing', chatId],
    queryFn: () => (chatId ? mockTyping.has(chatId) : false),
    enabled: MOCK_FEATURES && Boolean(chatId),
    initialData: false,
  })
  useEffect(() => {
    if (!MOCK_FEATURES) return
    return mockSubscribe(() => {
      void queryClient.invalidateQueries({ queryKey: ['typing', chatId] })
    })
  }, [chatId, queryClient])
  return query.data
}

export function useNotifications(limit = 30) {
  return useQuery({
    queryKey: keys.notifications,
    queryFn: () => api.notifications(limit, 0),
    refetchInterval: USE_MOCKS ? false : 30_000,
  })
}

export function useMarkRead() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (id: string) => api.markNotificationRead(id),
    onMutate: async (id) => {
      await queryClient.cancelQueries({ queryKey: keys.notifications })
      const previous = queryClient.getQueryData<Awaited<ReturnType<typeof api.notifications>>>(
        keys.notifications,
      )
      queryClient.setQueryData(keys.notifications, (list: typeof previous) =>
        list?.map((item) => (item.id === id ? { ...item, is_read: true } : item)),
      )
      return { previous }
    },
    onError: (_error, _id, context) => {
      if (context?.previous) queryClient.setQueryData(keys.notifications, context.previous)
    },
    onSettled: () => queryClient.invalidateQueries({ queryKey: keys.notifications }),
  })
}

export function useMatchHistory(limit = 50) {
  return useQuery({
    queryKey: keys.matches,
    queryFn: () => api.matchHistory(limit, 0),
  })
}

export function useCurrentMatch() {
  return useQuery({ queryKey: keys.currentMatch, queryFn: () => api.currentMatch() })
}

export function useAnswerMatch() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, decision }: { id: string; decision: SwipeDecision }) =>
      api.answerMatch(id, decision),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['matches'] })
      void queryClient.invalidateQueries({ queryKey: keys.chats })
      void queryClient.invalidateQueries({ queryKey: keys.notifications })
      void queryClient.invalidateQueries({ queryKey: ['feed'] })
    },
  })
}

export function useChats() {
  return useQuery({ queryKey: keys.chats, queryFn: () => api.chats() })
}

export function useMessages(chatId: string | null) {
  return useQuery({
    queryKey: keys.messages(chatId ?? 'none'),
    queryFn: () => api.messages(chatId!, 200, 0),
    enabled: Boolean(chatId),
    refetchInterval: MOCK_FEATURES ? false : 3_000,
    refetchOnWindowFocus: MOCK_FEATURES ? false : 'always',
  })
}

export function useSendMessage(chatId: string) {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ text, media }: { text: string; media: File[] }) =>
      api.sendMessage(chatId, text, media),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: keys.messages(chatId) })
      void queryClient.invalidateQueries({ queryKey: keys.chats })
    },
  })
}

export function useCreateChat() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (contactIds: string[]) => api.createChat(contactIds),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: keys.chats }),
  })
}

export function useFeed(filters: FeedFilters) {
  return useQuery({
    queryKey: keys.feed(filters),
    queryFn: () => api.feed(filters),
    placeholderData: (previous) => previous,
  })
}

export function usePerson(id: string | null) {
  return useQuery({
    queryKey: keys.person(id ?? 'none'),
    queryFn: () => api.publicProfile(id!),
    enabled: Boolean(id),
  })
}

export function useSwipe() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ profileId, decision }: { profileId: string; decision: SwipeDecision }) =>
      api.swipe(profileId, decision),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['matches'] })
      void queryClient.invalidateQueries({ queryKey: keys.chats })
      void queryClient.invalidateQueries({ queryKey: keys.notifications })
    },
  })
}

export function useUndoSwipe() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: (profileId: string) => api.undoSwipe(profileId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ['feed'] })
      void queryClient.invalidateQueries({ queryKey: ['matches'] })
      void queryClient.invalidateQueries({ queryKey: keys.chats })
    },
  })
}
