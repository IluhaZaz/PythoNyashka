export function plural(n: number, one: string, few: string, many: string): string {
  const mod10 = n % 10
  const mod100 = n % 100
  if (mod10 === 1 && mod100 !== 11) return one
  if (mod10 >= 2 && mod10 <= 4 && (mod100 < 10 || mod100 >= 20)) return few
  return many
}

export function years(n: number): string {
  return `${n} ${plural(n, 'год', 'года', 'лет')}`
}

const MINUTE = 60_000
const HOUR = 60 * MINUTE
const DAY = 24 * HOUR

export function timeAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  if (Number.isNaN(diff)) return ''
  if (diff < MINUTE) return 'только что'
  if (diff < HOUR) {
    const m = Math.floor(diff / MINUTE)
    return `${m} ${plural(m, 'минуту', 'минуты', 'минут')} назад`
  }
  if (diff < DAY) {
    const h = Math.floor(diff / HOUR)
    return `${h} ${plural(h, 'час', 'часа', 'часов')} назад`
  }
  const d = Math.floor(diff / DAY)
  if (d < 7) return `${d} ${plural(d, 'день', 'дня', 'дней')} назад`
  return new Date(iso).toLocaleDateString('ru-RU', { day: 'numeric', month: 'short' })
}

export function shortAgo(iso: string): string {
  const diff = Date.now() - new Date(iso).getTime()
  if (diff < MINUTE) return 'сейчас'
  if (diff < HOUR) return `${Math.floor(diff / MINUTE)}м`
  if (diff < DAY) return `${Math.floor(diff / HOUR)}ч`
  return `${Math.floor(diff / DAY)}д`
}

export function clockTime(iso: string): string {
  return new Date(iso).toLocaleTimeString('ru-RU', { hour: '2-digit', minute: '2-digit' })
}

export function dayLabel(iso: string): string {
  const date = new Date(iso)
  const today = new Date()
  const yesterday = new Date(today.getTime() - DAY)
  const same = (a: Date, b: Date) => a.toDateString() === b.toDateString()
  if (same(date, today)) return 'Сегодня'
  if (same(date, yesterday)) return 'Вчера'
  return date.toLocaleDateString('ru-RU', { day: 'numeric', month: 'long' })
}

export function initials(name: string, surname?: string): string {
  return `${name.charAt(0)}${surname ? surname.charAt(0) : ''}`.toUpperCase()
}

export function km(n: number): string {
  return `${n} ${plural(n, 'км', 'км', 'км')}`
}
