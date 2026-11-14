import { useState } from 'react'
import type { FormEvent } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { ApiError, USE_MOCKS } from '@/api'
import { DEMO_EMAIL, DEMO_PASSWORD } from '@/api/mock/seed'
import { useAuth } from '@/state/auth'
import { useToast } from '@/state/toast'
import { Logo } from '@/components/layout/Background'
import { Button } from '@/components/ui/Button'
import { PasswordField, TextField } from '@/components/ui/Field'
import { Icon } from '@/components/ui/Icon'
import { Sticker } from '@/components/ui/Sticker'

const HERO_TAGS = ['python', 'fastapi', 'react', 'ctf', 'kubernetes', 'ui-ux', 'gamedev'] as const

export function LoginPage() {
  const { login, authenticated } = useAuth()
  const { push } = useToast()
  const navigate = useNavigate()
  const [email, setEmail] = useState(USE_MOCKS ? DEMO_EMAIL : '')
  const [password, setPassword] = useState(USE_MOCKS ? DEMO_PASSWORD : '')
  const [error, setError] = useState<string | null>(null)
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const [busy, setBusy] = useState(false)

  if (authenticated) return <Navigate to="/swipes" replace />

  const submit = async (event: FormEvent) => {
    event.preventDefault()
    setError(null)
    setFieldErrors({})

    const local: Record<string, string> = {}
    if (!email.trim()) local.email = 'Укажи почту'
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) local.email = 'Похоже, это не почта'
    if (!password) local.password = 'Введи пароль'
    if (Object.keys(local).length) {
      setFieldErrors(local)
      return
    }

    setBusy(true)
    try {
      await login(email.trim(), password)
      push({ tone: 'mint', emoji: '🐍', title: 'С возвращением!', text: 'Лента уже обновилась.' })
      navigate('/swipes', { replace: true })
    } catch (caught) {
      if (caught instanceof ApiError) {
        setError(caught.message)
        setFieldErrors(caught.fieldErrors ?? {})
      } else {
        setError('Не удалось связаться с сервером. Проверь, что BFF запущен на :8003.')
      }
    } finally {
      setBusy(false)
    }
  }

  return (
    <div className="mx-auto grid min-h-dvh max-w-[1200px] items-center gap-10 px-5 py-10 lg:grid-cols-[1.05fr_minmax(0,420px)] lg:gap-16">
      <section className="hidden lg:block">
        <div className="mb-6 flex items-center gap-3">
          <Logo size={46} />
          <div>
            <p className="font-display text-lg font-extrabold tracking-tight">PythoNyashka</p>
            <p className="font-mono text-[11px] text-dim">import love from stack</p>
          </div>
        </div>
        <h1 className="font-display text-[46px] leading-[1.05] font-extrabold tracking-tight">
          Найди няшку
          <br />
          <span className="text-coral-deep">по своему стеку</span>
        </h1>
        <p className="mt-4 max-w-md text-[15px] leading-relaxed text-sub">
          Дейтинг для айтишников: анкета — это твой стек, мэтч — это пересечение тегов. Никаких
          «привет, как дела» — сразу обсуждаете, почему Postgres лучше.
        </p>

        <div className="mt-7 flex max-w-md flex-wrap gap-2">
          {HERO_TAGS.map((tag) => (
            <Sticker key={tag} tag={tag} />
          ))}
        </div>

        <div className="quote-block mt-8 max-w-md">
          <p className="font-mono text-[12.5px] leading-relaxed text-sub">
            <span className="text-coral-deep">&gt;&gt;&gt;</span> match = swipe(like=True)
            <br />
            <span className="text-coral-deep">&gt;&gt;&gt;</span> match.status
            <br />
            <span className="text-mint-deep">'accepted'</span>
          </p>
        </div>

        <div className="mt-8 grid max-w-md grid-cols-3 gap-3">
          {[
            { value: '52', label: 'тега в словаре' },
            { value: '16', label: 'анкет в демо' },
            { value: '0', label: 'скучных смолтоков' },
          ].map((item) => (
            <div key={item.label} className="card-flat px-4 py-3">
              <p className="font-display text-2xl font-extrabold text-coral-deep">{item.value}</p>
              <p className="text-[12px] text-sub">{item.label}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="card w-full p-6 sm:p-8">
        <div className="mb-6 flex items-center gap-3 lg:hidden">
          <Logo size={42} />
          <div>
            <p className="font-display text-base font-extrabold">PythoNyashka</p>
            <p className="font-mono text-[11px] text-dim">няшка по стеку</p>
          </div>
        </div>

        <p className="panel-title mb-1">вход</p>
        <h2 className="text-2xl">Рады видеть снова</h2>
        <p className="hint mt-1">Введи почту и пароль — вернём тебя к ленте.</p>

        <form className="mt-6 space-y-4" onSubmit={submit} noValidate>
          <TextField
            label="Почта"
            type="email"
            autoComplete="email"
            placeholder="you@nyashka.dev"
            value={email}
            error={fieldErrors.email}
            onChange={(event) => setEmail(event.target.value)}
          />
          <PasswordField
            label="Пароль"
            autoComplete="current-password"
            placeholder="••••••••"
            value={password}
            error={fieldErrors.password}
            onChange={(event) => setPassword(event.target.value)}
          />

          {error && (
            <div className="flex items-start gap-2 rounded-2xl border border-coral/40 bg-coral-soft px-4 py-3">
              <Icon name="info" size={17} className="mt-0.5 shrink-0 text-coral-deep" />
              <p className="text-[13px] text-coral-deep">{error}</p>
            </div>
          )}

          <Button type="submit" size="lg" className="w-full" loading={busy} iconRight="arrow-right">
            Войти
          </Button>
        </form>

        {USE_MOCKS && (
          <div className="mt-5 rounded-3xl border border-dashed border-line-strong bg-cream-deep/60 p-4">
            <p className="font-mono text-[11px] text-dim">демо-режим · бэкенд не нужен</p>
            <p className="mt-1 text-[13px] text-sub">
              Аккаунт{' '}
              <code className="font-mono text-[12px] text-coral-deep">{DEMO_EMAIL}</code> / пароль{' '}
              <code className="font-mono text-[12px] text-coral-deep">{DEMO_PASSWORD}</code> уже
              подставлен — просто жми «Войти».
            </p>
          </div>
        )}

        <p className="mt-6 text-center text-[13.5px] text-sub">
          Ещё нет анкеты?{' '}
          <Link to="/register" className="link">
            Собрать за минуту
          </Link>
        </p>
      </section>
    </div>
  )
}
