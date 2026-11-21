import { ButtonLink } from '@/components/ui/Button'
import { Logo } from '@/components/layout/Background'

export function NotFoundPage() {
  return (
    <div className="mx-auto flex max-w-xl flex-col items-center py-10 text-center">
      <Logo size={64} />
      <p className="font-display mt-6 text-[64px] leading-none font-extrabold text-coral-deep">404</p>
      <h1 className="mt-3 text-2xl">Такой анкеты нет в базе</h1>
      <p className="mt-2 text-[14px] text-sub">
        Похоже, страницу удалили сборщиком мусора. Вернёмся к живым людям.
      </p>
      <pre className="quote-block mt-6 w-full text-left whitespace-pre-wrap break-words">
        <code>{`Traceback (most recent call last):
  File "router.py", line 404, in resolve
RouteNotFound: ${window.location.pathname}`}</code>
      </pre>
      <div className="mt-6 flex flex-wrap justify-center gap-2">
        <ButtonLink to="/swipes" icon="cards">
          К свайпам
        </ButtonLink>
        <ButtonLink to="/chats" variant="ghost" icon="chat">
          Мои чаты
        </ButtonLink>
      </div>
    </div>
  )
}
