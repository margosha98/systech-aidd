import { Github } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { ThemeToggle } from '@/components/theme-toggle';

/**
 * Header приложения с логотипом, переключателем темы и ссылкой на GitHub
 */
export function Header() {
  return (
    <header className="flex items-center justify-between border-b px-6 py-4">
      <div className="flex items-center gap-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-md border bg-primary text-primary-foreground">
          <span className="text-sm font-semibold">З</span>
        </div>
        <h1 className="text-xl font-semibold">Знайкин Dashboard</h1>
      </div>
      <div className="flex items-center gap-2">
        <ThemeToggle />
        <Button variant="outline" size="sm" asChild>
          <a
            href="https://github.com/systech-aidd/telegram-bot"
            target="_blank"
            rel="noopener noreferrer"
            className="flex items-center gap-2"
          >
            <Github className="h-4 w-4" />
            GitHub
          </a>
        </Button>
      </div>
    </header>
  );
}

