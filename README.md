# conversation-anigraph

Уровень по сетке вкладов GitHub. Пират вылезает из бочки SAKE на палубе, прыгает по клеткам, собирает мясо на самых насыщенных днях и доходит до штурвала. У мачты смотровой спускается с марса.

Основа взята из [sapthesh/Mario-Contribution-Graph](https://github.com/sapthesh/Mario-Contribution-Graph) (MIT, Copyright (c) 2026 Sapthesh V). Персонаж здесь свой.

## Что менять

В `generate.py`:

- `RUNNER_PIXELS` и `RUNNER_COLORS` — персонаж, каждый символ это пиксель
- `CLOUD_PIXELS`, `BUSH_PIXELS`, `MEAT_PIXELS`, `LOOKOUT_PIXELS` — облака, мандариновые кусты, мясо и смотровой
- ниже по файлу бочка, палуба, мачта и штурвал нарисованы фигурами

## Профиль

```html
<img alt="Contribution level" src="https://raw.githubusercontent.com/rakhmanov-tr/conversation-anigraph/output/level.svg" />
```

## Локально

```bash
python generate.py --user rakhmanov-tr --out dist/level.svg
```
