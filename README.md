# Posto — Telegram Channel Post Maker Bot

> **Create. Format. Publish.**  
> A production-ready Telegram Channel Post Maker Bot with a sleek native web editor, custom typography, MongoDB persistence, watermark engine, auto-pin, and scheduled auto-delete.

---

## 1. Features

- **Custom Presentation Font**: All user-facing bot messages and button labels are automatically formatted in the custom small-caps alphabet (`ᴧʙᴄᴅєꜰɢʜιᴊᴋʟᴍɴσᴩǫʀѕтυνω᥊ʏᴢ`) without corrupting technical identifiers or URLs.
- **Telegram Native Web Post Creator**: Clean, zero-build, responsive web panel built with vanilla HTML5/CSS/JavaScript and served directly by Python.
- **Full Media Support**: Upload and publish Photos (JPEG, PNG), Videos (MP4), Audio (MP3), Documents (PDF, ZIP), and formatted Text-Only announcements.
- **Strict Telegram Limit Enforcement**: Live character counter dynamically enforcing Telegram's official caption limits (1,024 characters for media captions, 4,096 characters for text messages) with custom warning banners.
- **Full Formatting Toolbar**: Support for Telegram Markdown and HTML entities (Bold, Italic, Underline, Strikethrough, Spoiler, Code, Code Block, Links, Blockquotes).
- **Custom Inline URL Buttons**: Dynamic multi-row inline button builder with live URL validation.
- **Reactions Configurator**: Toggle native Telegram reaction buttons (👍, ❤️, 🔥, 🎉, 👏, ⚡, 💯, 🤔).
- **Image Watermarking Engine**: Clean transparency overlay for channel branding with customizable position (bottom-right, bottom-left, top-right, top-left, center), opacity, and size. Skips re-encoding when disabled.
- **Auto-Pinning**: Automatically pins published posts to the channel if the bot has admin pin permissions.
- **Persistent Auto-Delete Scheduler**: Messages scheduled for deletion are stored in MongoDB to survive bot and server restarts.
- **Protected Content**: One-click toggle for `protect_content` (disables forward & copy).
- **Multi-Channel Management**: Connect, verify administrator permissions, and switch between multiple managed channels.
- **Drafts System**: Save and load incomplete posts directly from the web panel or Telegram interface.
- **Fast Async Architecture**: Built on non-blocking async Python, async MongoDB (Motor) with connection pooling, and `aiohttp`.

---

## 2. Interface Preview

```
+--------------------------------------------------------------+
| ✈️ Posto v2.4                    📂 Drafts (3)  ● Connected  |
+-------------------------------+------------------------------+
| 📢 TARGET CHANNEL              | 📱 LIVE TELEGRAM PREVIEW     |
| [ Demo Announcements (@demo) ]| +--------------------------+ |
|                               | | 📢 Demo Announcements    | |
| 🖼️ MEDIA ATTACHMENT           | | +----------------------+ | |
| [Photo] [Video] [Audio] [Doc] | | | [ Image Preview ]    | | |
| [ 📤 Click or Drag & Drop ]   | | |    @PostoChannel (wm)| | |
|                               | | +----------------------+ | |
| ✍️ POST CAPTION               | | <b>WELCOME TO POSTO</b>  | |
| [B] [I] [U] [S] [Sp] [C] [Link| | Create. Format. Publish. | |
| Caption text with markdown... | | 👁️ 1.4k  12:45  📌 🔒    | |
| 45 / 1024 characters          | +--------------------------+ |
|                               | [ ᴡᴀᴛᴄʜ ]  [ ᴅᴏᴡɴʟᴏᴀᴅ ]      |
| 🔘 INLINE BUTTONS             | [ ᴜᴘᴅᴀᴛᴇꜱ ]                  |
| Row 1: [ ᴡᴀᴛᴄʜ ] [ ᴅᴏᴡɴʟᴏᴀᴅ ] | 👍 12   ❤️ 8   🔥 24        |
| Row 2: [ ᴜᴘᴅᴀᴛᴇꜱ ]            +------------------------------+
|                                                              |
| 🚀 PUBLISH NOW   💾 SAVE DRAFT   ⏰ SCHEDULE   🗑️ RESET      |
+--------------------------------------------------------------+
```

---

## 3. Requirements

- **Python**: 3.9, 3.10, 3.11, or 3.12
- **MongoDB**: MongoDB 5.0+ or MongoDB Atlas (Free M0 cluster supported)
- **Telegram Bot Token**: From [@BotFather](https://t.me/BotFather)
- **Telegram API Credentials**: From [my.telegram.org](https://my.telegram.org) (API ID & API Hash)
- **No Node.js or Vite required**: Plain HTML, CSS, and vanilla JS served directly by the Python application.

---

## 4. Telegram Bot Setup

1. Open Telegram and message [@BotFather](https://t.me/BotFather).
2. Send `/newbot`.
3. Choose a display name (e.g., `Posto Post Maker`).
4. Choose a username ending in `bot` (e.g., `PostoChannelPostBot`).
5. Copy the generated `BOT_TOKEN`.
6. Visit [my.telegram.org](https://my.telegram.org), log in, navigate to **API Development Tools**, and obtain your `API_ID` (integer) and `API_HASH` (hex string).

---

## 5. BotFather Configuration

To optimize your bot's UX:
- `/setdescription`: Set a brief overview of Posto.
- `/setabouttext`: `Posto — Create. Format. Publish. The ultimate channel post maker.`
- `/setuserpic`: Upload an avatar icon.
- `/setcommands`: Register the following commands:
  ```
  start - Launch the Posto home dashboard
  web - Open the Web Post Creator
  channels - List your connected channels
  addchannel - Connect a channel where bot is admin
  drafts - View and manage saved drafts
  help - Display usage instructions
  ```
- `/setmenubutton`: Configure the web app menu button pointing to your `BASE_URL`.

---

## 6. MongoDB Setup

Posto utilizes an async Motor MongoDB client with connection pooling.

### Option A: MongoDB Atlas (Cloud Free Tier)
1. Sign up at [mongodb.com/cloud/atlas](https://www.mongodb.com/cloud/atlas).
2. Create a free **M0** cluster.
3. Under **Database Access**, create a user with read/write privileges.
4. Under **Network Access**, add IP `0.0.0.0/0` (allow access from anywhere).
5. Click **Connect** > **Drivers** > **Python**, and copy the connection string:
   ```env
   MONGO_URI=mongodb+srv://username:password@cluster0.mongodb.net/?retryWrites=true&w=majority
   DATABASE_NAME=posto
   ```

### Option B: Local MongoDB (Linux / macOS / Termux)
```bash
sudo systemctl start mongod
# Connection URI:
MONGO_URI=mongodb://localhost:27017
DATABASE_NAME=posto
```

---

## 7. Environment Variables

Create a `.env` file in the project root:

| Variable | Required | Default | Description |
| :--- | :---: | :---: | :--- |
| `BOT_TOKEN` | **Yes** | - | Telegram Bot token from @BotFather |
| `API_ID` | **Yes** | - | Telegram API ID from my.telegram.org |
| `API_HASH` | **Yes** | - | Telegram API Hash from my.telegram.org |
| `MONGO_URI` | **Yes** | - | MongoDB connection URI string |
| `DATABASE_NAME` | No | `posto` | Database name |
| `OWNER_ID` | No | `0` | Telegram user ID of bot administrator |
| `WEB_HOST` | No | `0.0.0.0` | Bind host for Python web server |
| `WEB_PORT` | No | `8080` | Port for web panel (reads `PORT` if set) |
| `BASE_URL` | No | `http://localhost:8080` | Public URL for WebApp links |
| `START_IMAGE` | No | `start_image.jpg` | Welcome image path or public URL |
| `LOG_CHANNEL_ID`| No | - | Telegram channel ID for error logs |
| `SESSION_SECRET`| No | auto-generated | Secret key for signing web tokens |

---

## 8. Local Installation

```bash
# 1. Clone repository
git clone https://github.com/your-username/posto.git
cd posto

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install Python dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
nano .env  # Enter your BOT_TOKEN, API_ID, API_HASH, MONGO_URI

# 5. Launch Posto
python bot.py
```

---

## 9. Termux Installation (Android)

Run directly on your Android phone using Termux:

```bash
# 1. Update Termux packages
pkg update && pkg upgrade -y
pkg install -y python git clang libjpeg-turbo libpng

# 2. Clone repository
git clone https://github.com/your-username/posto.git
cd posto

# 3. Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
nano .env

# 5. Start Posto in background or screen
python bot.py
```

---

## 10. VPS Deployment (Ubuntu / Debian / systemd)

```bash
# 1. Clone to /opt
cd /opt
sudo git clone https://github.com/your-username/posto.git
cd posto

# 2. Setup venv & dependencies
sudo python3 -m venv venv
sudo ./venv/bin/pip install -r requirements.txt
sudo cp .env.example .env
sudo nano .env

# 3. Create systemd service
sudo nano /etc/systemd/system/posto.service
```

Paste into `/etc/systemd/system/posto.service`:
```ini
[Unit]
Description=Posto Telegram Channel Post Maker Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/posto
ExecStart=/opt/posto/venv/bin/python /opt/posto/bot.py
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now posto
sudo systemctl status posto
```

---

## 11. Render Deployment

1. Create a new **Web Service** on [Render](https://render.com).
2. Connect your Git repository.
3. Configure settings:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
4. In **Environment Variables**, add:
   - `BOT_TOKEN`
   - `API_ID`
   - `API_HASH`
   - `MONGO_URI`
   - `BASE_URL` (e.g. `https://your-service.onrender.com`)
5. Click **Deploy**.

---

## 12. Railway Deployment

1. Create a new project on [Railway](https://railway.app).
2. Select **Deploy from GitHub repo**.
3. Under **Variables**, add all required `.env` values.
4. Railway automatically detects `requirements.txt` and binds to `$PORT`.
5. Under **Settings**, generate a public domain and set it as `BASE_URL`.

---

## 13. Koyeb Deployment

1. On [Koyeb](https://www.koyeb.com), click **Create App**.
2. Select **GitHub** as the deployment source.
3. Builder: **Buildpack** (Python).
4. Run command: `python bot.py`.
5. Set environment variables (`BOT_TOKEN`, `API_ID`, `API_HASH`, `MONGO_URI`, `BASE_URL`).
6. Deploy!

---

## 14. Heroku / Dokku Deployment

Create `Procfile`:
```
web: python bot.py
```
Set config vars:
```bash
heroku config:set BOT_TOKEN="your_token" API_ID="12345" API_HASH="abcde" MONGO_URI="mongodb+srv://..."
git push heroku main
```

---

## 15. Channel Setup

To publish posts to a Telegram channel:
1. Open your target Telegram channel.
2. Go to **Channel Settings** > **Administrators** > **Add Administrator**.
3. Search for your bot username (`@YourBotUsername`) and add it.
4. Grant the required permissions (see section below).
5. Open your bot in private chat and send:
   ```
   /addchannel @YourChannelUsername
   ```
   Or send your channel ID:
   ```
   /addchannel -1001234567890
   ```
6. The bot verifies its administrator privileges and connects the channel to your account.

---

## 16. Permissions Required

| Permission | Required | Purpose |
| :--- | :---: | :--- |
| **Post Messages** | **Yes** | Allows publishing text, media, buttons, and reactions |
| **Edit Messages** | **Yes** | Enables updating published posts |
| **Delete Messages**| **Yes** | Required for the persistent **Auto-Delete Scheduler** |
| **Pin Messages** | Optional | Required if the **Auto-Pin** feature is enabled |

---

## 17. Web Panel Usage

1. In Telegram, send `/web` or tap `ᴄʀєᴧтє ᴩσѕт` > `🌐 ᴄʀєᴧтє ᴩσѕт (ωєʙ єᴅιтσʀ)`.
2. The web editor opens in your browser or Telegram WebApp.
3. Select your target channel from the dropdown.
4. Choose media type (`Photo`, `Video`, `Audio`, `Document`, or `Text Only`) and upload files via drag-and-drop.
5. Compose your caption using the formatting toolbar (`**bold**`, `__italic__`, `||spoiler||`, `code`, blockquotes).
6. Build interactive inline URL button rows.
7. Configure watermarks, auto-pin, auto-delete intervals, and protected content mode.
8. Review the real-time **Live Telegram Post Preview** on the right side.
9. Click **🚀 Publish Now** or **💾 Save Draft**.

---

## 18. Troubleshooting

- **`Unable to connect channel`**: Ensure the bot is added as an **Administrator** with *Post Messages* enabled. Check that the channel username or `-100...` ID is correct.
- **`Media caption exceeds 1024 limit`**: Telegram caps media captions at 1,024 characters. Shorten your caption or switch to a **Text Only** post (which supports up to 4,096 characters).
- **`start_image.jpg not showing`**: Verify `start_image.jpg` exists in the root folder or set `START_IMAGE` in `.env` to a valid file path or public image URL.
- **`MongoDB connection timeout`**: In MongoDB Atlas, verify that IP `0.0.0.0/0` is allowed in **Network Access**, and that your database username and password are correct.

---

## 19. Security Notes

- **Zero Secret Exposure**: Tokens, API hashes, and database URIs are stored server-side and never sent to frontend JavaScript.
- **HMAC Web Authentication**: Web panel sessions use HMAC-SHA256 cryptographically signed tokens tied to the user's Telegram ID.
- **Permission Verification**: The server verifies that the requesting user is an administrator of the target channel before publishing or scheduling.
- **Safe File Handling**: Uploaded files are streamed and sanitized.

---

## 20. License

This project is released under the **MIT License**. Free for personal, commercial, and open-source use.
