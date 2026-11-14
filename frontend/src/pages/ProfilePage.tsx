import { useEffect, useMemo, useRef, useState } from 'react'
import { useMutation } from '@tanstack/react-query'
import { ApiError, api } from '@/api'
import type { Gender, ProfileUpdateInput } from '@/api/types'
import { isProfileTag, type ProfileTag } from '@/lib/tags'
import { cn } from '@/lib/cn'
import { timeAgo, years } from '@/lib/format'
import { useAuth } from '@/state/auth'
import { useToast } from '@/state/toast'
import { Avatar } from '@/components/MediaImage'
import { TagPicker } from '@/components/TagPicker'
import { Button } from '@/components/ui/Button'
import { SectionTitle, Skeleton } from '@/components/ui/Feedback'
import { Segmented, TextArea, TextField } from '@/components/ui/Field'
import { Icon } from '@/components/ui/Icon'
import { StickerRow } from '@/components/ui/Sticker'

interface Draft {
  name: string
  surname: string
  age: string
  gender: Gender
  bio: string
  tags: ProfileTag[]
}

export function ProfilePage() {
  const { profile, profileLoading, reloadProfile } = useAuth()
  const { push } = useToast()
  const fileRef = useRef<HTMLInputElement>(null)
  const [draft, setDraft] = useState<Draft | null>(null)
  const [avatarFile, setAvatarFile] = useState<File | null>(null)
  const [avatarPreview, setAvatarPreview] = useState<string | null>(null)
  const [errors, setErrors] = useState<Record<string, string>>({})

  const base = useMemo<Draft>(
    () => ({
      name: profile?.name ?? '',
      surname: profile?.surname ?? '',
      age: profile ? String(profile.age) : '',
      gender: profile?.gender ?? 'female',
      bio: profile?.bio ?? '',
      tags: (profile?.tags ?? []).filter(isProfileTag),
    }),
    [profile],
  )

  const form = draft ?? base
  const ageNumber = Number(form.age)

  useEffect(
    () => () => {
      if (avatarPreview) URL.revokeObjectURL(avatarPreview)
    },
    [avatarPreview],
  )

  const patch = (next: Partial<Draft>) => {
    setDraft({ ...form, ...next })
    setErrors({})
  }

  const dirtyFields = useMemo(() => {
    const changed: ProfileUpdateInput = {}
    if (form.name.trim() !== base.name) changed.name = form.name.trim()
    if (form.surname.trim() !== base.surname) changed.surname = form.surname.trim()
    if (ageNumber !== Number(base.age)) changed.age = ageNumber
    if (form.gender !== base.gender) changed.gender = form.gender
    if (form.bio !== base.bio) changed.bio = form.bio
    if (JSON.stringify(form.tags) !== JSON.stringify(base.tags)) changed.tags = form.tags
    if (avatarFile) changed.avatar = avatarFile
    return changed
  }, [form, base, ageNumber, avatarFile])

  const dirty = Object.keys(dirtyFields).length > 0

  const save = useMutation({
    mutationFn: (input: ProfileUpdateInput) => api.updateProfile(input),
    onSuccess: async () => {
      await reloadProfile()
      setDraft(null)
      setAvatarFile(null)
      setAvatarPreview((previous) => {
        if (previous) URL.revokeObjectURL(previous)
        return null
      })
      push({ tone: 'mint', emoji: '✨', title: 'Анкета обновлена', text: 'Лента пересчитает мэтчи.' })
    },
    onError: (error) => {
      if (error instanceof ApiError) {
        setErrors(error.fieldErrors ?? {})
        push({ tone: 'coral', title: 'Не сохранилось', text: error.message })
      } else {
        push({ tone: 'coral', title: 'Сервер не ответил' })
      }
    },
  })

  const validate = () => {
    const next: Record<string, string> = {}
    if (!form.name.trim()) next.name = 'Имя не может быть пустым'
    if (!form.surname.trim()) next.surname = 'Фамилия не может быть пустой'
    if (!Number.isFinite(ageNumber) || ageNumber < 1 || ageNumber > 149) next.age = 'Возраст от 1 до 149'
    if (form.bio.length > 1000) next.bio = 'Максимум 1000 символов'
    if (form.tags.length === 0) next.tags = 'Оставь хотя бы один тег'
    setErrors(next)
    return Object.keys(next).length === 0
  }

  const pickFile = (file: File | null) => {
    if (!file) return
    if (!file.type.startsWith('image/')) {
      push({ tone: 'coral', title: 'Нужна картинка', text: 'png, jpg, webp или gif.' })
      return
    }
    if (file.size > 5 * 1024 * 1024) {
      push({ tone: 'coral', title: 'Файл больше 5 МБ' })
      return
    }
    setAvatarFile(file)
    setAvatarPreview((previous) => {
      if (previous) URL.revokeObjectURL(previous)
      return URL.createObjectURL(file)
    })
  }

  const checks = [
    { done: Boolean(form.name && form.surname), label: 'Имя и фамилия' },
    { done: Number.isFinite(ageNumber) && ageNumber > 0, label: 'Возраст' },
    { done: form.bio.trim().length >= 40, label: 'О себе от 40 символов' },
    { done: form.tags.length >= 3, label: 'Минимум 3 тега' },
    { done: Boolean(avatarFile || profile?.avatar), label: 'Фото профиля' },
  ]
  const completeness = Math.round((checks.filter((item) => item.done).length / checks.length) * 100)

  if (profileLoading || !profile) {
    return (
      <div className="grid gap-6 lg:grid-cols-[340px_minmax(0,1fr)]">
        <Skeleton className="h-96" />
        <Skeleton className="h-[520px]" />
      </div>
    )
  }

  return (
    <>
      <SectionTitle
        eyebrow="профиль"
        title="Моя анкета"
        action={
          <div className="flex items-center gap-2">
            {dirty && <span className="mono-badge bg-sun-soft text-sun-deep">есть изменения</span>}
            <Button
              icon="check"
              loading={save.isPending}
              disabled={!dirty}
              onClick={() => validate() && save.mutate(dirtyFields)}
            >
              Сохранить
            </Button>
          </div>
        }
      />

      <div className="grid gap-6 lg:grid-cols-[340px_minmax(0,1fr)]">
        <aside className="space-y-4">
          <div className="card overflow-hidden p-0">
            <div className="relative h-28 bg-[linear-gradient(135deg,#ffd9c7,#ffe9a8_50%,#e6d8ff)]">
              <span className="mono-badge absolute top-3 right-3 bg-surface text-ink shadow-[var(--shadow-lift)]">
                {completeness}% заполнено
              </span>
            </div>
            <div className="-mt-10 px-5 pb-5">
              {avatarPreview ? (
                <img
                  src={avatarPreview}
                  alt="Новый аватар"
                  className="h-20 w-20 rounded-3xl border-4 border-surface object-cover"
                />
              ) : (
                <Avatar
                  mediaId={profile.avatar}
                  seed={profile.id}
                  name={profile.name}
                  size={80}
                  className="[&>img]:border-4 [&>img]:border-surface"
                />
              )}
              <p className="font-display mt-3 text-xl font-extrabold">
                {form.name || 'Без имени'} {form.surname}
              </p>
              <p className="font-mono text-[11.5px] text-dim">
                {Number.isFinite(ageNumber) ? years(ageNumber) : '—'} ·{' '}
                {form.gender === 'female' ? 'девушка' : 'парень'}
              </p>
              <p className="mt-3 text-[13.5px] leading-relaxed text-sub">
                {form.bio || 'Расскажи о себе — так мэтчей будет больше.'}
              </p>
              <div className="mt-4">
                <StickerRow tags={form.tags} limit={10} />
              </div>
              <div className="mt-4 space-y-1 border-t border-line pt-3 font-mono text-[11px] text-dim">
                <p>{profile.email}</p>
                <p>создана {timeAgo(profile.created_at)}</p>
                <p>обновлена {timeAgo(profile.updated_at)}</p>
              </div>
            </div>
          </div>

          <div className="card-flat p-5">
            <p className="panel-title mb-3">чек-лист анкеты</p>
            <ul className="space-y-2">
              {checks.map((item) => (
                <li key={item.label} className="flex items-center gap-2 text-[13px]">
                  <span
                    className={cn(
                      'grid h-5 w-5 shrink-0 place-items-center rounded-full',
                      item.done ? 'bg-mint-deep text-white' : 'bg-cream-deep text-dim',
                    )}
                  >
                    <Icon name={item.done ? 'check' : 'close'} size={11} />
                  </span>
                  <span className={item.done ? 'text-sub line-through' : 'font-semibold'}>
                    {item.label}
                  </span>
                </li>
              ))}
            </ul>
            <div className="mt-4 h-2 overflow-hidden rounded-full bg-cream-deep">
              <div
                className="h-full rounded-full bg-[linear-gradient(90deg,#ff5d73,#ffc24b)] transition-all duration-500"
                style={{ width: `${completeness}%` }}
              />
            </div>
          </div>
        </aside>

        <section className="card space-y-5 p-6">
          <div>
            <p className="panel-title mb-3">фото</p>
            <div className="flex flex-wrap items-center gap-4">
              {avatarPreview ? (
                <img
                  src={avatarPreview}
                  alt="Предпросмотр"
                  className="h-20 w-20 rounded-3xl border border-line object-cover"
                />
              ) : (
                <Avatar mediaId={profile.avatar} seed={profile.id} name={profile.name} size={80} />
              )}
              <input
                ref={fileRef}
                type="file"
                accept="image/*"
                className="hidden"
                onChange={(event) => pickFile(event.target.files?.[0] ?? null)}
              />
              <div className="flex flex-wrap gap-2">
                <Button variant="ghost" icon="camera" onClick={() => fileRef.current?.click()}>
                  {profile.avatar || avatarFile ? 'Заменить фото' : 'Загрузить фото'}
                </Button>
                {avatarFile && (
                  <Button
                    variant="quiet"
                    icon="trash"
                    onClick={() => {
                      setAvatarFile(null)
                      setAvatarPreview((previous) => {
                        if (previous) URL.revokeObjectURL(previous)
                        return null
                      })
                    }}
                  >
                    Отменить
                  </Button>
                )}
              </div>
              <p className="hint w-full sm:w-auto">Без фото — сгенерированный няшный аватар.</p>
            </div>
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <TextField
              label="Имя"
              maxLength={100}
              value={form.name}
              error={errors.name}
              onChange={(event) => patch({ name: event.target.value })}
            />
            <TextField
              label="Фамилия"
              maxLength={100}
              value={form.surname}
              error={errors.surname}
              onChange={(event) => patch({ surname: event.target.value })}
            />
          </div>

          <div className="grid gap-4 sm:grid-cols-2">
            <TextField
              label="Возраст"
              type="number"
              min={1}
              max={149}
              value={form.age}
              error={errors.age}
              onChange={(event) => patch({ age: event.target.value })}
            />
            <div>
              <p className="label">Пол</p>
              <Segmented
                value={form.gender}
                onChange={(value) => patch({ gender: value })}
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
            value={form.bio}
            error={errors.bio}
            placeholder="Чем горишь, что пилишь по вечерам, какой редактор защищаешь в спорах…"
            onChange={(event) => patch({ bio: event.target.value })}
          />

          <div>
            <p className="panel-title mb-3">стек · до 12 тегов</p>
            <TagPicker value={form.tags} onChange={(tags) => patch({ tags })} />
            {errors.tags && <p className="error-text mt-2">{errors.tags}</p>}
          </div>

          <div className="sticky bottom-2 flex flex-wrap items-center gap-3 rounded-3xl border border-line bg-surface/95 px-4 py-3 backdrop-blur">
            <p className="flex-1 text-[13px] text-sub">
              {dirty
                ? `Изменено полей: ${Object.keys(dirtyFields).length}. Сохрани, чтобы лента пересчиталась.`
                : 'Всё сохранено. Анкета видна другим участникам.'}
            </p>
            {dirty && (
              <Button
                variant="ghost"
                onClick={() => {
                  setDraft(null)
                  setAvatarFile(null)
                  setErrors({})
                  setAvatarPreview((previous) => {
                    if (previous) URL.revokeObjectURL(previous)
                    return null
                  })
                }}
              >
                Отменить
              </Button>
            )}
            <Button
              icon="check"
              loading={save.isPending}
              disabled={!dirty}
              onClick={() => validate() && save.mutate(dirtyFields)}
            >
              Сохранить
            </Button>
          </div>
        </section>
      </div>
    </>
  )
}
