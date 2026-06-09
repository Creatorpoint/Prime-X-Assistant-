# 🤖 Prime X Assistant

**Owner:** @PREMGUPTA2M  
**Language:** Hinglish (Hindi + English)  
**Framework:** Pyrogram 2.0 + Gemini AI

---

## 📁 Project Structure

```
prime_x_bot/
├── main.py          # Bot handlers & entry point
├── ai.py            # Gemini AI integration
├── database.py      # SQLite database layer
├── config.py        # Environment variable loader
├── keep_alive.py    # Flask keep-alive server
├── requirements.txt
├── runtime.txt
├── Procfile
└── .env.example
```

---

## ⚙️ Setup

### 1. Clone & Install
```bash
git clone <your-repo>
cd prime_x_bot
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env and fill in all values
```

### 3. Run Locally
```bash
python main.py
```

---

## 🚀 Deploy

### Railway
1. Push code to GitHub
2. Connect repo to Railway
3. Add environment variables from `.env.example`
4. Deploy — it auto-detects `Procfile`

### Render
1. Create a new **Background Worker**
2. Connect GitHub repo
3. Set `Start Command`: `python main.py`
4. Add all environment variables

### Koyeb
1. Deploy from GitHub
2. Set build command: `pip install -r requirements.txt`
3. Set run command: `python main.py`
4. Add environment variables

### VPS / Ubuntu Server
```bash
# Install Python 3.11
sudo apt update && sudo apt install python3.11 python3-pip -y

# Install dependencies
pip3 install -r requirements.txt

# Run with screen or systemd
screen -S primebot
python3 main.py
```

### Termux (Android)
```bash
pkg update && pkg install python
pip install -r requirements.txt
python main.py
```

---

## 📋 Environment Variables

| Variable | Description |
|---|---|
| `BOT_TOKEN` | From @BotFather |
| `API_ID` | From my.telegram.org |
| `API_HASH` | From my.telegram.org |
| `OWNER_ID` | Your Telegram user ID |
| `GEMINI_API_KEY` | From aistudio.google.com |
| `CHANNEL_LINK` | Force subscribe channel link |
| `GROUP_LINK` | Community group link |
| `WELCOME_IMAGE` | Welcome image URL |

---

## 🤖 Commands

| Command | Access | Description |
|---|---|---|
| `/start` | All | Start bot & welcome |
| `/stats` | Owner only | Bot statistics |
| `/broadcast` | Owner only | Message to all users |
| `/gbroadcast` | Owner only | Message to all groups |
| `/strikes` | All | View your strikes |
| `/resetstrikes` | Admins | Reset user strikes |
| `/warns` | Admins | View moderation logs |

---

## ✨ Features

- ✅ Force Subscribe System
- ✅ AI Chat (private & group)
- ✅ Gemini-powered Hinglish responses
- ✅ Anti-spam & Anti-flood
- ✅ 5-strike moderation system
- ✅ Auto-mute on 5th strike
- ✅ SQLite database
- ✅ Broadcast system
- ✅ Keep-alive Flask server
- ✅ Deployment ready

---

**Owner:** @PREMGUPTA2M | **Channel:** https://t.me/+bQUSBWIVT-dmZjA9
