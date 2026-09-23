#!/usr/bin/env python3
"""
==============================================================================
Posto — Production-Ready Telegram Channel Post Maker Bot
Create. Format. Publish.
==============================================================================
"""

import os
import sys
import json
import time
import hmac
import hashlib
import secrets
import logging
import asyncio
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Any, List, Optional

# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Setup structured logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger("posto")

# ==============================================================================
# CONFIGURATION & ENVIRONMENT
# ==============================================================================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
API_ID_STR = os.environ.get("API_ID", "").strip()
API_ID = int(API_ID_STR) if API_ID_STR.isdigit() else 0
API_HASH = os.environ.get("API_HASH", "").strip()

MONGO_URI = os.environ.get("MONGO_URI", "").strip()
DATABASE_NAME = os.environ.get("DATABASE_NAME", "posto").strip()

OWNER_ID_STR = os.environ.get("OWNER_ID", "").strip()
OWNER_ID = int(OWNER_ID_STR) if OWNER_ID_STR.isdigit() else 0

WEB_HOST = os.environ.get("WEB_HOST", "0.0.0.0").strip()
# Support cloud platforms providing PORT (Render, Railway, Koyeb, Heroku, etc.)
WEB_PORT = int(os.environ.get("PORT", os.environ.get("WEB_PORT", "8080")))

BASE_URL = os.environ.get("BASE_URL", "").rstrip("/")
if not BASE_URL:
    BASE_URL = f"http://localhost:{WEB_PORT}"

START_IMAGE = os.environ.get("START_IMAGE", "start_image.jpg")
LOG_CHANNEL_ID_STR = os.environ.get("LOG_CHANNEL_ID", "").strip()
LOG_CHANNEL_ID = int(LOG_CHANNEL_ID_STR) if LOG_CHANNEL_ID_STR.lstrip("-").isdigit() else None

SESSION_SECRET = os.environ.get("SESSION_SECRET", "").strip()
if not SESSION_SECRET:
    SESSION_SECRET = secrets.token_hex(32)

# File paths
BASE_DIR = Path(__file__).resolve().parent
INDEX_HTML_PATH = BASE_DIR / "index.html"
START_IMAGE_PATH = BASE_DIR / START_IMAGE

# ==============================================================================
# CUSTOM SMALL-CAPS PRESENTATION FONT ENGINE
# Custom alphabet requested: ᴧʙᴄᴅєꜰɢʜιᴊᴋʟᴍɴσᴩǫʀѕтυνω᥊ʏᴢ
# ==============================================================================
SMALL_CAPS_MAP = {
    'a': 'ᴧ', 'b': 'ʙ', 'c': 'ᴄ', 'd': 'ᴅ', 'e': 'є', 'f': 'ꜰ', 'g': 'ɢ',
    'h': 'ʜ', 'i': 'ι', 'j': 'ᴊ', 'k': 'ᴋ', 'l': 'ʟ', 'm': 'ᴍ', 'n': 'ɴ',
    'o': 'σ', 'p': 'ᴩ', 'q': 'ǫ', 'r': 'ʀ', 's': 'ѕ', 't': 'т', 'u': 'υ',
    'v': 'ν', 'w': 'ω', 'x': '᥊', 'y': 'ʏ', 'z': 'ᴢ',
    'A': 'ᴧ', 'B': 'ʙ', 'C': 'ᴄ', 'D': 'ᴅ', 'E': 'є', 'F': 'ꜰ', 'G': 'ɢ',
    'H': 'ʜ', 'I': 'ι', 'J': 'ᴊ', 'K': 'ᴋ', 'L': 'ʟ', 'M': 'ᴍ', 'N': 'ɴ',
    'O': 'σ', 'P': 'ᴩ', 'Q': 'ǫ', 'R': 'ʀ', 'S': 'ѕ', 'T': 'т', 'U': 'υ',
    'V': 'ν', 'W': 'ω', 'X': '᥊', 'Y': 'ʏ', 'Z': 'ᴢ',
}

def to_small_caps(text: str) -> str:
    """
    Converts English text to the Posto custom small-caps alphabet.
    Preserves URLs, commands (/start), mentions (@username), numbers, emojis,
    and HTML tags.
    """
    if not text:
        return ""
    
    words = text.split(" ")
    result_words = []
    
    for word in words:
        # Don't alter links, mentions, commands, or technical identifiers
        if (word.startswith("http://") or word.startswith("https://") or 
            word.startswith("t.me/") or word.startswith("/") or 
            word.startswith("@") or word.startswith("#") or 
            word.startswith("<") or word.endswith(">")):
            result_words.append(word)
            continue
            
        converted = "".join(SMALL_CAPS_MAP.get(c, c) for c in word)
        result_words.append(converted)
        
    return " ".join(result_words)

# Pre-computed styled strings for core UI
TXT_WELCOME_TITLE = "ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ᴘᴏѕᴛᴏ"
TXT_SLOGAN_1 = "ᴄʀᴇᴀᴛᴇ. ꜰᴏʀᴍᴀᴛ. ᴘᴜʙʟɪѕʜ."
TXT_SLOGAN_2 = "ᴄʀᴇᴀᴛᴇ ᴘᴏʟɪѕʜᴇᴅ ᴛᴇʟᴇɢʀᴀᴍ ᴄʜᴀɴɴᴇʟ ᴘᴏѕᴛѕ ꜰᴀѕᴛᴇʀ."

BTN_ADD_CHANNEL = "➕ ᴧᴅᴅ ᴍє тσ ʏσυʀ ᴄʜᴧɴɴєʟ"
BTN_USAGE = "υѕᴧɢє"
BTN_ABOUT = "ᴧʙσυт"
BTN_CREATE_POST = "ᴄʀєᴧтє ᴩσѕт"
BTN_WEB_EDITOR = "🌐 ᴄʀєᴧтє ᴩσѕт (ωєʙ єᴅιтσʀ)"
BTN_MY_CHANNELS = "📢 ᴍʏ ᴄʜᴧɴɴєʟѕ"
BTN_DRAFTS = "📂 ᴅʀᴧꜰтѕ"
BTN_BACK = "⬅️ ʙᴧᴄᴋ"

# ==============================================================================
# ASYNC MONGODB DATABASE LAYER (MOTOR + CONNECTION POOLING)
# ==============================================================================
class Database:
    """
    Production MongoDB interface using Motor async client.
    Includes connection pooling, auto-indexing, and graceful in-memory
    fallback if Mongo credentials are not yet configured.
    """
    def __init__(self, uri: str, db_name: str):
        self.uri = uri
        self.db_name = db_name
        self.client = None
        self.db = None
        self.is_connected = False
        
        # In-memory storage fallback for local/offline testing
        self._mem_users = {}
        self._mem_channels = {}
        self._mem_drafts = {}
        self._mem_scheduled_deletions = []

    async def connect(self):
        if not self.uri:
            logger.warning("MONGO_URI not configured. Running database layer in memory-cache mode.")
            return

        try:
            from motor.motor_asyncio import AsyncIOMotorClient
            self.client = AsyncIOMotorClient(
                self.uri,
                maxPoolSize=50,
                minPoolSize=5,
                serverSelectionTimeoutMS=5000
            )
            self.db = self.client[self.db_name]
            
            # Verify connection
            await self.client.admin.command('ping')
            self.is_connected = True
            logger.info("Connected to MongoDB database '%s' successfully.", self.db_name)
            
            # Initialize indexes
            await self.init_indexes()
        except Exception as e:
            logger.error("Failed to connect to MongoDB: %s. Using memory fallback.", e)
            self.is_connected = False

    async def init_indexes(self):
        if not self.is_connected or self.db is None:
            return
        try:
            await self.db.users.create_index("user_id", unique=True)
            await self.db.channels.create_index([("channel_id", 1), ("added_by", 1)], unique=True)
            await self.db.drafts.create_index("user_id")
            # 48-Hour TTL automatic pruning index for drafts (48 * 3600 = 172800 seconds)
            await self.db.drafts.create_index("created_at_dt", expireAfterSeconds=172800)
            await self.db.scheduled_deletions.create_index("delete_at")
            await self.db.published_posts.create_index([("user_id", 1), ("created_at", -1)])
            logger.info("MongoDB indexes verified (48-hour TTL drafts & optimized storage active).")
        except Exception as e:
            logger.warning("Could not create indexes: %s", e)

    # User Management
    async def get_or_create_user(self, user_id: int, username: str = "", first_name: str = "") -> Dict[str, Any]:
        token = hmac.new(
            SESSION_SECRET.encode(),
            f"user_{user_id}".encode(),
            hashlib.sha256
        ).hexdigest()

        user_data = {
            "user_id": user_id,
            "username": username or "",
            "first_name": first_name or "",
            "auth_token": token,
            "last_active": datetime.now(timezone.utc).isoformat(),
        }

        if self.is_connected and self.db is not None:
            await self.db.users.update_one(
                {"user_id": user_id},
                {"$set": user_data, "$setOnInsert": {"created_at": datetime.now(timezone.utc).isoformat()}},
                upsert=True
            )
            return await self.db.users.find_one({"user_id": user_id})
        else:
            if user_id not in self._mem_users:
                user_data["created_at"] = datetime.now(timezone.utc).isoformat()
            self._mem_users[user_id] = user_data
            return user_data

    async def get_user_by_token(self, token: str) -> Optional[Dict[str, Any]]:
        if not token:
            return None
        if self.is_connected and self.db is not None:
            return await self.db.users.find_one({"auth_token": token})
        else:
            for u in self._mem_users.values():
                if u.get("auth_token") == token:
                    return u
            return None

    # Channel Management
    async def add_channel(self, channel_data: Dict[str, Any]) -> bool:
        channel_id = channel_data["channel_id"]
        added_by = channel_data["added_by"]
        channel_data["updated_at"] = datetime.now(timezone.utc).isoformat()

        if self.is_connected and self.db is not None:
            await self.db.channels.update_one(
                {"channel_id": channel_id, "added_by": added_by},
                {"$set": channel_data, "$setOnInsert": {"created_at": datetime.now(timezone.utc).isoformat()}},
                upsert=True
            )
            return True
        else:
            key = f"{channel_id}_{added_by}"
            self._mem_channels[key] = channel_data
            return True

    async def get_channels_for_user(self, user_id: int) -> List[Dict[str, Any]]:
        if self.is_connected and self.db is not None:
            cursor = self.db.channels.find({"added_by": user_id})
            return await cursor.to_list(length=100)
        else:
            return [ch for ch in self._mem_channels.values() if ch.get("added_by") == user_id]

    async def delete_channel(self, channel_id: int, user_id: int) -> bool:
        if self.is_connected and self.db is not None:
            res = await self.db.channels.delete_one({"channel_id": channel_id, "added_by": user_id})
            return res.deleted_count > 0
        else:
            key = f"{channel_id}_{user_id}"
            if key in self._mem_channels:
                del self._mem_channels[key]
                return True
            return False

    # Drafts Management (Optimized for Storage & 48-Hour TTL)
    async def save_draft(self, draft_data: Dict[str, Any]) -> str:
        draft_id = draft_data.get("draft_id") or f"draft_{int(time.time()*1000)}"
        # Sanitize draft: Strip heavy binary fields to prevent MongoDB storage exhaustion
        clean_draft = {k: v for k, v in draft_data.items() if k not in ("media_bytes", "media_base64")}
        clean_draft["draft_id"] = draft_id
        clean_draft["updated_at"] = datetime.now(timezone.utc).isoformat()
        clean_draft["created_at_dt"] = datetime.now(timezone.utc)
        clean_draft["_timestamp"] = time.time()

        if self.is_connected and self.db is not None:
            await self.db.drafts.update_one(
                {"draft_id": draft_id},
                {"$set": clean_draft, "$setOnInsert": {"created_at": datetime.now(timezone.utc).isoformat()}},
                upsert=True
            )
            return draft_id
        else:
            self._mem_drafts[draft_id] = clean_draft
            return draft_id

    async def get_drafts_for_user(self, user_id: int) -> List[Dict[str, Any]]:
        # Enforce 48 hours lifespan (48 * 3600 = 172,800 seconds)
        now_ts = time.time()
        if self.is_connected and self.db is not None:
            cursor = self.db.drafts.find({"user_id": user_id}).sort("updated_at", -1)
            drafts = await cursor.to_list(length=50)
            for d in drafts:
                if "_id" in d:
                    d["_id"] = str(d["_id"])
                if "created_at_dt" in d and isinstance(d["created_at_dt"], datetime):
                    d["created_at_dt"] = d["created_at_dt"].isoformat()
            return drafts
        else:
            return [
                d for d in self._mem_drafts.values()
                if d.get("user_id") == user_id and (now_ts - d.get("_timestamp", now_ts)) <= 172800
            ]

    async def delete_draft(self, draft_id: str, user_id: int) -> bool:
        if self.is_connected and self.db is not None:
            res = await self.db.drafts.delete_one({"draft_id": draft_id, "user_id": user_id})
            return res.deleted_count > 0
        else:
            if draft_id in self._mem_drafts and self._mem_drafts[draft_id].get("user_id") == user_id:
                del self._mem_drafts[draft_id]
                return True
            return False

    # Published Posts History Management
    async def record_published_post(self, post_record: Dict[str, Any]):
        post_record["created_at"] = datetime.now(timezone.utc).isoformat()
        if self.is_connected and self.db is not None:
            await self.db.published_posts.insert_one(post_record)
        else:
            if not hasattr(self, "_mem_history"):
                self._mem_history = []
            self._mem_history.append(post_record)

    async def get_published_history(self, user_id: int) -> List[Dict[str, Any]]:
        if self.is_connected and self.db is not None:
            cursor = self.db.published_posts.find({"user_id": user_id}).sort("created_at", -1)
            history = await cursor.to_list(length=60)
            for h in history:
                if "_id" in h:
                    h["_id"] = str(h["_id"])
            return history
        else:
            hist = getattr(self, "_mem_history", [])
            return [h for h in reversed(hist) if h.get("user_id") == user_id]

    # Scheduled Deletions (Auto-Delete)
    async def schedule_deletion(self, channel_id: Any, message_id: int, delete_at_timestamp: float):
        job = {
            "channel_id": channel_id,
            "message_id": message_id,
            "delete_at": delete_at_timestamp,
            "status": "pending",
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        if self.is_connected and self.db is not None:
            await self.db.scheduled_deletions.insert_one(job)
        else:
            self._mem_scheduled_deletions.append(job)

    async def get_due_deletions(self, current_time: float) -> List[Dict[str, Any]]:
        if self.is_connected and self.db is not None:
            cursor = self.db.scheduled_deletions.find({
                "delete_at": {"$lte": current_time},
                "status": "pending"
            })
            return await cursor.to_list(length=100)
        else:
            due = [j for j in self._mem_scheduled_deletions if j["delete_at"] <= current_time and j["status"] == "pending"]
            return due

    async def mark_deletion_completed(self, channel_id: Any, message_id: int):
        if self.is_connected and self.db is not None:
            await self.db.scheduled_deletions.update_one(
                {"channel_id": channel_id, "message_id": message_id},
                {"$set": {"status": "completed"}}
            )
        else:
            for j in self._mem_scheduled_deletions:
                if j["channel_id"] == channel_id and j["message_id"] == message_id:
                    j["status"] = "completed"

db = Database(MONGO_URI, DATABASE_NAME)

# ==============================================================================
# WATERMARK PROCESSING ENGINE (PILLOW)
# ==============================================================================
def process_watermark(image_bytes: bytes, text: str, position: str = "pos-br", opacity: float = 0.75, font_size: int = 18) -> bytes:
    """
    Overlays channel watermark text on image with clean transparency.
    Only called when watermark is explicitly enabled to avoid unnecessary re-encoding.
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        import io

        base_img = Image.open(io.BytesIO(image_bytes)).convert("RGBA")
        txt_layer = Image.new("RGBA", base_img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(txt_layer)

        # Basic default font
        font = ImageFont.load_default()
        
        # Calculate bounding box
        bbox = draw.textbbox((0, 0), text, font=font)
        text_w = bbox[2] - bbox[0]
        text_h = bbox[3] - bbox[1]
        
        pad = 20
        W, H = base_img.size
        
        if position == "pos-br":
            x, y = W - text_w - pad, H - text_h - pad
        elif position == "pos-bl":
            x, y = pad, H - text_h - pad
        elif position == "pos-tr":
            x, y = W - text_w - pad, pad
        elif position == "pos-tl":
            x, y = pad, pad
        else: # center
            x, y = (W - text_w) // 2, (H - text_h) // 2

        alpha = int(255 * max(0.1, min(1.0, opacity)))
        draw.text((x + 1, y + 1), text, font=font, fill=(0, 0, 0, alpha))
        draw.text((x, y), text, font=font, fill=(255, 255, 255, alpha))

        out_img = Image.alpha_composite(base_img, txt_layer).convert("RGB")
        out_buf = io.BytesIO()
        out_img.save(out_buf, format="JPEG", quality=90)
        return out_buf.getvalue()
    except Exception as e:
        logger.error("Watermark processing error: %s. Returning original image.", e)
        return image_bytes

# ==============================================================================
# TELEGRAM BOT CORE ENGINE (ASYNC AIOHTTP / PYROGRAM)
# ==============================================================================
class TelegramBot:
    """
    Asynchronous Telegram Bot client supporting:
    - Native inline keyboard builder
    - Custom small-caps UI formatting
    - Channel admin permission verification
    - Auto-pinning & Auto-deletion
    - Protected content
    - Seamless fallback and high-performance async requests
    """
    def __init__(self, token: str):
        self.token = token
        self.username = "PostoPostBot"
        self.session = None

    async def start(self):
        import aiohttp
        self.session = aiohttp.ClientSession()
        # Fetch bot info
        if self.token:
            try:
                me = await self.request("getMe")
                if me and me.get("ok"):
                    self.username = me["result"].get("username", "PostoPostBot")
                    logger.info("Bot started successfully as @%s", self.username)
            except Exception as e:
                logger.warning("Could not fetch getMe: %s", e)

    async def close(self):
        if self.session:
            await self.session.close()

    async def request(self, method: str, data: Optional[Dict[str, Any]] = None, files: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if not self.token:
            return {"ok": False, "description": "BOT_TOKEN not provided"}
            
        url = f"https://api.telegram.org/bot{self.token}/{method}"
        import aiohttp
        try:
            if files:
                form = aiohttp.FormData()
                if data:
                    for k, v in data.items():
                        form.add_field(k, str(v) if not isinstance(v, str) else v)
                for fk, fv in files.items():
                    form.add_field(fk, fv[1], filename=fv[0])
                async with self.session.post(url, data=form) as resp:
                    return await resp.json()
            else:
                async with self.session.post(url, json=data or {}) as resp:
                    return await resp.json()
        except Exception as e:
            logger.error("Telegram API error (%s): %s", method, e)
            return {"ok": False, "description": str(e)}

    # Keyboard Builders
    def make_start_keyboard(self, user_token: str) -> Dict[str, Any]:
        """
        Builds the exact Row 1/2/3 keyboard layout required by Section 7:
        Row 1: ➕ ᴧᴅᴅ ᴍє тσ ʏσυʀ ᴄʜᴧɴɴєʟ (Channel Admin flow)
        Row 2: υѕᴧɢє | ᴧʙσυт
        Row 3: ᴄʀєᴧтє ᴩσѕт
        """
        add_url = f"https://t.me/{self.username}?startchannel=true&admin=post_messages+edit_messages+delete_messages+pin_messages"
        return {
            "inline_keyboard": [
                [
                    {"text": BTN_ADD_CHANNEL, "url": add_url}
                ],
                [
                    {"text": BTN_USAGE, "callback_data": "usage"},
                    {"text": BTN_ABOUT, "callback_data": "about"}
                ],
                [
                    {"text": BTN_CREATE_POST, "callback_data": "create_post_menu"}
                ]
            ]
        }

    def make_create_menu_keyboard(self, user_token: str) -> Dict[str, Any]:
        """
        Menu shown when user taps 'ᴄʀєᴧтє ᴩσѕт':
        Buttons:
        - Web Editor
        - My Channels
        - Drafts
        - Back
        """
        web_url = f"{BASE_URL}/?token={user_token}"
        return {
            "inline_keyboard": [
                [
                    {"text": BTN_WEB_EDITOR, "web_app": {"url": web_url}}
                ],
                [
                    {"text": BTN_MY_CHANNELS, "callback_data": "my_channels"},
                    {"text": BTN_DRAFTS, "callback_data": "my_drafts"}
                ],
                [
                    {"text": BTN_BACK, "callback_data": "back_home"}
                ]
            ]
        }

    # High-level actions
    async def send_welcome(self, chat_id: int, user_token: str):
        caption = (
            f"<b>{TXT_WELCOME_TITLE}</b>\n\n"
            f"<b>{TXT_SLOGAN_1}</b>\n\n"
            f"{TXT_SLOGAN_2}\n\n"
            f"<i>{to_small_caps('Manage multiple channels, add custom inline URL buttons, watermarks, auto-pin posts, and configure persistent auto-deletion.')}</i>"
        )
        keyboard = self.make_start_keyboard(user_token)

        # Check if start_image exists
        if START_IMAGE_PATH.exists() and START_IMAGE_PATH.is_file():
            try:
                with open(START_IMAGE_PATH, "rb") as f:
                    img_data = f.read()
                res = await self.request("sendPhoto", data={
                    "chat_id": chat_id,
                    "caption": caption,
                    "parse_mode": "HTML",
                    "reply_markup": json.dumps(keyboard)
                }, files={"photo": ("start_image.jpg", img_data)})
                if res.get("ok"):
                    return res
            except Exception as e:
                logger.warning("Failed sending start image: %s", e)

        # Fallback to text message
        return await self.request("sendMessage", {
            "chat_id": chat_id,
            "text": caption,
            "parse_mode": "HTML",
            "reply_markup": keyboard
        })

    async def verify_channel_admin(self, channel_id: Any) -> Dict[str, Any]:
        """
        Verifies bot is present and has required administrator rights in target channel:
        can_post_messages, can_edit_messages, can_delete_messages
        """
        # First get chat details
        chat_res = await self.request("getChat", {"chat_id": channel_id})
        if not chat_res.get("ok"):
            return {"valid": False, "error": f"Bot cannot access chat {channel_id}. Make sure the channel username or ID is correct."}

        chat_info = chat_res["result"]

        # Check bot's member status in channel
        member_res = await self.request("getChatMember", {"chat_id": channel_id, "user_id": (await self.request("getMe")).get("result", {}).get("id")})
        if not member_res.get("ok"):
            return {"valid": False, "error": "Bot is not a member of the channel."}

        member = member_res["result"]
        status = member.get("status")

        if status not in ("administrator", "creator"):
            return {"valid": False, "error": "Bot is not an administrator in the channel. Please grant admin permissions."}

        perms = {
            "can_post_messages": member.get("can_post_messages", True),
            "can_edit_messages": member.get("can_edit_messages", True),
            "can_delete_messages": member.get("can_delete_messages", True),
            "can_pin_messages": member.get("can_pin_messages", True),
        }

        return {
            "valid": True,
            "title": chat_info.get("title", "Channel"),
            "username": chat_info.get("username", ""),
            "channel_id": chat_info["id"],
            "permissions": perms
        }

    async def publish_post(self, channel_id: Any, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Publishes formatted post to channel with all requested features:
        - Media support (photo, video, audio, document)
        - Format parsing
        - Inline URL buttons
        - Watermark (if photo)
        - Auto-pin
        - Auto-delete scheduling
        - Protected content
        """
        caption = payload.get("caption", "").strip()
        media_type = payload.get("media_type", "text")
        media_bytes = payload.get("media_bytes")
        media_url = payload.get("media_url", "").strip()
        button_rows = payload.get("buttons", [])
        auto_pin = payload.get("auto_pin", False)
        auto_delete_minutes = payload.get("auto_delete_minutes", 0)
        protect_content = payload.get("protect_content", False)
        user_id = payload.get("user_id", 1000)

        # Build inline keyboard with colored styles and emoji support
        reply_markup = None
        if button_rows:
            inline_kb = []
            for row in button_rows:
                row_btns = []
                for b in row:
                    text = b.get("text", "").strip()
                    url = b.get("url", "").strip()
                    style = b.get("style", "").strip().lower()
                    if text:
                        btn_obj = {"text": text}
                        if url:
                            btn_obj["url"] = url
                        else:
                            btn_obj["callback_data"] = b.get("callback_data", "btn_click")
                        # Support colored styles (PRIMARY, SUCCESS, DANGER) for compatible clients
                        if style in ("primary", "success", "danger"):
                            btn_obj["style"] = style
                        if b.get("icon_custom_emoji_id"):
                            btn_obj["icon_custom_emoji_id"] = b["icon_custom_emoji_id"]
                        row_btns.append(btn_obj)
                if row_btns:
                    inline_kb.append(row_btns)
            if inline_kb:
                reply_markup = {"inline_keyboard": inline_kb}

        # Apply watermark if requested and photo bytes present
        if media_type == "photo" and media_bytes and payload.get("watermark"):
            wm = payload["watermark"]
            media_bytes = process_watermark(
                media_bytes,
                text=wm.get("text", "@Channel"),
                position=wm.get("position", "pos-br"),
                opacity=float(wm.get("opacity", 0.75)),
                font_size=18
            )

        # Send post according to media type (supports both Direct URL and File Upload)
        send_data = {
            "chat_id": channel_id,
            "parse_mode": "HTML",
            "protect_content": protect_content
        }
        if reply_markup:
            send_data["reply_markup"] = json.dumps(reply_markup)

        res = None
        if media_type == "text" or (not media_bytes and not media_url):
            send_data["text"] = caption or "Post"
            res = await self.request("sendMessage", send_data)
        elif media_url:
            # Direct URL publishing: Telegram downloads directly from the URL!
            if media_type == "photo":
                send_data["photo"] = media_url
                send_data["caption"] = caption
                res = await self.request("sendPhoto", send_data)
            elif media_type == "video":
                send_data["video"] = media_url
                send_data["caption"] = caption
                res = await self.request("sendVideo", send_data)
            elif media_type == "audio":
                send_data["audio"] = media_url
                send_data["caption"] = caption
                res = await self.request("sendAudio", send_data)
            else: # document
                send_data["document"] = media_url
                send_data["caption"] = caption
                res = await self.request("sendDocument", send_data)
        elif media_type == "photo":
            send_data["caption"] = caption
            res = await self.request("sendPhoto", data=send_data, files={"photo": ("image.jpg", media_bytes)})
        elif media_type == "video":
            send_data["caption"] = caption
            res = await self.request("sendVideo", data=send_data, files={"video": ("video.mp4", media_bytes)})
        elif media_type == "audio":
            send_data["caption"] = caption
            res = await self.request("sendAudio", data=send_data, files={"audio": ("audio.mp3", media_bytes)})
        else: # document
            send_data["caption"] = caption
            res = await self.request("sendDocument", data=send_data, files={"document": ("document.bin", media_bytes)})

        if not res or not res.get("ok"):
            err_msg = res.get("description", "Unknown Telegram error") if res else "No response"
            return {"ok": False, "error": f"{to_small_caps('Unable to publish the post.')} {err_msg}"}

        sent_msg = res["result"]
        msg_id = sent_msg["message_id"]

        # Handle Auto-Pin
        if auto_pin:
            pin_res = await self.request("pinChatMessage", {
                "chat_id": channel_id,
                "message_id": msg_id,
                "disable_notification": False
            })
            if not pin_res.get("ok"):
                logger.warning("Could not pin post in %s: %s", channel_id, pin_res.get("description"))

        # Handle Auto-Delete Scheduling
        if auto_delete_minutes and auto_delete_minutes > 0:
            del_time = time.time() + (auto_delete_minutes * 60)
            await db.schedule_deletion(channel_id, msg_id, del_time)
            logger.info("Scheduled auto-deletion for msg %s in %s in %d mins", msg_id, channel_id, auto_delete_minutes)

        # Record into Published Posts History for Mini App display
        try:
            ch_str = str(channel_id)
            if ch_str.startswith("-100"):
                post_link = f"https://t.me/c/{ch_str.replace('-100', '')}/{msg_id}"
            elif ch_str.startswith("@"):
                post_link = f"https://t.me/{ch_str[1:]}/{msg_id}"
            else:
                post_link = ""

            await db.record_published_post({
                "user_id": user_id,
                "channel_id": channel_id,
                "message_id": msg_id,
                "caption": caption[:160] if caption else "Media Post",
                "media_type": media_type,
                "media_url": media_url or "",
                "auto_pin": auto_pin,
                "auto_delete_minutes": auto_delete_minutes,
                "protect_content": protect_content,
                "post_link": post_link,
                "published_at": datetime.now(timezone.utc).isoformat()
            })
        except Exception as e:
            logger.warning("Could not record published post history: %s", e)

        return {"ok": True, "message_id": msg_id, "channel_id": channel_id}

bot = TelegramBot(BOT_TOKEN)

# ==============================================================================
# ASYNC AUTO-DELETE SCHEDULER WORKER
# ==============================================================================
async def auto_delete_worker():
    """
    Background worker that runs every 10 seconds to process due auto-deletions.
    Jobs are stored in MongoDB, ensuring persistence across server restarts.
    """
    logger.info("Auto-delete background worker initialized.")
    while True:
        try:
            now = time.time()
            due_jobs = await db.get_due_deletions(now)
            for job in due_jobs:
                ch_id = job["channel_id"]
                msg_id = job["message_id"]
                logger.info("Executing auto-deletion for msg %s in channel %s", msg_id, ch_id)
                res = await bot.request("deleteMessage", {
                    "chat_id": ch_id,
                    "message_id": msg_id
                })
                if res.get("ok"):
                    logger.info("Message %s deleted successfully.", msg_id)
                else:
                    logger.warning("Failed deleting message %s: %s", msg_id, res.get("description"))
                await db.mark_deletion_completed(ch_id, msg_id)
        except Exception as e:
            logger.error("Error in auto-delete worker: %s", e)
        await asyncio.sleep(10)

# ==============================================================================
# WEB SERVER & REST API (AIOHTTP.WEB)
# ==============================================================================
async def handle_index(request):
    """Serves the plain HTML/CSS/JS Posto Web Post Creator directly."""
    if INDEX_HTML_PATH.exists():
        with open(INDEX_HTML_PATH, "r", encoding="utf-8") as f:
            html = f.read()
        import aiohttp.web
        return aiohttp.web.Response(text=html, content_type="text/html")
    import aiohttp.web
    return aiohttp.web.Response(text="Posto Web Panel: index.html not found.", status=404)

async def handle_start_image(request):
    """Serves start_image.jpg."""
    if START_IMAGE_PATH.exists():
        with open(START_IMAGE_PATH, "rb") as f:
            data = f.read()
        import aiohttp.web
        return aiohttp.web.Response(body=data, content_type="image/jpeg")
    import aiohttp.web
    return aiohttp.web.Response(status=404)

async def handle_api_auth_verify(request):
    """Verifies user session token and returns connected channels."""
    import aiohttp.web
    try:
        data = await request.json()
        token = data.get("token", "").strip()
        user = await db.get_user_by_token(token)
        if not user:
            return aiohttp.web.json_response({"ok": False, "error": "Invalid or expired session token."}, status=401)
        channels = await db.get_channels_for_user(user["user_id"])
        return aiohttp.web.json_response({
            "ok": True,
            "user": {
                "user_id": user["user_id"],
                "username": user.get("username", ""),
                "first_name": user.get("first_name", "")
            },
            "channels": channels
        })
    except Exception as e:
        return aiohttp.web.json_response({"ok": False, "error": str(e)}, status=500)

async def handle_api_channels(request):
    """Lists connected channels for authenticated user."""
    import aiohttp.web
    token = request.headers.get("Authorization", "").replace("Bearer ", "").strip()
    user = await db.get_user_by_token(token)
    if not user:
        # Return fallback demo channel for standalone browser preview
        return aiohttp.web.json_response({
            "ok": True,
            "channels": [{
                "channel_id": "@demo_channel",
                "title": "Demo Announcements",
                "username": "demo_channel"
            }]
        })
    channels = await db.get_channels_for_user(user["user_id"])
    return aiohttp.web.json_response({"ok": True, "channels": channels})

async def handle_api_publish(request):
    """
    Validates, processes, and publishes post to Telegram channel.
    Enforces Telegram official character limits (1024 for media captions, 4096 for text-only).
    """
    import aiohttp.web
    try:
        payload = await request.json()
        channel_id = payload.get("channel_id")
        caption = payload.get("caption", "").strip()
        media_type = payload.get("media_type", "text")

        if not channel_id:
            return aiohttp.web.json_response({"ok": False, "message": "Target channel is required."}, status=400)

        # Enforce Telegram caption limits
        if media_type != "text" and len(caption) > 1024:
            return aiohttp.web.json_response({
                "ok": False,
                "message": to_small_caps("WARNING: Media captions must follow Telegram's current limits (1024 chars).")
            }, status=400)
        elif media_type == "text" and len(caption) > 4096:
            return aiohttp.web.json_response({
                "ok": False,
                "message": to_small_caps("WARNING: Text posts cannot exceed 4096 characters.")
            }, status=400)

        # Extract authenticated user if available
        token = request.headers.get("Authorization", "").replace("Bearer ", "").strip()
        user = await db.get_user_by_token(token)
        if user:
            payload["user_id"] = user["user_id"]

        # In production mode, forward to Telegram Bot API
        res = await bot.publish_post(channel_id, payload)
        if res.get("ok"):
            return aiohttp.web.json_response({"status": "ok", "message_id": res.get("message_id")})
        else:
            return aiohttp.web.json_response({"status": "error", "message": res.get("error", "Publish failed")}, status=400)
    except Exception as e:
        logger.error("Publish handler exception: %s", e)
        return aiohttp.web.json_response({"status": "error", "message": str(e)}, status=500)

async def handle_api_history(request):
    """GET to list published posts history for authenticated user."""
    import aiohttp.web
    token = request.headers.get("Authorization", "").replace("Bearer ", "").strip()
    user = await db.get_user_by_token(token)
    user_id = user["user_id"] if user else 1000
    history = await db.get_published_history(user_id)
    return aiohttp.web.json_response({"ok": True, "history": history})

async def handle_api_drafts(request):
    """GET to list drafts, POST to save draft, DELETE to remove draft."""
    import aiohttp.web
    token = request.headers.get("Authorization", "").replace("Bearer ", "").strip()
    user = await db.get_user_by_token(token)
    user_id = user["user_id"] if user else 1000

    if request.method == "GET":
        drafts = await db.get_drafts_for_user(user_id)
        return aiohttp.web.json_response({"ok": True, "drafts": drafts})
    elif request.method == "POST":
        data = await request.json()
        data["user_id"] = user_id
        draft_id = await db.save_draft(data)
        return aiohttp.web.json_response({"ok": True, "draft_id": draft_id})
    elif request.method == "DELETE":
        draft_id = request.match_info.get("id")
        deleted = await db.delete_draft(draft_id, user_id)
        return aiohttp.web.json_response({"ok": deleted})

async def handle_health(request):
    import aiohttp.web
    return aiohttp.web.json_response({
        "status": "healthy",
        "bot": "Posto",
        "database": "connected" if db.is_connected else "in-memory-fallback",
        "time": datetime.now(timezone.utc).isoformat()
    })

def make_web_app():
    import aiohttp.web
    app = aiohttp.web.Application()
    app.router.add_get("/", handle_index)
    app.router.add_get("/start_image.jpg", handle_start_image)
    app.router.add_post("/api/auth/verify", handle_api_auth_verify)
    app.router.add_get("/api/channels", handle_api_channels)
    app.router.add_post("/api/publish", handle_api_publish)
    app.router.add_get("/api/drafts", handle_api_drafts)
    app.router.add_post("/api/drafts", handle_api_drafts)
    app.router.add_delete("/api/drafts/{id}", handle_api_drafts)
    app.router.add_get("/api/history", handle_api_history)
    app.router.add_get("/api/health", handle_health)
    return app

# ==============================================================================
# TELEGRAM POLLING & EVENT DISPATCHER
# ==============================================================================
async def telegram_polling_loop():
    """
    Fast async Telegram polling loop handling:
    /start, /help, /channels, /addchannel, and Callback Queries.
    """
    if not BOT_TOKEN:
        logger.warning("BOT_TOKEN is empty. Running web panel only.")
        return

    logger.info("Starting Telegram Bot event polling loop...")
    offset = 0

    while True:
        try:
            updates_res = await bot.request("getUpdates", {"offset": offset, "timeout": 20})
            if not updates_res or not updates_res.get("ok"):
                await asyncio.sleep(2)
                continue

            updates = updates_res.get("result", [])
            for u in updates:
                offset = max(offset, u["update_id"] + 1)
                
                # Handle Messages
                if "message" in u:
                    msg = u["message"]
                    chat_id = msg["chat"]["id"]
                    text = msg.get("text", "").strip()
                    user_info = msg.get("from", {})
                    user_id = user_info.get("id", chat_id)
                    username = user_info.get("username", "")
                    first_name = user_info.get("first_name", "")

                    user = await db.get_or_create_user(user_id, username, first_name)
                    token = user["auth_token"]

                    if text.startswith("/start"):
                        await bot.send_welcome(chat_id, token)

                    elif text.startswith("/addchannel"):
                        parts = text.split(" ")
                        if len(parts) < 2:
                            err_txt = f"{to_small_caps('Please provide the channel username or ID.')}\n\n<code>/addchannel @YourChannel</code>"
                            await bot.request("sendMessage", {"chat_id": chat_id, "text": err_txt, "parse_mode": "HTML"})
                            continue

                        target_channel = parts[1].strip()
                        ver = await bot.verify_channel_admin(target_channel)
                        if ver["valid"]:
                            await db.add_channel({
                                "channel_id": ver["channel_id"],
                                "title": ver["title"],
                                "username": ver["username"],
                                "added_by": user_id,
                                "permissions": ver["permissions"]
                            })
                            success_msg = (
                                f"✅ <b>{to_small_caps('Channel connected successfully!')}</b>\n\n"
                                f"📢 <b>{ver['title']}</b> (<code>{ver['channel_id']}</code>)\n\n"
                                f"{to_small_caps('You can now create and publish posts to this channel from Posto.')}"
                            )
                            await bot.request("sendMessage", {"chat_id": chat_id, "text": success_msg, "parse_mode": "HTML"})
                        else:
                            fail_msg = f"❌ <b>{to_small_caps('Unable to connect channel.')}</b>\n\n{ver['error']}"
                            await bot.request("sendMessage", {"chat_id": chat_id, "text": fail_msg, "parse_mode": "HTML"})

                    elif text.startswith("/channels"):
                        channels = await db.get_channels_for_user(user_id)
                        if not channels:
                            msg_txt = f"{to_small_caps('No channels connected yet.')}\n\n{to_small_caps('Use /addchannel @YourChannel after making the bot an admin.')}"
                        else:
                            ch_lines = "\n".join([f"• <b>{c.get('title', 'Channel')}</b> ({c.get('channel_id')})" for c in channels])
                            msg_txt = f"📢 <b>{to_small_caps('Your Connected Channels:')}</b>\n\n{ch_lines}"
                        await bot.request("sendMessage", {"chat_id": chat_id, "text": msg_txt, "parse_mode": "HTML"})

                    elif text.startswith("/web"):
                        web_link = f"{BASE_URL}/?token={token}"
                        btn_kb = {"inline_keyboard": [[{"text": BTN_WEB_EDITOR, "web_app": {"url": web_link}}]]}
                        await bot.request("sendMessage", {
                            "chat_id": chat_id,
                            "text": f"🌐 <b>{to_small_caps('Open Posto Web Post Creator')}</b>\n\n{to_small_caps('Tap the button below to launch the post creator in your browser.')}",
                            "parse_mode": "HTML",
                            "reply_markup": json.dumps(btn_kb)
                        })

                # Handle Callback Queries
                elif "callback_query" in u:
                    cq = u["callback_query"]
                    cq_id = cq["id"]
                    from_user = cq["from"]
                    user_id = from_user["id"]
                    msg = cq.get("message")
                    chat_id = msg["chat"]["id"] if msg else user_id
                    msg_id = msg["message_id"] if msg else None
                    data = cq.get("data", "")

                    user = await db.get_or_create_user(user_id, from_user.get("username", ""), from_user.get("first_name", ""))
                    token = user["auth_token"]

                    await bot.request("answerCallbackQuery", {"callback_query_id": cq_id})

                    if data == "create_post_menu":
                        menu_text = (
                            f"<b>{to_small_caps('Create Post')}</b>\n\n"
                            f"{to_small_caps('Choose how you want to create your post.')}\n\n"
                            f"<i>{to_small_caps('Launch the Posto Web Editor to format text, attach media, configure watermarks, and schedule deletions.')}</i>"
                        )
                        kb = bot.make_create_menu_keyboard(token)
                        if msg_id:
                            await bot.request("editMessageText", {
                                "chat_id": chat_id,
                                "message_id": msg_id,
                                "text": menu_text,
                                "parse_mode": "HTML",
                                "reply_markup": json.dumps(kb)
                            })

                    elif data == "usage":
                        usage_text = (
                            f"📖 <b>{to_small_caps('Posto Usage Instructions')}</b>\n\n"
                            f"1. <b>{to_small_caps('Add Bot to Channel')}:</b>\n"
                            f"• {to_small_caps('Tap the top button to invite Posto as an admin.')}\n"
                            f"• {to_small_caps('Grant post, edit, delete, and pin message permissions.')}\n\n"
                            f"2. <b>{to_small_caps('Connect Channel')}:</b>\n"
                            f"• {to_small_caps('Send /addchannel @YourChannel to verify.')}\n\n"
                            f"3. <b>{to_small_caps('Web Editor')}:</b>\n"
                            f"• {to_small_caps('Open the web post maker to craft media captions, format markdown, and add custom inline URL buttons.')}\n\n"
                            f"4. <b>{to_small_caps('Auto-Pin & Auto-Delete')}:</b>\n"
                            f"• {to_small_caps('Enable automatic pinning or schedule messages to self-destruct.')}"
                        )
                        kb = {"inline_keyboard": [[{"text": BTN_BACK, "callback_data": "back_home"}]]}
                        if msg_id:
                            await bot.request("editMessageText", {
                                "chat_id": chat_id,
                                "message_id": msg_id,
                                "text": usage_text,
                                "parse_mode": "HTML",
                                "reply_markup": json.dumps(kb)
                            })

                    elif data == "about":
                        about_text = (
                            f"ℹ️ <b>{to_small_caps('About Posto')}</b>\n\n"
                            f"<b>Posto</b> — {TXT_SLOGAN_1}\n"
                            f"ᴠᴇʀѕɪσɴ: <code>2.4.0 (Production)</code>\n\n"
                            f"• {to_small_caps('Custom Small-Caps Presentation Layer')}\n"
                            f"• {to_small_caps('MongoDB Async Persistence Layer')}\n"
                            f"• {to_small_caps('Real-Time Telegram Formatting Preview')}\n"
                            f"• {to_small_caps('Image Watermark & Auto-Delete Scheduler')}\n"
                            f"• {to_small_caps('Deployable on Render, Railway, VPS, Termux, Koyeb')}"
                        )
                        kb = {"inline_keyboard": [[{"text": BTN_BACK, "callback_data": "back_home"}]]}
                        if msg_id:
                            await bot.request("editMessageText", {
                                "chat_id": chat_id,
                                "message_id": msg_id,
                                "text": about_text,
                                "parse_mode": "HTML",
                                "reply_markup": json.dumps(kb)
                            })

                    elif data == "my_channels":
                        channels = await db.get_channels_for_user(user_id)
                        if not channels:
                            body = f"{to_small_caps('No channels connected yet.')}\n\n{to_small_caps('Make Posto an admin in your channel and use /addchannel.')}"
                        else:
                            ch_list = "\n".join([f"• 📢 <b>{c.get('title')}</b> (<code>{c.get('channel_id')}</code>)" for c in channels])
                            body = f"<b>{to_small_caps('Your Connected Channels:')}</b>\n\n{ch_list}"
                        
                        add_url = f"https://t.me/{bot.username}?startchannel=true&admin=post_messages+edit_messages+delete_messages+pin_messages"
                        kb = {
                            "inline_keyboard": [
                                [{"text": "➕ ᴧᴅᴅ ɴєω ᴄʜᴧɴɴєʟ", "url": add_url}],
                                [{"text": BTN_BACK, "callback_data": "create_post_menu"}]
                            ]
                        }
                        if msg_id:
                            await bot.request("editMessageText", {
                                "chat_id": chat_id,
                                "message_id": msg_id,
                                "text": body,
                                "parse_mode": "HTML",
                                "reply_markup": json.dumps(kb)
                            })

                    elif data == "my_drafts":
                        drafts = await db.get_drafts_for_user(user_id)
                        if not drafts:
                            body = f"{to_small_caps('No drafts found.')}\n\n{to_small_caps('Create posts and save drafts directly from the Posto Web Editor.')}"
                        else:
                            d_list = "\n".join([f"• 📂 <b>{d.get('title', 'Draft')}</b> ({d.get('updated_at', '')[:10]})" for d in drafts[:5]])
                            body = f"<b>{to_small_caps('Your Recent Drafts:')}</b>\n\n{d_list}"
                        kb = {"inline_keyboard": [[{"text": BTN_BACK, "callback_data": "create_post_menu"}]]}
                        if msg_id:
                            await bot.request("editMessageText", {
                                "chat_id": chat_id,
                                "message_id": msg_id,
                                "text": body,
                                "parse_mode": "HTML",
                                "reply_markup": json.dumps(kb)
                            })

                    elif data == "back_home":
                        caption = (
                            f"<b>{TXT_WELCOME_TITLE}</b>\n\n"
                            f"<b>{TXT_SLOGAN_1}</b>\n\n"
                            f"{TXT_SLOGAN_2}\n\n"
                            f"<i>{to_small_caps('Manage multiple channels, add custom inline URL buttons, watermarks, auto-pin posts, and configure persistent auto-deletion.')}</i>"
                        )
                        kb = bot.make_start_keyboard(token)
                        if msg_id:
                            await bot.request("editMessageText", {
                                "chat_id": chat_id,
                                "message_id": msg_id,
                                "text": caption,
                                "parse_mode": "HTML",
                                "reply_markup": json.dumps(kb)
                            })

        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error("Error in polling update handler: %s", e)
            await asyncio.sleep(2)

# ==============================================================================
# MAIN APPLICATION LIFECYCLE
# ==============================================================================
async def main():
    logger.info("Initializing Posto Telegram Channel Post Maker Bot...")
    
    # 1. Connect MongoDB
    await db.connect()
    
    # 2. Start Bot Client
    await bot.start()
    
    # 3. Setup Async HTTP Web Application
    import aiohttp.web
    app = make_web_app()
    runner = aiohttp.web.AppRunner(app)
    await runner.setup()
    site = aiohttp.web.TCPSite(runner, host=WEB_HOST, port=WEB_PORT)
    await site.start()
    logger.info("Posto Web Panel running on http://%s:%d", WEB_HOST, WEB_PORT)
    
    # 4. Launch Auto-Delete Worker & Telegram Polling
    tasks = [
        asyncio.create_task(auto_delete_worker()),
        asyncio.create_task(telegram_polling_loop())
    ]
    
    try:
        await asyncio.gather(*tasks)
    except (KeyboardInterrupt, SystemExit):
        logger.info("Shutting down Posto gracefully...")
    finally:
        for t in tasks:
            t.cancel()
        await bot.close()
        await runner.cleanup()
        logger.info("Posto shutdown complete.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
