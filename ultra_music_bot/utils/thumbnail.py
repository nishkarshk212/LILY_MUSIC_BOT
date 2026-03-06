from PIL import Image, ImageDraw, ImageFont, ImageFilter
import requests
from io import BytesIO
import os
import asyncio

def _is_url(s):
    return isinstance(s, str) and s.startswith("http")

async def generate_thumb(*args, **kwargs):
    loop = asyncio.get_running_loop()
    if args and len(args) >= 4:
        a0, a1, a2, a3 = args[:4]
        if _is_url(a2) and _is_url(a3):
            return await loop.run_in_executor(None, _generate_glass_thumb_sync, a0, a1, a2, a3)
        return await loop.run_in_executor(None, _generate_glass_thumb_sync, a0, None, a3, None)
    title = kwargs.get("title") or kwargs.get("song_title")
    user = kwargs.get("user") or kwargs.get("user_name")
    thumb_url = kwargs.get("thumb_url") or kwargs.get("song_thumb") or kwargs.get("thumbnail_url")
    user_pfp = kwargs.get("user_pfp") or kwargs.get("user_photo")
    return await loop.run_in_executor(None, _generate_glass_thumb_sync, title, user, thumb_url, user_pfp)

async def generate_thumbnail(song_title, user_name=None, song_thumb=None, user_photo=None, duration=None, position=None):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _generate_thumbnail_sync, song_title, user_name, song_thumb, user_photo, duration, position)

def _generate_glass_thumb_sync(title, user, thumb_url, user_pfp):
    W = 1280
    H = 720
    try:
        r = requests.get(thumb_url)
        bg = Image.open(BytesIO(r.content)).resize((W, H)).convert("RGB") if r.status_code == 200 else Image.new("RGB", (W, H), (18, 18, 18))
    except Exception:
        bg = Image.new("RGB", (W, H), (18, 18, 18))
    bg = bg.filter(ImageFilter.GaussianBlur(18))
    overlay = Image.new("RGBA", (W, H), (0, 0, 0, 150))
    bg.paste(overlay, (0, 0), overlay)
    draw = ImageDraw.Draw(bg)
    card = Image.new("RGBA", (900, 350), (30, 30, 30, 180))
    card = card.filter(ImageFilter.GaussianBlur(2))
    bg.paste(card, (190, 180), card)
    try:
        r2 = requests.get(thumb_url)
        album = Image.open(BytesIO(r2.content)).resize((260, 260)) if r2.status_code == 200 else None
    except Exception:
        album = None
    if album:
        bg.paste(album, (220, 220))
    if user_pfp:
        try:
            r3 = requests.get(user_pfp)
            avatar = Image.open(BytesIO(r3.content)).resize((90, 90)) if r3.status_code == 200 else None
        except Exception:
            avatar = None
        if avatar:
            mask = Image.new("L", (90, 90), 0)
            d = ImageDraw.Draw(mask)
            d.ellipse((0, 0, 90, 90), fill=255)
            bg.paste(avatar, (950, 220), mask)
    try:
        title_font = ImageFont.truetype("arial.ttf", 55)
        small_font = ImageFont.truetype("arial.ttf", 35)
    except IOError:
        title_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    draw.text((520, 260), str(title or "")[:64], fill="white", font=title_font)
    if user:
        draw.text((520, 340), f"Requested by {user}", fill="white", font=small_font)
    x = 520
    y = 420
    w = 420
    draw.rectangle((x, y, x + w, y + 12), fill=(80, 80, 80))
    draw.rectangle((x, y, x + 220, y + 12), fill=(0, 180, 255))
    path = "music_thumb.png"
    bg.save(path)
    return path

def _generate_thumbnail_sync(song_title, user_name, song_thumb, user_photo, duration, position):
    width = 1280
    height = 720
    bg = Image.new("RGB", (width, height), (18, 18, 18))
    try:
        r = requests.get(song_thumb) if song_thumb else None
        img = Image.open(BytesIO(r.content)).resize((1280, 720)) if r and r.status_code == 200 else Image.new("RGB", (1280, 720), (60, 60, 60))
    except Exception:
        img = Image.new("RGB", (1280, 720), (60, 60, 60))
    bg.paste(img, (0, 0))
    overlay = Image.new("RGBA", (1280, 720), (0, 0, 0, 150))
    bg.paste(overlay, (0, 0), overlay)
    if user_photo:
        try:
            r2 = requests.get(user_photo)
            uimg = Image.open(BytesIO(r2.content)).resize((160, 160)) if r2.status_code == 200 else None
        except Exception:
            uimg = None
        if uimg:
            mask = Image.new("L", (160, 160), 0)
            md = ImageDraw.Draw(mask)
            md.ellipse((0, 0, 160, 160), fill=255)
            bg.paste(uimg, (50, 520), mask)
    draw = ImageDraw.Draw(bg)
    try:
        font_big = ImageFont.truetype("arial.ttf", 60)
        font_small = ImageFont.truetype("arial.ttf", 35)
    except IOError:
        font_big = ImageFont.load_default()
        font_small = ImageFont.load_default()
    draw.text((250, 540), str(song_title or "")[:60], font=font_big, fill="white")
    if user_name:
        draw.text((250, 610), f"Requested by {user_name}", font=font_small, fill="white")
    bar_x = 250
    bar_y = 660
    bar_width = 800
    if duration and position is not None and duration > 0:
        prog = max(0, min(bar_width, int((position / duration) * bar_width)))
        draw.rectangle((bar_x, bar_y, bar_x + bar_width, bar_y + 12), fill=(60, 60, 60))
        draw.rectangle((bar_x, bar_y, bar_x + prog, bar_y + 12), fill=(255, 0, 0))
    path = "music_thumb.png"
    bg.save(path)
    return path

def _progress_bar_text(current, total, length=8):
    try:
        if total and total > 0:
            filled = int(length * current / total)
        else:
            filled = 0
    except Exception:
        filled = 0
    filled = max(0, min(length - 1, filled))
    return "▰" * filled + "●" + "▱" * (length - filled - 1)

async def generate_ultra_thumb(title, user_name, youtube_thumb, user_avatar, duration=100, position=40):
    loop = asyncio.get_running_loop()
    return await loop.run_in_executor(None, _generate_ultra_thumb_sync, title, user_name, youtube_thumb, user_avatar, duration, position)

def _generate_ultra_thumb_sync(title, user_name, youtube_thumb, user_avatar, duration=100, position=40):
    WIDTH = 1280
    HEIGHT = 720
    try:
        r = requests.get(youtube_thumb)
        yt_img = Image.open(BytesIO(r.content)).resize((WIDTH, HEIGHT)) if r.status_code == 200 else Image.new("RGB", (WIDTH, HEIGHT), (18, 18, 18))
    except Exception:
        yt_img = Image.new("RGB", (WIDTH, HEIGHT), (18, 18, 18))
    bg = yt_img.filter(ImageFilter.GaussianBlur(30))
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 160))
    bg.paste(overlay, (0, 0), overlay)
    draw = ImageDraw.Draw(bg)
    card = Image.new("RGBA", (900, 400), (30, 30, 30, 180))
    card = card.filter(ImageFilter.GaussianBlur(2))
    bg.paste(card, (190, 160), card)
    album = yt_img.resize((300, 300))
    bg.paste(album, (230, 210))
    if user_avatar:
        try:
            r2 = requests.get(user_avatar)
            avatar = Image.open(BytesIO(r2.content)).resize((120, 120)) if r2.status_code == 200 else None
        except Exception:
            avatar = None
        if avatar:
            mask = Image.new("L", (120, 120), 0)
            d = ImageDraw.Draw(mask)
            d.ellipse((0, 0, 120, 120), fill=255)
            bg.paste(avatar, (930, 200), mask)
    try:
        title_font = ImageFont.truetype("arial.ttf", 55)
        small_font = ImageFont.truetype("arial.ttf", 35)
    except IOError:
        title_font = ImageFont.load_default()
        small_font = ImageFont.load_default()
    draw.text((560, 240), str(title or "")[:64], fill="white", font=title_font)
    if user_name:
        draw.text((560, 320), f"Requested by {user_name}", fill=(200, 200, 200), font=small_font)
    bar_text = _progress_bar_text(position or 0, duration or 0)
    draw.text((560, 400), bar_text, fill=(0, 200, 255), font=title_font)
    file = "ultra_music_thumb.png"
    bg.save(file)
    return file
