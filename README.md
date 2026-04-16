# Music Recommendation System

Weekly music digest, automatically sourced from Bandcamp Daily, NTS Radio, and Stereogum, filtered through a detailed personal taste profile, and delivered by email every Monday at 9am.

## Setup (plain English — no coding required)

Follow the steps in order. Each step tells you exactly what to do.

---

### Step 1 — Get the code onto GitHub

1. Go to [github.com](https://github.com) and sign in (or create a free account).
2. Click the **+** in the top right → **New repository**.
3. Name it `music-rec`. Leave everything else as default. Click **Create repository**.
4. On your Mac, open the **Terminal** app (search for it in Spotlight with ⌘+Space).
5. Type these commands one at a time, pressing Enter after each:

```bash
cd ~/Desktop/music-rec
git init
git add .
git commit -m "Initial build"
git branch -M main
git remote add origin https://github.com/YOUR_GITHUB_USERNAME/music-rec.git
git push -u origin main
```

Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username.

---

### Step 2 — Get your API keys

You need three things:

**A) Anthropic API key** (powers the recommendation engine)
1. Go to [console.anthropic.com](https://console.anthropic.com) and create an account.
2. Go to **API Keys** → **Create Key**. Copy it — it starts with `sk-ant-`.

**B) Resend API key** (sends the weekly email)
1. Go to [resend.com](https://resend.com) and create a free account.
2. Go to **API Keys** → **Create API Key**. Copy it — it starts with `re_`.
3. In Resend, go to **Domains** and verify your email address so Resend can send from it. Follow the on-screen instructions — it usually just requires clicking a verification link they send you.

**C) App secret** (protects your feedback buttons)
- Make up any long random string. Example: `xK9mP2qL8nR4wT6y`. Write it down.

---

### Step 3 — Deploy to Railway

1. Go to [railway.app](https://railway.app) and create a free account (use your GitHub login).
2. Click **New Project** → **Deploy from GitHub repo** → select `music-rec`.
3. Railway will detect the project and start deploying. Wait for it to go green.
4. Click on your service → **Variables** tab → add these one at a time:

| Variable name | Value |
|---|---|
| `ANTHROPIC_API_KEY` | your Anthropic key (sk-ant-...) |
| `RESEND_API_KEY` | your Resend key (re_...) |
| `DELIVERY_EMAIL` | the email address to send digests to |
| `APP_SECRET` | the random string you made up |
| `DB_PATH` | `/data/music.db` |
| `PORT` | `8080` |

5. After adding variables, click **Settings** → **Volumes** → **Add Volume**, mount path: `/data`. This makes sure your database isn't wiped when Railway restarts.
6. Go back to **Deployments** and click **Redeploy** so the volume takes effect.
7. Copy your app's public URL — it looks like `https://music-rec-production-xxxx.up.railway.app`. You'll need this next.
8. Add one more variable: `APP_URL` = your Railway URL (from step 7).

---

### Step 4 — Set up the cron jobs

In Railway, cron jobs are separate services that run on a schedule.

For each cron job below:
1. In your Railway project, click **+ New** → **Empty Service**.
2. Name it as shown.
3. In the service's **Settings**, find **Start Command** and enter the command shown.
4. Under **Cron Schedule**, enter the schedule shown.
5. Under **Variables**, add the same variables as Step 3 (all 7 of them).

| Service name | Start Command | Cron Schedule |
|---|---|---|
| `scrape-main` | `python main.py scrape-main` | `0 9 * * 1,3,5` |
| `scrape-nts` | `python main.py scrape-nts` | `0 9 * * 2,4` |
| `recommend` | `python main.py recommend` | `0 20 * * 0` |
| `deliver` | `python main.py deliver` | `0 9 * * 1` |

> All times are UTC. If you're on US West Coast time (UTC-7), 9am UTC = 2am local, 8pm UTC = 1pm local. Adjust the hours if you prefer different times — just make sure `recommend` always runs before `deliver`.

---

### Step 5 — Test it manually

Before waiting for the automatic schedule, you can trigger a test run:

1. In Railway, find your `scrape-main` service → click **Deploy** to run it now.
2. Wait for it to finish (check **Logs** tab).
3. Repeat for `scrape-nts`.
4. Then trigger `recommend` — this builds your first digest.
5. Then trigger `deliver` — this sends your first email.

Check your inbox. If it arrives, everything is working.

---

### After that — you're done

The system runs itself from here. Every week:
- Mon/Wed/Fri: scrapes Bandcamp and Stereogum
- Tue/Thu: scrapes NTS Radio
- Sunday evening: builds the digest
- Monday 9am: sends the email

The feedback buttons in the email all write back to the database automatically.

---

## Troubleshooting

**No email arrived:** Check the Railway logs for the `deliver` service. Most common causes: wrong email address in `DELIVERY_EMAIL`, or Resend account not verified.

**"Not enough candidates" error:** The scrapers need to run at least once before the recommendation engine has anything to work with. Trigger `scrape-main` and `scrape-nts` first.

**Feedback buttons show an error:** Make sure `APP_URL` in Railway variables matches your actual Railway URL exactly, and that `APP_SECRET` is the same in all services.
