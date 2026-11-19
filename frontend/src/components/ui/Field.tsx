import { useId, useState } from 'react'
import type { InputHTMLAttributes, ReactNode, TextareaHTMLAttributes } from 'react'
import { cn } from '@/lib/cn'
import { Icon } from './Icon'

interface WrapProps {
  label: string
  hint?: string
  error?: string
  counter?: string
  children: ReactNode
  htmlFor?: string
}

export function FieldWrap({ label, hint, error, counter, children, htmlFor }: WrapProps) {
  return (
    <div>
      <div className="flex items-baseline justify-between gap-3">
        <label className="label" htmlFor={htmlFor}>
          {label}
        </label>
        {counter && <span className="mb-1.5 font-mono text-[11px] text-dim">{counter}</span>}
      </div>
      {children}
      {error ? (
        <p className="error-text mt-1.5">{error}</p>
      ) : hint ? (
        <p className="hint mt-1.5">{hint}</p>
      ) : null}
    </div>
  )
}

export function TextField({
  label,
  hint,
  error,
  className,
  ...rest
}: { label: string; hint?: string; error?: string } & InputHTMLAttributes<HTMLInputElement>) {
  const id = useId()
  return (
    <FieldWrap label={label} hint={hint} error={error} htmlFor={id}>
      <input id={id} className={cn('field', error && 'field-invalid', className)} {...rest} />
    </FieldWrap>
  )
}

export function PasswordField({
  label,
  hint,
  error,
  ...rest
}: { label: string; hint?: string; error?: string } & InputHTMLAttributes<HTMLInputElement>) {
  const id = useId()
  const [visible, setVisible] = useState(false)
  return (
    <FieldWrap label={label} hint={hint} error={error} htmlFor={id}>
      <div className="relative">
        <input
          id={id}
          type={visible ? 'text' : 'password'}
          className={cn('field pr-12', error && 'field-invalid')}
          {...rest}
        />
        <button
          type="button"
          onClick={() => setVisible((value) => !value)}
          aria-label={visible ? 'Скрыть пароль' : 'Показать пароль'}
          className="absolute top-1/2 right-3 -translate-y-1/2 text-dim transition hover:text-coral-deep"
        >
          <Icon name={visible ? 'eye-off' : 'eye'} size={18} />
        </button>
      </div>
    </FieldWrap>
  )
}

export function TextArea({
  label,
  hint,
  error,
  maxLength,
  value,
  className,
  ...rest
}: { label: string; hint?: string; error?: string } & TextareaHTMLAttributes<HTMLTextAreaElement>) {
  const id = useId()
  const length = typeof value === 'string' ? value.length : 0
  return (
    <FieldWrap
      label={label}
      hint={hint}
      error={error}
      htmlFor={id}
      counter={maxLength ? `${length}/${maxLength}` : undefined}
    >
      <textarea
        id={id}
        value={value}
        maxLength={maxLength}
        className={cn('field resize-y leading-relaxed', error && 'field-invalid', className)}
        {...rest}
      />
    </FieldWrap>
  )
}

export function Toggle({
  checked,
  onChange,
  label,
  hint,
}: {
  checked: boolean
  onChange: (value: boolean) => void
  label: string
  hint?: string
}) {
  return (
    <button
      type="button"
      role="switch"
      aria-checked={checked}
      onClick={() => onChange(!checked)}
      className="flex w-full items-center justify-between gap-4 text-left"
    >
      <span>
        <span className="block text-sm font-bold">{label}</span>
        {hint && <span className="hint block">{hint}</span>}
      </span>
      <span
        className={cn(
          'relative h-7 w-12 shrink-0 rounded-full border transition',
          checked ? 'border-coral bg-coral' : 'border-line bg-cream-deep',
        )}
      >
        <span
          className={cn(
            'absolute top-0.5 h-5 w-5 rounded-full bg-surface shadow transition-all',
            checked ? 'left-[24px]' : 'left-0.5',
          )}
        />
      </span>
    </button>
  )
}

export function Segmented<T extends string>({
  options,
  value,
  onChange,
  className,
}: {
  options: { value: T; label: string; count?: number }[]
  value: T
  onChange: (value: T) => void
  className?: string
}) {
  return (
    <div className={cn('inline-flex gap-1 rounded-full border border-line bg-surface p-1', className)}>
      {options.map((option) => (
        <button
          key={option.value}
          type="button"
          onClick={() => onChange(option.value)}
          className={cn(
            'rounded-full px-4 py-1.5 text-[13px] font-bold transition',
            value === option.value
              ? 'bg-ink text-cream shadow-[0_6px_14px_-8px_rgba(74,59,56,.9)]'
              : 'text-sub hover:bg-cream-deep hover:text-ink',
          )}
        >
          {option.label}
          {option.count !== undefined && (
            <span className={cn('ml-1.5 font-mono text-[11px]', value === option.value ? 'text-cream/70' : 'text-dim')}>
              {option.count}
            </span>
          )}
        </button>
      ))}
    </div>
  )
}
