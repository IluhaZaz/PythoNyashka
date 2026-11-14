import type { NyashkaApi } from './contract'
import { liveApi } from './live'
import { mockApi } from './mock'

export const USE_MOCKS = (import.meta.env.VITE_USE_MOCKS ?? 'true') !== 'false'

export const api: NyashkaApi = USE_MOCKS ? mockApi : liveApi

export { ApiError } from './http'
export { tokenStore } from './tokens'
export type * from './types'
