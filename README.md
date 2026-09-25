<p align="center">
  <a href="https://github.com/YOUR-USERNAME/YOUR-REPO">
    <img
      src="https://iili.io/nA7Jv0x.jpg"
      alt="The Posto Banner"
      width="600"
      style="border: 3px solid #5865F2; border-radius: 20px;"
    />
  </a>
</p>

<h1 align="center">✈️ The Posto — Telegram Channel Post Maker Bot</h1>

<p align="center">
  <b>Create. Format. Publish.</b><br>
  A production-ready Telegram Channel Post Maker Bot with a Dark Red & Black Mini App, live formatting preview, colored inline buttons, direct media URL support, and automatic scheduling.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-crimson?style=for-the-badge&logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/Deploy-Render-black?style=for-the-badge&logo=render&logoColor=red" />
  <img src="https://img.shields.io/badge/Database-MongoDB-green?style=for-the-badge&logo=mongodb&logoColor=white" />
  <img src="https://img.shields.io/badge/Mini%20App-Dark%20Red%20%26%20Black-darkred?style=for-the-badge" />
</p>

---

## ✨ Features

- 🎨 **Dark Red & Black Web Mini App**: Telegram-native web panel with real-time live preview.
- 🔵🟢🔴 **Colored Inline Buttons**: Add Default, Primary (Blue), Success (Green), and Danger (Red) inline buttons.
- 🔗 **Direct Media URLs**: Upload files or paste remote image/video/audio links directly.
- 💾 **Smart 48-Hour Drafts**: Automatically saves drafts and prunes them after 48 hours to save MongoDB storage.
- 📜 **Published Posts History**: View and re-load previously published channel posts with 1-click.
- ⏱️ **Auto-Delete & Auto-Pin**: Scheduled auto-deletion and auto-pinning for channel announcements.
- 🩺 **Built-in `/health` Check**: Easy UptimeRobot integration so Render free instances **never sleep**!

---

## 🚀 One-Click Deploy to Render

### Step 1: Push Code to GitHub
Fork or push this repository to your GitHub account.

### Step 2: Deploy on Render
1. Go to [Render Dashboard](https://dashboard.render.com/) and click **New +** → **Web Service**.
2. Connect your GitHub repository.
3. Configure the following:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python3 bot.py`
   - **Health Check Path**: `/health`
4. Add your **Environment Variables** (see table below).
5. Click **Deploy Web Service**!

---

## ⏰ How to Keep Render Awake 24/7 (UptimeRobot)

Render free web services enter sleep mode after 15 minutes of inactivity. To keep your bot running **24/7 for free**:

1. Go to [UptimeRobot.com](https://uptimerobot.com/) (Free).
2. Click **Add New Monitor**.
3. Set:
   - **Monitor Type**: `HTTP(s)`
   - **Friendly Name**: `Posto Bot Health`
   - **URL / IP**: `https://YOUR-APP-NAME.onrender.com/health`
   - **Monitoring Interval**: `Every 5 minutes`
4. Click **Create Monitor**.
> 💡 *Done! UptimeRobot will ping `/health` every 5 minutes, preventing Render from ever sleeping.*

---

## ⚙️ Environment Variables

Add these in your `.env` or Render **Environment** tab:

| Variable | Required | Description | Example |
| :--- | :---: | :--- | :--- |
| `BOT_TOKEN` | **Yes** | Telegram Bot Token from [@BotFather](https://t.me/BotFather) | `123456:ABC-DEF...` |
| `API_ID` | **Yes** | Telegram API ID from [my.telegram.org](https://my.telegram.org) | `12345678` |
| `API_HASH` | **Yes** | Telegram API Hash from [my.telegram.org](https://my.telegram.org) | `0123456789abcdef...` |
| `MONGO_URI` | **Yes** | MongoDB Atlas Connection URI | `mongodb+srv://user:pass@cluster.mongodb.net` |
| `DATABASE_NAME` | No | Database name (Default: `posto`) | `posto` |
| `OWNER_ID` | **Yes** | Your Telegram numerical User ID | `86742154` |
| `BASE_URL` | No | Public URL of your deployed Web App | `https://your-bot.onrender.com` |
| `PORT` | No | Web port (Default: `8080`, Render sets this automatically) | `8080` |

---

## 💻 Run Locally

```bash
# 1. Clone repo
git clone https://github.com/your-username/posto.git
cd posto

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create .env file & add your keys
cp .env.example .env

# 4. Start Posto
python3 bot.py
```
Open `http://localhost:8080` in your browser to access the Web Editor!

---

## 🐳 Run with Docker

```bash
docker build -t the-posto .
docker run -d -p 8080:8080 --env-file .env the-posto
```

---

## 🎨 How to Use Colored Inline Buttons

In your Pyrogram bot scripts, you can send colored buttons:

```python
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.enums import ButtonStyle

buttons = InlineKeyboardMarkup([
    [
        InlineKeyboardButton(
            text="🔵 Primary Button",
            url="https://t.me/yourchannel",
            style=ButtonStyle.PRIMARY   # 🔵 Dark Blue / Accent
        )
    ],
    [
        InlineKeyboardButton(
            text="🟢 Success Button",
            url="https://t.me/yourchannel",
            style=ButtonStyle.SUCCESS   # 🟢 Green
        )
    ],
    [
        InlineKeyboardButton(
            text="🔴 Danger Button",
            url="https://t.me/yourchannel",
            style=ButtonStyle.DANGER    # 🔴 Red
        )
    ]
])

await message.reply("Choose an option:", reply_markup=buttons)
```

---

<h2 align="center">📊 Project Status</h2>

<p align="center">
  <img src="https://img.shields.io/badge/Status-Active-138808?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Version-1.0.0-FF9933?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Maintained-Yes-138808?style=for-the-badge"/>
</p>

## 📱 Bot Commands

- `/start` — Welcome message with Web App button & quick guide.
- `/channels` — Manage connected channels & verify admin rights.
- `/addchannel` — Instructions to add the bot as channel admin.
- `/help` — Full guide and formatting cheat sheet.

---

## 📜 License

This project is licensed under the MIT License.
See the `LICENSE` file for details.

<p align="center">
  <b>The Posto</b> • Built for Telegram Creators with ❤️
</p>

<h2 align="center">❤️ Community</h2>

<p align="center">
  If you find <b>The Posto</b> useful, consider ⭐ starring the repository.
  <br><br>
  <p align="center">
  <a href="https://t.me/providerborz">
    <img src="https://img.shields.io/badge/🇮🇳%20JOIN%20OUR%20TELEGRAM-@providerborz-FF9933?style=for-the-badge&logo=telegram&logoColor=white&labelColor=138808" alt="Join Telegram"/>
  </a>
</p>
