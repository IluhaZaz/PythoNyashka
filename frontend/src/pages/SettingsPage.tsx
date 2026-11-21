import { useState } from 'react'
import type { FormEvent } from 'react'
import { useNavigate } from 'react-router-dom'
import { ApiError, IS_HYBRID, USE_MOCKS, api } from '@/api'
import { API_BASE } from '@/api/http'
import { mockReset } from '@/api/mock'
import { cn } from '@/lib/cn'
import { useAuth } from '@/state/auth'
import { useToast } from '@/state/toast'
import { Button } from '@/components/ui/Button'
import { SectionTitle } from '@/components/ui/Feedback'
import { PasswordField } from '@/components/ui/Field'
import { Icon } from '@/components/ui/Icon'
import { Modal } from '@/components/ui/Modal'

export function SettingsPage() {
  const { profile, logout } = useAuth()
  const { push } = useToast()
  const navigate = useNavigate()

  const [oldPassword, setOldPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [repeat, setRepeat] = useState('')
  const [errors, setErrors] = useState<Record<string, string>>({})
  const [busy, setBusy] = useState(false)
  const [confirmReset, setConfirmReset] = useState(false)

  const changePassword = async (event: FormEvent) => {
    event.preventDefault()
    const next: Record<string, string> = {}
    if (!oldPassword) next.old_password = 'Введи текущий пароль'
    if (newPassword.length < 8) next.new_password = 'Минимум 8 символов'
    if (newPassword === oldPassword && newPassword) next.new_password = 'Новый пароль совпадает со старым'
    if (repeat !== newPassword) next.repeat = 'Пароли не совпадают'
    setErrors(next)
    if (Object.keys(next).length) return

    setBusy(true)
    try {
      await api.changePassword(oldPassword, newPassword)
      push({
        tone: 'mint',
        emoji: '🔒',
        title: 'Пароль изменён',
        text: 'Все сессии закрыты — войди с новым паролем.',
      })
      navigate('/login', { replace: true })
    } catch (error) {
      if (error instanceof ApiError) {
        setErrors(error.fieldErrors ?? {})
        push({ tone: 'coral', title: 'Не получилось', text: error.message })
      } else {
        push({ tone: 'coral', title: 'Сервер не ответил' })
      }
    } finally {
      setBusy(false)
    }
  }

  const exportProfile = () => {
    if (!profile) return
    const blob = new Blob([JSON.stringify(profile, null, 2)], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `nyashka-profile-${profile.id.slice(0, 8)}.json`
    link.click()
    URL.revokeObjectURL(url)
    push({ tone: 'sky', emoji: '📦', title: 'Анкета выгружена', text: 'JSON сохранён в загрузки.' })
  }

  const doReset = () => {
    mockReset()
    setConfirmReset(false)
    push({ tone: 'sun', emoji: '🧪', title: 'Демо сброшено', text: 'Перезагружаю…' })
    window.setTimeout(() => window.location.reload(), 700)
  }

  return (
    <div className="mx-auto max-w-3xl">
      <SectionTitle eyebrow="аккаунт" title="Настройки" />

      <div className="space-y-5">
        <section className="card p-6">
          <p className="panel-title mb-4">аккаунт</p>
          <dl className="grid gap-3 sm:grid-cols-2">
            {[
              { label: 'Почта', value: profile?.email ?? '—' },
              { label: 'Имя', value: `${profile?.name ?? ''} ${profile?.surname ?? ''}`.trim() || '—' },
              { label: 'ID профиля', value: profile?.id ?? '—', mono: true },
              { label: 'Тегов в анкете', value: String(profile?.tags.length ?? 0) },
            ].map((row) => (
              <div key={row.label} className="rounded-2xl bg-cream-deep/60 px-4 py-3">
                <dt className="text-[11.5px] font-bold text-dim">{row.label}</dt>
                <dd className={cn('mt-0.5 truncate text-[13.5px] font-semibold', row.mono && 'font-mono text-[12px]')}>
                  {row.value}
                </dd>
              </div>
            ))}
          </dl>
        </section>

        <section className="card p-6">
          <p className="panel-title mb-1">безопасность</p>
          <h2 className="text-xl">Смена пароля</h2>
          <p className="hint mt-1">После смены все активные сессии завершатся.</p>

          <form className="mt-5 space-y-4" onSubmit={changePassword} noValidate>
            <PasswordField
              label="Текущий пароль"
              autoComplete="current-password"
              value={oldPassword}
              error={errors.old_password}
              onChange={(event) => setOldPassword(event.target.value)}
            />
            <div className="grid gap-4 sm:grid-cols-2">
              <PasswordField
                label="Новый пароль"
                autoComplete="new-password"
                value={newPassword}
                error={errors.new_password}
                onChange={(event) => setNewPassword(event.target.value)}
              />
              <PasswordField
                label="Повтори новый"
                autoComplete="new-password"
                value={repeat}
                error={errors.repeat}
                onChange={(event) => setRepeat(event.target.value)}
              />
            </div>
            <Button type="submit" icon="lock" loading={busy}>
              Изменить пароль
            </Button>
          </form>
        </section>

        <section className="card p-6">
          <p className="panel-title mb-4">данные и режим</p>

          <div
            className={cn(
              'flex items-start gap-3 rounded-2xl border px-4 py-3',
              USE_MOCKS
                ? 'border-sun/50 bg-sun-soft'
                : IS_HYBRID
                  ? 'border-sky/40 bg-sky-soft'
                  : 'border-mint/40 bg-mint-soft',
            )}
          >
            <Icon
              name={USE_MOCKS ? 'code' : IS_HYBRID ? 'spark' : 'check'}
              size={18}
              className={cn(
                'mt-0.5 shrink-0',
                USE_MOCKS ? 'text-sun-deep' : IS_HYBRID ? 'text-sky-deep' : 'text-mint-deep',
              )}
            />
            <div className="text-[13px]">
              <p className="font-display font-bold">
                {USE_MOCKS
                  ? 'Демо-режим: встроенные моки'
                  : IS_HYBRID
                    ? 'Гибрид: живой BFF + моки'
                    : 'Живой API через BFF'}
              </p>
              <p className="mt-0.5 text-ink/75">
                {USE_MOCKS
                  ? 'Данные живут в localStorage браузера: свайпы, мэтчи, чаты и автоответы. Бэкенд не нужен.'
                  : IS_HYBRID
                    ? 'Аккаунт, анкета и уведомления — живой BFF. Лента, мэтчи и чаты пока на моках (бэкенд их ещё не реализовал).'
                    : `Запросы идут на ${API_BASE} → BFF :8003.`}
              </p>
              <p className="mt-1 font-mono text-[11px] text-dim">
                VITE_USE_MOCKS={USE_MOCKS ? 'true' : IS_HYBRID ? 'hybrid' : 'false'} ·
                VITE_API_BASE={API_BASE}
              </p>
            </div>
          </div>

          <div className="mt-4 flex flex-wrap gap-2">
            <Button variant="ghost" icon="image" onClick={exportProfile} disabled={!profile}>
              Выгрузить анкету (JSON)
            </Button>
            {(USE_MOCKS || IS_HYBRID) && (
              <Button variant="sun" icon="refresh" onClick={() => setConfirmReset(true)}>
                Сбросить демо-данные
              </Button>
            )}
          </div>
        </section>

        <section className="card border-coral/30 p-6">
          <p className="panel-title mb-2">сессия</p>
          <div className="flex flex-wrap items-center justify-between gap-3">
            <p className="text-[13.5px] text-sub">
              Выйдешь — refresh-токен отзовётся, локальная сессия очистится.
            </p>
            <Button
              variant="danger"
              icon="logout"
              onClick={async () => {
                await logout()
                push({ tone: 'sky', emoji: '👋', title: 'Ты вышел' })
                navigate('/login', { replace: true })
              }}
            >
              Выйти из аккаунта
            </Button>
          </div>
        </section>
      </div>

      <Modal
        open={confirmReset}
        onClose={() => setConfirmReset(false)}
        title="Сбросить демо-данные?"
        footer={
          <>
            <Button variant="ghost" onClick={() => setConfirmReset(false)}>
              Отмена
            </Button>
            <Button variant="danger" icon="refresh" onClick={doReset}>
              Сбросить
            </Button>
          </>
        }
      >
        <p className="text-[14px] leading-relaxed text-sub">
          Все свайпы, мэтчи, чаты и загруженные картинки вернутся к исходному состоянию. Аккаунты,
          созданные вручную в демо-режиме, тоже удалятся. Живой бэкенд это не затрагивает.
        </p>
      </Modal>
    </div>
  )
}
