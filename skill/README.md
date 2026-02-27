# HR Resume Processor — Kaji Skill

Chat-native HR assistant for the Ski Lift Operator hiring pipeline.
Same backend as the dashboard — Mattermost is the interface.

## Installation

### 1. Copy skill files

```bash
cp -r skill/ /root/gitrepos/.claude/skills/hr-resume-processor/
```

### 2. Set up environment

```bash
cp skill/.env.example /root/gitrepos/.claude/skills/hr-resume-processor/.env
# Edit .env and set HR_APP_URL
```

### 3. Verify

```bash
cd /root/gitrepos/.claude/skills/hr-resume-processor
python hr_client.py summary
```

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

See [SKILL.md](./SKILL.md) for full command reference.

## Requirements

- Python 3.10+
- No extra packages needed (uses stdlib only)
- HR app backend must be running and accessible
