export const PROFILE_TAGS = [
  'backend',
  'frontend',
  'fullstack',
  'mobile',
  'gamedev',
  'devops',
  'qa',
  'data-science',
  'data-engineering',
  'machine-learning',
  'cybersecurity',
  'ui-ux',
  'systems-analysis',
  'python',
  'javascript',
  'typescript',
  'java',
  'csharp',
  'c',
  'cpp',
  'go',
  'rust',
  'kotlin',
  'swift',
  'php',
  'ruby',
  'sql',
  'react',
  'vue',
  'angular',
  'fastapi',
  'django',
  'spring',
  'dotnet',
  'flutter',
  'postgresql',
  'mongodb',
  'redis',
  'docker',
  'kubernetes',
  'linux',
  'git',
  'open-source',
  'hackathons',
  'competitive-programming',
  'algorithms',
  'system-design',
  'pet-projects',
  'startups',
  'mentoring',
  'tech-meetups',
  'ctf',
] as const

export type ProfileTag = (typeof PROFILE_TAGS)[number]

export const TAG_GROUPS: { title: string; emoji: string; tags: ProfileTag[] }[] = [
  {
    title: 'Кто ты в команде',
    emoji: '🧭',
    tags: [
      'backend',
      'frontend',
      'fullstack',
      'mobile',
      'gamedev',
      'devops',
      'qa',
      'data-science',
      'data-engineering',
      'machine-learning',
      'cybersecurity',
      'ui-ux',
      'systems-analysis',
    ],
  },
  {
    title: 'Языки',
    emoji: '⌨️',
    tags: [
      'python',
      'javascript',
      'typescript',
      'java',
      'csharp',
      'c',
      'cpp',
      'go',
      'rust',
      'kotlin',
      'swift',
      'php',
      'ruby',
      'sql',
    ],
  },
  {
    title: 'Фреймворки',
    emoji: '🧩',
    tags: ['react', 'vue', 'angular', 'fastapi', 'django', 'spring', 'dotnet', 'flutter'],
  },
  {
    title: 'Инфра и данные',
    emoji: '🛠',
    tags: ['postgresql', 'mongodb', 'redis', 'docker', 'kubernetes', 'linux', 'git'],
  },
  {
    title: 'Движ и интересы',
    emoji: '✨',
    tags: [
      'open-source',
      'hackathons',
      'competitive-programming',
      'algorithms',
      'system-design',
      'pet-projects',
      'startups',
      'mentoring',
      'tech-meetups',
      'ctf',
    ],
  },
]

const STICKER_CLASSES = ['st-pink', 'st-sun', 'st-mint', 'st-grape', 'st-sky'] as const

export function stickerClass(tag: string): string {
  let hash = 0
  for (let i = 0; i < tag.length; i += 1) hash = (hash * 31 + tag.charCodeAt(i)) % 9973
  return STICKER_CLASSES[hash % STICKER_CLASSES.length]
}

export function isProfileTag(value: string): value is ProfileTag {
  return (PROFILE_TAGS as readonly string[]).includes(value)
}
