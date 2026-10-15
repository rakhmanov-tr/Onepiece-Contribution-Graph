# conversation-anigraph

Мальчик идёт по сетке вкладов GitHub и ест то, что встречает: мясо на кости, яблоко, банан и рис. На еде у него открывается рот. На обратном ряду он разворачивается.

Клетки остаются цветами GitHub. Персонаж и еда нарисованы своими фигурами.

## Профиль

После запуска Action файлы лежат в ветке `output`. В README профиля:

```html
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/rakhmanov-tr/conversation-anigraph/output/eater-dark.svg" />
  <source media="(prefers-color-scheme: light)" srcset="https://raw.githubusercontent.com/rakhmanov-tr/conversation-anigraph/output/eater.svg" />
  <img alt="A boy eating across GitHub contributions" src="https://raw.githubusercontent.com/rakhmanov-tr/conversation-anigraph/output/eater.svg" />
</picture>
```

## Локально

```bash
python generate.py --user rakhmanov-tr --out dist
```

Нужен только Python 3. Скрипт читает публичный календарь и пишет `dist/eater.svg` и `dist/eater-dark.svg`.

Action обновляет ветку `output` каждый день и по кнопке Run workflow.
