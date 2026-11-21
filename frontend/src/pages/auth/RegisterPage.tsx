import { useMemo, useRef, useState } from 'react'
import { Link, Navigate, useNavigate } from 'react-router-dom'
import { ApiError } from '@/api'
import type { Gender, ProfileCreateInput } from '@/api/types'
import type { ProfileTag } from '@/lib/tags'
import { cn } from '@/lib/cn'
import { years } from '@/lib/format'
import { useAuth } from '@/state/auth'
import { useToast } from '@/state/toast'
import { Logo } from '@/components/layout/Background'
import { TagPicker } from '@/components/TagPicker'
import { Button } from '@/components/ui/Button'
import { PasswordField, Segmented, TextArea, TextField } from '@/components/ui/Field'
import { Icon } from '@/components/ui/Icon'
import { StickerRow } from '@/components/ui/Sticker'

const STEPS = [
  { key: 'account', title: 'Аккаунт', emoji: '🔐' },
  { key: 'about', title: 'Анкета', emoji: '🙋' },
  { key: 'tags', title: 'Стек', emoji: '🏷️' },
  { key: 'avatar', title: 'Аватар', emoji: '📸' },
] as const

type Errors = Record<string, string>

export function RegisterPage() {
  const { register, authenticated } = useAuth()
  const { push } = useToast()
  const navigate = useNavigate()
  const fileRef = useRef<HTMLInputElement>(null)

  const [step, setStep] = useState(0)
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [repeat, setRepeat] = useState('')
  const [name, setName] = useState('')
  const [surname, setSurname] = useState('')
  const [age, setAge] = useState('23')
  const [gender, setGender] = useState<Gender>('female')
  const [bio, setBio] = useState('')
  const [tags, setTags] = useState<ProfileTag[]>([])
  const [avatar, setAvatar] = useState<File | null>(null)
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null)
  const [errors, setErrors] = useState<Errors>({})
  const [serverError, setServerError] = useState<string | null>(null)
  const [busy, setBusy] = useState(false)

  const ageNumber = Number(age)

  const strength = useMemo(() => {
    let score = 0
    if (password.length >= 8) score++
    if (/[A-ZА-Я]/.test(password)) score++
    if (/\d/.test(password)) score++
    if (/[^\w\s]/.test(password)) score++
    return score
  }, [password])

  if (authenticated) return <Navigate to="/swipes" replace />

  const validateStep = (index: number): Errors => {
    const next: Errors = {}
    if (index === 0) {
      if (!email.trim()) next.email = 'Укажи почту'
      else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email.trim())) next.email = 'Похоже, это не почта'
      if (password.length < 8) next.password = 'Минимум 8 символов'
      if (repeat !== password) next.repeat = 'Пароли не совпадают'
    }
    if (index === 1) {
      if (!name.trim()) next.name = 'Как тебя зовут?'
      if (name.trim().length > 100) next.name = 'Слишком длинно (макс. 100)'
      if (!surname.trim()) next.surname = 'Укажи фамилию'
      if (surname.trim().length > 100) next.surname = 'Слишком длинно (макс. 100)'
      if (!Number.isFinite(ageNumber) || ageNumber < 1 || ageNumber > 149)
        next.age = 'Возраст от 1 до 149'
      if (bio.length > 1000) next.bio = 'Максимум 1000 символов'
    }
    if (index === 2 && tags.length === 0) next.tags = 'Выбери хотя бы один тег — по ним и мэтчим'
    return next
  }

  const goNext = () => {
    const found = validateStep(step)
    setErrors(found)
    if (Object.keys(found).length) return
    setStep((value) => Math.min(value + 1, STEPS.length - 1))
  }

  const pickFile = (file: File | null) => {
    if (!file) return
    if (!file.type.startsWith('image/')) {
      setErrors({ avatar: 'Нужна картинка: png, jpg, webp или gif' })
      return
    }
    if (file.size > 5 * 1024 * 1024) {
      setErrors({ avatar: 'Файл больше 5 МБ — сожми его чуть-чуть' })
      return
    }
    setErrors({})
    setAvatar(file)
    setAvatarPreview((previous) => {
      if (previous) URL.revokeObjectURL(previous)
      return URL.createObjectURL(file)
    })
  }

  const submit = async () => {
    for (let index = 0; index < 3; index++) {
      const found = validateStep(index)
      if (Object.keys(found).length) {
        setErrors(found)
        setStep(index)
        return
      }
    }

    const input: ProfileCreateInput = {
      email: email.trim(),
      password,
      name: name.trim(),
      surname: surname.trim(),
      age: ageNumber,
      bio: bio.trim(),
      gender,
      tags,
      avatar,
    }

    setBusy(true)
    setServerError(null)
    try {
      await register(input)
      push({
        tone: 'mint',
        emoji: '🎉',
        title: 'Анкета готова!',
        text: 'Мы уже подобрали первых няшек по твоему стеку.',
      })
      navigate('/swipes', { replace: true })
    } catch (caught) {
      if (caught instanceof ApiError) {
        setServerError(caught.message)
        setErrors(caught.fieldErrors ?? {})
      } else {
        setServerError('Сервер не ответил. Проверь, что BFF запущен на :8003.')
      }
    } finally {
      setBusy(false)
    }
  }

  const completeness = Math.round(
    ((email && password ? 1 : 0) +
      (name && surname ? 1 : 0) +
      (bio.trim() ? 1 : 0) +
      (tags.length ? 1 : 0) +
      (avatar ? 1 : 0)) *
      20,
  )

  return (
    <div className="mx-auto grid min-h-dvh max-w-[1240px] gap-8 px-5 py-8 lg:grid-cols-[minmax(0,1fr)_340px] lg:py-12">
      <section className="card p-6 sm:p-8">
        <div className="mb-6 flex items-center gap-3">
          <Logo size={40} />
          <div className="min-w-0">
            <p className="font-display text-base font-extrabold">Собираем анкету</p>
            <p className="font-mono text-[11px] text-dim">шаг {step + 1} из {STEPS.length}</p>
          </div>
          <Link to="/login" className="link ml-auto shrink-0 text-[13px]">
            Уже есть аккаунт
          </Link>
        </div>

        <div className="mb-7 flex gap-1.5">
          {STEPS.map((item, index) => (
            <button
              key={item.key}
              type="button"
              onClick={() => index < step && setStep(index)}
              disabled={index > step}
              className="group flex-1 text-left"
            >
              <span
                className={cn(
                  'block h-1.5 rounded-full transition-all',
                  index <= step ? 'bg-coral' : 'bg-line',
                )}
              />
              <span
                className={cn(
                  'mt-2 block truncate text-[11.5px] font-bold transition',
                  index === step ? 'text-ink' : 'text-dim',
                )}
              >
                {item.emoji} {item.title}
              </span>
            </button>
          ))}
        </div>

        {step === 0 && (
          <div className="animate-rise space-y-4">
            <h2 className="text-2xl">Сначала — вход</h2>
            <p className="hint -mt-2">Почта нужна для логина, пароль — минимум 8 символов.</p>
            <TextField
              label="Почта"
              type="email"
              autoComplete="email"
              placeholder="you@nyashka.dev"
              value={email}
              error={errors.email}
              onChange={(event) => setEmail(event.target.value)}
            />
            <PasswordField
              label="Пароль"
              autoComplete="new-password"
              value={password}
              error={errors.password}
              onChange={(event) => setPassword(event.target.value)}
            />
            {password && (
              <div className="flex items-center gap-2">
                {[0, 1, 2, 3].map((index) => (
                  <span
                    key={index}
                    className={cn(
                      'h-1.5 flex-1 rounded-full transition',
                      index < strength
                        ? strength <= 1
                          ? 'bg-coral'
                          : strength === 2
                            ? 'bg-sun'
                            : 'bg-mint'
                        : 'bg-line',
                    )}
                  />
                ))}
                <span className="mono-badge">
                  {['слабый', 'слабый', 'средний', 'хороший', 'отличный'][strength]}
                </span>
              </div>
            )}
            <PasswordField
              label="Повтори пароль"
              autoComplete="new-password"
              value={repeat}
              error={errors.repeat}
              onChange={(event) => setRepeat(event.target.value)}
            />
          </div>
        )}

        {step === 1 && (
          <div className="animate-rise space-y-4">
            <h2 className="text-2xl">Кто ты в проде?</h2>
            <p className="hint -mt-2">Это увидят другие анкеты. Честность повышает мэтчи.</p>
            <div className="grid gap-4 sm:grid-cols-2">
              <TextField
                label="Имя"
                placeholder="Аня"
                maxLength={100}
                value={name}
                error={errors.name}
                onChange={(event) => setName(event.target.value)}
              />
              <TextField
                label="Фамилия"
                placeholder="Соколова"
                maxLength={100}
                value={surname}
                error={errors.surname}
                onChange={(event) => setSurname(event.target.value)}
              />
            </div>
            <div className="grid gap-4 sm:grid-cols-2">
              <TextField
                label="Возраст"
                type="number"
                min={1}
                max={149}
                value={age}
                error={errors.age}
                onChange={(event) => setAge(event.target.value)}
              />
              <div>
                <p className="label">Пол</p>
                <Segmented
                  value={gender}
                  onChange={setGender}
                  options={[
                    { value: 'female', label: 'Женский' },
                    { value: 'male', label: 'Мужской' },
                  ]}
                  className="w-full [&>button]:flex-1"
                />
              </div>
            </div>
            <TextArea
              label="О себе"
              rows={5}
              maxLength={1000}
              placeholder="Пишу на Python, ревьюю чужие PR по ночам, коллекционирую механические клавиатуры…"
              value={bio}
              error={errors.bio}
              hint="Можно оставить пустым и дописать позже."
              onChange={(event) => setBio(event.target.value)}
            />
          </div>
        )}

        {step === 2 && (
          <div className="animate-rise space-y-4">
            <h2 className="text-2xl">Твой стек</h2>
            <p className="hint -mt-2">
              До 12 тегов. Чем точнее — тем релевантнее лента. Мэтч считается по пересечению.
            </p>
            <TagPicker value={tags} onChange={setTags} />
            {errors.tags && <p className="error-text">{errors.tags}</p>}
          </div>
        )}

        {step === 3 && (
          <div className="animate-rise space-y-5">
            <h2 className="text-2xl">Фото — по желанию</h2>
            <p className="hint -mt-2">
              Без фото поставим милый сгенерированный аватар. Можно поменять в любой момент.
            </p>

            <input
              ref={fileRef}
              type="file"
              accept="image/*"
              className="hidden"
              onChange={(event) => pickFile(event.target.files?.[0] ?? null)}
            />

            <button
              type="button"
              onClick={() => fileRef.current?.click()}
              onDragOver={(event) => event.preventDefault()}
              onDrop={(event) => {
                event.preventDefault()
                pickFile(event.dataTransfer.files?.[0] ?? null)
              }}
              className="flex w-full flex-col items-center gap-3 rounded-[28px] border-2 border-dashed border-line-strong bg-cream-deep/50 px-6 py-10 transition hover:border-coral hover:bg-coral-soft/40"
            >
              {avatarPreview ? (
                <img
                  src={avatarPreview}
                  alt="Предпросмотр аватара"
                  className="h-28 w-28 rounded-3xl border border-line object-cover"
                />
              ) : (
                <span className="grid h-20 w-20 place-items-center rounded-3xl bg-surface text-coral-deep shadow-[var(--shadow-soft)]">
                  <Icon name="camera" size={30} />
                </span>
              )}
              <span className="font-display text-sm font-bold">
                {avatar ? 'Выбрать другое фото' : 'Перетащи файл или нажми'}
              </span>
              <span className="hint">png · jpg · webp · до 5 МБ</span>
            </button>

            {avatar && (
              <div className="flex items-center justify-between gap-3 rounded-2xl border border-line bg-surface px-4 py-3">
                <span className="truncate font-mono text-[12px] text-sub">{avatar.name}</span>
                <Button
                  variant="quiet"
                  size="sm"
                  icon="trash"
                  onClick={() => {
                    setAvatar(null)
                    if (avatarPreview) URL.revokeObjectURL(avatarPreview)
                    setAvatarPreview(null)
                  }}
                >
                  Убрать
                </Button>
              </div>
            )}
            {errors.avatar && <p className="error-text">{errors.avatar}</p>}
          </div>
        )}

        {serverError && (
          <div className="mt-5 flex items-start gap-2 rounded-2xl border border-coral/40 bg-coral-soft px-4 py-3">
            <Icon name="info" size={17} className="mt-0.5 shrink-0 text-coral-deep" />
            <p className="text-[13px] text-coral-deep">{serverError}</p>
          </div>
        )}

        <div className="mt-7 flex items-center gap-3">
          {step > 0 && (
            <Button variant="ghost" icon="arrow-left" onClick={() => setStep((value) => value - 1)}>
              Назад
            </Button>
          )}
          {step < STEPS.length - 1 ? (
            <Button className="ml-auto" iconRight="arrow-right" onClick={goNext}>
              Дальше
            </Button>
          ) : (
            <Button className="ml-auto" size="lg" icon="spark" loading={busy} onClick={submit}>
              Создать анкету
            </Button>
          )}
        </div>
      </section>

      <aside className="hidden lg:block">
        <div className="sticky top-8 space-y-4">
          <p className="panel-title">предпросмотр анкеты</p>
          <div className="card overflow-hidden p-0">
            <div className="relative h-32 bg-[linear-gradient(135deg,#ffd9c7,#ffe9a8_45%,#e6d8ff)]">
              <div className="absolute -bottom-8 left-5">
                {avatarPreview ? (
                  <img
                    src={avatarPreview}
                    alt="Аватар"
                    className="h-20 w-20 rounded-3xl border-4 border-surface object-cover"
                  />
                ) : (
                  <span className="grid h-20 w-20 place-items-center rounded-3xl border-4 border-surface bg-cream text-3xl">
                    🐍
                  </span>
                )}
              </div>
              <span className="mono-badge absolute top-3 right-3">{completeness}% готово</span>
            </div>
            <div className="px-5 pt-11 pb-5">
              <p className="font-display text-lg font-extrabold">
                {name || 'Твоё имя'} {surname}
                {age && Number.isFinite(ageNumber) && (
                  <span className="ml-1 font-body text-base font-medium text-sub">
                    , {ageNumber}
                  </span>
                )}
              </p>
              <p className="mt-1 font-mono text-[11px] text-dim">
                {email || 'почта появится здесь'}
              </p>
              <p className="mt-3 text-[13.5px] leading-relaxed text-sub">
                {bio || 'Пара строк о себе — и анкета станет живой.'}
              </p>
              <div className="mt-4">
                {tags.length ? (
                  <StickerRow tags={tags} limit={8} />
                ) : (
                  <p className="hint">Теги появятся на шаге 3</p>
                )}
              </div>
            </div>
          </div>

          <div className="card-flat p-4">
            <p className="panel-title mb-2">что дальше</p>
            <ul className="space-y-2 text-[13px] text-sub">
              {[
                'Лента отсортирована по совпадению стека',
                'Взаимный лайк сразу открывает чат',
                'Анкету можно редактировать в любой момент',
              ].map((line) => (
                <li key={line} className="flex gap-2">
                  <Icon name="check" size={15} className="mt-0.5 shrink-0 text-mint-deep" />
                  {line}
                </li>
              ))}
            </ul>
          </div>

          {name && Number.isFinite(ageNumber) && ageNumber > 0 && (
            <p className="hint text-center">
              {name}, тебе {years(ageNumber)} — отличный возраст для пет-проектов.
            </p>
          )}
        </div>
      </aside>
    </div>
  )
}
