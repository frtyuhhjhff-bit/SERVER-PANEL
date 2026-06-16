import os
import json
import re
import socket
import threading
import time
import sys
import requests
import random
import jwt
from datetime import datetime, timedelta
from flask import Flask, send_from_directory, request, jsonify, redirect, session
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from google.protobuf.timestamp_pb2 import Timestamp
import telebot
from telebot import types

import asyncio
import pickle
import binascii
import base64
import urllib3
import tempfile
from concurrent.futures import ThreadPoolExecutor
from protobuf_decoder.protobuf_decoder import Parser

# ========== استيرادات الملفات المساعدة ==========
from byte import *
from byte import xSendTeamMsg
from byte import Auth_Chat
from xHeaders import *

# ========== إعدادات Flask ==========
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "DATA")
USERS_DB = os.path.join(DATA_DIR, "users.json")
KEYS_DB = os.path.join(DATA_DIR, "pro_keys.json")
os.makedirs(DATA_DIR, exist_ok=True)

app = Flask(__name__)
app.secret_key = os.environ.get("PANEL_SECRET_KEY", "CHANGE_ME_" + os.urandom(16).hex())

ADMIN_USERNAME = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASSWORD = os.environ.get("ADMIN_PASS", "admin")
ADMIN_SECRET_CODE = "STRAVEX2025"

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

# ========== حسابات Free Fire والهجمات ==========
SHARED_CONNECTED_CLIENTS = {}
SHARED_CONNECTED_CLIENTS_LOCK = threading.Lock()
SHARED_ACTIVE_SPAM_TARGETS = {}
SHARED_ACTIVE_SPAM_LOCK = threading.Lock()
SHARED_ACCOUNTS = []

active_bots = {}
bot_tokens = {}

def ChEck_Commande(code):
    try:
        if code and len(str(code)) >= 5:
            return True
        return False
    except:
        return False

def DeCode_PackEt(hex_string):
    try:
        bytes_data = bytes.fromhex(hex_string)
        return bytes_data.decode('utf-8', errors='ignore')
    except:
        return '{}'

def EnC_PacKeT(data, key, iv):
    return data

def EnC_AEs(hex_string):
    return hex_string

def DecodE_HeX(timestamp):
    return hex(timestamp)[2:]

def EnC_Uid(uid, Tp='Uid'):
    return str(uid)

def GenResponsMsg(msg, type_code, from_uid, to_uid, key, iv):
    return msg.encode()

def xMsGFixinG(val):
    return val

def JoinTeamCode(teamcode, key, iv):
    return f'JOIN:{teamcode}'.encode()

def ExitBot(code, key, iv):
    return f'EXIT:{code}'.encode()

def GhostPakcet(team_id, name, sq, key, iv):
    return f'GHOST:{team_id}:{name}:{sq}'.encode()

def OpEnSq(key, iv):
    return b'OPEN_ROOM'

def SPamSq(target_id, key, iv):
    return f'SPAM:{target_id}'.encode()

def cHSq(type_num, account_uid, key, iv):
    return f'CHANGE:{type_num}:{account_uid}'.encode()

def SEnd_InV(val1, target_id, key, iv):
    return f'INVITE:{val1}:{target_id}'.encode()

def openroom(key, iv):
    return b'OPEN_ROOM_SPAM'

def spmroom(key, iv, target_id):
    return f'SPAM_ROOM:{target_id}'.encode()

class xKEys:
    class MyMessage:
        def ParseFromString(self, data):
            self.field21 = 0
            self.field22 = 'fake_key_32_bytes_long_string!!'
            self.field23 = 'fake_iv_16_bytes!!'

class FF_CLient():
    def __init__(self, id, password):
        self.id = id
        self.password = password
        self.key = None
        self.iv = None
        self.Get_FiNal_ToKen_0115()

    def Connect_SerVer_OnLine(self, Token, tok, host, port, key, iv, host2, port2):
        try:
            self.AutH_ToKen_0115 = tok
            self.CliEnts2 = socket.create_connection((host2, int(port2)))
            self.CliEnts2.send(bytes.fromhex(self.AutH_ToKen_0115))
        except:
            pass
        while True:
            try:
                self.DaTa2 = self.CliEnts2.recv(99999)
                if '0500' in self.DaTa2.hex()[0:4] and len(self.DaTa2.hex()) > 30:
                    self.packet = json.loads(DeCode_PackEt(f'08{self.DaTa2.hex().split("08", 1)[1]}'))
                    self.AutH = self.packet['5']['data']['7']['data']
            except:
                pass

    def Connect_SerVer(self, Token, tok, host, port, key, iv, host2, port2):
        self.AutH_ToKen_0115 = tok
        self.CliEnts = socket.create_connection((host, int(port)))
        self.CliEnts.send(bytes.fromhex(self.AutH_ToKen_0115))
        self.DaTa = self.CliEnts.recv(1024)
        threading.Thread(target=self.Connect_SerVer_OnLine, args=(Token, tok, host, port, key, iv, host2, port2)).start()
        self.Exemple = xMsGFixinG('12345678')
        self.key = key
        self.iv = iv
        with SHARED_CONNECTED_CLIENTS_LOCK:
            SHARED_CONNECTED_CLIENTS[self.id] = self
            print(f"[FF] ✅ {self.id} متصل - الإجمالي: {len(SHARED_CONNECTED_CLIENTS)}")
        while True:
            try:
                self.DaTa = self.CliEnts.recv(1024)
                if len(self.DaTa) == 0:
                    self.Reconnect(Token, tok, host, port, key, iv, host2, port2)
                if '1200' in self.DaTa.hex()[0:4] and 900 > len(self.DaTa.hex()) > 100:
                    if b"***" in self.DaTa:
                        self.DaTa = self.DaTa.replace(b"***", b"106")
                    try:
                        self.BesTo_data = json.loads(DeCode_PackEt(self.DaTa.hex()[10:]))
                        self.input_msg = 'besto_love' if '8' in self.BesTo_data["5"]["data"] else self.BesTo_data["5"]["data"]["4"]["data"]
                    except:
                        self.input_msg = None
                    self.DeCode_CliEnt_Uid = self.BesTo_data["5"]["data"]["1"]["data"]
                    self.CliEnt_Uid = EnC_Uid(self.DeCode_CliEnt_Uid, Tp='Uid')
                if 'besto_love' in self.input_msg[:10]:
                    self.CliEnts.send(GenResponsMsg(f'''
[C][B][000000]━━━━━━━━━━━━   
[FFD700] WELCOME TO RAGNAR BOT
[00FF7F]FF SPAM SYSTEM
[00BFFF]Telegram: @STRAVEX_vib
[C][B][000000]━━━━━━━━━━━━''', 2, self.DeCode_CliEnt_Uid, self.DeCode_CliEnt_Uid, key, iv))
                    time.sleep(0.3)
                    self.CliEnts.close()
                    if hasattr(self, 'CliEnts2'):
                        self.CliEnts2.close()
                    self.Connect_SerVer(Token, tok, host, port, key, iv, host2, port2)
            except Exception as e:
                self.Reconnect(Token, tok, host, port, key, iv, host2, port2)

    def Reconnect(self, Token, tok, host, port, key, iv, host2, port2):
        try:
            self.CliEnts.close()
            if hasattr(self, 'CliEnts2'):
                self.CliEnts2.close()
        except:
            pass
        self.Connect_SerVer(Token, tok, host, port, key, iv, host2, port2)

    def GeT_Key_Iv(self, serialized_data):
        my_message = xKEys.MyMessage()
        my_message.ParseFromString(serialized_data)
        timestamp, key, iv = my_message.field21, my_message.field22, my_message.field23
        timestamp_obj = Timestamp()
        timestamp_obj.FromNanoseconds(timestamp)
        timestamp_seconds = timestamp_obj.seconds
        timestamp_nanos = timestamp_obj.nanos
        combined_timestamp = timestamp_seconds * 1000000000 + timestamp_nanos
        return combined_timestamp, key, iv

    def Guest_GeneRaTe(self, uid, password):
        url = "https://100067.connect.garena.com/oauth/guest/token/grant"
        headers = {"Host": "100067.connect.garena.com", "User-Agent": "GarenaMSDK/4.0.19P4(G011A ;Android 9;en;US;)", "Content-Type": "application/x-www-form-urlencoded", "Accept-Encoding": "gzip, deflate, br", "Connection": "close"}
        data = {"uid": f"{uid}", "password": f"{password}", "response_type": "token", "client_type": "2", "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3", "client_id": "100067"}
        try:
            response = requests.post(url, headers=headers, data=data, timeout=30).json()
            access_token, open_id = response['access_token'], response['open_id']
            time.sleep(0.5)
            return self.ToKen_GeneRaTe(access_token, open_id)
        except:
            time.sleep(5)
            return self.Guest_GeneRaTe(uid, password)

    def GeT_LoGin_PorTs(self, JwT_ToKen, PayLoad):
        url = 'https://clientbp.common.ggbluefox.com/GetLoginData'
        headers = {'Expect': '100-continue', 'Authorization': f'Bearer {JwT_ToKen}', 'X-Unity-Version': '2018.4.11f1', 'X-GA': 'v1 1', 'ReleaseVersion': 'OB53', 'Content-Type': 'application/x-www-form-urlencoded', 'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 9; G011A Build/PI)', 'Host': 'clientbp.common.ggbluefox.com', 'Connection': 'close', 'Accept-Encoding': 'gzip, deflate, br'}
        try:
            response = requests.post(url, headers=headers, data=PayLoad, verify=False, timeout=30)
            if response.content:
                hex_content = response.content.hex()
                data = json.loads(DeCode_PackEt(hex_content))
                address = data['32']['data']; address2 = data['14']['data']
                ip = address[:len(address) - 6]; ip2 = address2[:len(address2) - 6]
                port = address[len(address) - 5:]; port2 = address2[len(address2) - 5:]
                return ip, port, ip2, port2
            return None, None, None, None
        except:
            return None, None, None, None

    def ToKen_GeneRaTe(self, Access_ToKen, Access_Uid):
        url = "https://loginbp.ggblueshark.com/MajorLogin"
        headers = {'X-Unity-Version': '2018.4.11f1', 'ReleaseVersion': 'OB53', 'Content-Type': 'application/x-www-form-urlencoded', 'X-GA': 'v1 1', 'Content-Length': '928', 'User-Agent': 'Dalvik/2.1.0 (Linux; U; Android 7.1.2; ASUS_Z01QD Build/QKQ1.190825.002)', 'Host': 'loginbp.common.ggbluefox.com', 'Connection': 'Keep-Alive', 'Accept-Encoding': 'gzip'}
        base_data = '1a13323032362d30312d31382032333a35343a3039220966726565206669726528013a05312e312e31423a416e64726f6964204f532039202f204150492d32382028505133422e3139303830312e31303130313834362f47393635305a48553241524336294a0848616e6468656c645207566572697a6f6e5a045749464960800f68b80872033238307a2141524d3634204650204153494d442041455320564d48207c2032383635207c20348001bb178a010f416472656e6f2028544d29203634309201134f70656e474c20455320332e312076312e34369a012b476f6f676c657c33346137646364662d613764352d346362362d386437652d336230653434386130633537a2010d3232332e3139312e35312e3839aa0102656eb201203433303632343537393364653836646134323561353263616164663231656564ba010134c2010848616e6468656c64ca010430374051ea014034653739616666653331343134393031353434656161626562633437303537333866653638336139326464346335656533646233333636326232653936363466f00101ca0207566572697a6f6ed2020457494649ca03203734323862323533646566633136343031386336303461316562626665626466e0038b9b02e803e7f401f003d713f803bf058004b2c301880484d0019004e0810298048b9b02c80403d2043f2f646174612f6170702f636f6d2e6474732e667265656669726574682d59504b4d386a484577414a6c68706d68446876354d513d3d2f6c69622f61726d3634e00401ea045f35623839326161616264363838653537316636383830353331313861313632627c2f646174612f6170702f636f6d2e6474732e667265656669726574682d59504b4d386a484577414a6c68706d68446876354d513d3d2f626173652e61706bf00403f804028a050236349a050a32303139313138363935b205094f70656e474c455332b805ff7fc00504ca0530467751565467555058315561556c6c4444776357435242705741554f556773764131736e576c42614f316b4659673d3de005fc69ea0507616e64726f6964f2055c4b71734854796d77352f354742323359476e6955594e322f71343747415472713765466552617466304e6b774c4b454d5130504b35424b456b37326450666c4178556c454269723656746579383358714635393371736c386877593df805b9db068806019006019a060134a2060134'
        try:
            dt = bytes.fromhex(base_data)
            current_time = str(datetime.now())[:-7].encode()
            dt = dt.replace(b'2025-07-30 14:11:20', current_time)
            dt = dt.replace(b'4e79affe31414901544eaabebc4705738fe683a92dd4c5ee3db33662b2e9664f', Access_ToKen.encode())
            dt = dt.replace(b'4306245793de86da425a52caadf21eed', Access_Uid.encode())
            try:
                hex_data = dt.hex()
                encoded_data = EnC_AEs(hex_data)
                payload = bytes.fromhex(encoded_data)
            except:
                payload = dt
        except:
            payload = f"uid={Access_Uid}&token={Access_ToKen}".encode()
        try:
            response = requests.post(url, headers=headers, data=payload, verify=False, timeout=30)
            if response.status_code == 200 and len(response.text) > 10:
                if response.content:
                    hex_content = response.content.hex()
                    data = json.loads(DeCode_PackEt(hex_content))
                    jwt_token = data['8']['data']
                    combined_timestamp, key, iv = self.GeT_Key_Iv(response.content)
                    ip, port, ip2, port2 = self.GeT_LoGin_PorTs(jwt_token, payload)
                    return jwt_token, key, iv, combined_timestamp, ip, port, ip2, port2
            time.sleep(2)
            return self.ToKen_GeneRaTe(Access_ToKen, Access_Uid)
        except:
            time.sleep(5)
            return self.ToKen_GeneRaTe(Access_ToKen, Access_Uid)

    def Get_FiNal_ToKen_0115(self):
        try:
            result = self.Guest_GeneRaTe(self.id, self.password)
            if not result:
                time.sleep(2)
                return self.Get_FiNal_ToKen_0115()
            token, key, iv, Timestamp, ip, port, ip2, port2 = result
            if not all([ip, port, ip2, port2]):
                time.sleep(2)
                return self.Get_FiNal_ToKen_0115()
            self.JwT_ToKen = token
            try:
                decoded = jwt.decode(token, options={"verify_signature": False})
                self.AccounT_Uid = decoded.get('account_id')
                self.EncoDed_AccounT = hex(self.AccounT_Uid)[2:]
                self.HeX_VaLue = DecodE_HeX(Timestamp)
                self.TimE_HEx = self.HeX_VaLue
                self.JwT_ToKen_ = token.encode().hex()
                print(f'✅ تم تسجيل الدخول: {self.AccounT_Uid}')
            except:
                time.sleep(2)
                return self.Get_FiNal_ToKen_0115()
            try:
                self.Header = hex(len(EnC_PacKeT(self.JwT_ToKen_, key, iv)) // 2)[2:]
                length = len(self.EncoDed_AccounT)
                zeros = '00000000'
                if length == 9: zeros = '0000000'
                elif length == 8: zeros = '00000000'
                elif length == 10: zeros = '000000'
                elif length == 7: zeros = '000000000'
                self.Header = f'0115{zeros}{self.EncoDed_AccounT}{self.TimE_HEx}00000{self.Header}'
                self.FiNal_ToKen_0115 = self.Header + EnC_PacKeT(self.JwT_ToKen_, key, iv)
            except:
                time.sleep(5)
                return self.Get_FiNal_ToKen_0115()
            self.AutH_ToKen = self.FiNal_ToKen_0115
            self.Connect_SerVer(self.JwT_ToKen, self.AutH_ToKen, ip, port, key, iv, ip2, port2)
            return self.AutH_ToKen, key, iv
        except Exception as e:
            print(f"❌ خطأ: {e}")
            time.sleep(10)
            return self.Get_FiNal_ToKen_0115()

# ========== دوال حسابات Free Fire ==========
def load_accounts_from_file(filename="accs.txt"):
    global SHARED_ACCOUNTS
    accounts = []
    try:
        with open(filename, "r", encoding="utf-8") as file:
            for line in file:
                line = line.strip()
                if line and not line.startswith("#"):
                    if ":" in line:
                        parts = line.split(":")
                        if len(parts) >= 2:
                            accounts.append({'id': parts[0].strip(), 'password': parts[1].strip()})
                    else:
                        accounts.append({'id': line.strip(), 'password': ''})
        SHARED_ACCOUNTS = accounts
        print(f"[FF] 📁 تم تحميل {len(accounts)} حساب من {filename}")
    except FileNotFoundError:
        print(f"[FF] ⚠️ ملف {filename} غير موجود!")
    return accounts

def start_account(account):
    try:
        print(f"[FF] 🚀 بدء حساب: {account['id']}")
        FF_CLient(account['id'], account['password'])
    except Exception as e:
        print(f"[FF] ❌ خطأ في الحساب {account['id']}: {e}")
        time.sleep(5)
        start_account(account)

def start_all_accounts():
    if not SHARED_ACCOUNTS:
        print("[FF] ❌ لا توجد حسابات!")
        return
    for account in SHARED_ACCOUNTS[:100]:
        threading.Thread(target=start_account, args=(account,), daemon=True).start()
        time.sleep(0.1)

# ========== دوال الهجمات للبوتات ==========
def get_random_accounts(count=1):
    with SHARED_CONNECTED_CLIENTS_LOCK:
        if not SHARED_CONNECTED_CLIENTS:
            return []
        available_clients = list(SHARED_CONNECTED_CLIENTS.values())
        if count >= len(available_clients):
            return available_clients
        return random.sample(available_clients, count)

def execute_ghost_command(client, teamcode, name):
    success = False
    try:
        if hasattr(client, 'CliEnts2') and client.CliEnts2 and hasattr(client, 'key') and client.key:
            join_packet = JoinTeamCode(teamcode, client.key, client.iv)
            client.CliEnts2.send(join_packet)
            time.sleep(1)
            ghost_packet = GhostPakcet(teamcode, name, "1", client.key, client.iv)
            client.CliEnts2.send(ghost_packet)
            success = True
    except:
        pass
    return success

def execute_get_command(client, teamcode, name):
    success = False
    try:
        if hasattr(client, 'CliEnts2') and client.CliEnts2 and hasattr(client, 'key') and client.key:
            for i in range(50):
                join_packet = JoinTeamCode(teamcode, client.key, client.iv)
                client.CliEnts2.send(join_packet)
                time.sleep(0.1)
            success = True
    except:
        pass
    return success

def execute_lag_command(client, teamcode):
    success = False
    try:
        if hasattr(client, 'CliEnts2') and client.CliEnts2 and hasattr(client, 'key') and client.key:
            for i in range(100):
                join_packet = JoinTeamCode(teamcode, client.key, client.iv)
                client.CliEnts2.send(join_packet)
                time.sleep(0.05)
            success = True
    except:
        pass
    return success

def execute_5x_command(client, target_id):
    success = False
    try:
        if hasattr(client, 'CliEnts2') and client.CliEnts2 and hasattr(client, 'key') and client.key:
            packet = f'TEAM5:{target_id}'.encode()
            client.CliEnts2.send(packet)
            success = True
    except:
        pass
    return success

def execute_6x_command(client, target_id):
    success = False
    try:
        if hasattr(client, 'CliEnts2') and client.CliEnts2 and hasattr(client, 'key') and client.key:
            packet = f'TEAM6:{target_id}'.encode()
            client.CliEnts2.send(packet)
            success = True
    except:
        pass
    return success

def infinite_spam_worker(target_id):
    while True:
        with SHARED_ACTIVE_SPAM_LOCK:
            if target_id not in SHARED_ACTIVE_SPAM_TARGETS:
                break
        try:
            with SHARED_CONNECTED_CLIENTS_LOCK:
                for client in SHARED_CONNECTED_CLIENTS.values():
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

def register_bot_handlers(bot_instance, username):
    # دالة لإضافة سجل
    def add_log(message):
        try:
            log_file = os.path.join(DATA_DIR, f"bot_logs_{username}.txt")
            timestamp = datetime.now().strftime("%H:%M:%S")
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(f"{timestamp}|{message}\n")
        except:
            pass
    
    @bot_instance.message_handler(commands=['start'])
    def start_command(message):
        user_id = message.from_user.id
        user_name = message.from_user.first_name
        add_log(f"📱 مستخدم جديد: {user_name} (ID: {user_id})")
        db = load_users()
        owner = None
        for u in db.get("users", []):
            if u.get("username") == username:
                owner = u
                break
        owner_name = owner.get("owner_name", "STRAVEX") if owner else "STRAVEX"
        welcome_text = f"""
🌟 <b>مرحباً {user_name}!</b> 🌟

✅ <b>بوت المقبرة يعمل بكامل طاقته</b>
👑 <b>المالك:</b> {owner_name}

📌 <b>لرؤية الأوامر المتاحة:</b>
<code>/help</code>

🔥 <b>استمتع بالتجربة</b>
        """
        bot_instance.send_message(message.chat.id, welcome_text, parse_mode='HTML')
    
    @bot_instance.message_handler(commands=['help'])
    def help_command(message):
        help_text = """
WELCOME TO HELP BOT
<b>أوامر البوت:</b>

ارسال أشباح للفريق 
<code>/ghost [TEAM CODE] [name]</code>
هجوم مكثف بأشباح على الفريق
<code>/get [TEAM CODE] [name]</code> 

بدء المقبرة على اللاعب
<code>/sp [PLAYER ID]</code>
إيقاف المقبرة
<code>/stop [PLAYER ID]</code>

فتح فريق خماسي
<code>/5 [PLAYER ID]</code>

مقبرة التيم كود
<code>/lag [TEAM CODE]</code>
        """
        bot_instance.send_message(message.chat.id, help_text, parse_mode='HTML')
    
    @bot_instance.message_handler(func=lambda m: m.text.startswith('/ghost'))
    def ghost_command(message):
        parts = message.text.split()
        if len(parts) < 3:
            bot_instance.reply_to(message, "⚠️ استخدم: /ghost [كود الفريق] [الاسم]")
            return
        teamcode, name = parts[1], ' '.join(parts[2:])
        add_log(f"👻 إرسال أشباح إلى فريق: {teamcode}, الاسم: {name}")
        clients = get_random_accounts(4)
        if not clients:
            bot_instance.reply_to(message, "❌ لا توجد حسابات متصلة")
            return
        for client in clients:
            threading.Thread(target=execute_ghost_command, args=(client, teamcode, name)).start()
        bot_instance.reply_to(message, f"✅ تم إرسال الأشباح إلى {teamcode}")
    
    @bot_instance.message_handler(func=lambda m: m.text.startswith('/get'))
    def get_command(message):
        parts = message.text.split()
        if len(parts) < 3:
            bot_instance.reply_to(message, "⚠️ استخدم: /get [كود الفريق] [الاسم]")
            return
        teamcode, name = parts[1], ' '.join(parts[2:])
        add_log(f"⚡ هجوم مكثف على فريق: {teamcode}, الاسم: {name}")
        clients = get_random_accounts(3)
        if not clients:
            bot_instance.reply_to(message, "❌ لا توجد حسابات متصلة")
            return
        for client in clients:
            threading.Thread(target=execute_get_command, args=(client, teamcode, name)).start()
        bot_instance.reply_to(message, f"✅ تم تنفيذ Get على {teamcode}")
    
    @bot_instance.message_handler(func=lambda m: m.text.startswith('/lag'))
    def lag_command(message):
        parts = message.text.split()
        if len(parts) < 2:
            bot_instance.reply_to(message, "⚠️ استخدم: /lag [كود الفريق]")
            return
        teamcode = parts[1]
        add_log(f"🐌 مقبرة تيم كود: {teamcode}")
        clients = get_random_accounts(3)
        if not clients:
            bot_instance.reply_to(message, "❌ لا توجد حسابات متصلة")
            return
        for client in clients:
            threading.Thread(target=execute_lag_command, args=(client, teamcode)).start()
        bot_instance.reply_to(message, f"✅ تم تنفيذ Lag على {teamcode}")
    
    @bot_instance.message_handler(func=lambda m: m.text.startswith('/5'))
    def team5_command(message):
        parts = message.text.split()
        if len(parts) < 2:
            bot_instance.reply_to(message, "⚠️ استخدم: /5 [ايدي اللاعب]")
            return
        target = parts[1]
        add_log(f"5️⃣ فتح فريق خماسي للاعب: {target}")
        clients = get_random_accounts(1)
        if not clients:
            bot_instance.reply_to(message, "❌ لا توجد حسابات متصلة")
            return
        execute_5x_command(clients[0], target)
        bot_instance.reply_to(message, f"✅ تم إرسال فريق 5 إلى {target}")
    
    @bot_instance.message_handler(func=lambda m: m.text.startswith('/6'))
    def team6_command(message):
        parts = message.text.split()
        if len(parts) < 2:
            bot_instance.reply_to(message, "⚠️ استخدم: /6 [ايدي اللاعب]")
            return
        target = parts[1]
        add_log(f"6️⃣ فتح فريق سداسي للاعب: {target}")
        clients = get_random_accounts(1)
        if not clients:
            bot_instance.reply_to(message, "❌ لا توجد حسابات متصلة")
            return
        execute_6x_command(clients[0], target)
        bot_instance.reply_to(message, f"✅ تم إرسال فريق 6 إلى {target}")
    
    @bot_instance.message_handler(commands=['sp'])
    def sp_command(message):
        parts = message.text.split()
        if len(parts) < 2:
            bot_instance.reply_to(message, "⚠️ استخدم: /sp [ايدي اللاعب]")
            return
        target = parts[1]
        add_log(f"💀 بدء مقبرة على اللاعب: {target}")
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
        add_log(f"🛑 إيقاف مقبرة على اللاعب: {target}")
        with SHARED_ACTIVE_SPAM_LOCK:
            if target in SHARED_ACTIVE_SPAM_TARGETS:
                del SHARED_ACTIVE_SPAM_TARGETS[target]
                bot_instance.reply_to(message, f"🛑 تم إيقاف السبام على {target}")
            else:
                bot_instance.reply_to(message, f"ℹ️ لا يوجد سبام نشط على {target}")

def start_bot_for_user(username, token):
    try:
        bot_instance = telebot.TeleBot(token, parse_mode='HTML')
        register_bot_handlers(bot_instance, username)
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

# ========== واجهات API للواجهة العربية ==========
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
        return jsonify({"success": True, "username": username, "is_master": True, "is_pro": True, "owner_expiry": (datetime.now() + timedelta(days=365)).isoformat()})
    
    db = load_users()
    u = find_user(db, username)
    if not u:
        return jsonify({"success": False, "error": "بيانات غير صحيحة"}), 401
    if not check_password_hash(u.get("password_hash", ""), password):
        return jsonify({"success": False, "error": "بيانات غير صحيحة"}), 401
    
    session["user"] = {"username": u.get("username"), "is_admin": False, "is_pro": u.get("is_pro", False)}
    expiry = u.get("expiry_date", (datetime.now() + timedelta(days=7)).isoformat())
    return jsonify({"success": True, "username": username, "is_master": False, "is_pro": u.get("is_pro", False), "expiry_date": expiry})

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
            print(f"[KEY] ✅ تم استخدام المفتاح {key} بواسطة {username}")
        elif key != "FREE-KEY":
            return jsonify({"success": False, "error": "مفتاح PRO غير صالح"}), 400
    
    new_user = {
        "username": username,
        "password_hash": generate_password_hash(password),
        "active": True,
        "is_pro": is_pro,
        "telegram_token": "",
        "admin_password": "X1R_RAGNAR",
        "max_users": 100,
        "active_users": 0,
        "owner_id": "",
        "owner_name": "",
        "welcome_message": "",
        "help_message": "",
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

@app.route("/api/bot-runner-data", methods=["POST"])
def bot_runner_data():
    data = request.get_json(silent=True) or {}
    db = load_users()
    users = []
    for u in db.get("users", []):
        users.append({
            "username": u.get("username"),
            "token": u.get("telegram_token", ""),
            "admin_password": u.get("admin_password", "X1R_RAGNAR"),
            "max_users": u.get("max_users", 100),
            "is_active": u.get("active", True),
            "active_users": u.get("active_users", 0),
            "owner_id": u.get("owner_id", ""),
            "owner_name": u.get("owner_name", ""),
            "welcome_message": u.get("welcome_message", ""),
            "help_message": u.get("help_message", ""),
            "is_pro": u.get("is_pro", False)
        })
    return jsonify({"success": True, "users": users})

@app.route("/api/get-owner-info", methods=["POST"])
def get_owner_info():
    db = load_users()
    first_user = db.get("users", [])[0] if db.get("users") else {}
    return jsonify({
        "owner_id": first_user.get("owner_id", ""),
        "owner_name": first_user.get("owner_name", "STRAVEX"),
        "welcome_message": first_user.get("welcome_message", "مرحباً بك في بوت STRAVEX"),
        "help_message": first_user.get("help_message", "الاوامر: /spam, /stop, /status")
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

@app.route("/api/update-messages", methods=["POST"])
def update_messages():
    data = request.get_json(silent=True) or {}
    admin_key = data.get("admin_key", "")
    if admin_key != ADMIN_SECRET_CODE:
        return jsonify({"success": False, "error": "غير مصرح"}), 403
    
    db = load_users()
    if db.get("users"):
        db["users"][0]["welcome_message"] = data.get("welcome_message", "")
        db["users"][0]["help_message"] = data.get("help_message", "")
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
        "admin_password": u.get("admin_password", ""),
        "max_users": u.get("max_users", 100),
        "active_users": u.get("active_users", 0),
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
    
    if "admin_password" in data:
        u["admin_password"] = data.get("admin_password")
    if "max_users" in data:
        u["max_users"] = data.get("max_users")
    
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

@app.route("/api/update-user-messages", methods=["POST"])
def update_user_messages():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    db = load_users()
    u = find_user(db, username)
    if not u:
        return jsonify({"success": False, "error": "User not found"}), 404
    if "welcome_message" in data:
        u["welcome_message"] = data.get("welcome_message")
    if "help_message" in data:
        u["help_message"] = data.get("help_message")
    save_users(db)
    return jsonify({"success": True})

@app.route("/api/admin/users", methods=["GET"])
def admin_users():
    db = load_users()
    users = []
    for u in db.get("users", []):
        users.append({
            "username": u.get("username"),
            "email": u.get("email", ""),
            "active": u.get("active", True),
            "is_pro": u.get("is_pro", False),
            "has_token": bool(u.get("telegram_token", ""))
        })
    return jsonify({"success": True, "users": users})

@app.route("/api/admin/quickstats", methods=["GET"])
def admin_quickstats():
    db = load_users()
    total_users = len(db.get("users", []))
    active_users = sum(1 for u in db.get("users", []) if u.get("active", True))
    premium_users = sum(1 for u in db.get("users", []) if u.get("is_pro", False))
    bots_running = len(active_bots)
    
    total_likes_today = sum(u.get("likes_today", 0) for u in db.get("users", []))
    
    return jsonify({"success": True, "stats": {
        "users_total": total_users,
        "users_active": active_users,
        "users_premium": premium_users,
        "bots_running": bots_running,
        "ff_accounts": len(SHARED_CONNECTED_CLIENTS),
        "likes_today": total_likes_today,
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

# ========== واجهات API إضافية ==========
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

@app.route("/api/update-bot-stats", methods=["POST"])
def update_bot_stats():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    active_users = data.get("active_users", 0)
    groups_count = data.get("groups_count", 0)
    
    if not username:
        return jsonify({"error": "Username required"}), 400
    
    db = load_users()
    u = find_user(db, username)
    if u:
        u["active_users"] = active_users
        u["groups_count"] = groups_count
        save_users(db)
    
    return jsonify({"success": True})

@app.route("/api/update-likes-stats", methods=["POST"])
def update_likes_stats():
    data = request.get_json(silent=True) or {}
    username = data.get("username")
    likes_today = data.get("likes_today", 0)
    last_like_time = data.get("last_like_time", "")
    
    if not username:
        return jsonify({"error": "Username required"}), 400
    
    db = load_users()
    u = find_user(db, username)
    if u:
        u["likes_today"] = likes_today
        u["last_like_time"] = last_like_time
        save_users(db)
    
    return jsonify({"success": True})
    
# ========== التشغيل الرئيسي ==========
if __name__ == "__main__":
    load_accounts_from_file("accs.txt")
    threading.Thread(target=start_all_accounts, daemon=True).start()
    start_all_bots_from_db()
    port = int(os.environ.get("PORT", 11773))
    app.run(host="0.0.0.0", port=port, debug=False)