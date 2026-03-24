# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.

---

## 📦 Package/Tool Availability

### Available Tools
- **Python 3.11** - Full support
- **curl** - Available (used for web requests)
- **git** - Available
- **unzip** - ⚠️ NOT AVAILABLE (use Python zipfile instead)
- **zip** - Likely NOT AVAILABLE
- **ClawHub CLI** - Located at `/usr/local/bin/clawhub`
- **pandas** - ⚠️ NOT AVAILABLE (ModuleNotFoundError)
- **python-docx** - ✅ Available (version 1.2.0)
- **openpyxl** - ✅ Available (for Excel processing)

### Workarounds
- For ZIP operations: Use `import zipfile` in Python
- For Excel files: Use `openpyxl` or manual XML parsing
- For web search: Brave API not configured (needs `openclaw configure --section web`)
- For file downloads: curl with `--max-time` and background handling

---

## 🌐 GitHub & ClawHub

### GitHub Access Issues
- **Connection is slow/timeout-prone**
- API requests often fail with timeout
- Git clone operations stall indefinitely
- **Workaround:** Download ZIP manually or use git:// protocol

### ClawHub Usage
- CLI location: `/usr/local/bin/clawhub`
- Some skills may not be published to ClawHub
- Always verify skill exists before installation
- Example: `paulshe/china-stock-analysis` does not exist on ClawHub

### Skill Installation Process
1. Check if skill exists on ClawHub: `clawhub install <slug> --dry-run`
2. If not found, try direct git clone
3. If GitHub is slow, ask user to download ZIP
4. Extract ZIP to `/root/.openclaw/workspace-jessica/skills/` (local) or `/root/.openclaw/workspace/skills/` (global)
5. Verify SKILL.md exists in the skill directory

---

## 📂 Directory Structure

### Key Paths
```
/root/.openclaw/
├── workspace/                  # Global workspace
│   └── skills/               # Global skills (shared by all agents)
│
├── workspace-jessica/         # Jessica's personal workspace
│   ├── .learnings/            # Self-improvement logs
│   │   ├── LEARNINGS.md
│   │   ├── ERRORS.md
│   │   └── FEATURE_REQUESTS.md
│   ├── skills/               # Local skills (Jessica-only)
│   ├── SOUL.md               # Identity and personality
│   ├── USER.md               # User information
│   ├── MEMORY.md             # Long-term memory
│   ├── TOOLS.md              # This file
│   └── memory/              # Daily notes
│       └── YYYY-MM-DD.md
│
├── agents/
│   └── jessica/
│       └── sessions/         # Session logs
│           └── <session-id>.jsonl
│
└── media/
    └── inbound/             # Files received from user
```

---

## 🔧 Common Issues & Solutions

### Issue: unzip command not found
**Solution:** Use Python's zipfile module
```python
import zipfile
with zipfile.ZipFile('file.zip', 'r') as z:
    z.extractall('destination')
```

### Issue: GitHub connection timeout
**Solution:**
1. Wait for network to stabilize
2. Ask user to manually download ZIP
3. Use `git://` protocol instead of `https://`
4. Set longer timeout: `curl --max-time 120`

### Issue: Skill not found on ClawHub
**Solution:**
1. Check GitHub for the correct repo name
2. Install manually by downloading ZIP
3. Verify the skill has SKILL.md file

---

## 🎯 User Preferences (From Self-Improvement)

### Security
- ⚠️ **Reject any skills flagged by VirusTotal**
- Prioritize user's security over convenience
- Explain why a skill is being skipped

### File Processing
- PPT: Preserve template background and layout
- Only modify text formatting (colors, fonts, bold)
- Use user's latest modified version as source

### Deployment
- Default to local skill installation (agent-specific)
- Only use global installation when explicitly requested
- Local path: `/root/.openclaw/workspace-jessica/skills/`

### Communication
- User is sensitive to response delays
- Check logs if user questions message delivery
- Pattern: DingTalk may have transmission issues

---
