<div align="center">

**English** | [Русский](README.ru.md)

# ☀️ Thousand Sunny GitHub Contribution Graph

![Python](https://img.shields.io/badge/python-3.12-blue.svg?style=for-the-badge&logo=python&logoColor=white)
![GitHub Actions](https://img.shields.io/badge/github%20actions-%232671E5.svg?style=for-the-badge&logo=githubactions&logoColor=white)
![SVG](https://img.shields.io/badge/SVG-Dynamic_Animation-ffb000?style=for-the-badge&logo=svg&logoColor=white)
![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg?style=for-the-badge)

[![Generate One Piece Contribution Graph](https://img.shields.io/github/actions/workflow/status/rakhmanov-tr/Onepiece-Contribution-Graph/onepiece-graph.yml?style=for-the-badge&label=Build%20Status)](https://github.com/rakhmanov-tr/Onepiece-Contribution-Graph/actions)

---

### ⚓ Turn your GitHub contribution graph into the deck of the Thousand Sunny

A Python script and GitHub Actions read your contribution calendar through the GitHub GraphQL API and plot a course across the year. Luffy climbs out of a barrel of Zoro's sake, hops the tallest cells, snatches meat on your busiest days, and takes the helm. Zoro slides down from the crow's nest. Nami's tangerine trees line the deck.

[**Report a Bug**](https://github.com/rakhmanov-tr/Onepiece-Contribution-Graph/issues) • [**Security Policy**](SECURITY.md)

</div>

---

## 🚀 See it in action

<picture>
  <img alt="Luffy crossing the Thousand Sunny contribution graph" src="onepiece_contribution.svg" width="100%">
</picture>

---

## 🌟 What the Sunny can do

| Piece of the ship | What happens |
|---|---|
| 🏃‍♂️ **Luffy's parkour** | Luffy does not jog in a straight line. Each week he lands on the highest cell that has contributions, and he jumps when the height changes. |
| 🍖 **Meat** | Your busiest days (level 4) set out a cut of meat. Luffy grabs it as he passes: the piece pops up and fades. |
| 🍶 **Zoro's sake** | The run starts inside a sake barrel. Luffy climbs out of it onto the deck. |
| 🍊 **Nami's grove** | Tangerine trees sit along the edge of the Sunny, the same grove Nami keeps on board. |
| ⚔️ **Zoro on watch** | Zoro waits in the crow's nest. When Luffy reaches the mast, Zoro slides down to the deck. |
| 🏴 **The helm** | Luffy crosses the year, rides the mast down, and finishes at the ship's wheel. |
| 🛡️ **Pure SVG** | The whole scene is SVG, with no external images. One crossing takes 20 seconds and loops on its own. |

---

## 🛠️ Add it to your own profile

`generate.py` is already in this repository. Copy it into your repo, or fork this one. The workflow uses the repository owner's login.

### 1. The script

Put `generate.py` from this repository in yours.

Try it locally:

```bash
python generate.py --user YOUR_USERNAME
```

That writes `onepiece_contribution.svg` in the repo root. [`preview/index.html`](preview/index.html) shows the same file.

### 2. The automation

Create `.github/workflows/onepiece-graph.yml`:

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

The workflow runs on a schedule and when you start it by hand. It commits `onepiece_contribution.svg` to `main`. The picture lives on that one branch.

### 3. Write permission

1. Open **Settings → Actions → General**.
2. Under **Workflow permissions**, select **Read and write permissions**.
3. Click **Save**.

### 4. First run

On a fork, open the **Actions** tab and click **I understand my workflows, go ahead and enable them**. GitHub leaves workflows off until you do. Then choose **Generate One Piece Contribution Graph** and click **Run workflow**. When the job finishes, `onepiece_contribution.svg` is in the root of `main`.

---

## 🖼️ Show it on your profile

Paste this into your profile `README.md`. Replace `YOUR_USERNAME` and `YOUR_REPO`:

```html
<div align="center">
  <a href="https://github.com/YOUR_USERNAME/YOUR_REPO">
    <img src="https://raw.githubusercontent.com/YOUR_USERNAME/YOUR_REPO/main/onepiece_contribution.svg" width="100%" />
  </a>
</div>
```

---

## 🎨 Change the crew

Everything lives in `generate.py`:

- **Speed.** `LOOP_SECONDS` is the length of one crossing. It is 20 seconds.
- **Luffy.** `RUNNER_PIXELS` and `RUNNER_COLORS`. Each character in a row is one pixel.
- **Zoro.** `LOOKOUT_PIXELS`. He stands in the crow's nest.
- **The rest of the scene.** `CLOUD_PIXELS`, `BUSH_PIXELS`, and `MEAT_PIXELS` are the clouds, Nami's tangerine trees, and the meat.
- **The Sunny.** The sake barrel, deck, mast, and helm are drawn as shapes further down the file.
- **Sky.** The `.bg` color in the SVG styles.

---

## 🤝 Credit

The level idea and the path math come from [sapthesh/Mario-Contribution-Graph](https://github.com/sapthesh/Mario-Contribution-Graph) (MIT, Copyright (c) 2026 Sapthesh V). The Straw Hat sprites in this copy are original.

<div align="center">

Built in the wake of the Mario Contribution Graph · [MIT](LICENSE)

</div>
