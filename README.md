# conversation-anigraph

Короткий дракон проходит по сетке вкладов GitHub. Клетки остаются цветами GitHub, дракон — отдельный знак: тёмный на светлой теме, светлый на тёмной, одна латунная точка глаза.

Идея маршрута взята у [Platane/snk](https://github.com/Platane/snk). Рисунок и код здесь свои.

## Профиль

После первого запуска Action файлы лежат в ветке `output`. В README профиля:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/rakhmanov-tr/conversation-anigraph/output/dragon-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/rakhmanov-tr/conversation-anigraph/output/dragon.svg" />
  <img alt="Dragon crossing GitHub contributions" src="https://raw.githubusercontent.com/rakhmanov-tr/conversation-anigraph/output/dragon.svg" />
</picture>
```

## Локально

```bash
python generate.py --user rakhmanov-tr --out dist
```

Нужен только Python 3. Скрипт читает публичный календарь и пишет `dist/dragon.svg` и `dist/dragon-dark.svg`.

Action обновляет ветку `output` каждый день и по кнопке Run workflow.
