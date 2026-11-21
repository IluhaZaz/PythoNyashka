const SKIN = ['#F7D9C4', '#F0C9A8', '#E0AC85', '#C68863', '#8D5524']
const HAIR = ['#3B2A26', '#5A3E36', '#8B5E3C', '#C98A3E', '#2F2A3D', '#7C4DDB', '#E8365A']
const SHIRT = ['#FF5D73', '#FFC24B', '#34D399', '#6FB6FF', '#B98BFF', '#FF8A6B']
const BACK = [
  ['#FFD9C7', '#FFE9A8'],
  ['#C9EDDC', '#DFEEFF'],
  ['#FFE9A8', '#FFE1E6'],
  ['#E6D8FF', '#DFEEFF'],
  ['#FFE1E6', '#E6D8FF'],
  ['#D9F2E6', '#FFF1C9'],
]

function hash(seed: string): number {
  let h = 2166136261
  for (let i = 0; i < seed.length; i += 1) {
    h ^= seed.charCodeAt(i)
    h = Math.imul(h, 16777619)
  }
  return Math.abs(h)
}

function pick<T>(list: T[], n: number): T {
  return list[n % list.length]
}

/** Детерминированный векторный аватар: одинаковый seed — одинаковая мордашка. */
export function avatarSvg(seed: string): string {
  const h = hash(seed)
  const skin = pick(SKIN, h)
  const hair = pick(HAIR, h >> 3)
  const shirt = pick(SHIRT, h >> 6)
  const [c1, c2] = pick(BACK, h >> 9)
  const style = (h >> 12) % 4
  const glasses = (h >> 15) % 3 === 0
  const smile = (h >> 18) % 2 === 0
  const id = `g${h % 100000}`

  const hairPath =
    style === 0
      ? `<path d="M100 62c-26 0-42 18-42 42 0 6 1 11 3 16 2-20 15-30 39-30s37 10 39 30c2-5 3-10 3-16 0-24-16-42-42-42Z" fill="${hair}"/>`
      : style === 1
        ? `<path d="M100 58c-28 0-45 20-45 46 0 10 3 18 7 24V104c14 6 26 8 38 8s24-2 38-8v24c4-6 7-14 7-24 0-26-17-46-45-46Z" fill="${hair}"/><circle cx="60" cy="128" r="12" fill="${hair}"/><circle cx="140" cy="128" r="12" fill="${hair}"/>`
        : style === 2
          ? `<path d="M100 60c-25 0-43 17-43 40 0 8 2 15 5 21l6-30 12 10 10-16 12 14 12-14 10 16 12-10 6 30c3-6 5-13 5-21 0-23-18-40-43-40Z" fill="${hair}"/>`
          : `<path d="M100 60c-26 0-44 18-44 42 0 7 1 13 4 19 3-18 10-26 20-28 8 8 20 12 32 12 10 0 18-2 24-6 4 5 6 12 7 22 3-6 5-12 5-19 0-24-18-42-48-42Z" fill="${hair}"/>`

  const eyes = glasses
    ? `<circle cx="84" cy="112" r="13" fill="none" stroke="#4A3B38" stroke-width="3"/><circle cx="116" cy="112" r="13" fill="none" stroke="#4A3B38" stroke-width="3"/><path d="M97 112h6" stroke="#4A3B38" stroke-width="3"/><circle cx="84" cy="112" r="4" fill="#4A3B38"/><circle cx="116" cy="112" r="4" fill="#4A3B38"/>`
    : `<circle cx="85" cy="112" r="4.5" fill="#4A3B38"/><circle cx="115" cy="112" r="4.5" fill="#4A3B38"/>`

  const mouth = smile
    ? `<path d="M88 130c4 7 20 7 24 0" stroke="#4A3B38" stroke-width="3.5" fill="none" stroke-linecap="round"/>`
    : `<path d="M90 131h20" stroke="#4A3B38" stroke-width="3.5" fill="none" stroke-linecap="round"/>`

  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" width="200" height="200">
<defs><linearGradient id="${id}" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="${c1}"/><stop offset="1" stop-color="${c2}"/></linearGradient></defs>
<rect width="200" height="200" fill="url(#${id})"/>
<circle cx="158" cy="44" r="20" fill="#FFFFFF" opacity=".35"/>
<circle cx="36" cy="164" r="26" fill="#FFFFFF" opacity=".25"/>
<path d="M100 152c-30 0-54 18-58 48h116c-4-30-28-48-58-48Z" fill="${shirt}"/>
<path d="M84 140h32v20c0 8-32 8-32 0v-20Z" fill="${skin}"/>
<ellipse cx="100" cy="112" rx="40" ry="44" fill="${skin}"/>
${hairPath}
${eyes}
${mouth}
<ellipse cx="72" cy="126" rx="7" ry="4.5" fill="#FF5D73" opacity=".28"/>
<ellipse cx="128" cy="126" rx="7" ry="4.5" fill="#FF5D73" opacity=".28"/>
</svg>`
}

export function avatarDataUrl(seed: string): string {
  return `data:image/svg+xml;charset=utf-8,${encodeURIComponent(avatarSvg(seed))}`
}

export function avatarGradient(seed: string): string {
  const [c1, c2] = pick(BACK, hash(seed) >> 9)
  return `linear-gradient(135deg, ${c1}, ${c2})`
}
