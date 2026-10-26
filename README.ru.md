<div align="center">

[English](README.md) | **Русский**

# ☀️ Таузенд Санни на графике вкладов GitHub

![Python](https://img.shields.io/badge/python-3.12-blue.svg?style=for-the-badge&logo=python&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
![SVG](https://img.shields.io/badge/SVG-Dynamic_Animation-ffb000?style=for-the-badge&logo=svg&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

[![Generate One Piece Contribution Graph](https://img.shields.io/github/actions/workflow/status/rakhmanov-tr/Onepiece-Contribution-Graph/onepiece-graph.yml?style=for-the-badge&label=Build%20Status)](https://github.com/rakhmanov-tr/Onepiece-Contribution-Graph/actions)

---

### ⚓ График вкладов становится палубой Таузенд Санни

Python-скрипт и GitHub Actions читают календарь вкладов через GitHub GraphQL API и прокладывают курс на год. Луффи вылезает из бочки с саке Зоро, прыгает по самым высоким клеткам, хватает мясо в самые насыщенные дни и берётся за штурвал. Зоро съезжает с марсовой площадки. По краю палубы растут мандариновые деревья Нами.

[**Сообщить о баге**](https://github.com/rakhmanov-tr/Onepiece-Contribution-Graph/issues) • [**Политика безопасности**](SECURITY.md)

</div>

---

## 🚀 Как это выглядит

<picture>
  <img alt="Луффи на графике вкладов Таузенд Санни" src="onepiece_contribution.svg" width="100%">
</picture>

---

## 🌟 Что умеет Санни

| Часть корабля | Что происходит |
|---|---|
| 🏃‍♂️ **Паркур Луффи** | Луффи не бежит по прямой. На каждой неделе он встаёт на самую высокую клетку с вкладами и перепрыгивает, если высота меняется. |
| 🍖 **Мясо** | Самые насыщенные дни (уровень 4) ставят на клетку кусок мяса. Луффи подбирает его на ходу: кусок поднимается и исчезает. |
| 🍶 **Саке Зоро** | Забег начинается внутри бочки с саке. Луффи вылезает из неё на палубу. |
| 🍊 **Роща Нами** | Вдоль борта Санни растут мандариновые деревья, та самая роща, которую Нами держит на корабле. |
| ⚔️ **Зоро на вахте** | Зоро ждёт на марсе. Когда Луффи добирается до мачты, Зоро съезжает на палубу. |
| 🏴 **Штурвал** | Луффи проходит год, съезжает по мачте и заканчивает у штурвала. |
| 🛡️ **Чистый SVG** | Вся сцена собрана из SVG, без внешних картинок. Один проход длится 20 секунд и крутится сам. |

---

## 🛠️ Как поставить себе

`generate.py` уже лежит в этом репозитории. Скопируй его к себе или сделай форк: workflow возьмёт логин владельца репозитория.

### 1. Скрипт

Положи в свой репозиторий `generate.py` из этого.

Проверка локально:

```bash
python generate.py --user YOUR_USERNAME
```

Команда пишет `onepiece_contribution.svg` в корень. Страница [`preview/index.html`](preview/index.html) показывает тот же файл.

### 2. Автоматизация

Создай `.github/workflows/onepiece-graph.yml`:

```yaml
name: Generate One Piece Contribution Graph

on:
  schedule:
    - cron: "0 0 * * *" # every day at midnight UTC
  workflow_dispatch: # run it by hand

jobs:
  build:
    runs-on: ubuntu-latest
    permissions:
      contents: write
    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Generate One Piece SVG
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GITHUB_ACTOR: ${{ github.repository_owner }}
        run: python generate.py

      - name: Commit and push SVG
        run: |
          git config user.name "github-actions[bot]"
          git config user.email "41898282+github-actions[bot]@users.noreply.github.com"
          git add onepiece_contribution.svg
          git commit -m "Update One Piece contribution graph" || echo "No changes to commit"
          git push
```

Workflow запускается по расписанию и вручную. Он коммитит `onepiece_contribution.svg` в `main`. Картинка живёт в этой одной ветке.

### 3. Права на запись

1. Открой **Settings → Actions → General**.
2. В блоке **Workflow permissions** выбери **Read and write permissions**.
3. Нажми **Save**.

### 4. Первый запуск

В форке открой вкладку **Actions** и нажми **I understand my workflows, go ahead and enable them**. GitHub не запускает workflows, пока это не сделано. Затем выбери **Generate One Piece Contribution Graph** и нажми **Run workflow**. Когда сборка закончится, `onepiece_contribution.svg` появится в корне `main`.

---

## 🖼️ Как показать на профиле

Вставь это в `README.md` своего профиля. Замени `YOUR_USERNAME` и `YOUR_REPO`:

```html
<div align="center">
  <a href="https://github.com/YOUR_USERNAME/YOUR_REPO">
    <img src="https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/onepiece_contribution.svg" width="100%" />
  </a>
</div>
```

---

## 🎨 Как поменять команду

Всё лежит в `generate.py`:

- **Скорость.** `LOOP_SECONDS` — длина одного прохода. Сейчас это 20 секунд.
- **Луффи.** `RUNNER_PIXELS` и `RUNNER_COLORS`. Каждый символ в строке — один пиксель.
- **Зоро.** `LOOKOUT_PIXELS`. Он стоит на марсе.
- **Остальная сцена.** `CLOUD_PIXELS`, `BUSH_PIXELS` и `MEAT_PIXELS` — облака, мандариновые деревья Нами и мясо.
- **Санни.** Бочка с саке, палуба, мачта и штурвал нарисованы фигурами ниже по файлу.
- **Небо.** Цвет класса `.bg` в стилях SVG.

---

## 🤝 Основа

Идея уровня и расчёт пути взяты из [sapthesh/Mario-Contribution-Graph](https://github.com/sapthesh/Mario-Contribution-Graph) (MIT, Copyright (c) 2026 Sapthesh V). Спрайты Мугивар в этой копии свои.

<div align="center">

Сделано по следу Mario Contribution Graph · [MIT](LICENSE)

</div>
