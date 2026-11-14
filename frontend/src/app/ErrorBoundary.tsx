import { Component } from 'react'
import type { ErrorInfo, ReactNode } from 'react'
import { Button } from '@/components/ui/Button'

interface State {
  error: Error | null
}

export class ErrorBoundary extends Component<{ children: ReactNode }, State> {
  state: State = { error: null }

  static getDerivedStateFromError(error: Error): State {
    return { error }
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('UI crashed', error, info.componentStack)
  }

  render() {
    const { error } = this.state
    if (!error) return this.props.children

    return (
      <div className="mx-auto flex min-h-dvh max-w-lg flex-col items-center justify-center px-6 text-center">
        <span className="text-5xl">🐍</span>
        <h1 className="mt-4 text-2xl">Интерфейс споткнулся</h1>
        <p className="mt-2 text-[14px] text-sub">
          Что-то пошло не так при отрисовке. Перезагрузка обычно лечит; данные демо не потеряются.
        </p>
        <pre className="quote-block mt-5 w-full text-left">
          <code>{`${error.name}: ${error.message}`}</code>
        </pre>
        <div className="mt-6 flex gap-2">
          <Button icon="refresh" onClick={() => window.location.reload()}>
            Перезагрузить
          </Button>
          <Button variant="ghost" onClick={() => this.setState({ error: null })}>
            Попробовать снова
          </Button>
        </div>
      </div>
    )
  }
}
