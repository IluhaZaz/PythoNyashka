import type { MediaAttachment } from './contract'
import { tokenStore } from './tokens'
import type { AuthTokens } from './types'

export const API_BASE = import.meta.env.VITE_API_BASE ?? '/api'

export class ApiError extends Error {
  readonly status: number
  readonly fieldErrors: Record<string, string>

  constructor(status: number, message: string, fieldErrors: Record<string, string> = {}) {
    super(message)
    this.name = 'ApiError'
    this.status = status
    this.fieldErrors = fieldErrors
  }
}

interface RequestOptions {
  method?: 'GET' | 'POST' | 'PATCH' | 'DELETE'
  json?: unknown
  form?: FormData
  auth?: boolean
  signal?: AbortSignal
}

const FIELD_LABELS: Record<string, string> = {
  email: 'Почта',
  password: 'Пароль',
  name: 'Имя',
  surname: 'Фамилия',
  age: 'Возраст',
  bio: 'О себе',
  gender: 'Пол',
  tags: 'Теги',
  avatar: 'Аватар',
  old_password: 'Текущий пароль',
  new_password: 'Новый пароль',
  refresh_token: 'Сессия',
}

function humanizeValidation(detail: unknown): { message: string; fields: Record<string, string> } {
  const fields: Record<string, string> = {}
  if (!Array.isArray(detail)) return { message: 'Проверь заполненные поля', fields }

  for (const item of detail) {
    if (!item || typeof item !== 'object') continue
    const entry = item as { loc?: unknown[]; msg?: string }
    const loc = Array.isArray(entry.loc) ? entry.loc : []
    const field = String(loc[loc.length - 1] ?? '')
    const label = FIELD_LABELS[field] ?? field
    const msg = entry.msg ?? 'некорректное значение'
    fields[field] = `${label}: ${msg}`
  }
  const first = Object.values(fields)[0]
  return { message: first ?? 'Проверь заполненные поля', fields }
}

async function toError(response: Response): Promise<ApiError> {
  const text = await response.text().catch(() => '')
  let payload: unknown = null
  try {
    payload = text ? JSON.parse(text) : null
  } catch {
    payload = null
  }

  if (payload && typeof payload === 'object') {
    const record = payload as { error?: unknown; detail?: unknown }
    if (typeof record.error === 'string') return new ApiError(response.status, record.error)
    if (record.detail !== undefined) {
      if (typeof record.detail === 'string') return new ApiError(response.status, record.detail)
      const { message, fields } = humanizeValidation(record.detail)
      return new ApiError(response.status, message, fields)
    }
  }

  const fallback: Record<number, string> = {
    400: 'Некорректный запрос',
    401: 'Сессия истекла — войди заново',
    403: 'Недостаточно прав',
    404: 'Не найдено',
    409: 'Такая запись уже существует',
    413: 'Файл слишком большой',
    422: 'Проверь заполненные поля',
    429: 'Слишком много запросов, подожди чуть-чуть',
    500: 'Сервер заварил кофе и упал. Попробуй ещё раз',
    502: 'Бэкенд недоступен',
    503: 'Сервис временно недоступен',
  }
  return new ApiError(
    response.status,
    fallback[response.status] ?? `Ошибка ${response.status}. Попробуй ещё раз`,
  )
}

let refreshInFlight: Promise<string | null> | null = null

async function refreshAccessToken(): Promise<string | null> {
  const refreshToken = tokenStore.refresh()
  if (!refreshToken) return null

  refreshInFlight ??= (async () => {
    try {
      const response = await fetch(`${API_BASE}/auth/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refreshToken }),
      })
      if (!response.ok) {
        tokenStore.clear()
        return null
      }
      const tokens = (await response.json()) as AuthTokens
      tokenStore.set(tokens)
      return tokens.access_token
    } catch {
      return null
    } finally {
      refreshInFlight = null
    }
  })()

  return refreshInFlight
}

async function send(path: string, options: RequestOptions, token: string | null): Promise<Response> {
  const headers: Record<string, string> = {}
  if (options.json !== undefined) headers['Content-Type'] = 'application/json'
  if (token) headers.Authorization = `Bearer ${token}`

  return fetch(`${API_BASE}${path}`, {
    method: options.method ?? 'GET',
    headers,
    body: options.form ?? (options.json !== undefined ? JSON.stringify(options.json) : undefined),
    signal: options.signal,
  })
}

export async function request<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const useAuth = options.auth !== false
  let response: Response
  try {
    response = await send(path, options, useAuth ? tokenStore.access() : null)
  } catch {
    throw new ApiError(0, 'Нет связи с сервером. Проверь, что BFF запущен на :8003')
  }

  if (response.status === 401 && useAuth && tokenStore.refresh()) {
    const fresh = await refreshAccessToken()
    if (fresh) {
      response = await send(path, options, fresh)
    }
  }

  if (!response.ok) throw await toError(response)
  if (response.status === 204) return undefined as T

  const contentType = response.headers.get('content-type') ?? ''
  if (!contentType.includes('json')) return undefined as T
  return (await response.json()) as T
}

async function mediaResponse(path: string, signal?: AbortSignal): Promise<Response> {
  let response: Response
  try {
    response = await send(path, { signal }, tokenStore.access())
  } catch {
    throw new ApiError(0, 'Нет связи с сервером')
  }
  if (response.status === 401 && tokenStore.refresh()) {
    const fresh = await refreshAccessToken()
    if (fresh) response = await send(path, { signal }, fresh)
  }
  if (!response.ok) throw await toError(response)
  return response
}

export async function requestBlob(path: string, signal?: AbortSignal): Promise<Blob> {
  return (await mediaResponse(path, signal)).blob()
}

function dispositionFileName(header: string | null): string | null {
  if (!header) return null
  const encoded = /(?:^|;)\s*filename\*\s*=\s*UTF-8'[^']*'([^;\s]+)/i.exec(header)?.[1]
  if (encoded) {
    try {
      return decodeURIComponent(encoded)
    } catch {
      // A malformed extended name can still have a valid plain filename.
    }
  }
  const plain = /(?:^|;)\s*filename\s*=\s*(?:"((?:[^"\\]|\\.)*)"|([^;]*))/i.exec(header)
  return plain?.[1]?.replace(/\\(.)/g, '$1') || plain?.[2]?.trim() || null
}

export async function requestAttachment(path: string, signal?: AbortSignal): Promise<MediaAttachment> {
  const response = await mediaResponse(path, signal)
  return {
    blob: await response.blob(),
    fileName: dispositionFileName(response.headers.get('content-disposition')),
  }
}
