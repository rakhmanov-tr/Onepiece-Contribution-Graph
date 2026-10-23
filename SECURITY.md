# 🛡️ Security Policy

## Supported versions

This repository reads a public GitHub contribution calendar and commits an SVG with the default Actions token.

| Version | Supported |
| --- | --- |
| latest on `main` | Yes |
| older copies | No |

## Reporting a vulnerability

Do not open a public issue for a security report, and do not paste tokens into the report.

Use **Security → Report a vulnerability** on this repository. Include:

- what the workflow or script does wrong
- how to reproduce it
- what a token, the log, or the committed SVG could expose

| Stage | What to expect |
| --- | --- |
| Acknowledgement | A reply on the private report |
| Fix | A commit on `main` when the report is valid |

## For people who run the workflow

| Practice | Why |
| --- | --- |
| Use `${{ secrets.GITHUB_TOKEN }}` | GitHub issues this token for the job, and it expires with the job. |
| Keep `contents: write` as the only permission | The job only needs to commit `onepiece_contribution.svg`. |
| Read the Actions log after a run | The log shows which login was drawn and whether the SVG was pushed. |
