# HR Resume Processor — Kaji Skill

Chat-native HR assistant for the Ski Lift Operator hiring pipeline.
Same backend as the dashboard — Mattermost is the interface.

---

## Install via Skills Marketplace (Recommended)

The fastest way — use the Kaji Admin Monitor web app.

### Step 1 — Open the Skills Marketplace

Go to: **https://kaji-admin-monitor.dev.hyperplane.dev**

Navigate to **Skills** in the left sidebar.

### Step 2 — Add the repo

Click **"Install from GitHub"** and enter:

```
robert-shakudo/hr-resume-demo
```

The marketplace will scan the repo and detect the skill at `skill/SKILL.md`.

### Step 3 — Select and install

Select **`hr-resume-processor`** from the detected skills list and click **Install**.

The skill is now available to Kaji on your pod.

### Step 4 — Configure the backend URL

In the Skills section, find `hr-resume-processor` → **Configure** → set:

```
HR_APP_URL = https://hr-resume-demo.dev.hyperplane.dev
```

---

## Install via CLI (`openskills`)

Alternatively, run from a terminal in your Kaji session:

```bash
openskills install robert-shakudo/hr-resume-demo/skill
```

This clones the repo, finds `skill/SKILL.md`, and installs `hr-resume-processor` to `.claude/skills/`.

Set the environment variable:

```bash
echo "HR_APP_URL=https://hr-resume-demo.dev.hyperplane.dev" \
  >> /root/gitrepos/.claude/skills/hr-resume-processor/.env
```

Verify it works:

```bash
openskills list
# hr-resume-processor (project) — Chat-native HR assistant...
```

---

## Usage in Mattermost

Once installed, tag Kaji in any thread:

```
@kaji show top 10 ski lift candidates
@kaji score all candidates
@kaji email the top 5 in reviewing
@kaji book interviews for everyone who replied
@kaji give me a hiring summary
@kaji sync paycom
```

Kaji calls the HR app API and returns Mattermost-formatted results in the thread.

See [SKILL.md](./SKILL.md) for the full command reference.

---

## Requirements

- Python 3.10+ (pre-installed in Kaji sessions)
- No extra packages — uses Python stdlib only
- HR app backend running at `HR_APP_URL`
