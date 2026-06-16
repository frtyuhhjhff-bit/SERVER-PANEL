import os
import sys
import time
import json
import re
import socket
import base64
import binascii
import threading
import random
import string
import logging
import io
import pickle
import datetime
import html
import codecs
import urllib3
import requests
import psutil
import jwt
import hmac
import hashlib
from datetime import datetime, timedelta
from threading import Thread, Lock, Event
from concurrent.futures import ThreadPoolExecutor

from flask import Flask, send_from_directory, request, jsonify, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

import telebot
from telebot import types
try:
    from cfonts import render, say
except ImportError:
    print("⚠️ cfonts غير مثبتة: pip install python-cfonts")

try:
    from Crypto.Cipher import AES
    from Crypto.Util.Padding import pad, unpad
    print("✅ تم تحميل Crypto")
except ImportError:
    try:
        from Cryptodome.Cipher import AES
        from Cryptodome.Util.Padding import pad, unpad
        print("✅ تم تحميل Cryptodome")
    except ImportError:
        print("❌ ثبت pycryptodome: pip install pycryptodome")
        exit()

try:
    from protobuf_decoder.protobuf_decoder import Parser
except ImportError:
    class Parser:
        def parse(self, data):
            return {"error": "protobuf_decoder not installed"}
    print("⚠️ protobuf_decoder غير متوفر")

from google.protobuf.timestamp_pb2 import Timestamp

try:
    import xKEys
    from xBLACKxXR import *
    from OTMAN import *
except Exception as e:
    print(f"⚠️ مشكلة في استيراد ملفاتك: {e}")

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ========== إعدادات Flask ==========
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "DATA")
USERS_DB = os.path.join(DATA_DIR, "users.json")
KEYS_DB = os.path.join(DATA_DIR, "pro_keys.json")
os.makedirs(DATA_DIR, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("PANEL_SECRET_KEY", "CHANGE_ME_" + os.urandom(16).hex())

ADMIN_USERNAME = os.environ.get("ADMIN_USER", "OTMAN")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASS", "OTMAN_KEY_PRO")
ADMIN_SECRET_CODE = "OTMAN2025"

# ========== تحميل وحفظ البيانات ==========
def load_users():
    if not os.path.exists(USERS_DB):
        return {"users": []}
    try:
        with open(USERS_DB, "r", encoding="utf-8") as f:
            return json.load(f) or {"users": []}
    except:
        return {"users": []}

def save_users(db):
    with open(USERS_DB, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

def load_pro_keys():
    if not os.path.exists(KEYS_DB):
        return {"keys": []}
    try:
        with open(KEYS_DB, "r", encoding="utf-8") as f:
            return json.load(f) or {"keys": []}
    except:
        return {"keys": []}

def save_pro_keys(db):
    with open(KEYS_DB, "w", encoding="utf-8") as f:
        json.dump(db, f, indent=2, ensure_ascii=False)

def find_user(db, username):
    u = (username or "").strip().lower()
    for x in db.get("users", []):
        if (x.get("username") or "").strip().lower() == u:
            return x
    return None

def is_admin_session():
    u = session.get("user") or {}
    return bool(u.get("is_admin"))

def current_username():
    u = session.get("user") or {}
    return (u.get("username") or "").strip()

def login_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user"):
            return redirect("/login")
        return fn(*args, **kwargs)
    return wrapper

def admin_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        if not session.get("user"):
            return redirect("/login")
        if not is_admin_session():
            return jsonify({"success": False, "message": "Admin only"}), 403
        return fn(*args, **kwargs)
    return wrapper

# ========== الدوال الجديدة المضافة بعد load_users() ==========
#تم التعديل - دوال جديدة
def get_admin_password():
    db = load_users()
    first_user = db.get("users", [])[0] if db.get("users") else {}
    return first_user.get("admin_password", "OTMAN")

def get_owner_name():
    db = load_users()
    first_user = db.get("users", [])[0] if db.get("users") else {}
    return first_user.get("owner_name", "OTMAN")

def get_owner_id():
    db = load_users()
    first_user = db.get("users", [])[0] if db.get("users") else {}
    return first_user.get("owner_id", "")

# ========== إعدادات OTMAN ==========
ADMIN_ID = None
ADMIN_IDS = []
MAX_ACCOUNTS = 15
PaSs = "OTMAN"

socket_lock = Lock()
data_lock = Lock()
connected_clients = {}
connected_clients_lock = threading.Lock()

SERVER_URL = "http://172.17.0.29:6002"
API_KEY = "OTMAN"
SUBSCRIPTION_CHANNEL_ID = -100323449437
SUBSCRIPTION_CHANNEL_LINK = "https://t.me/othmane8"

DATA_FILE = os.path.join(DATA_DIR, "users.json")
GROUPS_FILE = os.path.join(DATA_DIR, "groups.json")
MAINTENANCE_FILE = os.path.join(DATA_DIR, "maintenance.json")

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ========== دوال OTMAN الأساسية ==========
def ChEck_Commande(code):
    try:
        if code and len(str(code)) >= 5:
            return True
        return False
    except:
        return False

def ResTarT_bot():
    print("Done Start bot.!")
    time.sleep(5)
    python = sys.executable
    os.execl(python, python, *sys.argv)

def safe_story_de_json(obj):
    try:
        return telebot.types.Story(**{k: v for k, v in obj.items() if k != "chat"})
    except Exception:
        return None

telebot.types.Story.de_json = staticmethod(safe_story_de_json)

# بيانات التشفير
ENCRYPTION_KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
ENCRYPTION_IV = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

def encrypt_packet(plain_text, key=ENCRYPTION_KEY, iv=ENCRYPTION_IV):
    plain_text_bytes = bytes.fromhex(plain_text)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    cipher_text = cipher.encrypt(pad(plain_text_bytes, AES.block_size))
    return cipher_text.hex()

def decrypt_packet(cipher_text, key=ENCRYPTION_KEY, iv=ENCRYPTION_IV):
    cipher_text_bytes = bytes.fromhex(cipher_text)
    cipher = AES.new(key, AES.MODE_CBC, iv)
    plain_text = unpad(cipher.decrypt(cipher_text_bytes), AES.block_size)
    return plain_text.hex()

def dec_to_hex(ask):
    ask_result = hex(ask)
    final_result = str(ask_result)[2:]
    if len(final_result) == 1:
        final_result = "0" + final_result
        return final_result
    else:
        return final_result

def generate_random_hex_color():
    top_colors = [
        "FF4500", "FFD700", "32CD32", "87CEEB", "9370DB",
        "FF69B4", "8A2BE2", "00BFFF", "1E90FF", "20B2AA",
        "00FA9A", "008000", "FFFF00", "FF8C00", "DC143C",
        "FF6347", "FFA07A", "FFDAB9", "CD853F", "D2691E",
        "BC8F8F", "F0E68C", "556B2F", "808000", "4682B4",
        "6A5ACD", "7B68EE", "8B4513", "C71585", "4B0082",
        "B22222", "228B22", "8B008B", "483D8B", "556B2F",
        "800000", "008080", "000080", "800080", "808080",
        "A9A9A9", "D3D3D3", "F0F0F0"
    ]
    return random.choice(top_colors)

def bunner_():
    ra = random.randint(203, 213)
    final_num = str(ra).zfill(3)
    bunner = "902000" + final_num
    bunner = random.choice(numbers)
    return bunner

numbers = [
    902000208, 902000209, 902000210, 902000211
]

def Encrypt_ID(number):
    number = int(number)
    encoded_bytes = []
    while True:
        byte = number & 0x7F
        number >>= 7
        if number:
            byte |= 0x80
        encoded_bytes.append(byte)
        if not number:
            break
    return bytes(encoded_bytes).hex()

def Encrypt(number):
    number = int(number)
    encoded_bytes = []
    while True:
        byte = number & 0x7F
        number >>= 7
        if number:
            byte |= 0x80
        encoded_bytes.append(byte)
        if not number:
            break
    return bytes(encoded_bytes).hex()

def Decrypt(encoded_bytes):
    encoded_bytes = bytes.fromhex(encoded_bytes)
    number = 0
    shift = 0
    for byte in encoded_bytes:
        value = byte & 0x7F
        number |= value << shift
        shift += 7
        if not byte & 0x80:
            break
    return number

def decrypt_api(cipher_text):
    return decrypt_packet(cipher_text, ENCRYPTION_KEY, ENCRYPTION_IV)

def encrypt_api(plain_text):
    return encrypt_packet(plain_text, ENCRYPTION_KEY, ENCRYPTION_IV)

# ===== دوال JWT =====
def TOKEN_MAKER(OLD_ACCESS_TOKEN, NEW_ACCESS_TOKEN, OLD_OPEN_ID, NEW_OPEN_ID, uid):
    now = datetime.now()
    now = str(now)[:len(str(now)) - 7]
    data = bytes.fromhex('1a13323032352d31312d32362030313a35313a3238220966726565206669726528013a07312e3132332e314232416e64726f6964204f532039202f204150492d3238202850492f72656c2e636a772e32303232303531382e313134313333294a0848616e6468656c64520c4d544e2f537061636574656c5a045749464960800a68d00572033234307a2d7838362d3634205353453320535345342e3120535345342e32204156582041565832207c2032343030207c20348001e61e8a010f416472656e6f2028544d292036343092010d4f70656e474c20455320332e329a012b476f6f676c657c36323566373136662d393161372d343935622d396631362d303866653964336336353333a2010e3137362e32382e3133392e313835aa01026172b201203433303632343537393364653836646134323561353263616164663231656564ba010134c2010848616e6468656c64ca010d4f6e65506c7573204135303130ea014063363961653230386661643732373338623637346232383437623530613361316466613235643161313966616537343566633736616334613065343134633934f00101ca020c4d544e2f537061636574656cd2020457494649ca03203161633462383065636630343738613434323033626638666163363132306635e003b5ee02e8039a8002f003af13f80384078004a78f028804b5ee029004a78f029804b5ee02b00404c80401d2043d2f646174612f6170702f636f6d2e6474732e667265656669726574682d66705843537068495636644b43376a4c2d574f7952413d3d2f6c69622f61726de00401ea045f65363261623933353464386662356662303831646233333861636233333439317c2f646174612f6170702f636f6d2e6474732e667265656669726574682d66705843537068495636644b43376a4c2d574f7952413d3d2f626173652e61706bf00406f804018a050233329a050a32303139313139303236a80503b205094f70656e474c455332b805ff01c00504e005be7eea05093372645f7061727479f205704b717348543857393347646347335a6f7a454e6646775648746d377171316552554e6149444e67526f626f7a4942744c4f695943633459367a767670634943787a514632734f453463627974774c7334785a62526e70524d706d5752514b6d654f35766373386e51594268777148374bf805e7e4068806019006019a060134a2060134b2062213521146500e590349510e460900115843395f005b510f685b560a6107576d0f0366')
    data = data.replace(OLD_OPEN_ID.encode(), NEW_OPEN_ID.encode())
    data = data.replace(OLD_ACCESS_TOKEN.encode(), NEW_ACCESS_TOKEN.encode())
    d = encrypt_api(data.hex())
    Final_Payload = bytes.fromhex(d)
    
    headers = {
        "Host": "loginbp.ggpolarbear.com",
        "X-Unity-Version": "2018.4.11f1",
        "Accept": "*/*",
        "Authorization": "Bearer",
        "ReleaseVersion": "OB53",
        "X-GA": "v1 1",
        "Accept-Encoding": "gzip",
        "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        "Content-Type": "application/x-www-form-urlencoded",
        "Content-Length": str(len(Final_Payload)),
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; G011A Build/PI)",
        "Connection": "keep-alive"
    }
    
    URL = "https://loginbp.ggpolarbear.com/MajorLogin"
    RESPONSE = requests.post(URL, headers=headers, data=Final_Payload, verify=False)
    
    if RESPONSE.status_code == 200:
        if len(RESPONSE.text) < 10:
            return False
        BASE64_TOKEN = RESPONSE.text[RESPONSE.text.find("eyJhbGciOiJIUzI1NiIsInN2ciI6IjEiLCJ0eXAiOiJKV1QifQ"):-1]
        second_dot_index = BASE64_TOKEN.find(".", BASE64_TOKEN.find(".") + 1)
        BASE64_TOKEN = BASE64_TOKEN[:second_dot_index + 44]
        return BASE64_TOKEN
    else:
        print(f"MajorLogin failed with status: {RESPONSE.status_code}")
        print(f"Response: {RESPONSE.text}")
        return False

def fetch_jwt_token_direct(server_key):
    try:
        GUEST_ACCOUNTS = {
            "me": {
                "uid": "4929563871",
                "pass": "otman-HHLNJTOADJoT"
            },
            "ind": {
                "uid": "4930179410",
                "pass": "STAR-OC3Y01PGM-CORE"
            },
            "eu": {
                "uid": "4930224927",
                "pass": "xotman-B8TSU1DZAx7m"
            }
        }
        if server_key not in GUEST_ACCOUNTS:
            print(f"❌ Server {server_key} not found!")
            return None
        account = GUEST_ACCOUNTS[server_key]
        uid = account["uid"]
        password = account["pass"]
        url = "https://100067.connect.garena.com/oauth/guest/token/grant"
        headers = {
            "Host": "100067.connect.garena.com",
            "User-Agent": "GarenaMSDK/4.0.19P4(G011A ;Android 9;en;US;)",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "close",
        }
        data = {
            "uid": f"{uid}",
            "password": f"{password}",
            "response_type": "token",
            "client_type": "2",
            "client_secret": "",
            "client_id": "100067",
        }
        response = requests.post(url, headers=headers, data=data)
        res_data = response.json()
        if "access_token" in res_data:
            return TOKEN_MAKER(
                "c69ae208fad72738b674b2847b50a3a1dfa25d1a19fae745fc76ac4a0e414c94",
                res_data['access_token'],
                "4306245793de86da425a52caadf21eed",
                res_data['open_id'],
                uid
            )
        return None
    except Exception as e:
        print(f"⚠️ Error: {e}")
        return None

def fetch_jwt_token():
    server_name = "me"
    server_name = "ind"
    server_name = "eu"
    return fetch_jwt_token_direct(server_name)

# ===== دوال API =====
def send_friend_request(player_id):
    global JWT_TOKEN
    if not JWT_TOKEN:
        return "⚠️ التوكن غير متاح حاليًا أو غير صالح. يرجى محاولة التحديث يدوياً أو انتظار التحديث."
    enc_id = Encrypt_ID(player_id)
    payload = f"08a7c4839f1e10{enc_id}1801"
    encrypted_payload = encrypt_api(payload)
    url = "https://clientbp.ggpolarbear.com/RequestAddingFriend"
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "X-Unity-Version": "2018.4.11f1",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB53",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; G011A Build/PI)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip"
    }
    try:
        r = requests.post(url, headers=headers, data=bytes.fromhex(encrypted_payload), timeout=15, verify=False)
        if r.status_code == 200:
            if "BR_FRIEND_NOT_SAME_REGION" in r.text:
                return "❌ لا يمكن إضافة اللاعب لأنه ليس في نفس منطقتك"
            return "✅ تم إرسال طلب الصداقة بنجاح!"
        elif r.status_code == 400:
            if "BR_FRIEND_NOT_SAME_REGION" in r.text:
                return "❌ لا يمكن إضافة اللاعب لأنه ليس في نفس منطقتك"
            return "❌ خطأ في الطلب - قد يكون اللاعب من منطقة مختلفة"
        elif r.status_code == 401:
            JWT_TOKEN = None
            return "❌ التوكن غير صالح أو منتهي الصلاحية."
        elif r.status_code == 404:
            return "❌ اللاعب غير موجود أو خطأ في الاتصال."
        else:
            return f"❌ فشل إرسال الطلب. كود الخطأ: {r.status_code}"
    except Exception as e:
        return f"❌ حدث خطأ أثناء إرسال الطلب: {str(e)}"

def remove_friend(player_id):
    global JWT_TOKEN
    if not JWT_TOKEN:
        return "⚠️ التوكن غير متاح حاليا أو غير صالح. سيتم إصلاحه حالا."
    enc_id = Encrypt_ID(player_id)
    payload = f"08a7c4839f1e10{enc_id}1802"
    encrypted_payload = encrypt_api(payload)
    url = "https://clientbp.ggpolarbear.com/RemoveFriend"
    headers = {
        "Authorization": f"Bearer {JWT_TOKEN}",
        "X-Unity-Version": "2018.4.11f1",
        "X-GA": "v1 1",
        "ReleaseVersion": "OB53",
        "Content-Type": "application/x-www-form-urlencoded",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; G011A Build/PI)",
        "Connection": "Keep-Alive",
        "Accept-Encoding": "gzip"
    }
    try:
        r = requests.post(url, headers=headers, data=bytes.fromhex(encrypted_payload), timeout=15, verify=False)
        if r.status_code != 200:
            print(f"DEBUG: RemoveFriend FAILED. Status={r.status_code}, Response Body={r.text}")
        if r.status_code == 200:
            return "✅ تم الحذف بنجاح!"
        elif r.status_code == 401:
            JWT_TOKEN = None
            return "❌ التوكن غير صالح أو منتهي الصلاحية. سيتم إصلاحه حالا."
        elif r.status_code == 400:
            server_error = r.text.strip()
            if server_error:
                return f"❌ فشل الحذف. كود الخطأ: 400. استجابة السيرفر: {server_error}"
            return "❌ فشل الحذف. كود الخطأ: 400 - تحقق من الحمولة Protobuf)."
        elif r.status_code == 404:
            return "❌ اللاعب غير موجود في قائمة الأصدقاء أو حدث خطأ."
        else:
            return f"❌ فشل الحذف {r.status_code}"
    except Exception as e:
        return f"❌ حدث خطأ أثناء الحذف: {str(e)}"

# ===== دوال تحميل البيانات =====
def load_users():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                if isinstance(data, dict):
                    return data
            except json.JSONDecodeError:
                pass
    return {}

def save_users():
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(users, file, ensure_ascii=False, indent=4)

def load_groups():
    if os.path.exists(GROUPS_FILE):
        with open(GROUPS_FILE, "r", encoding="utf-8") as file:
            try:
                data = json.load(file)
                if isinstance(data, dict):
                    return {k: v for k, v in data.items()}
            except json.JSONDecodeError:
                pass
    return {}

def save_groups():
    with open(GROUPS_FILE, "w", encoding="utf-8") as file:
        json.dump(group_activations, file, ensure_ascii=False, indent=4)

def load_maintenance_status():
    if os.path.exists(MAINTENANCE_FILE):
        with open(MAINTENANCE_FILE, "r", encoding="utf-8") as file:
            try:
                return json.load(file).get("maintenance_mode", False)
            except json.JSONDecodeError:
                pass
    return False

def save_maintenance_status(status):
    with open(MAINTENANCE_FILE, "w", encoding="utf-8") as file:
        json.dump({"maintenance_mode": status}, file)

# ===== دوال المساعدين (المعدلة) =====
#تم التعديل - تم تحديث الدوال لاستخدام owner_id و owner_name
def is_admin(message):
    user_id = message.from_user.id if hasattr(message, 'from_user') else message
    owner_id = get_owner_id()
    return str(user_id) == str(owner_id) if owner_id else False

def is_allowed_group(message):
    chat_id_str = str(message.chat.id)
    owner_name = get_owner_name()
    if chat_id_str in group_activations:
        expiry_timestamp = group_activations[chat_id_str]
        if expiry_timestamp > time.time():
            return True
        else:
            del group_activations[chat_id_str]
            save_groups()
            bot.send_message(message.chat.id, f"⚠️ انتهت صلاحية البوت في هذه المجموعة.\nيرجى التواصل مع {owner_name} لإعادة التفعيل.", parse_mode="Markdown")
            return False
    else:
        bot.send_message(message.chat.id, f"⚠️ البوت غير مفعل في هذه المجموعة.\nيرجى التواصل مع {owner_name} ليقوم بتفعيل البوت.", parse_mode="Markdown")
        return False

def is_subscribed(message):
    try:
        status = bot.get_chat_member(SUBSCRIPTION_CHANNEL_ID, message.from_user.id).status
        return status in ['member', 'administrator', 'creator']
    except telebot.apihelper.ApiTelegramException as e:
        if "chat not found" in str(e) or "user not found" in str(e):
            print(f"Error checking subscription: {e}")
            return False
        return False

def format_remaining_time(expiry_time):
    remaining = int(expiry_time - time.time())
    if remaining <= 0:
        return "😭 انتهت الصلاحية"
    days = remaining // 86400
    hours = (remaining % 86400) // 3600
    minutes = ((remaining % 86400) % 3600) // 60
    seconds = remaining % 60
    parts = []
    if days > 0:
        parts.append(f"{days} Day")
    if hours > 0:
        parts.append(f"{hours} Hours")
    if minutes > 0:
        parts.append(f"{minutes} Minutes")
    parts.append(f"{seconds} Seconds")
    return " ".join(parts)

def get_total_users_count():
    count = 0
    for uid, data in users.items():
        if isinstance(data, dict) and "name" in data and "expiry" in data:
            count += 1
    return count

# ===== دوال OTMAN الإضافية =====
hex_Key = "32656534343831396539623435393838343531343130363762323831363231383734643064356437616639643866376530306331653534373135623764316533"
MaIn_KeY = bytes.fromhex(hex_Key)

ReGiOnMaP = {
    "ME": "ar", "IND": "hi", "ID": "id", "VN": "vi", "TH": "th",
    "BD": "bn", "PK": "ur", "TW": "zh", "EU": "en", "CIS": "ru",
    "NA": "en", "SAC": "es", "BR": "pt"
}

ReGiOnUrLs = {
    "IND": "https://client.ind.freefiremobile.com/",
    "ID": "https://clientbp.ggpolarbear.com/",
    "BR": "https://client.us.freefiremobile.com/",
    "ME": "https://clientbp.common.ggbluefox.com/",
    "VN": "https://clientbp.ggpolarbear.com/",
    "TH": "https://clientbp.common.ggbluefox.com/",
    "CIS": "https://clientbp.ggpolarbear.com/",
    "BD": "https://clientbp.ggpolarbear.com/",
    "PK": "https://clientbp.ggpolarbear.com/",
    "SG": "https://clientbp.ggpolarbear.com/",
    "NA": "https://client.us.freefiremobile.com/",
    "SAC": "https://client.us.freefiremobile.com/",
    "EU": "https://clientbp.ggpolarbear.com/",
    "TW": "https://clientbp.ggpolarbear.com/"
}

SUPERSCRIPT_MAP = {
    '0': '⁰', '1': '¹', '2': '²', '3': '³', '4': '⁴',
    '5': '⁵', '6': '⁶', '7': '⁷', '8': '⁸', '9': '⁹'
}

def to_superscript(num_str):
    return ''.join(SUPERSCRIPT_MAP.get(ch, ch) for ch in num_str)

def GeTlAnG(cOde):
    return ReGiOnMaP.get(cOde)

def GeTuRl(cOde):
    return ReGiOnUrLs.get(cOde)

def eNcVr(nUm):
    if nUm < 0:
        return b''
    rEsUlT = []
    while True:
        bYtE = nUm & 0x7F
        nUm >>= 7
        if nUm:
            bYtE |= 0x80
        rEsUlT.append(bYtE)
        if not nUm:
            break
    return bytes(rEsUlT)

def cReAtEvAr(fIeLdNuM, vAl):
    fIeLdHeAdEr = (fIeLdNuM << 3) | 0
    return eNcVr(fIeLdHeAdEr) + eNcVr(vAl)

def cReAtElEnGtH(fIeLdNuM, vAl):
    fIeLdHeAdEr = (fIeLdNuM << 3) | 2
    eNcOdEd = vAl.encode() if isinstance(vAl, str) else vAl
    return eNcVr(fIeLdHeAdEr) + eNcVr(len(eNcOdEd)) + eNcOdEd

def cReAtEpRoTo(fIeLdS):
    pAcKeT = bytearray()
    for fIeLd, vAl in fIeLdS.items():
        if isinstance(vAl, dict):
            nEsTeD = cReAtEpRoTo(vAl)
            pAcKeT.extend(cReAtElEnGtH(fIeLd, nEsTeD))
        elif isinstance(vAl, int):
            pAcKeT.extend(cReAtEvAr(fIeLd, vAl))
        elif isinstance(vAl, (str, bytes)):
            pAcKeT.extend(cReAtElEnGtH(fIeLd, vAl))
    return pAcKeT

def eNcAeS(pLaInTeXt):
    pLaIn = bytes.fromhex(pLaInTeXt)
    kEy = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iV = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cIpHeR = AES.new(kEy, AES.MODE_CBC, iV)
    rEsUlT = cIpHeR.encrypt(pad(pLaIn, AES.block_size))
    return bytes.fromhex(rEsUlT.hex())

def eNcApI(pT):
    pT = bytes.fromhex(pT)
    kEy = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
    iV = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])
    cIpHeR = AES.new(kEy, AES.MODE_CBC, iV)
    cT = cIpHeR.encrypt(pad(pT, AES.block_size))
    return cT.hex()

def gEnNaMe(prefix):
    digits = ''.join(str(random.randint(0, 9)) for _ in range(5))
    sup_digits = to_superscript(digits)
    return prefix + sup_digits

def gEnPaSsWoRd(lEn=9):
    cHaRs = string.ascii_letters + string.digits
    rAnD = ''.join(random.choice(cHaRs) for _ in range(lEn)).upper()
    return f"OTMAN_{rAnD}_HERE"

def eNcOdEsTr(oRiG):
    kEyStReAm = [
        0x30, 0x30, 0x30, 0x32, 0x30, 0x31, 0x37, 0x30,
        0x30, 0x30, 0x30, 0x30, 0x32, 0x30, 0x31, 0x37,
        0x30, 0x30, 0x30, 0x30, 0x30, 0x32, 0x30, 0x31,
        0x37, 0x30, 0x30, 0x30, 0x30, 0x30, 0x32, 0x30
    ]
    eNcOdEd = ""
    for i in range(len(oRiG)):
        oRiGbYtE = ord(oRiG[i])
        kEyByTe = kEyStReAm[i % len(kEyStReAm)]
        rEsByTe = oRiGbYtE ^ kEyByTe
        eNcOdEd += chr(rEsByTe)
    return {"open_id": oRiG, "f14": eNcOdEd}

def tOuNiCoDeEsC(sTr):
    return ''.join(c if 32 <= ord(c) <= 126 else f'\\u{ord(c):04x}' for c in sTr)

def pArSeRoOm(iT):
    try:
        data = bytes.fromhex(iT)
        result = {}
        pos = 0
        while pos < len(data):
            tag = data[pos]
            field_num = tag >> 3
            wire_type = tag & 0x07
            pos += 1
            if wire_type == 0:
                value = 0
                shift = 0
                while pos < len(data):
                    byte = data[pos]
                    pos += 1
                    value |= (byte & 0x7F) << shift
                    if not (byte & 0x80):
                        break
                    shift += 7
                result[str(field_num)] = value
            elif wire_type == 2:
                length = 0
                shift = 0
                while pos < len(data):
                    byte = data[pos]
                    pos += 1
                    length |= (byte & 0x7F) << shift
                    if not (byte & 0x80):
                        break
                    shift += 7
                value = data[pos:pos+length]
                pos += length
                result[str(field_num)] = value.hex()
        return json.dumps(result)
    except Exception:
        return None

def cHoOsErEgIoN(dAtA, jWt):
    uRl = "https://loginbp.ggpolarbear.com/ChooseRegion"
    hEaDeRs = {
        'User-Agent': "Dalvik/2.1.0 (Linux; U; Android 12; M2101K7AG Build/SKQ1.210908.001)",
        'Connection': "Keep-Alive",
        'Accept-Encoding': "gzip",
        'Content-Type': "application/x-www-form-urlencoded",
        'Expect': "100-continue",
        'Authorization': f"Bearer {jWt}",
        'X-Unity-Version': "2018.4.11f1",
        'X-GA': "v1 1",
        'ReleaseVersion': "OB53"
    }
    rEs = requests.post(uRl, data=dAtA, headers=hEaDeRs, verify=False)
    return rEs.status_code

def gEtLoGiNdAtA(jWt, pL, rEg):
    if rEg.lower() == "me":
        uRl = 'https://clientbp.ggpolarbear.com/GetLoginData'
    else:
        lInK = GeTuRl(rEg)
        uRl = f"{lInK}GetLoginData"
    hEaDeRs = {
        'Expect': '100-continue',
        'Authorization': f'Bearer {jWt}',
        'X-Unity-Version': '2018.4.11f1',
        'X-GA': 'v1 1',
        'ReleaseVersion': 'OB53',
        'Content-Type': 'application/x-www-form-urlencoded',
        'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 10; G011A Build/PI)',
        'Host': 'clientbp.ggpolarbear.com',
        'Connection': 'close',
        'Accept-Encoding': 'gzip, deflate, br',
    }
    mAxTrY = 1
    aTt = 0
    while aTt < mAxTrY:
        try:
            rEs = requests.post(uRl, headers=hEaDeRs, data=pL, verify=False)
            rEs.raise_for_status()
            x = rEs.content.hex()
            jR = pArSeRoOm(x)
            if jR is None:
                return None
            pD = json.loads(jR)
            return pD
        except Exception:
            aTt += 1
            time.sleep(0.5)
    return None

def gEtPaYlOaD(jWt, nAt, dAtE, rEsP, cOdE, nAmE, uId, pAsS, rEg):
    try:
        tPb = jWt.split('.')[1]
        tPb += '=' * ((4 - len(tPb) % 4) % 4)
        dP = base64.urlsafe_b64decode(tPb).decode('utf-8')
        dP = json.loads(dP)
        nEiD = dP['external_id']
        sMd5 = dP['signature_md5']
        nOw = datetime.now()
        nOw = str(nOw)[:len(str(nOw)) - 7]
        pL = b':\x071.111.2\xaa\x01\x02ar\xb2\x01 55ed759fcf94f85813e57b2ec8492f5c\xba\x01\x014\xea\x01@6fb7fdef8658fd03174ed551e82b71b21db8187fa0612c8eaf1b63aa687f1eae\x9a\x06\x014\xa2\x06\x014'
        pL = pL.replace(b"2023-12-24 04:21:34", str(nOw).encode())
        pL = pL.replace(b"c69ae208fad72738b674b2847b50a3a1dfa25d1a19fae745fc76ac4a0e414c94", nAt.encode("UTF-8"))
        pL = pL.replace(b"4306245793de86da425a52caadf21eed", nEiD.encode("UTF-8"))
        pL = pL.replace(b"4306245793de86da425a52caadf21eed", sMd5.encode("UTF-8"))
        pHex = pL.hex()
        pEnC = eNcApI(pHex)
        pByTeS = bytes.fromhex(pEnC)
        dAtA = gEtLoGiNdAtA(jWt, pByTeS, rEg)
        return {
            "data": dAtA,
            "response": rEsP,
            "status_code": cOdE,
            "name": nAmE,
            "uid": uId,
            "password": pAsS
        }
    except Exception:
        return None

def uSeRlOgIn(uId, pAsS, aT, oId, rEsP, cOdE, nAmE, rEg):
    lAnG = GeTlAnG(rEg)
    lB = lAnG.encode("ascii")
    hEaDeRs = {
        "Accept-Encoding": "gzip",
        "Authorization": "Bearer",
        "Connection": "Keep-Alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Expect": "100-continue",
        "Host": "loginbp.ggpolarbear.com",
        "ReleaseVersion": "OB53",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_I005DA Build/PI)",
        "X-GA": "v1 1",
        "X-Unity-Version": "2018.4.11f1"
    }
    pL = b'\x1a\x132025-11-26 01:51:28"\tfree fire(\x01:\x071.123.1B2Android OS 9 / API-28 (PI/rel.cjw.20220518.114133)J\x08HandheldR\x0cMTN/SpacetelZ\x04WIFI`\x80\nh\xd0\x05r\x03240z-x86-64 SSE3 SSE4.1 SSE4.2 AVX AVX2 | 2400 | 4\x80\x01\xe6\x1e\x8a\x01\x0fAdreno (TM) 640\x92\x01\rOpenGL ES 3.2\x9a\x01+Google|625f716f-91a7-495b-9f16-08fe9d3c6533\xa2\x01\x0e176.28.139.185\xaa\x01\x02ar\xb2\x01 4306245793de86da425a52caadf21eed\xba\x01\x014\xc2\x01\x08Handheld\xca\x01\rOnePlus A5010\xea\x01@c69ae208fad72738b674b2847b50a3a1dfa25d1a19fae745fc76ac4a0e414c94\xf0\x01\x01\xca\x02\x0cMTN/Spacetel\xd2\x02\x04WIFI\xca\x03 1ac4b80ecf0478a44203bf8fac6120f5\xe0\x03\xb5\xee\x02\xe8\x03\x9a\x80\x02\xf0\x03\xaf\x13\xf8\x03\x84\x07\x80\x04\xa7\x8f\x02\x88\x04\xb5\xee\x02\x90\x04\xa7\x8f\x02\x98\x04\xb5\xee\x02\xb0\x04\x04\xc8\x04\x01\xd2\x04=/data/app/com.dts.freefireth-fpXCSphIV6dKC7jL-WOyRA==/lib/arm\xe0\x04\x01\xea\x04_e62ab9354d8fb5fb081db338acb33491|/data/app/com.dts.freefireth-fpXCSphIV6dKC7jL-WOyRA==/base.apk\xf0\x04\x06\xf8\x04\x01\x8a\x05\x0232\x9a\x05\n2019119026\xa8\x05\x03\xb2\x05\tOpenGLES2\xb8\x05\xff\x01\xc0\x05\x04\xe0\x05\xbe~\xea\x05\t3rd_party\xf2\x05pKqsHT8W93GdcG3ZozENfFwVHtm7qq1eRUNaIDNgRobozIBtLOiYCc4Y6zvvpcICxzQF2sOE4cbytwLs4xZbRnpRMpmWRQKmeO5vcs8nQYBhwqH7K\xf8\x05\xe7\xe4\x06\x88\x06\x01\x90\x06\x01\x9a\x06\x014\xa2\x06\x014\xb2\x06"\x13R\x11FP\x0eY\x03IQ\x0eF\t\x00\x11XC9_\x00[Q\x0fh[V\na\x07Wm\x0f\x03f'
    pL = pL.replace(b'c69ae208fad72738b674b2847b50a3a1dfa25d1a19fae745fc76ac4a0e414c94', aT.encode())
    pL = pL.replace(b'4306245793de86da425a52caadf21eed', oId.encode())
    d = eNcApI(pL.hex())
    fP = bytes.fromhex(d)
    if rEg.lower() == "me":
        uRl = "https://loginbp.common.ggbluefox.com/MajorLogin"
    else:
        uRl = "https://loginbp.ggpolarbear.com/MajorLogin"
    rEs = requests.post(uRl, headers=hEaDeRs, data=fP, verify=False)
    if rEs.status_code == 200:
        if len(rEs.text) < 10:
            return False
        if lAnG.lower() not in ["ar", "en"]:
            jR = pArSeRoOm(rEs.content.hex())
            if jR is None:
                return False
            pD = json.loads(jR)
            tOkEn = None
            for key in ['8', 'data']:
                if key in pD:
                    tOkEn = pD[key]
                    break
            if not tOkEn:
                return False
            if rEg.lower() == "cis":
                rEg = "RU"
            fIeLdS = {1: rEg}
            fByTeS = bytes.fromhex(eNcApI(cReAtEpRoTo(fIeLdS).hex()))
            cR = cHoOsErEgIoN(fByTeS, tOkEn)
            if cR == 200:
                return lOgInSeRvEr(uId, pAsS, aT, oId, rEsP, cOdE, nAmE, rEg)
        else:
            tOkEn = rEs.text[rEs.text.find("eyJhbGciOiJIUzI1NiIsInN2ciI6IjEiLCJ0eXAiOiJKV1QifQ"):-1]
        sDi = tOkEn.find(".", tOkEn.find(".") + 1)
        time.sleep(0.2)
        tOkEn = tOkEn[:sDi + 44]
        return gEtPaYlOaD(tOkEn, aT, 1, rEsP, cOdE, nAmE, uId, pAsS, rEg)
    return False

def lOgInSeRvEr(uId, pAsS, aT, oId, rEsP, cOdE, nAmE, rEg):
    lAnG = GeTlAnG(rEg)
    lB = lAnG.encode("ascii")
    hEaDeRs = {
        "Accept-Encoding": "gzip",
        "Authorization": "Bearer",
        "Connection": "Keep-Alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Expect": "100-continue",
        "Host": "loginbp.ggpolarbear.com",
        "ReleaseVersion": "OB53",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_I005DA Build/PI)",
        "X-GA": "v1 1",
        "X-Unity-Version": "2018.4.11f1"
    }
    pL = b'\x1a\x13\x32\x30\x32\x36\x2d\x30\x31\x2d\x31\x34\x20\x31\x35\x3a\x32\x36\x3a\x30\x39\x22\x09\x66\x72\x65\x65\x20\x66\x69\x72\x65\x3a\x07\x31\x2e\x31\x32\x30\x2e\x33\x42\x0a\x69\x4f\x53\x20\x31\x35\x2e\x38\x2e\x32\x4a\x08\x48\x61\x6e\x64\x68\x65\x6c\x64\x65\x64\x52\x0e\x4f\x72\x61\x6e\x67\x65\x20\x54\x75\x6e\x69\x73\x69\x61\x5a\x04\x57\x49\x46\x49\x60\xb6\x0a\x68\xee\x05\x72\x03\x33\x32\x36\x7a\x0d\x61\x72\x6d\x36\x34\x20\x7c\x20\x30\x20\x7c\x20\x32\x80\x01\xd0\x0f\x8a\x01\x0d\x41\x70\x70\x6c\x65\x20\x41\x31\x30\x20\x47\x50\x55\x92\x01\x05\x4d\x65\x74\x61\x6c\x9a\x01\x2a\x41\x70\x70\x6c\x65\x7c\x34\x37\x36\x33\x42\x30\x36\x46\x2d\x31\x41\x46\x42\x2d\x34\x39\x31\x46\x2d\x39\x43\x31\x39\x2d\x37\x46\x43\x46\x38\x42\x38\x30\x39\x32\x33\x30\xa2\x01\x0e\x31\x30\x32\x2e\x31\x35\x32\x2e\x36\x33\x2e\x31\x33\x38\xaa\x01\x05\x67\x70\x74\x2d\x62\x72\xb2\x01\x20\x30\x35\x63\x32\x64\x30\x65\x38\x62\x32\x30\x36\x62\x34\x64\x37\x65\x39\x62\x30\x32\x38\x62\x38\x34\x32\x62\x61\x32\x63\x61\x32\xba\x01\x01\x34\xc2\x01\x08\x48\x61\x6e\x64\x68\x65\x6c\x64\x65\x64\xca\x01\x09\x69\x50\x68\x6f\x6e\x65\x39\x2c\x33\xea\x01\x40\x33\x32\x31\x62\x66\x36\x65\x31\x66\x64\x36\x63\x65\x37\x62\x32\x32\x64\x34\x39\x64\x36\x35\x35\x38\x63\x31\x30\x63\x65\x31\x35\x38\x30\x30\x62\x66\x62\x33\x35\x39\x64\x65\x37\x36\x63\x64\x30\x34\x32\x65\x65\x62\x66\x34\x32\x31\x39\x64\x63\x34\x61\x62\x65\xf0\x01\x01\xf0\x03\xa1\xee\x01\xf8\x03\xbd\x1b\xb0\x04\x02\xc8\x04\x02\xe0\x04\x01\xea\x04\x09\x49\x4f\x53\x44\x65\x76\x69\x63\x65\xf0\x04\x03\xf8\x04\x01\x9a\x05\x07\x31\x2e\x31\x32\x30\x2e\x31\xa8\x05\x03\xb2\x05\x05\x54\x4d\x65\x74\x61\x6c\xb8\x05\xff\x7f\xc0\x05\x04\xe0\x05\xca\xc8\x02\xea\x05\x03\x69\x6f\x73\xf2\x05\x48\x4b\x71\x73\x48\x54\x38\x43\x6a\x38\x69\x6d\x33\x32\x57\x70\x5a\x44\x64\x59\x2f\x6e\x51\x31\x58\x77\x43\x4c\x36\x55\x69\x2f\x32\x37\x48\x6e\x79\x6b\x32\x78\x34\x32\x69\x41\x72\x68\x7a\x64\x61\x30\x75\x4f\x44\x56\x64\x74\x6c\x51\x36\x46\x45\x30\x54\x2f\x52\x49\x7a\x6e\x6c\x70\x41\x3d\x3d\x90\x06\x01\x9a\x06\x01\x34\xa2\x06\x01\x34\xb2\x06\x0e\x60\x00\x17\x12\x72\x13\x59\x58\x21\x54\x5f\x12\x0d\x10\x09\x09\x09\x09\x09\x09\x09\x09\x09'
    pL = pL.replace(b'c69ae208fad72738b674b2847b50a3a1dfa25d1a19fae745fc76ac4a0e414c94', aT.encode())
    pL = pL.replace(b'4306245793de86da425a52caadf21eed', oId.encode())
    d = eNcApI(pL.hex())
    fP = bytes.fromhex(d)
    if rEg.lower() == "me":
        uRl = "https://loginbp.common.ggbluefox.com/MajorLogin"
    else:
        uRl = "https://loginbp.ggpolarbear.com/MajorLogin"
    rEs = requests.post(uRl, headers=hEaDeRs, data=fP, verify=False)
    if rEs.status_code == 200:
        if len(rEs.text) < 10:
            return False
        jR = pArSeRoOm(rEs.content.hex())
        if jR is None:
            return False
        pD = json.loads(jR)
        tOkEn = pD.get('8', pD.get('data', None))
        if not tOkEn:
            return False
        sDi = tOkEn.find(".", tOkEn.find(".") + 1)
        time.sleep(0.2)
        tOkEn = tOkEn[:sDi + 44]
        return gEtPaYlOaD(tOkEn, aT, 1, rEsP, cOdE, nAmE, uId, pAsS, rEg)
    return False

def cReAtEaCc(rEg, name_prefix):
    pAsS = gEnPaSsWoRd()
    dAtA = f"password={pAsS}&client_type=2&source=2&app_id=100067"
    mSg = dAtA.encode('utf-8')
    sIg = hmac.new(MaIn_KeY, mSg, hashlib.sha256).hexdigest()
    uRl = "https://100067.connect.garena.com/oauth/guest/register"
    hEaDeRs = {
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; M2101K7AG Build/SKQ1.210908.001)",
        "Authorization": "Signature " + sIg,
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip",
        "Connection": "Keep-Alive"
    }
    rEsPoNsE = requests.post(uRl, headers=hEaDeRs, data=dAtA)
    try:
        uId = rEsPoNsE.json()['uid']
        return gEtToKeN(uId, pAsS, rEg, name_prefix)
    except:
        return cReAtEaCc(rEg, name_prefix)

def gEtToKeN(uId, pAsS, rEg, name_prefix):
    uRl = "https://100067.connect.garena.com/oauth/guest/token/grant"
    hEaDeRs = {
        "Accept-Encoding": "gzip",
        "Connection": "Keep-Alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Host": "100067.connect.garena.com",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; M2101K7AG Build/SKQ1.210908.001)",
    }
    bOdY = {
        "uid": uId,
        "password": pAsS,
        "response_type": "token",
        "client_type": "2",
        "client_secret": MaIn_KeY,
        "client_id": "100067"
    }
    rEsPoNsE = requests.post(uRl, headers=hEaDeRs, data=bOdY)
    oPeNiD = rEsPoNsE.json()['open_id']
    aCcEsStOkEn = rEsPoNsE.json()["access_token"]
    rEs = eNcOdEsTr(oPeNiD)
    fIeLd = tOuNiCoDeEsC(rEs['f14'])
    fIeLd = codecs.decode(fIeLd, 'unicode_escape').encode('latin1')
    return rEgMaJoR(aCcEsStOkEn, oPeNiD, fIeLd, uId, pAsS, rEg, name_prefix)

def rEgMaJoR(aT, oId, f, uId, pAsS, rEg, name_prefix):
    uRl = "https://loginbp.ggpolarbear.com/MajorRegister"
    nAmE = gEnNaMe(name_prefix)
    hEaDeRs = {
        "Accept-Encoding": "gzip",
        "Authorization": "Bearer",
        "Connection": "Keep-Alive",
        "Content-Type": "application/x-www-form-urlencoded",
        "Expect": "100-continue",
        "Host": "loginbp.ggpolarbear.com",
        "ReleaseVersion": "OB53",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_I005DA Build/PI)",
        "X-GA": "v1 1",
        "X-Unity-Version": "2018.4."
    }
    pAyLoAd = {
        1: nAmE,
        2: aT,
        3: oId,
        5: 102000007,
        6: 4,
        7: 1,
        13: 1,
        14: f,
        15: "en",
        16: 1,
        17: 1
    }
    pHex = cReAtEpRoTo(pAyLoAd).hex()
    pEnC = eNcAeS(pHex).hex()
    bOdY = bytes.fromhex(pEnC)
    rEs = requests.post(uRl, headers=hEaDeRs, data=bOdY, verify=False)
    return uSeRlOgIn(uId, pAsS, aT, oId, rEs.content.hex(), rEs.status_code, nAmE, rEg)

def generate_accounts(region, name_prefix, count):
    region = region.upper()
    if region not in ReGiOnMaP:
        raise ValueError("Invalid region")
    if count > MAX_ACCOUNTS:
        raise ValueError(f"Maximum allowed accounts is {MAX_ACCOUNTS}")
    accounts = []
    for i in range(count):
        try:
            result = cReAtEaCc(region, name_prefix)
            if result and result.get('status_code') == 200:
                accounts.append({
                    "name": result.get('name'),
                    "uid": result.get('uid'),
                    "password": result.get('password')
                })
            else:
                accounts.append({"error": f"Failed to generate account {i+1}"})
        except Exception as e:
            accounts.append({"error": f"Account {i+1} error: {str(e)}"})
    return accounts

def escape_md(text: str) -> str:
    if not text:
        return ""
    special_chars = r'_*\[\]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(special_chars)}])', r'\\\1', str(text))

def format_time(seconds):
    if seconds is None:
        return "N/A"
    mins, secs = divmod(int(seconds), 60)
    hrs, mins = divmod(mins, 60)
    if hrs > 0:
        return f"{hrs}h {mins}m {secs}s"
    elif mins > 0:
        return f"{mins}m {secs}s"
    else:
        return f"{secs}s"
# ========== كلاس العميل OTMAN ==========
class xCLF():
    def __init__(xSeT, id, password):
        xSeT.id = id
        xSeT.password = password
        xSeT.thread_pool = ThreadPoolExecutor(max_workers=20)
        xSeT.active_threads = []
        xSeT.thread_timeout = 30
        xSeT.InPuTMsG = ""
        xSeT.DeCode_CliEnt_Uid = ""
        xSeT.max_retries = 3
        xSeT.retry_count = 0
        with connected_clients_lock:
            connected_clients[xSeT.id] = xSeT
        xSeT.GeNToKeNLogin()

    def GeTinFoSqMsG(xSeT, teamcode):
        try:
            if hasattr(xSeT, 'CliEnts2') and xSeT.CliEnts2:
                xSeT.DaTa2 = b""
                xSeT.CliEnts2.send(JoinSq(teamcode, xSeT.key, xSeT.iv))
                start_wait = time.time()
                response_received = False
                while time.time() - start_wait < 5:
                    try:
                        xSeT.CliEnts2.settimeout(0.5)
                        chunk = xSeT.CliEnts2.recv(99999)
                        if chunk:
                            xSeT.DaTa2 += chunk
                            hex_data = xSeT.DaTa2.hex()
                            if len(hex_data) >= 10 and '0500' in hex_data[:10]:
                                try:
                                    if len(hex_data) > 10:
                                        decoded_data = DeCode_PackEt(hex_data[10:])
                                        dT = json.loads(decoded_data)
                                        OwNer_UiD, SQuAD_CoDe, ChaT_CoDe = GeTSQDaTa(dT)
                                        if OwNer_UiD and ChaT_CoDe:
                                            xSeT.CliEnts2.send(ExitSq('000000', xSeT.key, xSeT.iv))
                                            time.sleep(0.2)
                                            response_received = True
                                            return {
                                                "success": True,
                                                "Owner_UiD": OwNer_UiD,
                                                "Squad_Code": SQuAD_CoDe,
                                                "Chat_Code": ChaT_CoDe
                                            }
                                except:
                                    pass
                    except socket.timeout:
                        continue
                    except:
                        break
                    time.sleep(0.1)
            return {"success": False, "reason": "No response or invalid data"}
        except Exception as e:
            return {"success": False, "reason": str(e)}

    def SeNd_MsG(xSeT, client, OwNer_UiD, ChaT_CoDe, message, count=100):
        try:
            if hasattr(client, 'CliEnts') and client.CliEnts:
                client.CliEnts.send(OpenCh(OwNer_UiD, ChaT_CoDe, client.key, client.iv))
                time.sleep(1)
                for i in range(count):
                    client.CliEnts.send(MsqSq(f'[b][c]{generate_random_color()}{message}', OwNer_UiD, client.key, client.iv))
                    time.sleep(0.5)
        except:
            pass

    def SeNd_SpaM_MsG(xSeT, OwNer_UiD, ChaT_CoDe, message, count=100):
        try:
            threads = []
            message_clients = list(connected_clients.values())[:3]
            for client in message_clients:
                thread = threading.Thread(target=xSeT.SeNd_MsG, args=(client, OwNer_UiD, ChaT_CoDe, message, count))
                threads.append(thread)
                thread.start()
            for thread in threads:
                thread.join(timeout=30)
            return True
        except:
            return False

    def cleanup_threads(xSeT):
        current_time = time.time()
        xSeT.active_threads = [t for t in xSeT.active_threads
                              if t['thread'].is_alive() and
                              current_time - t['start_time'] < xSeT.thread_timeout]

    def ConnEcT_SerVer_OnLiNe(xSeT, Token, tok, host, port, key, iv, host2, port2):
        xSeT.key = key
        xSeT.iv = iv
        while True:
            try:
                xSeT.CliEnts2 = socket.create_connection((host2, int(port2)))
                xSeT.CliEnts2.send(bytes.fromhex(tok))
                while True:
                    try:
                        xSeT.DaTa2 = xSeT.CliEnts2.recv(99999)
                        if not xSeT.DaTa2:
                            break
                        if len(xSeT.DaTa2.hex()) > 4 and '0500' in xSeT.DaTa2.hex()[0:4] and len(xSeT.DaTa2.hex()) > 30:
                            xSeT.packet = json.loads(DeCode_PackEt(f'08{xSeT.DaTa2.hex().split("08", 1)[1]}'))
                            if '5' in xSeT.packet and 'data' in xSeT.packet['5'] and '7' in xSeT.packet['5']['data'] and 'data' in xSeT.packet['5']['data']['7']:
                                xSeT.AutH = xSeT.packet['5']['data']['7']['data']
                    except:
                        break
            except:
                time.sleep(2)
                continue

    def ConnEcT_SerVer(xSeT, Token, tok, host, port, key, iv, host2, port2):
        xSeT.key = key
        xSeT.iv = iv
        try:
            xSeT.CliEnts = socket.create_connection((host, int(port)))
            xSeT.CliEnts.send(bytes.fromhex(tok))
            xSeT.DaTa = xSeT.CliEnts.recv(1024)
        except:
            time.sleep(2)
            xSeT.ConnEcT_SerVer(Token, tok, host, port, key, iv, host2, port2)
            return
        secondary_thread = threading.Thread(target=xSeT.ConnEcT_SerVer_OnLiNe, args=(Token, tok, host, port, key, iv, host2, port2), daemon=True)
        secondary_thread.start()
        xSeT.Exemple = xMsGFixinG('NoooB')
        while True:
            try:
                xSeT.DaTa = xSeT.CliEnts.recv(1024)
                if len(xSeT.DaTa) == 0:
                    try:
                        xSeT.CliEnts.close()
                        if hasattr(xSeT, 'CliEnts2') and xSeT.CliEnts2:
                            xSeT.CliEnts2.close()
                        xSeT.ConnEcT_SerVer(Token, tok, host, port, key, iv, host2, port2)
                    except:
                        ResTarT_bot()
                xSeT.retry_count = 0
                xSeT.cleanup_threads()
            except:
                xSeT.retry_count += 1
                if xSeT.retry_count >= xSeT.max_retries:
                    return
                try:
                    if xSeT.CliEnts:
                        xSeT.CliEnts.close()
                    if hasattr(xSeT, 'CliEnts2') and xSeT.CliEnts2:
                        xSeT.CliEnts2.close()
                except:
                    pass
                time.sleep(2)
                xSeT.ConnEcT_SerVer(Token, tok, host, port, key, iv, host2, port2)

    def GeT_Key_Iv(xSeT, serialized_data):
        try:
            import Xr
            my_message = Xr.MyMessage()
            my_message.ParseFromString(serialized_data)
            timestamp, key, iv = my_message.field21, my_message.field22, my_message.field23
            timestamp_obj = Timestamp()
            timestamp_obj.FromNanoseconds(timestamp)
            timestamp_seconds = timestamp_obj.seconds
            timestamp_nanos = timestamp_obj.nanos
            combined_timestamp = timestamp_seconds * 1_000_000_000 + timestamp_nanos
            return combined_timestamp, key, iv
        except:
            return None, None, None

    def GuestLogin(xSeT, uid, password):
        url = "https://100067.connect.garena.com/oauth/guest/token/grant"
        headers = {
            "Host": "100067.connect.garena.com",
            "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "close",
        }
        data = {
            "uid": f"{uid}",
            "password": f"{password}",
            "response_type": "token",
            "client_type": "2",
            "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
            "client_id": "100067",
        }
        try:
            xSeT.response = requests.post(url, headers=headers, data=data).json()
            xSeT.Access_ToKen, xSeT.Access_Uid = xSeT.response['access_token'], xSeT.response['open_id']
            time.sleep(0.2)
            return xSeT.MajorLogin(xSeT.Access_ToKen, xSeT.Access_Uid)
        except:
            print('Error ➩ Guest Login!')
            sys.exit()

    def DataLogin(xSeT, JwT_ToKen, PayLoad):
        url = 'https://clientbp.ggpolarbear.com/GetLoginData'
        headers = {
            'Expect': '100-continue',
            'Authorization': f'Bearer {JwT_ToKen}',
            'X-Unity-Version': '2022.3.47f1',
            'X-GA': 'v1 1',
            'ReleaseVersion': 'OB53',
            'Content-Type': 'application/x-www-form-urlencoded',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Host': 'clientbp.ggpolarbear.com',
            'Connection': 'close',
            'Accept-Encoding': 'gzip'}
        try:
            xSeT.Res = requests.post(url, headers=headers, data=PayLoad, verify=False)
            xSeT.DaTa_Pb2 = json.loads(DeCode_PackEt(xSeT.Res.content.hex()))
            address, address2 = xSeT.DaTa_Pb2['32']['data'], xSeT.DaTa_Pb2['14']['data']
            ip, ip2 = address[:len(address) - 6], address2[:len(address2) - 6]
            port, port2 = address[len(address) - 5:], address2[len(address2) - 5:]
            return ip, port, ip2, port2
        except:
            print("Error ➩ Data Login!")
            return None, None

    def MajorLogin(xSeT, Access_ToKen, Access_Uid):
        url = "https://loginbp.ggpolarbear.com/MajorLogin"
        headers = {
            'X-Unity-Version': '2022.3.47f1',
            'ReleaseVersion': 'OB53',
            'Content-Type': 'application/x-www-form-urlencoded',
            'X-GA': 'v1 1',
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Host': 'loginbp.ggpolarbear.com',
            'Connection': 'Keep-Alive',
            'Accept-Encoding': 'gzip'}

        xSeT.dT = b'\x1a\x132025-11-26 01:51:28"\tfree fire(\x01:\x071.123.1B2Android OS 9 / API-28 (PI/rel.cjw.20220518.114133)J\x08HandheldR\x0cMTN/SpacetelZ\x04WIFI`\x80\nh\xd0\x05r\x03240z-x86-64 SSE3 SSE4.1 SSE4.2 AVX AVX2 | 2400 | 4\x80\x01\xe6\x1e\x8a\x01\x0fAdreno (TM) 640\x92\x01\rOpenGL ES 3.2\x9a\x01+Google|625f716f-91a7-495b-9f16-08fe9d3c6533\xa2\x01\x0e176.28.139.185\xaa\x01\x02ar\xb2\x01 4306245793de86da425a52caadf21eed\xba\x01\x014\xc2\x01\x08Handheld\xca\x01\rOnePlus A5010\xea\x01@c69ae208fad72738b674b2847b50a3a1dfa25d1a19fae745fc76ac4a0e414c94\xf0\x01\x01\xca\x02\x0cMTN/Spacetel\xd2\x02\x04WIFI\xca\x03 1ac4b80ecf0478a44203bf8fac6120f5\xe0\x03\xb5\xee\x02\xe8\x03\x9a\x80\x02\xf0\x03\xaf\x13\xf8\x03\x84\x07\x80\x04\xa7\x8f\x02\x88\x04\xb5\xee\x02\x90\x04\xa7\x8f\x02\x98\x04\xb5\xee\x02\xb0\x04\x04\xc8\x04\x01\xd2\x04=/data/app/com.dts.freefireth-fpXCSphIV6dKC7jL-WOyRA==/lib/arm\xe0\x04\x01\xea\x04_e62ab9354d8fb5fb081db338acb33491|/data/app/com.dts.freefireth-fpXCSphIV6dKC7jL-WOyRA==/base.apk\xf0\x04\x06\xf8\x04\x01\x8a\x05\x0232\x9a\x05\n2019119026\xa8\x05\x03\xb2\x05\tOpenGLES2\xb8\x05\xff\x01\xc0\x05\x04\xe0\x05\xbe~\xea\x05\t3rd_party\xf2\x05pKqsHT8W93GdcG3ZozENfFwVHtm7qq1eRUNaIDNgRobozIBtLOiYCc4Y6zvvpcICxzQF2sOE4cbytwLs4xZbRnpRMpmWRQKmeO5vcs8nQYBhwqH7K\xf8\x05\xe7\xe4\x06\x88\x06\x01\x90\x06\x01\x9a\x06\x014\xa2\x06\x014\xb2\x06"\x13R\x11FP\x0eY\x03IQ\x0eF\t\x00\x11XC9_\x00[Q\x0fh[V\na\x07Wm\x0f\x03f'

        xSeT.dT = xSeT.dT.replace(b'2026-01-14 12:19:02', str(datetime.now())[:-7].encode())
        xSeT.dT = xSeT.dT.replace(b'4306245793de86da425a52caadf21eed', Access_Uid.encode())
        xSeT.dT = xSeT.dT.replace(b'c69ae208fad72738b674b2847b50a3a1dfa25d1a19fae745fc76ac4a0e414c94', Access_ToKen.encode())

        xSeT.PaYload = bytes.fromhex(EnC_AEs(xSeT.dT.hex()))
        xSeT.ResPonse = requests.post(url, headers=headers, data=xSeT.PaYload, verify=False)
        if xSeT.ResPonse.status_code == 200 and len(xSeT.ResPonse.text) > 10:
            xSeT.DaTa_Pb2 = json.loads(DeCode_PackEt(xSeT.ResPonse.content.hex()))
            xSeT.JwT_ToKen = xSeT.DaTa_Pb2['8']['data']
            xSeT.combined_timestamp, xSeT.key, xSeT.iv = xSeT.GeT_Key_Iv(xSeT.ResPonse.content)
            ip, port, ip2, port2 = xSeT.DataLogin(xSeT.JwT_ToKen, xSeT.PaYload)
            return xSeT.JwT_ToKen, xSeT.key, xSeT.iv, xSeT.combined_timestamp, ip, port, ip2, port2
        else:
            print(f"Error MajorLogin: Status Code {xSeT.ResPonse.status_code}")
            sys.exit()

    def GeNToKeNLogin(xSeT):
        token, key, iv, Timestamp, ip, port, ip2, port2 = xSeT.GuestLogin(xSeT.id, xSeT.password)
        xSeT.JwT_ToKen = token
        try:
            xSeT.AfTer_DeC_JwT = jwt.decode(token, options={"verify_signature": False})
            xSeT.AccounT_Uid = xSeT.AfTer_DeC_JwT.get('account_id')
            xSeT.EncoDed_AccounT = hex(xSeT.AccounT_Uid)[2:]
            xSeT.HeX_VaLue = DecodE_HeX(Timestamp)
            xSeT.TimE_HEx = xSeT.HeX_VaLue
            xSeT.JwT_ToKen_ = token.encode().hex()
        except:
            print(f"Error ➩ Get Token Login!")
            return
        try:
            xSeT.Header = hex(len(EnC_PacKeT(xSeT.JwT_ToKen_, key, iv)) // 2)[2:]
            length = len(xSeT.EncoDed_AccounT)
            xSeT.__ = '00000000'
            if length == 9: xSeT.__ = '0000000'
            elif length == 8: xSeT.__ = '00000000'
            elif length == 10: xSeT.__ = '000000'
            elif length == 7: xSeT.__ = '000000000'
            else:
                print('Unexpected length encountered')
            xSeT.Header = f'0115{xSeT.__}{xSeT.EncoDed_AccounT}{xSeT.TimE_HEx}00000{xSeT.Header}'
            xSeT.FiNal_ToKen_0115 = xSeT.Header + EnC_PacKeT(xSeT.JwT_ToKen_, key, iv)
        except:
            print(f"Error ➩ in Final Token!")
        xSeT.AutH_ToKen = xSeT.FiNal_ToKen_0115
        xSeT.ConnEcT_SerVer(xSeT.JwT_ToKen, xSeT.AutH_ToKen, ip, port, key, iv, ip2, port2)
        return xSeT.AutH_ToKen, key, iv

def GeTSQDaTa(dT):
    try:
        if '5' in dT and 'data' in dT['5']:
            data_field = dT['5']['data']
            OwNer_UiD = data_field.get('1', {}).get('data') if '1' in data_field else None
            SQuAD_CoDe = data_field.get('31', {}).get('data') if '31' in data_field else None
            ChaT_CoDe = data_field.get('17', {}).get('data') if '17' in data_field else None
            if not ChaT_CoDe and '14' in data_field:
                ChaT_CoDe = data_field['14'].get('data')
            return OwNer_UiD, SQuAD_CoDe, ChaT_CoDe
        return None, None, None
    except:
        return None, None, None

def ChEck_TeamCode(team_code):
    if team_code and len(team_code) >= 4:
        return True
    return False

# ========== حسابات Free Fire ==========
xA = [
    {'id': '4791536266', 'password': 'xsa9r-KKKRWSBVTxsa9r'},
    {'id': '4791536267', 'password': 'xsa9r-0GOSJPD44xsa9r'},
    {'id': '4791537527', 'password': 'xsa9r-YVZEY08EJxsa9r'},
    {'id': '4791537921', 'password': 'xsa9r-BML4GB9E3xsa9r'},
    {'id': '4791541116', 'password': 'xsa9r-4UGZUXWKUxsa9r'},
    {'id': '4791541236', 'password': 'xsa9r-BVNTXKNQ2xsa9r'},
    {'id': '4791541741', 'password': 'xsa9r-HSYTXLQGTxsa9r'},
    {'id': '4791541817', 'password': 'xsa9r-T0LPDCWOTxsa9r'},
    {'id': '4791542328', 'password': 'xsa9r-0RRESGS5Nxsa9r'},
]

def STaRT_AccoUnT(account):
    try:
        xCLF(account['id'], account['password'])
    except Exception as e:
        print(f"Error ➩ Starting Account {account['id']}: {e}")
        time.sleep(10)
        STaRT_AccoUnT(account)

def StarT_SerVer():
    time.sleep(1)
    threads = []
    for account in xA:
        thread = threading.Thread(target=STaRT_AccoUnT, args=(account,))
        thread.daemon = True
        threads.append(thread)
        thread.start()
        time.sleep(3)
    for thread in threads:
        thread.join()

def MeMoRy_CmD():
    while True:
        memory_usage = psutil.Process().memory_percent()
        if memory_usage > 80:
            print(f"High memory usage detected ({memory_usage}%). Restarting...")
            ResTarT_bot()
        time.sleep(60)

memory_thread = threading.Thread(target=MeMoRy_CmD, daemon=True)
memory_thread.start()
# ========== متغيرات البوت ==========
bot = None
users = {}
group_activations = {}
maintenance_mode = False
JWT_TOKEN = None
authorized_sessions = {}

active_bots = {}
SHARED_ACTIVE_SPAM_TARGETS = {}
SHARED_ACTIVE_SPAM_LOCK = threading.Lock()

def get_player_info(uid):
    try:
        res = requests.get(f"https://rizerxinfo1234.vercel.app/player-info?uid={uid}", timeout=10)
        data = res.json()
        info = data["basicInfo"]
        name = info["nickname"]
        region = info["region"]
        level = info["level"]
        return name, region, level
    except Exception as e:
        print(f"⚠️ Error fetching info for {uid}: {e}")
        return "غير معروف", "N/A", "N/A"

def send_message_to_all_groups(message_text):
    for chat_id in list(group_activations.keys()):
        try:
            if bot:
                bot.send_message(chat_id, message_text, parse_mode="Markdown")
                time.sleep(0.5)
        except telebot.apihelper.ApiTelegramException as e:
            error_text = str(e).lower()
            if "chat not found" in error_text or "kicked" in error_text or "bot was blocked" in error_text:
                print(f"⚠️ حذف مجموعة/شات غير متاح: {chat_id}")
                if chat_id in group_activations:
                    del group_activations[chat_id]
                save_groups()
            else:
                print(f"⚠️ خطأ API مع {chat_id}: {e}")
        except Exception as e:
            print(f"❌ خطأ غير متوقع عند الإرسال لـ {chat_id}: {e}")

def get_random_accounts(count=1):
    with connected_clients_lock:
        if not connected_clients:
            return []
        available_clients = list(connected_clients.values())
        if count >= len(available_clients):
            return available_clients
        return random.sample(available_clients, count)

def infinite_spam_worker(target_id):
    while True:
        with SHARED_ACTIVE_SPAM_LOCK:
            if target_id not in SHARED_ACTIVE_SPAM_TARGETS:
                break
        try:
            with connected_clients_lock:
                for client in connected_clients.values():
                    try:
                        if hasattr(client, 'CliEnts2') and client.CliEnts2 and hasattr(client, 'key') and client.key:
                            for i in range(30):
                                client.CliEnts2.send(SEnd_InV(1, target_id, client.key, client.iv))
                                client.CliEnts2.send(OpEnSq(client.key, client.iv))
                                client.CliEnts2.send(SPamSq(target_id, client.key, client.iv))
                    except:
                        pass
            time.sleep(0.05)
        except:
            time.sleep(0.05)

def generate_random_color():
    color_list = [
        "[00FF00][b][c]", "[FFDD00][b][c]", "[3813F3][b][c]", "[FF0000][b][c]",
        "[0000FF][b][c]", "[FFA500][b][c]", "[DF07F8][b][c]", "[11EAFD][b][c]",
        "[DCE775][b][c]", "[A8E6CF][b][c]", "[7CB342][b][c]"
    ]
    return random.choice(color_list)

# ========== وظائف التوافق ==========
def safe_story_de_json(obj):
    try:
        return telebot.types.Story(**{k: v for k, v in obj.items() if k != "chat"})
    except Exception:
        return None

telebot.types.Story.de_json = staticmethod(safe_story_de_json)

# ========== جميع أوامر البوت ==========
#تم التعديل - الدالة الرئيسية المعدلة
def register_bot_handlers(bot_instance):
    global bot, ADMIN_IDS, PaSs
    bot = bot_instance
    
    # جلب البيانات من users.json
    #تم التعديل - جلب البيانات الجديدة
    owner_name = get_owner_name()
    owner_id = get_owner_id()
    admin_password = get_admin_password()
    
    # تحديث ADMIN_IDS من owner_id
    #تم التعديل - تحديث ADMIN_IDS
    if owner_id and str(owner_id).isdigit():
        ADMIN_IDS = [int(owner_id)]
    
    # تحديث PaSs من admin_password
    #تم التعديل - تحديث PaSs
    PaSs = admin_password

    # ===== دوال المساعدين (المعدلة) =====
    #تم التعديل - دوال is_admin و is_allowed_group معدلة
    def is_admin(message):
        user_id = message.from_user.id if hasattr(message, 'from_user') else message
        return str(user_id) == str(owner_id) if owner_id else False

    def is_allowed_group(message):
        chat_id_str = str(message.chat.id)
        if chat_id_str in group_activations:
            expiry_timestamp = group_activations[chat_id_str]
            if expiry_timestamp > time.time():
                return True
            else:
                del group_activations[chat_id_str]
                save_groups()
                bot_instance.send_message(message.chat.id, f"⚠️ انتهت صلاحية البوت في هذه المجموعة.\nيرجى التواصل مع {owner_name} لإعادة التفعيل.", parse_mode="Markdown")
                return False
        else:
            bot_instance.send_message(message.chat.id, f"⚠️ البوت غير مفعل في هذه المجموعة.\nيرجى التواصل مع {owner_name} ليقوم بتفعيل البوت.", parse_mode="Markdown")
            return False

    @bot_instance.message_handler(func=lambda message: message.chat.type == 'private' and not is_admin(message))
    def handle_private_non_admin(message):
        bot_instance.send_message(message.chat.id, " للأسف لا يشتغل هنا تواصل معي t.me/otman_v2")

    @bot_instance.message_handler(commands=['start', 'help'])
    def handle_general_commands(message):
        if message.chat.type == 'private' and not is_admin(message):
            return
        if message.text.startswith('/start'):
            welcome_text = """ㅤㅤㅤㅤ
◑══ㅤ 𝙊𝙩𝙝𝙢𝙖𝙣𝙚 𝘽𝙤𝙏   ══◐

𝙒𝙚𝙡𝙘𝙤𝙢𝙚 𝙏𝙤 𝙏𝙝𝙚 𝙎𝙮𝙨𝙩𝙚𝙢 

𝙎𝙃𝙊𝙒 𝘾𝙊𝙈𝙈𝘼𝙉𝘿𝙎 :
/start  ◌  /help

𝙎𝙩𝙖𝙩𝙪𝙨 : 𝘼𝙘𝙩𝙞𝙫𝙚  🟢

𝘽𝙤𝙏 : 𝙊𝙣𝙡𝙞𝙣𝙚  🟢

Dev by : t.me/otman_v2  
    """
            bot_instance.send_message(message.chat.id, welcome_text)
        elif message.text.startswith('/help'):
            help_text = """  
𝗪𝗲𝗹𝗰𝗼𝗺𝗲 𝗧𝗼 𝗢𝘁𝗵𝗺𝗮𝗻𝗲 𝗕𝗼𝗧 

/DEV             - 𝖣𝖾𝗏𝗅𝗈𝗉𝖾𝗋 𝖨𝗇𝖿𝗈

/3 𝗂𝖽           - 𝖲𝖾𝗇𝖽 𝗌𝗊𝗎𝖺𝖽 3
/4 𝗂𝖽           - 𝖲𝖾𝗇𝖽 𝗌𝗊𝗎𝖺𝖽 4
/5 𝗂𝖽           - 𝖲𝖾𝗇𝖽 𝗌𝗊𝗎𝖺𝖽 5
/6 𝗂𝖽           - 𝖲𝖾𝗇𝖽 𝗌𝗊𝗎𝖺𝖽 6
/info 𝗂𝖽        - 𝖺𝖼𝖼𝗈𝗎𝗇𝗍 𝗂𝗇𝖿𝗈
/spam 𝗂𝖽        - 𝖥𝗋𝗂𝖾𝗇𝖽 𝖲𝗉𝖺𝗆
/ghost TC      - 𝖲𝖾𝗇𝖽 𝗀𝗁𝗈𝗌𝗍𝗌
/check 𝗂𝖽       - 𝖡𝖺𝗇 check
/wish 𝗂𝖽        - 𝖦𝖾𝗍 𝗐𝗂𝗌𝗁 𝗅𝗂𝗌𝗍
/evo             - 𝖣𝖺𝗇𝖼𝖾/𝖾𝗏𝗈
/dance & /emote  - Dance
++ 𝗂𝖽          - 𝗌𝗉𝖺𝗆 𝖺𝗇𝗒𝗈𝗇𝖾
-- 𝗂𝖽            - stop spam
/status 𝗂𝖽      - 𝖠𝖼𝖼𝗈𝗎𝗇𝗍 𝖲𝗍𝖺𝗍𝗎𝗌
/level 𝗂𝖽       - 𝖠𝖼𝖼𝗈𝗎𝗇𝗍 l𝖾𝗏𝖾𝗅 𝗂𝗇𝖿𝗈
/bnr 𝗂𝖽         - 𝖦𝖾𝗍 𝖻𝖺𝗇𝗇𝖾𝗋
/ban access      - 𝖡𝖺𝗇 𝖻𝗒 𝖺𝖼𝖼𝖾𝗌𝗌
/geban           - 𝖦𝗎𝖾𝗌𝗍 𝖻𝖺𝗇
/gen             - Generate 𝖺𝖼𝖼𝗈𝗎𝗇𝗍𝗌 𝗀𝗎𝖾𝗌𝗍
/clan            - 𝖢𝗅𝖺𝗇 𝗂𝗇𝖿𝗈
/spm 𝗂𝖽         - 𝖩𝗈𝗂𝗇 𝗌𝗉𝖺𝗆
/stp 𝗂𝖽         - 𝖲𝗍𝗈𝗉 𝗌𝗉𝖺𝗆
/ser name        - 𝖲𝖾𝖺𝗋𝖼𝗁 𝖻𝗒 𝗇𝖺𝗆𝖾
/𝖬𝖲𝖦  𝖳𝖢         - Send message with team code
/add 𝗂𝖽 server    - Friend bot
/remove 𝗂𝖽      - Remove bot
     
 Dev by : t.me/otman_v2
"""
            markup = types.InlineKeyboardMarkup()
            btn_close = types.InlineKeyboardButton("Close", callback_data="close_help")
            btn_next = types.InlineKeyboardButton("Next ", callback_data="next_page")
            markup.add(btn_close, btn_next)
            bot_instance.send_message(message.chat.id, help_text, reply_markup=markup)

    @bot_instance.callback_query_handler(func=lambda call: call.data in ["next_page", "close_help", "back_to_1"])
    def callback_help(call):
        if call.data == "next_page":
            second_page_text = """  
▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
ㅤㅤㅤㅤ𝗔𝗗𝗠𝗜𝗡ㅤ 𝗖𝗢𝗠𝗠𝗔𝗡𝗗𝗦
▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬▬
📊 𝗠𝗔𝗡𝗔𝗚𝗘𝗠𝗘𝗡𝗧:
/list
    ➝ عرض قائمة المضافين
/remove_all
    ➝ حذف الجميع
⚙️ 𝗦𝗬𝗦𝗧𝗘𝗠 𝗦𝗘𝗧𝗧𝗜𝗡𝗚𝗦:
/otman [DAYS]
    ➝ تفعيل صلاحية البوت للمجموعة
/stop
    ➝ إيقاف العمل داخل المجموعة
/maintenance
    ➝ إغلاق النظام (وضع الصيانة) 🛠
/unmaintenance
    ➝ تشغيل النظام وإلغاء الصيانة ✅
🛰 𝗥𝗘𝗠𝗢𝗧𝗘 𝗔𝗖𝗧𝗜𝗢𝗡𝗦:
/leave_group [ID]
    ➝ مغادرة البوت من المجموعة
     
             Dev by : @otman_v2
"""
            markup = types.InlineKeyboardMarkup()
            btn_back = types.InlineKeyboardButton("Back", callback_data="back_to_1")
            btn_close = types.InlineKeyboardButton("Close", callback_data="close_help")
            markup.add(btn_back, btn_close)
            bot_instance.edit_message_text(
                second_page_text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup
            )
        elif call.data == "back_to_1":
            first_page_text = """The commands is running :
/info - 𝖠𝖼𝖼𝗈𝗎𝗇𝗍 𝗂𝗇𝖿𝗈
/check - 𝖡𝖺𝗇 𝖼𝗁𝖾𝖼𝗄
/ghost TC - Sending Ghosts
/gen - 𝖦𝖾𝗇𝖾𝗋𝖺𝗍𝖾 𝖺𝖼𝖼𝗈𝗎𝗇𝗍𝗌 𝗀𝗎𝖾𝗌𝗍
/clan - 𝖢𝗅𝖺𝗇 𝗂𝗇𝖿𝗈
/MSG TC  - 𝖲𝖾𝗇𝖽 𝗆𝖾𝗌𝗌𝖺𝗀𝖾 𝗐𝗂𝗍𝗁 𝗍𝖾𝖺𝗆 𝖼𝗈𝖽𝖾
/add id - 𝖥𝗋𝗂𝖾𝗇𝖽 b𝗈𝗍

𝖠𝗇𝖽 wi𝗅l 𝖻𝖾 𝖺𝖽𝖽𝖾𝖽 𝗌𝗈𝗈𝗇:
/3 /4 /5 /6 squad commands
/wish /evo /dance ++ --
"""
            markup = types.InlineKeyboardMarkup()
            btn_close = types.InlineKeyboardButton("Close", callback_data="close_help")
            btn_next = types.InlineKeyboardButton("Next", callback_data="next_page")
            markup.add(btn_close, btn_next)
            bot_instance.edit_message_text(
                first_page_text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=markup
            )
        elif call.data == "close_help":
            try:
                bot_instance.delete_message(call.message.chat.id, call.message.message_id)
            except Exception as e:
                print(f"Delete message error: {e}")

    @bot_instance.message_handler(commands=['maintenance'])
    def enable_maintenance_mode(message):
        if not is_admin(message):
            bot_instance.send_message(message.chat.id, "⚠️ **Access Denied**\n\n👨🏻‍💻 **Authority:** Othmane\n🔒 **Permission:** Restricted", parse_mode="Markdown")
            return
        global maintenance_mode
        if maintenance_mode:
            bot_instance.send_message(message.chat.id, "⚠️ **Maintenance Status**\n\n🛡️ **Status:** Already Offline\n📝 **Details:** Maintenance is Currently Active", parse_mode="Markdown")
            return
        maintenance_mode = True
        save_maintenance_status(True)
        maintenance_message = (
            "⚙️ **SERVER CURRENTLY UNAVAILABLE** ⚙️\n\n"
            "⚠️ **STATUS:** Connection Interrupted\n"
            "📢 **DETAILS:** System Optimization in Progress\n"
            "⏳ **EXPECTED:** Restoring Services Soon\n\n"
            "*TThank You For Your Patience"
        )
        bot_instance.send_message(message.chat.id, "✅ **Maintenance Enabled**\n\n📡 **Action:** Alerting All Systems\n🛡️ **State:** Lockdown Active", parse_mode="Markdown")
        send_message_to_all_groups(maintenance_message)

    @bot_instance.message_handler(commands=['unmaintenance'])
    def disable_maintenance_mode(message):
        if not is_admin(message):
            bot_instance.send_message(message.chat.id, "⚠️ **Access Denied**\n\n👨🏻‍💻 **Authority:** Othmane\n🔒 **Permission:** Restricted", parse_mode="Markdown")
            return
        global maintenance_mode
        if not maintenance_mode:
            bot_instance.send_message(message.chat.id, "⚠️ **Maintenance Status**\n\n🛡️ **Status:** Already Operational\n📝 **Info:** Maintenance Mode is Not Active", parse_mode="Markdown")
            return
        maintenance_mode = False
        save_maintenance_status(False)
        unmaintenance_message = (
            "🎊 **System Online** 🎊\n\n"
            "🚀 **All Services Restored**\n"
            "✨ **Status:** Fully Operational\n"
            "✅ **Info:** Issues Resolved Successfully\n\n"
            "❤ *Thanks For Staying With Us*"
        )
        bot_instance.send_message(message.chat.id, "✅ **Maintenance Lifted**\n\n📢 **Action:** Notifying All Groups\n⚙️ **System:** Back To Normal", parse_mode="Markdown")
        send_message_to_all_groups(unmaintenance_message)

    @bot_instance.message_handler(commands=['add'])
    def add_user(message):
        chat_id = message.chat.id
        if message.chat.type == 'private' and not is_admin(message):
            return
        elif message.chat.type != 'private' and not is_allowed_group(message):
            return
        if maintenance_mode and not is_admin(message):
            bot_instance.send_message(chat_id, "⚙️ البوت في وضع الصيانة حالياً.")
            return
        current_count = get_total_users_count()
        if current_count >= 100:
            bot_instance.send_message(chat_id, "❌ وصل البوت للحد الأقصى من الإضافات.")
            return
        parts = message.text.split()
        if len(parts) < 2:
            bot_instance.send_message(chat_id, "❌ Usage: /add [id] [server]\nمثال: `/add 12345678 me`", parse_mode="Markdown")
            return
        uid = parts[1]
        server_name = parts[2] if len(parts) > 2 else "me"
        if not uid.isdigit():
            bot_instance.send_message(chat_id, "❌ يجب أن يكون الأيدي أرقام فقط.")
            return
        msg = bot_instance.send_message(chat_id, "<b>Please wait...</b>", parse_mode="HTML")
        try:
            res = requests.get(f"https://xza-get-region.vercel.app/region?uid={uid}", timeout=20)
            res.raise_for_status()
            data = res.json()
            if data.get("status") == "success":
                info = data.get("account_info", {})
                name = info.get('nickname', 'unknown')
                level = info.get('level', 'unknown')
                region = info.get('region', 'unknown')
                days = 1
                users[uid] = {
                    "name": name,
                    "expiry": time.time() + (days * 86400),
                    "added_by_tele_username": message.from_user.username or "unknown"
                }
                save_users()
                final_text = f"""
REQUEST SENT SUCCESSFULLY ✅

------------------------

Name: {name}

Level: {level}

Region: {region}

Uid: {uid}

Server: {server_name}

By: @{message.from_user.username or "unknown"}
------------------------
Remaining: 1
CREDIT : <a href='https://t.me/otman_v2'>𝙅𝙤𝙏 𝙊𝙩𝙝𝙢𝙖𝙣𝙚</a>
"""
                try:
                    bot_instance.edit_message_text(final_text, chat_id=chat_id, message_id=msg.message_id, parse_mode="HTML", disable_web_page_preview=True)
                except:
                    bot_instance.send_message(chat_id, final_text, parse_mode="HTML", disable_web_page_preview=True)
            else:
                bot_instance.edit_message_text("❌ لم يتم العثور على معلومات هذا الأيدي.", chat_id=chat_id, message_id=msg.message_id)
        except Exception as e:
            print(f"Error: {e}")
            try:
                bot_instance.edit_message_text(f"❌ Error: {str(e)}", chat_id=chat_id, message_id=msg.message_id)
            except:
                bot_instance.send_message(chat_id, f"❌ Error: {str(e)}")

    @bot_instance.message_handler(commands=['remove'])
    def remove_user(message):
        if message.chat.type == 'private' and not is_admin(message):
            return
        if message.chat.type != 'private' and not is_allowed_group(message):
            return
        if maintenance_mode and not is_admin(message):
            bot_instance.send_message(message, "⚙️ البوت في وضع الصيانة حالياً.\nسوف يتم إعادته بعد الانتهاء من الصيانة.\nيرجى الإنتظار.", parse_mode="Markdown")
            return
        try:
            parts = message.text.split()
            if len(parts) != 2:
                bot_instance.send_message(message, "❌ Usage:\n/remove <id>")
                return
            uid_to_remove = parts[1]
            user_tele_id = str(message.from_user.id)
            if uid_to_remove in users:
                if not is_admin(message) and users[uid_to_remove].get("added_by_tele_id") != user_tele_id:
                    bot_instance.send_message(message, "❌ غير مسموح لك بحذف هذا الأيدي. فقط الشخص الذي أضافه أو المطور.")
                    return
                name = users[uid_to_remove]['name']
                response = remove_friend(uid_to_remove)
                if "✅ تم الحذف بنجاح" in response:
                    del users[uid_to_remove]
                    save_users()
                    bot_instance.send_message(message, f"""الرد من السيرفر : ✅ نجح حذف الاعب  
👤 الاسم: {name}""")
                else:
                    bot_instance.send_message(message, f"""الرد من السيرفر : ❌ خطأ اثناء حذف الاعب  
👤 الاسم: {name}  
📩 الخطأ: {response}  
⚠️ اللاعب ما زال في القائمة حاول مرة أخرى.""")
            else:
                bot_instance.send_message(message, "❌ عذرا هذا الأيدي غير موجود في قائمة الأيديات.")
        except Exception as e:
            print(f"[REMOVE_ERROR] {e}")
            bot_instance.send_message(message, "❌ حدث خطأ تأكد من كتابة الأمر بشكل صحيح.")

    @bot_instance.message_handler(commands=['remove_all'])
    def remove_all_users(message):
        if not is_admin(message):
            bot_instance.send_message(message.chat.id, "⚠️ هذا الأمر مخصص فقط للمطور.")
            return
        if not users:
            bot_instance.send_message(message.chat.id, "📭 لا يوجد لاعبين.")
            return
        removed = []
        failed = []
        uids_to_remove = []
        for uid, data in users.items():
            if isinstance(data, dict) and "name" in data:
                uids_to_remove.append(uid)
        for uid in uids_to_remove:
            try:
                name = users[uid].get("name", "Unknown")
                response = remove_friend(uid)
                if "✅ تم الحذف بنجاح" in response:
                    del users[uid]
                    removed.append(f"👤 {name} | 🆔 {uid} ☞ Deleted ✅")
                else:
                    failed.append(f"👤 {name} | 🆔 {uid} ☞ Failed ❌: {response}")
                time.sleep(1)
            except Exception as e:
                failed.append(f"🆔 {uid} ☞ Error ❌: {str(e)}")
        save_users()
        reply_text = "📊 تقرير الحذف:\n\n"
        if removed:
            reply_text += f"deleted ✅ {len(removed)} Player:\n" + "\n".join(removed) + "\n\n"
        if failed:
            reply_text += f"Failed ❌ {len(failed)} Player:\n" + "\n".join(failed)
        if len(reply_text) > 4000:
            for i in range(0, len(reply_text), 4000):
                try:
                    bot_instance.send_message(message.chat.id, reply_text[i:i + 4000])
                except Exception as e:
                    print(f"Send Error: {e}")
        else:
            try:
                bot_instance.send_message(message.chat.id, reply_text)
            except Exception as e:
                print(f"Final Send Error: {e}")

    @bot_instance.message_handler(commands=['list'])
    def list_users(message):
        if message.chat.type != 'private' or not is_admin(message):
            bot_instance.send_message(message.chat.id, "⚠️ هذا الامر يخص المطور فقط.")
            return
        if maintenance_mode and not is_admin(message):
            bot_instance.send_message(message.chat.id, "⚙️ البوت في وضع الصيانة حالياً.\nسوف يتم إعادته بعد الانتهاء من الصيانة.\nيرجى الإنتظار.", parse_mode="Markdown")
            return
        if not users:
            bot_instance.send_message(message.chat.id, "📌 لا يوجد أي لاعبين بعد في القائمة !")
            return
        game_friends = {}
        for uid, data in users.items():
            if isinstance(data, dict) and "name" in data and "expiry" in data:
                game_friends[uid] = data
        if not game_friends:
            bot_instance.send_message(message.chat.id, "📌 لا يوجد أي لاعبين بعد في القائمة !")
            return
        total_count = get_total_users_count()
        text = f"📋 Ho Add ({total_count}/100):\n\n"
        for uid, data in game_friends.items():
            try:
                name = html.unescape(data.get("name", "Unknown"))
                remaining = format_remaining_time(data.get("expiry"))
                added_by = data.get("added_by_tele_id", "غير معروف")
                added_username = data.get("added_by_tele_username", "بدون معرف")
                added_date = data.get("added_date", "غير معروف")
                text += (
                    f"👤 {name}\n"
                    f"🆔 {uid}\n"
                    f"⏳ {remaining}\n"
                    f"👤 By: {added_by} (@{added_username})\n"
                    f"📅 Time Add: {added_date}\n"
                    f"───────────────────\n"
                )
            except Exception as e:
                print(f"List Error: {e}")
                continue
        if len(text) > 4000:
            chunks = [text[i:i+4000] for i in range(0, len(text), 4000)]
            for chunk in chunks:
                try:
                    bot_instance.send_message(message.chat.id, chunk)
                    time.sleep(1)
                except Exception as e:
                    print(f"Send Chunk Error: {e}")
        else:
            try:
                bot_instance.send_message(message.chat.id, text)
            except Exception as e:
                print(f"Final Send Error: {e}")

    @bot_instance.message_handler(commands=['DEV'])
    def dev_command(message):
        try:
            caption = (
                "ㅤㅤㅤㅤ𝘿𝙚𝙫 : 𝙊𝙏𝙈𝘼𝙉ㅤㅤㅤㅤ\n\n"
                "<a href='https://t.me/otman_team'>𝗢𝘁𝗵𝗺𝗮𝗻𝗲 ㅤ𖥞 ㅤ𝗚𝗿𝗼𝘂𝗽</a>\n\n"
                "<a href='https://t.me/othmane8'>𝗢𝘁𝗵𝗺𝗮𝗻𝗲 ㅤㅤ𖥞ㅤㅤ 𝗕𝗮𝗰𝗸</a>\n\n"
                "<a href='https://t.me/otman_v2'>𝙅𝙤𝙏 𝙊𝙩𝙝𝙢𝙖𝙣𝙚</a>\n\n"
            )
            bot_instance.send_message(message.chat.id, caption, parse_mode='HTML', disable_web_page_preview=False)
        except Exception as e:
            bot_instance.send_message(message, f"❌ حدث خطأ: {e}")

    @bot_instance.message_handler(commands=['otman'])
    def activate_group(message):
        if not is_admin(message):
            bot_instance.send_message(message, "⚠️ **Access Denied**\n\n👑 **Authority:** Othmane\n🔒 **Permission:** Restricted", parse_mode="Markdown")
            return
        if message.chat.type == 'private':
            bot_instance.send_message(message, "🚫 **Invalid Location**\n\n📍 **Scope:** Groups only\n📝 **Notice:** Activation Required Inside a group", parse_mode="Markdown")
            return
        if maintenance_mode:
            bot_instance.send_message(message, "⚙️ **System Under Maintenance**\n\n🛠 **Status:** offline\n📢 **info:** Improvements in Progress\n⏳ **Back.**", parse_mode="Markdown")
            return
        try:
            parts = message.text.split()
            if len(parts) != 2:
                bot_instance.send_message(message, "❌ **Invalid Format**\n\n💡 **Usage:** `/otman <days>`\nℹ️ **Example:** `/otman 20`", parse_mode="Markdown")
                return
            days = int(parts[1])
            chat_id = message.chat.id
            expiry_date = datetime.now() + timedelta(days=days)
            group_activations[str(chat_id)] = expiry_date.timestamp()
            save_groups()
            formatted_date = expiry_date.strftime("%Y-%m-%d %H:%M:%S UTC")
            bot_instance.send_message(message, f"✅ **SSuccessfully Activated The BoT**\n\n🛡️ **Status:** Active\n🗓️ **Duration:** {days} Days\n⏳ **Expiry date:** `{formatted_date}`\n\n*System is now Operational*", parse_mode="Markdown")
        except ValueError:
            bot_instance.send_message(message, "❌ **invalid input**\n\n⚠️ **Error:** Days Must be a Number\n🔢 **Format:** Use Integers", parse_mode="Markdown")
        except Exception as e:
            print(f"[SID_ERROR] {e}")
            bot_instance.send_message(message, "🆘 **System Error**\n\n⚙️ **Issue:** Activation Failed\n🛠️ **Action:** Contact Technical Support ", parse_mode="Markdown")

    @bot_instance.message_handler(commands=['stop'])
    def stop_group_activation(message):
        if not is_admin(message):
            bot_instance.send_message(message.chat.id, "⚠️ **Access Denied**\n\n🔒 **Permission:** Restricted \n👑 **Authority:** Othmane\n\n*This Command is Protected*", parse_mode="Markdown")
            return
        if message.chat.type == 'private':
            bot_instance.send_message(message.chat.id, "🚫 **Invalid Location**\n\n📍 **Scope:** Groups Only\n📝 **notice:** This Command Cannot Be Execute in Private Chats\n\n*Please Use This Command Inside a Group*", parse_mode="Markdown")
            return
        if maintenance_mode:
            bot_instance.send_message(message.chat.id, f"⚙️ **System Under Maintenance**\n\n🛠 **Status:** Temporarily Offline\n📢 **Info:** We are Working On Improvements\n⏳ **Back Soon..**\n\n*We Apologize For The Inconvenience*", parse_mode="Markdown")
            return
        chat_id_str = str(message.chat.id)
        if chat_id_str in group_activations:
            del group_activations[chat_id_str]
            save_groups()
            bot_instance.send_message(message.chat.id, "Successfully Stopped The BoT In This Group ✅")
        else:
            bot_instance.send_message(message.chat.id, "⚠️ **Activation Status**\n\n🛡️ **Status:** Already Inactive\n📍 **Location:** This Group\n\n*The Bot is not Running in this Chat*", parse_mode="Markdown")

    @bot_instance.message_handler(commands=['leave_group'])
    def leave_group_command(message):
        if not is_admin(message):
            bot_instance.send_message(message, "⚠️ **Access Denied**\n\n👑 **Authority:** Othmane\n🔒 **Permission:** Restricted", parse_mode="Markdown")
            return
        if message.chat.type != 'private':
            bot_instance.send_message(message, "🚫 **Secure Command**\n\n📍 **Location:** Private Chat Only\n📝 **Notice:** Execute This in Private For Security", parse_mode="Markdown")
            return
        try:
            parts = message.text.split()
            if len(parts) != 2:
                bot_instance.send_message(message, "📝 **Invalid Format**\n\n💡 **Usage:** `/leave_group <GROUP_ID>`\nℹ️ **Example:** `/leave_group -1001541366`", parse_mode="Markdown")
                return
            group_id = parts[1]
            try:
                bot_instance.leave_chat(group_id)
                bot_instance.send_message(message, f"✅ **Successfully Excited**\n\n🛰️ **Target id:** `{group_id}`\n🛡️ **Status:** Removed & Deactivated", parse_mode="Markdown")
                if str(group_id) in group_activations:
                    del group_activations[str(group_id)]
                    save_groups()
            except Exception as e:
                bot_instance.send_message(message, f"❌ **Operation Failed**\n\n⚠️ **Error:** `{e}`\n🔍 **Check:** BoT Permissions Or Group id", parse_mode="Markdown")
        except Exception as e:
            print(f"[LEAVE_GROUP_ERROR] {e}")
            bot_instance.send_message(message, "🆘 **System Error**\n\n⚙️ **Issue:** Unknown Exception\n🛠️ **Action:** Check Logs Immediately", parse_mode="Markdown")

    @bot_instance.message_handler(commands=['ghost'])
    def handle_ghost(message):
        try:
            parts = message.text.split()
            if len(parts) < 3:
                bot_instance.send_message(message.chat.id, "⚠️ **Invalid Format**\n💡 `/ghost <teamcode> <NAME>`", parse_mode="Markdown")
                return
            code, name = parts[1], parts[2]
            msg = bot_instance.send_message(message.chat.id, "<b>Please wait...</b>", parse_mode="HTML")
            response = requests.get(f"{SERVER_URL}/ghost?teamcode={code}&name={name}&api_key={API_KEY}", timeout=10)
            try:
                data = response.json()
            except:
                data = {}
            if response.status_code == 200:
                try:
                    bot_instance.edit_message_text(f"✅ **Ghost Sent**\n👤 **Name:** `{name}`\n🔑 **teamcode:** `{code}`", message.chat.id, msg.message_id, parse_mode="Markdown")
                except:
                    bot_instance.send_message(message.chat.id, "✅ تم الإرسال")
            else:
                try:
                    bot_instance.edit_message_text(f"⚠️ **Api Error:** {data.get('message', 'Failed')}", message.chat.id, msg.message_id)
                except:
                    bot_instance.send_message(message.chat.id, "⚠️ Api Error")
            time.sleep(1)
        except requests.exceptions.Timeout:
            bot_instance.send_message(message.chat.id, "⏱️ **Timeout**\nالسيرفر تأخر في الرد")
        except requests.exceptions.ConnectionError:
            bot_instance.send_message(message.chat.id, "🚫 **Service offline**")
        except Exception as e:
            bot_instance.send_message(message.chat.id, f"❌ Error: {e}")

    @bot_instance.message_handler(commands=['info'])
    def get_player_info(message):
        args = message.text.split()
        if len(args) != 2:
            bot_instance.send_message(message.chat.id, "<b>Usage:</b> /info &lt;UID&gt;", parse_mode="HTML")
            return
        uid = args[1]
        if not uid.isdigit():
            bot_instance.send_message(message.chat.id, "<b>⚠️ uid should be numbers only</b>", parse_mode="HTML")
            return
        msg = bot_instance.send_message(message.chat.id, "<b>Please wait...</b>", parse_mode="HTML")
        try:
            res = requests.get(f"https://otman-info.vercel.app/player-info?uid={uid}", timeout=30)
            res.raise_for_status()
            data = res.json()
        except Exception as e:
            print(f"API Error: {e}")
            try:
                bot_instance.edit_message_text("<b>⚠️ Failed to fetch player info</b>", chat_id=message.chat.id, message_id=msg.message_id, parse_mode="HTML")
            except:
                bot_instance.send_message(message.chat.id, "<b>⚠️ Failed to fetch player info</b>", parse_mode="HTML")
            return
        acc = data.get("AccountInfo", {})
        clan = data.get("GuildInfo", {})
        captain = data.get("captainBasicInfo", {})
        pet = data.get("petInfo", {})
        social = data.get("socialinfo", {})
        credit = data.get("creditScoreInfo", {})
        caption = "<b>"
        caption += "𝗔𝗖𝗖𝗢𝗨𝗡𝗧 𝗜𝗡𝗙𝗢\n\n"
        caption += f"Player : {acc.get('AccountName', 'Unknown')}\n"
        caption += f"UID : {uid}\n"
        caption += f"Region : {acc.get('AccountRegion', 'N/A')}\n"
        caption += f"Level : {acc.get('AccountLevel', 'N/A')} | EXP : {acc.get('AccountEXP', 0)}\n"
        caption += f"Likes : {acc.get('AccountLikes', 0)}\n"
        caption += f"Version : {acc.get('ReleaseVersion', 'N/A')}\n\n"
        caption += "𝗥𝗔𝗡𝗞 𝗜𝗡𝗙𝗢\n"
        caption += f"• BR Rank : {acc.get('BrMaxRank', 'N/A')} | {acc.get('BrRankPoint', 'N/A')} pts\n"
        caption += f"• CS Rank : {acc.get('CsMaxRank', 'N/A')} | {acc.get('CsRankPoint', 'N/A')} pts\n"
        caption += f"• Season : {acc.get('AccountSeasonId', 'N/A')}\n\n"
        if clan.get("GuildID"):
            caption += "𝗖𝗟𝗔𝗡 𝗜𝗡𝗙𝗢\n"
            caption += f"• Name : {clan.get('GuildName', 'N/A')}\n"
            caption += f"• ID : {clan.get('GuildID', 'N/A')}\n"
            caption += f"• Level : {clan.get('GuildLevel', 'N/A')}\n"
            caption += f"• Members : {clan.get('GuildMember', 'N/A')}/{clan.get('GuildCapacity', 'N/A')}\n\n"
        if captain.get("accountId"):
            caption += "𝗟𝗘𝗔𝗗𝗘𝗥 𝗜𝗡𝗙𝗢\n"
            caption += f"• name : {captain.get('nickname', 'N/A')}\n"
            caption += f"• UID : {captain.get('accountId', 'N/A')}\n"
            caption += f"• Level : {captain.get('level', 'N/A')}\n"
            caption += f"• Likes : {captain.get('liked', 0)}\n"
            caption += f"• Region : {captain.get('region', 'N/A')}\n\n"
        if pet:
            caption += "𝗣𝗘𝗧 𝗜𝗡𝗙𝗢\n"
            caption += f"• Pet ID : {pet.get('id', 'N/A')}\n"
            caption += f"• Level : {pet.get('level', 'N/A')}\n"
            caption += f"• EXP : {pet.get('exp', 0)}\n"
            caption += f"• Skill ID : {pet.get('selectedSkillId', 'N/A')}\n\n"
        if credit:
            caption += "𝗖𝗥𝗘𝗗𝗜𝗧 𝗦𝗖𝗢𝗥𝗘\n"
            caption += f"• Score : {credit.get('creditScore', 'N/A')}\n"
            caption += f"• Reward : {credit.get('rewardState', 'N/A')}\n\n"
        if social:
            caption += "𝗦𝗢𝗖𝗜𝗔𝗟 𝗜𝗡𝗙𝗢\n"
            caption += f"• Gender : {social.get('gender', 'N/A')}\n"
            caption += f"• Language : {social.get('language', 'N/A')}\n"
            caption += f"• Signature : {social.get('signature', 'N/A')}\n\n"
        caption += "Dev by : @otman_v2"
        caption += "</b>"
        try:
            img = requests.get(f"https://by-otman-outfit.vercel.app/render?uid={uid}&key=OTMAN-V2", timeout=40)
            if img.status_code == 200 and "image" in img.headers.get("Content-Type", ""):
                bio = BytesIO(img.content)
                bio.name = "outfit.jpg"
                bot_instance.send_photo(message.chat.id, bio, caption=caption, parse_mode="HTML")
            else:
                bot_instance.send_message(message.chat.id, caption, parse_mode="HTML")
        except Exception as e:
            print(f"Image Error: {e}")
            bot_instance.send_message(message.chat.id, caption, parse_mode="HTML")
        try:
            bot_instance.delete_message(message.chat.id, msg.message_id)
        except Exception as e:
            print(f"Delete message error: {e}")

    @bot_instance.message_handler(commands=['gen'])
    def gen_command(message):
        args = message.text.split()
        if len(args) != 4:
            bot_instance.send_message(message.chat.id, "<b>Usage:</b>\n<code>/gen ME othmane 10</code>", parse_mode="HTML")
            return
        region = args[1].upper()
        name = args[2]
        try:
            count = int(args[3])
            if count <= 0:
                raise ValueError
        except ValueError:
            bot_instance.send_message(message.chat.id, "❌ العدد يجب أن يكون رقماً صحيحاً.")
            return
        if count > MAX_ACCOUNTS:
            bot_instance.send_message(message.chat.id, f"❌ Max {MAX_ACCOUNTS} Accounts.")
            return
        msg = bot_instance.send_message(message.chat.id, "<b>Generating accounts, please wait...</b>", parse_mode="HTML")
        try:
            accounts = generate_accounts(region, name, count)
            json_data = json.dumps(accounts, indent=2, ensure_ascii=False)
            file = io.BytesIO(json_data.encode('utf-8'))
            file.name = f"{name}.json"
            caption_text = (
                f"Generation Complete ✅\n\n"
                f"Count: {count}\n"
                f"Region: {region}\n"
                f"By: @{message.from_user.username or 'unknown'}\n\n"
                f"Dev : @otman_v2"
            )
            bot_instance.send_document(message.chat.id, file, caption=caption_text)
            try:
                bot_instance.delete_message(message.chat.id, msg.message_id)
            except:
                pass
        except Exception as e:
            err = str(e).replace('<', '').replace('>', '')
            try:
                bot_instance.edit_message_text(f"❌ خطأ: {err}", message.chat.id, msg.message_id)
            except:
                bot_instance.send_message(message.chat.id, f"❌ خطأ: {err}")

    @bot_instance.message_handler(commands=['check'])
    def check_player_cmd(message):
        args = message.text.split()
        if len(args) < 2:
            return bot_instance.send_message(message, "⚠️ يرجى إدخال الآيدي بعد الأمر.\nمثال: `/check 12345678`", parse_mode="Markdown")
        uid = args[1]
        msg = bot_instance.send_message(message.chat.id, "<b>Please wait...</b>", parse_mode="HTML")
        url = f"https://api-check-band-alinas.vercel.app/check?uid={uid}"
        try:
            res = requests.get(url, timeout=15).json()
            response_msg = (
                f"✅ **{res.get('status')}**\n\n"
                f"🆔 **ID:** `{res.get('player_id')}`\n"
                f"👤 **Name:** {res.get('nickname')}\n"
                f"🌍 **Region:** {res.get('region')}\n"
                f"🛡️ **Status:** {res.get('account_status')}\n"
                f"⏳ **Duration:** {res.get('ban_duration')}\n"
                f"🚫 **Is Banned:** {res.get('is_banned')}\n\n"
                f"👨‍💻 **Dev:** {res.get('credits', {}).get('developer')}\n"
                f"📢 **Channel:** {res.get('credits', {}).get('channel')}"
            )
            bot_instance.edit_message_text(response_msg, message.chat.id, msg.message_id, parse_mode="Markdown", disable_web_page_preview=True)
        except Exception as e:
            bot_instance.edit_message_text("❌ فشل في جلب البيانات من الرابط.", message.chat.id, msg.message_id)

    @bot_instance.message_handler(commands=['id', 'ID'])
    def cmd_id(message):
        user = message.from_user
        chat = message.chat
        txt = []
        name = f"{user.first_name or ''} {user.last_name or ''}".strip()
        txt.append(f"👤 Your  Name: {escape_md(name)}")
        if user.username:
            txt.append(f"🔗 Your  User: @{escape_md(user.username)}")
        txt.append(f"🆔 Your  id: `{user.id}`")
        txt.append(f"💬 Group id: `{chat.id}`")
        if message.reply_to_message and message.reply_to_message.from_user:
            u = message.reply_to_message.from_user
            r_name = f"{u.first_name or ''} {u.last_name or ''}".strip()
            txt.append(f"↩️ بترد على: {escape_md(r_name)}")
            if u.username:
                txt.append(f"🔗 @{escape_md(u.username)}")
            txt.append(f"🆔 `{u.id}`")
        bot_instance.send_message(message, "\n".join(txt), parse_mode="MarkdownV2", disable_web_page_preview=True)

    @bot_instance.message_handler(commands=['MSG'])
    def handle_spam(message):
        if not is_authorized(message):
            bot_instance.send_photo(message.chat.id, AlInAs_Pp, caption="<b>Not Authorized</b>", parse_mode="HTML")
            return
        with connected_clients_lock:
            if not connected_clients:
                bot_instance.send_photo(message.chat.id, AlInAs_Pp, caption="<b>No Connected Accounts</b>\nPlease wait.", parse_mode="HTML")
                return
            first_client = list(connected_clients.values())[0]
        parts = message.text.split(maxsplit=2)
        if len(parts) < 3:
            bot_instance.send_photo(message.chat.id, AlInAs_Pp, caption="<b>❌ Error</b>\nUse: <code>/MSG &lt;teamcode&gt; &lt;message&gt;</code>", parse_mode="HTML")
            return
        teamcode = parts[1]
        msg_text = parts[2]
        msg_wait = bot_instance.send_message(message.chat.id, "<b>Please wait...</b>", parse_mode="HTML")
        try:
            team_data = first_client.GeTinFoSqMsG(teamcode)
        except Exception as e:
            try:
                bot_instance.delete_message(message.chat.id, msg_wait.message_id)
            except:
                pass
            bot_instance.send_photo(message.chat.id, AlInAs_Pp, caption=f"<b>Api Error</b>\n<code>{e}</code>", parse_mode="HTML")
            return
        try:
            bot_instance.delete_message(message.chat.id, msg_wait.message_id)
        except:
            pass
        if not team_data.get("success"):
            bot_instance.send_photo(message.chat.id, AlInAs_Pp, caption=f"<b>Failed</b>\nReason: <code>{team_data.get('reason','Unknown')}</code>", parse_mode="HTML")
            return
        OwNer_UiD = team_data.get("OwNer_UiD")
        ChaT_CoDe = team_data.get("ChaT_CoDe")
        SQuAD_CoDe = team_data.get("SQuAD_CoDe", "")
        info_msg = f"""
<b>Squad Found</b>

<b>Owner Uid</b>
<code>{OwNer_UiD}</code>

<b>Chat Code</b>
<code>{ChaT_CoDe}</code>

<b>Squad Code</b>
<code>{SQuAD_CoDe}</code>

<b>Sending 100 Msgs</b>
"""
        bot_instance.send_photo(message.chat.id, AlInAs_Pp, caption=info_msg, parse_mode="HTML")
        try:
            success = first_client.SeNd_SpaM_MsG(OwNer_UiD, ChaT_CoDe, msg_text, count=100)
        except Exception as e:
            bot_instance.send_photo(message.chat.id, AlInAs_Pp, caption=f"<b>Send Error</b>\n<code>{e}</code>", parse_mode="HTML")
            return
        if success:
            bot_instance.send_photo(message.chat.id, AlInAs_Pp, caption=f"<b>Done</b>\n100 messages sent to <code>{teamcode}</code>", parse_mode="HTML")
        else:
            bot_instance.send_photo(message.chat.id, AlInAs_Pp, caption="<b>Failed To Send Msgs</b>", parse_mode="HTML")

    @bot_instance.message_handler(commands=['clan', 'CLAN'])
    def get_clan_info(message):
        args = message.text.split()
        if len(args) != 2 or not args[1].isdigit():
            text_usage = (
                "<b>Othmaanee</b>\n"
                "<b>Usage:</b>\n"
                "<b>/clan &lt;CLAN_ID&gt;</b>\n\n"
                "<b>Example:</b>\n"
                "<code>/clan 3045136439</code>"
            )
            return bot_instance.send_message(message.chat.id, text_usage, parse_mode="HTML")
        clan_id = args[1]
        url = f"https://api-get-info-clan-by-alinas.vercel.app/get_clan_info?clan_id={clan_id}"
        wait_msg = bot_instance.send_message(message.chat.id, "<b>Please wait...</b>", parse_mode="HTML")
        try:
            res = requests.get(url, timeout=30)
            res.raise_for_status()
            data = res.json()
        except Exception as e:
            try:
                bot_instance.delete_message(message.chat.id, wait_msg.message_id)
            except:
                pass
            bot_instance.send_message(message.chat.id, "<b>Clan service is currently unavailable.</b>", parse_mode="HTML")
            return
        try:
            bot_instance.delete_message(message.chat.id, wait_msg.message_id)
        except:
            pass
        if not isinstance(data, dict) or "error" in data:
            return bot_instance.send_message(message.chat.id, "<b>oTman_here</b>\n<b>Error:</b> Failed to fetch clan information.", parse_mode="HTML")
        clan_name = data.get("clan_name", "Unknown")
        region = data.get("region", "Unknown")
        level = data.get("level", "N/A")
        rank = data.get("rank", "N/A")
        xp = data.get("xp", "N/A")
        energy = data.get("energy", "N/A")
        balance = data.get("balance", "N/A")
        achievements = data.get("achievements", "N/A")
        last_active = data.get("last_active", "N/A")
        welcome_message = data.get("welcome_message", "None")
        guild = data.get("guild_details", {})
        total_members = guild.get("total_members", "N/A")
        members_online = guild.get("members_online", "N/A")
        text = (
            "<b>𝗖𝗟𝗔𝗡 𝗜𝗡𝗙𝗢</b>\n\n"
            f"<b>Clan Name:</b> {clan_name}\n"
            f"<b>Clan ID:</b> {clan_id}\n"
            f"<b>Region:</b> {region}\n"
            f"<b>Level:</b> {level}\n"
            f"<b>Rank:</b> {rank}\n"
            f"<b>Exp:</b> {xp}\n"
            f"<b>Energy:</b> {energy}\n"
            f"<b>Balance:</b> {balance}\n"
            f"<b>Achievements:</b> {achievements}\n"
            f"<b>Total Members:</b> {total_members}\n"
            f"<b>Members Online:</b> {members_online}\n"
            f"<b>Last Active:</b> {last_active}\n\n"
            f"<b>Welcome Message:</b>\n{welcome_message}\n\n"
            "<a href='https://t.me/otman_v2'>𝙅𝙤𝙏 𝙊𝙩𝙝𝙢𝙖𝙣𝙚</a>"
        )
        try:
            bot_instance.send_message(message.chat.id, text, parse_mode="HTML")
        except Exception as e:
            bot_instance.send_message(message.chat.id, "❌ Error displaying clan info.", parse_mode="HTML")

    @bot_instance.message_handler(commands=['sp'])
    def sp_command(message):
        parts = message.text.split()
        if len(parts) < 2:
            bot_instance.reply_to(message, "⚠️ استخدم: /sp [ايدي اللاعب]")
            return
        target = parts[1]
        with SHARED_ACTIVE_SPAM_LOCK:
            if target not in SHARED_ACTIVE_SPAM_TARGETS:
                SHARED_ACTIVE_SPAM_TARGETS[target] = True
                threading.Thread(target=infinite_spam_worker, args=(target,), daemon=True).start()
                bot_instance.reply_to(message, f"✅ بدأ السبام على {target}")
            else:
                bot_instance.reply_to(message, f"⚠️ السبام يعمل بالفعل على {target}")

    @bot_instance.message_handler(commands=['stop'])
    def stop_command(message):
        parts = message.text.split()
        if len(parts) < 2:
            bot_instance.reply_to(message, "⚠️ استخدم: /stop [ايدي اللاعب]")
            return
        target = parts[1]
        with SHARED_ACTIVE_SPAM_LOCK:
            if target in SHARED_ACTIVE_SPAM_TARGETS:
                del SHARED_ACTIVE_SPAM_TARGETS[target]
                bot_instance.reply_to(message, f"🛑 تم إيقاف السبام على {target}")
            else:
                bot_instance.reply_to(message, f"ℹ️ لا يوجد سبام نشط على {target}")
# ========== دوال تشغيل البوتات ==========
def start_bot_for_user(username, token):
    try:
        bot_instance = telebot.TeleBot(token, parse_mode='HTML')
        register_bot_handlers(bot_instance)
        def polling_loop():
            try:
                bot_instance.infinity_polling()
            except Exception as e:
                print(f"[BOT] {username} توقف: {e}")
        thread = threading.Thread(target=polling_loop, daemon=True)
        thread.start()
        active_bots[username] = bot_instance
        print(f"[BOT] ✅ تم تشغيل بوت المستخدم {username}")
        return True
    except Exception as e:
        print(f"[BOT] ❌ فشل تشغيل بوت {username}: {e}")
        return False

def stop_bot_for_user(username):
    if username in active_bots:
        try:
            active_bots[username].stop_polling()
        except:
            pass
        del active_bots[username]
        print(f"[BOT] 🛑 تم إيقاف بوت {username}")

def start_all_bots_from_db():
    db = load_users()
    for u in db.get("users", []):
        username = u.get("username")
        token = u.get("telegram_token", "")
        if token and u.get("active", True):
            start_bot_for_user(username, token)

# ========== واجهات API ==========
@app.route("/")
def home():
    return send_from_directory(BASE_DIR, "index.html")

@app.route("/login")
def login_page():
    return send_from_directory(BASE_DIR, "login.html")

@app.route("/create")
def create_page():
    return send_from_directory(BASE_DIR, "create.html")

@app.route("/admin")
def admin_page():
    return send_from_directory(BASE_DIR, "admin.html")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect("/login")

# ========== API المصادقة ==========
@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    
    if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
        session["user"] = {"username": ADMIN_USERNAME, "is_admin": True, "is_pro": True}
        return jsonify({"success": True, "username": username, "is_master": True, "is_pro": True})
    
    db = load_users()
    u = find_user(db, username)
    if not u:
        return jsonify({"success": False, "error": "بيانات غير صحيحة"}), 401
    if not check_password_hash(u.get("password_hash", ""), password):
        return jsonify({"success": False, "error": "بيانات غير صحيحة"}), 401
    
    session["user"] = {"username": u.get("username"), "is_admin": False, "is_pro": u.get("is_pro", False)}
    return jsonify({"success": True, "username": username, "is_pro": u.get("is_pro", False)})

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json(silent=True) or {}
    username = (data.get("username") or "").strip()
    password = data.get("password") or ""
    key = (data.get("key") or "").strip().upper()
    
    if not username or len(username) < 3:
        return jsonify({"success": False, "error": "يجب أن يكون اسم المستخدم 3 أحرف على الأقل"}), 400
    if not re.fullmatch(r"[A-Za-z0-9_\.]+", username):
        return jsonify({"success": False, "error": "اسم المستخدم يحتوي على أحرف غير مسموحة"}), 400
    if len(password) < 4:
        return jsonify({"success": False, "error": "كلمة السر قصيرة جداً"}), 400
    
    db = load_users()
    if find_user(db, username):
        return jsonify({"success": False, "error": "اسم المستخدم موجود مسبقاً"}), 409
    
    is_pro = False
    expiry_days = 7
    
    if key:
        keys_db = load_pro_keys()
        found_key = None
        for k in keys_db.get("keys", []):
            if k.get("key") == key and not k.get("used", False):
                if datetime.fromisoformat(k.get("expiry")) > datetime.now():
                    found_key = k
                    break
        if found_key:
            is_pro = True
            found_key["used"] = True
            found_key["used_by"] = username
            found_key["used_at"] = datetime.now().isoformat()
            save_pro_keys(keys_db)
            expiry_days = 30
        elif key != "FREE-KEY":
            return jsonify({"success": False, "error": "مفتاح PRO غير صالح"}), 400
    
    new_user = {
        "username": username,
        "password_hash": generate_password_hash(password),
        "active": True,
        "is_pro": is_pro,
        "telegram_token": "",
        "owner_id": "",
        "owner_name": "",
        "expiry_date": (datetime.now() + timedelta(days=expiry_days)).isoformat()
    }
    db["users"].append(new_user)
    save_users(db)
    return jsonify({"success": True})

@app.route("/api/upgrade-to-pro", methods=["POST"])
def upgrade_to_pro():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    code = data.get("code", "").strip().upper()
    
    db = load_users()
    u = find_user(db, username)
    if not u:
        return jsonify({"success": False, "error": "المستخدم غير موجود"}), 404
    
    if u.get("is_pro", False):
        return jsonify({"success": False, "error": "أنت بالفعل في الإصدار PRO"}), 400
    
    keys_db = load_pro_keys()
    found_key = None
    for k in keys_db.get("keys", []):
        if k.get("key") == code and not k.get("used", False):
            if datetime.fromisoformat(k.get("expiry")) > datetime.now():
                found_key = k
                break
    
    if not found_key:
        return jsonify({"success": False, "error": "مفتاح PRO غير صالح"}), 400
    
    found_key["used"] = True
    found_key["used_by"] = username
    found_key["used_at"] = datetime.now().isoformat()
    save_pro_keys(keys_db)
    
    u["is_pro"] = True
    u["expiry_date"] = (datetime.now() + timedelta(days=30)).isoformat()
    save_users(db)
    
    if username in session.get("user", {}):
        session["user"]["is_pro"] = True
    
    return jsonify({"success": True, "message": "🎉 تم الترقية إلى PRO بنجاح!"})

@app.route("/api/generate-pro-key", methods=["POST"])
def generate_pro_key():
    data = request.get_json(silent=True) or {}
    admin_key = data.get("admin_key", "")
    if admin_key != ADMIN_SECRET_CODE:
        return jsonify({"success": False, "error": "غير مصرح"}), 403
    
    key_value = data.get("key")
    expiry_days = data.get("expiry_days", 7)
    
    keys_db = load_pro_keys()
    keys_db["keys"].append({
        "key": key_value,
        "expiry": (datetime.now() + timedelta(days=expiry_days)).isoformat(),
        "created": datetime.now().isoformat(),
        "used": False
    })
    save_pro_keys(keys_db)
    return jsonify({"success": True})

@app.route("/api/delete-pro-key", methods=["POST"])
def delete_pro_key():
    data = request.get_json(silent=True) or {}
    admin_key = data.get("admin_key", "")
    if admin_key != ADMIN_SECRET_CODE:
        return jsonify({"success": False, "error": "غير مصرح"}), 403
    
    key_value = data.get("key")
    keys_db = load_pro_keys()
    keys_db["keys"] = [k for k in keys_db.get("keys", []) if k.get("key") != key_value]
    save_pro_keys(keys_db)
    return jsonify({"success": True})

@app.route("/api/get-all-pro-keys", methods=["POST"])
def get_all_pro_keys():
    data = request.get_json(silent=True) or {}
    admin_key = data.get("admin_key", "")
    if admin_key != ADMIN_SECRET_CODE:
        return jsonify({"success": False, "error": "غير مصرح"}), 403
    
    keys_db = load_pro_keys()
    keys = keys_db.get("keys", [])
    available = [k for k in keys if not k.get("used", False) and datetime.fromisoformat(k.get("expiry")) > datetime.now()]
    return jsonify({"success": True, "keys": keys, "available_count": len(available), "total": len(keys)})

@app.route("/api/get-owner-info", methods=["POST"])
def get_owner_info():
    db = load_users()
    first_user = db.get("users", [])[0] if db.get("users") else {}
    return jsonify({
        "owner_id": first_user.get("owner_id", ""),
        "owner_name": first_user.get("owner_name", "OTMAN")
    })

@app.route("/api/update-owner-info", methods=["POST"])
def update_owner_info():
    data = request.get_json(silent=True) or {}
    admin_key = data.get("admin_key", "")
    if admin_key != ADMIN_SECRET_CODE:
        return jsonify({"success": False, "error": "غير مصرح"}), 403
    
    db = load_users()
    if db.get("users"):
        db["users"][0]["owner_id"] = data.get("owner_id", "")
        db["users"][0]["owner_name"] = data.get("owner_name", "")
    save_users(db)
    return jsonify({"success": True})

@app.route("/api/get-user-data", methods=["POST"])
def get_user_data():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    db = load_users()
    u = find_user(db, username)
    if not u:
        return jsonify({"success": False, "error": "User not found"}), 404
    return jsonify({
        "token": u.get("telegram_token", ""),
        "is_active": u.get("active", True),
        "is_pro": u.get("is_pro", False),
        "expiry_date": u.get("expiry_date")
    })

@app.route("/api/get-user-owner-info", methods=["POST"])
def get_user_owner_info():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    db = load_users()
    u = find_user(db, username)
    if not u:
        return jsonify({"success": False, "error": "User not found"}), 404
    return jsonify({
        "owner_id": u.get("owner_id", ""),
        "owner_name": u.get("owner_name", "")
    })

@app.route("/api/update-user-owner-info", methods=["POST"])
def update_user_owner_info():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    db = load_users()
    u = find_user(db, username)
    if not u:
        return jsonify({"success": False, "error": "User not found"}), 404
    u["owner_id"] = data.get("owner_id", "")
    u["owner_name"] = data.get("owner_name", "")
    save_users(db)
    return jsonify({"success": True})

@app.route("/api/update-user-bot", methods=["POST"])
def update_user_bot():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    db = load_users()
    u = find_user(db, username)
    if not u:
        return jsonify({"success": False, "error": "User not found"}), 404
    
    new_token = data.get("token", "").strip()
    old_token = u.get("telegram_token", "")
    
    if new_token != old_token:
        if old_token:
            stop_bot_for_user(username)
        u["telegram_token"] = new_token
        if new_token and u.get("active", True):
            start_bot_for_user(username, new_token)
    
    save_users(db)
    return jsonify({"success": True})

@app.route("/api/toggle-user-bot", methods=["POST"])
def toggle_user_bot():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    db = load_users()
    u = find_user(db, username)
    if not u:
        return jsonify({"success": False, "error": "User not found"}), 404
    
    new_state = not u.get("active", True)
    u["active"] = new_state
    save_users(db)
    
    if not new_state:
        stop_bot_for_user(username)
    else:
        token = u.get("telegram_token", "")
        if token:
            start_bot_for_user(username, token)
    
    return jsonify({"success": True, "is_active": new_state})

@app.route("/api/admin/users", methods=["GET"])
def admin_users():
    db = load_users()
    users_list = []
    for u in db.get("users", []):
        users_list.append({
            "username": u.get("username"),
            "active": u.get("active", True),
            "is_pro": u.get("is_pro", False),
            "has_token": bool(u.get("telegram_token", ""))
        })
    return jsonify({"success": True, "users": users_list})

@app.route("/api/admin/quickstats", methods=["GET"])
def admin_quickstats():
    db = load_users()
    total_users = len(db.get("users", []))
    active_users = sum(1 for u in db.get("users", []) if u.get("active", True))
    premium_users = sum(1 for u in db.get("users", []) if u.get("is_pro", False))
    bots_running = len(active_bots)
    
    return jsonify({"success": True, "stats": {
        "users_total": total_users,
        "users_active": active_users,
        "users_premium": premium_users,
        "bots_running": bots_running,
        "ff_accounts": len(connected_clients),
        "active_attacks": len(SHARED_ACTIVE_SPAM_TARGETS)
    }})

@app.route("/api/check-auth", methods=["GET"])
def check_auth():
    if session.get("user"):
        u = session.get("user")
        return jsonify({
            "logged_in": True,
            "username": u.get("username"),
            "is_admin": u.get("is_admin", False),
            "is_pro": u.get("is_pro", False)
        })
    return jsonify({"logged_in": False})

@app.route("/api/logout", methods=["POST"])
def api_logout():
    session.pop("user", None)
    return jsonify({"success": True})

@app.route("/api/get-bot-logs", methods=["GET"])
def get_bot_logs():
    if not session.get("user"):
        return jsonify({"error": "Unauthorized"}), 401
    
    username = request.args.get("user") or current_username()
    log_file = os.path.join(DATA_DIR, f"bot_logs_{username}.txt")
    logs = []
    if os.path.exists(log_file):
        try:
            with open(log_file, "r", encoding="utf-8") as f:
                for line in f.readlines()[-20:]:
                    line = line.strip()
                    if line:
                        parts = line.split("|", 1)
                        if len(parts) == 2:
                            logs.append({"time": parts[0], "message": parts[1]})
                        else:
                            logs.append({"time": "●", "message": line})
        except:
            pass
    
    if not logs:
        logs = [{"time": "●", "message": "📋 تم تسجيل الدخول إلى النظام"}]
    
    return jsonify({"logs": logs})

@app.route("/api/add-bot-log", methods=["POST"])
def add_bot_log():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    message = data.get("message", "")
    
    if not username:
        return jsonify({"error": "Username required"}), 400
    
    log_file = os.path.join(DATA_DIR, f"bot_logs_{username}.txt")
    timestamp = datetime.now().strftime("%H:%M:%S")
    try:
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(f"{timestamp}|{message}\n")
    except:
        pass
    
    return jsonify({"success": True})
    # ========== دوال الصيانة والخلفية ==========
#تم التعديل - إضافة دوال مفقودة

def update_jwt_periodically():
    """تحديث التوكن بشكل دوري كل ساعة"""
    global JWT_TOKEN
    while True:
        try:
            time.sleep(3600)  # كل ساعة
            new_token = fetch_jwt_token()
            if new_token:
                JWT_TOKEN = new_token
                print("✅ تم تحديث التوكن بنجاح!")
            else:
                print("⚠️ فشل تحديث التوكن، سيتم المحاولة مرة أخرى")
        except Exception as e:
            print(f"⚠️ خطأ في تحديث التوكن: {e}")
            time.sleep(60)

def check_expired_users():
    """التحقق من المستخدمين منتهية الصلاحية وحذفهم"""
    global users
    while True:
        try:
            time.sleep(60)  # كل دقيقة
            current_time = time.time()
            expired = []
            for uid, data in users.items():
                if isinstance(data, dict) and data.get("expiry", 0) < current_time:
                    expired.append(uid)
            
            if expired:
                for uid in expired:
                    if uid in users:
                        del users[uid]
                save_users()
                print(f"✅ تم حذف {len(expired)} مستخدم منتهي الصلاحية")
        except Exception as e:
            print(f"⚠️ خطأ في التحقق من الصلاحية: {e}")
            time.sleep(60)

def daily_reset_timer():
    """إعادة تعيين يومية"""
    while True:
        try:
            # انتظر حتى منتصف الليل
            now = datetime.now()
            tomorrow = datetime(now.year, now.month, now.day) + timedelta(days=1)
            seconds_until_midnight = (tomorrow - now).total_seconds()
            time.sleep(seconds_until_midnight)
            
            # تنفيذ إعادة التعيين اليومية
            print("🔄 تنفيذ إعادة التعيين اليومية...")
            # يمكنك إضافة منطق إعادة التعيين هنا
            print("✅ تم إعادة التعيين اليومية بنجاح!")
        except Exception as e:
            print(f"⚠️ خطأ في إعادة التعيين اليومية: {e}")
            time.sleep(60)

# ========== التشغيل الرئيسي ==========
if __name__ == "__main__":
    # تحميل البيانات
    users = load_users()
    group_activations = load_groups()
    maintenance_mode = load_maintenance_status()
    
    # جلب JWT Token
    print("🔄 جاري جلب التوكن للمرة الأولى...")
    for _ in range(5):
        JWT_TOKEN = fetch_jwt_token()
        if JWT_TOKEN:
            print("✅ تم جلب التوكن بنجاح!")
            break
        time.sleep(3)
    else:
        print("❌ فشل جلب التوكن بعد 5 محاولات!")
    
    if not JWT_TOKEN:
        print("⚠️ ملاحضة: البوت يعمل بدون توكن، قد لا تعمل بعض الوظائف!")
    
    # تشغيل خيوط المعالجة الخلفية
    threading.Thread(target=update_jwt_periodically, daemon=True).start()
    threading.Thread(target=check_expired_users, daemon=True).start()
    threading.Thread(target=daily_reset_timer, daemon=True).start()
    
    # تشغيل حسابات Free Fire
    threading.Thread(target=StarT_SerVer, daemon=True).start()
    
    time.sleep(5)
    
    # تشغيل البوتات من قاعدة البيانات
    start_all_bots_from_db()
    
    # تشغيل Flask
    port = int(os.environ.get("PORT", 11773))
    app.run(host="0.0.0.0", port=port, debug=False)