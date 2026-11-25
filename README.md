# Station Master Success 2026

Beginner-friendly RRB Station Master preparation starter for CEN 08/2026.

## Included
- CEN 08/2026 CBT pattern and syllabus overview from the user-provided notification page
- Day 1 English + Telugu fundamentals
- 10-question interactive quiz with scoring and explanations
- Responsive static website; no API keys, database, or paid service required
- GitHub Pages deployment workflow

## Run locally
Open `index.html` in a browser. For best results, serve this folder with a local static server because the quiz loads `data/day-01.json` using fetch.

## Deploy on GitHub Pages
1. Open Settings → Pages.
2. Set source to GitHub Actions.
3. The included workflow deploys the site after a push to `main`.
4. Your site will be available at `https://YOUR-USERNAME.github.io/station-master-success-2026/`.

## Add future lessons
Add `data/day-02.json` following the same question structure and extend the lesson UI.

## Important
This is an independent study aid, not an official RRB website. Confirm recruitment rules, exam pattern, dates, eligibility, and medical standards from the official CEN 08/2026 notification and RRB website.
## Automatic study emails (every 4 hours)

The `.github/workflows/study-email.yml` workflow sends a fresh random set of 10 bilingual questions from the question bank every four hours (UTC schedule; GitHub may start scheduled runs a little later). It also supports manual runs from Actions → Send Station Master Study Email → Run workflow.

### One-time Gmail setup
1. Enable 2-Step Verification on the Gmail account you will send from.
2. Create a Google App Password for this workflow (do not use your normal Gmail password).
3. In this repository, open Settings → Secrets and variables → Actions → New repository secret.
4. Add these two secrets:
   - `STUDY_GMAIL_USER` — your sending Gmail address.
   - `STUDY_GMAIL_APP_PASSWORD` — the 16-character Google App Password.
5. Open Actions → Send Station Master Study Email → Run workflow to test the first email.

The email is sent to the same address configured in the workflow. Never commit your Gmail password or App Password to the repository. If the secrets are missing or invalid, the email workflow will fail rather than expose credentials.
