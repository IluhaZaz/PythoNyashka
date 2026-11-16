import { liveApi } from './live'
import { mockApi } from './mock'
import { hybridApi } from './hybrid'
import type { ApiMode, NyashkaApi } from './contract'

const raw = import.meta.env.VITE_USE_MOCKS ?? 'true'

export type { ApiMode }

export const MODE: ApiMode = raw === 'false' ? 'live' : raw === 'hybrid' ? 'hybrid' : 'mock'
/** Полный мок-режим: демо-автологин, амбиент-события, всё из localStorage. */
export const USE_MOCKS = MODE === 'mock'
export const IS_HYBRID = MODE === 'hybrid'
/** Моковые доменные фичи (лента/мэтчи/чаты) активны. */
export const MOCK_FEATURES = MODE !== 'live'

export const api: NyashkaApi = MODE === 'live' ? liveApi : MODE === 'mock' ? mockApi : hybridApi

export { ApiError } from './http'
export { tokenStore } from './tokens'
export type * from './types'