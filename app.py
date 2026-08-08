import json
import os
import smtplib
import sqlite3
import threading
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from flask import Flask, redirect, render_template, request
from calculator import calculate_wuxing

app = Flask(__name__)
DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'wuxing.db')
GMAIL_USER = 'tangyuxi1002@gmail.com'
GMAIL_RECIPIENT = 'mxd@mxdyes.com'

GAMMA_LINK = 'https://gamma.app/docs/-df8wl8nfu0ykcin?openExternalBrowser=1'
LINE_OA_LINK = 'https://line.me/R/ti/p/@919elwkg'

# 免費研討會資訊（要改日期時間，只需改這裡）
WEBINAR_INFO = {
    'date': '8 月 26 日',
    'weekday': '週三',
    'time': '晚上 7:30 - 9:00',
    'datetime_iso': '2026-08-26T19:30:00+08:00',  # 倒數計時用
}

ELEMENT_DATA = {
    1: {
        'name': '金',
        'english': 'Metal',
        'color': '#B8860B',
        'bg_color': '#FDF8EE',
        'tagline': '清光自照，引路而行',
        'description': '你是一個清醒而獨立的女性，內心有著不需要他人認可的自信。你身上有一種天生的領導力——你知道方向在哪裡，也有勇氣率先踏出第一步。當你將這份創造力注入自己的風格，你的存在本身就是一種宣言。',
        'advice': '讓你的穿著說話，每一個選擇都是你內在力量的延伸。',
    },
    2: {
        'name': '水',
        'english': 'Water',
        'color': '#2C6E8A',
        'bg_color': '#EEF5F8',
        'tagline': '流水無聲，潤物於心',
        'description': '你擁有天生的感知力與溝通智慧，能讀懂他人未說出口的需求。你的美，在於那份讓人感到被理解的溫柔——你是關係中的橋樑，也是空間裡最安定的存在。當你學會先傾聽自己，你的外在將自然流露內在的深度。',
        'advice': '穿出讓自己感到平靜的顏色，你的和諧感會感染周圍的人。',
    },
    3: {
        'name': '火',
        'english': 'Fire',
        'color': '#A83222',
        'bg_color': '#FDF0EE',
        'tagline': '烈火生光，動中見美',
        'description': '你是充滿行動力的創造者，腦海裡永遠有新的想法在燃燒。你的美，在於那份擋不住的熱情與生命力——你走進哪裡，哪裡就有了溫度。當你讓風格跟上你的節奏，你的多彩將成為最真實的名片。',
        'advice': '大膽嘗試你一直想穿卻不敢穿的，你的勇氣就是你最好的搭配。',
    },
    4: {
        'name': '木',
        'english': 'Wood',
        'color': '#3E6B45',
        'bg_color': '#EEF5EF',
        'tagline': '深根靜長，秩序中綻放',
        'description': '你是一個有條理、有原則的女性，做事腳踏實地，讓人感到可靠與安心。你的美，在於那份沉穩的力量——不需要喧嘩，也能在任何場合站穩自己的位置。當你用同樣的邏輯整理衣櫃，你的風格將既清晰又有力。',
        'advice': '建立屬於自己的穿搭系統，規律中自然生出優雅。',
    },
    5: {
        'name': '土',
        'english': 'Earth',
        'color': '#7A5C1E',
        'bg_color': '#F8F3EA',
        'tagline': '大地為心，四方皆歸',
        'description': '你是一個內心自由、不受框架束縛的女性，同時又有著厚實的包容力作為根基。你的美，在於那份獨特的平衡——你能穩住自己，也能帶著好奇心探索未知。當你允許自己的風格自由生長，你將展現出最豐盛的能量場。',
        'advice': '今天試試一個你從未嘗試過的風格，探索就是你最好的成長。',
    },
    6: {
        'name': '金',
        'english': 'Metal',
        'color': '#B8860B',
        'bg_color': '#FDF8EE',
        'tagline': '智慧如光，溫柔有力',
        'description': '你是一個充滿智慧與關懷的女性，對身邊的人有著天然的責任感與保護欲。你的美，在於那份溫柔而堅定的力量——你知道如何照顧他人，也懂得在關係中保持優雅。當你學會將這份愛先給自己，你的風格將散發出成熟而迷人的光芒。',
        'advice': '為自己選一件真正讓你感到被呵護的衣服，照顧自己是一切的開始。',
    },
    7: {
        'name': '水',
        'english': 'Water',
        'color': '#2C6E8A',
        'bg_color': '#EEF5F8',
        'tagline': '靜水深流，智者自知',
        'description': '你擁有敏銳的洞察力與深刻的內省能力，能看見他人看不見的層次。你的美，在於那份深邃的智慧——你不輕易表態，卻總在關鍵時刻給出最精準的判斷。當你信任自己的直覺來選擇風格，你的品味將令人難以忘懷。',
        'advice': '少即是多，讓穿著保留留白，你的氣質自然流露。',
    },
    8: {
        'name': '火',
        'english': 'Fire',
        'color': '#A83222',
        'bg_color': '#FDF0EE',
        'tagline': '炎炎向上，格局燃天',
        'description': '你是一個有使命感、有格局的女性，心中燃燒著對成就與影響力的渴望。你的美，在於那份讓人信服的氣場——你的存在本身就帶著一種領袖的份量。當你讓外在形象配得上你的內在格局，你將成為最令人印象深刻的存在。',
        'advice': '投資一件讓你感到「配得上」的單品，形象是最值得的資產。',
    },
    9: {
        'name': '木',
        'english': 'Wood',
        'color': '#3E6B45',
        'bg_color': '#EEF5EF',
        'tagline': '木秀於林，圓滿天成',
        'description': '你是一個胸懷廣闊、充滿博愛精神的女性，身上有著整合一切、走向圓滿的力量。你的美，在於那份超越個人的眼界——你不只為自己而美，你的能量是一種分享與連結。當你讓風格反映你的心量，你將吸引與你同頻的美好。',
        'advice': '穿出你希望世界看到的樣子，你的能量將吸引與你共鳴的一切。',
    },
}


def get_db():
    conn = sqlite3.connect(DATABASE)
    return conn


def init_db():
    conn = get_db()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS calculations (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            birth_date TEXT NOT NULL,
            k_value   INTEGER NOT NULL,
            element   TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS registrations (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            phone      TEXT NOT NULL,
            email      TEXT NOT NULL,
            line_id    TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS webinar_registrations (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            name       TEXT NOT NULL,
            phone      TEXT NOT NULL,
            email      TEXT NOT NULL,
            line_id    TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.execute('''
        CREATE TABLE IF NOT EXISTS shopline_payments (
            id                 INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id           TEXT UNIQUE,
            event_type         TEXT,
            email              TEXT,
            phone              TEXT,
            name               TEXT,
            amount             TEXT,
            harvest_contact_id TEXT,
            raw_payload        TEXT,
            created_at         TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/calculate', methods=['POST'])
def calculate():
    try:
        from datetime import date as DateType
        year  = int(request.form['year'])
        month = int(request.form['month'])
        day   = int(request.form['day'])
        birth = DateType(year, month, day)
        result = calculate_wuxing(birth.year, birth.month, birth.day)
        element_info = ELEMENT_DATA[result['K']]

        conn = get_db()
        conn.execute(
            'INSERT INTO calculations (birth_date, k_value, element) VALUES (?, ?, ?)',
            (birth.isoformat(), result['K'], result['element'])
        )
        conn.commit()
        conn.close()

        birth_label = f"{birth.year}年{birth.month}月{birth.day}日"
        return render_template(
            'result.html',
            birth_date=birth_label,
            k_value=result['K'],
            element_info=element_info,
            gamma_link=GAMMA_LINK,
        )
    except (ValueError, KeyError):
        return render_template('index.html', error='請輸入有效的出生日期')


@app.route('/quiz')
def quiz():
    return render_template('index.html', form_action='/quiz/calculate')


@app.route('/quiz/calculate', methods=['POST'])
def quiz_calculate():
    try:
        from datetime import date as DateType
        year  = int(request.form['year'])
        month = int(request.form['month'])
        day   = int(request.form['day'])
        birth = DateType(year, month, day)
        result = calculate_wuxing(birth.year, birth.month, birth.day)
        element_info = ELEMENT_DATA[result['K']]

        conn = get_db()
        conn.execute(
            'INSERT INTO calculations (birth_date, k_value, element) VALUES (?, ?, ?)',
            (birth.isoformat(), result['K'], result['element'])
        )
        conn.commit()
        conn.close()

        birth_label = f"{birth.year}年{birth.month}月{birth.day}日"
        return render_template(
            'result.html',
            birth_date=birth_label,
            k_value=result['K'],
            element_info=element_info,
            gamma_link=LINE_OA_LINK,
        )
    except (ValueError, KeyError):
        return render_template('index.html', error='請輸入有效的出生日期')


@app.route('/daily')
def daily():
    from datetime import datetime
    import pytz
    today = datetime.now(pytz.timezone('Asia/Taipei')).date()
    digits = [int(d) for d in today.strftime('%Y%m%d')]
    total = sum(digits)
    while total >= 10:
        total = sum(int(d) for d in str(total))
    number = total

    # 五行元素資料（顏色、文字色）
    ELEMENTS = {
        '金': {'english': 'Metal', 'color': '#B8860B', 'colors': [('#FFFFFF','白色'), ('#C9A96E','金色'), ('#C0C0C0','銀色')]},
        '水': {'english': 'Water', 'color': '#2C6E8A', 'colors': [('#1A1A2E','深藍黑'), ('#2C6E8A','藏青藍'), ('#4A4A6A','靛紫灰')]},
        '火': {'english': 'Fire',  'color': '#A83222', 'colors': [('#A83222','酒紅'), ('#E8601C','橙紅'), ('#7B2D8B','深紫')]},
        '木': {'english': 'Wood',  'color': '#3E6B45', 'colors': [('#3E6B45','森林綠'), ('#6BAF7A','嫩草綠'), ('#5B9E9E','青碧色')]},
        '土': {'english': 'Earth', 'color': '#7A5C1E', 'colors': [('#C8A96E','暖駝色'), ('#7A5C1E','深棕'), ('#E8D5B0','米麥色')]},
    }

    # 相生順序：木→火→土→金→水→木
    GENERATES = {'木': '火', '火': '土', '土': '金', '金': '水', '水': '木'}
    # 反推：誰生了我（消耗來源）
    GENERATED_BY = {v: k for k, v in GENERATES.items()}

    NUMBER_TO_ELEMENT = {1:'金', 2:'水', 3:'火', 4:'木', 5:'土',
                         6:'金', 7:'水', 8:'火', 9:'木'}

    daily_elem  = NUMBER_TO_ELEMENT[number]
    noble_elem  = GENERATES[daily_elem]      # 我生的 → 貴人色
    drain_elem  = GENERATED_BY[daily_elem]   # 生我的 → 消耗色

    DAILY_DATA = {
        1: {'element': '金', 'english': 'Metal', 'color': '#B8860B', 'bg': '#FDF8EE',
            'message': '今天清醒而自信，穿出金屬般的光芒。'},
        2: {'element': '水', 'english': 'Water', 'color': '#2C6E8A', 'bg': '#EEF5F8',
            'message': '深邃的水色系，讓你的智慧與沉靜在今天最閃耀。'},
        3: {'element': '火', 'english': 'Fire', 'color': '#A83222', 'bg': '#FDF0EE',
            'message': '今天用火的溫度點亮自己，大膽穿出你最有力量的顏色。'},
        4: {'element': '木', 'english': 'Wood', 'color': '#3E6B45', 'bg': '#EEF5EF',
            'message': '今天用自然的綠意提醒自己：紮根，才能向上生長。'},
        5: {'element': '土', 'english': 'Earth', 'color': '#7A5C1E', 'bg': '#F8F3EA',
            'colors': [('#C8A96E','暖駝色'), ('#7A5C1E','深棕'), ('#E8D5B0','米麥色')],
            'message': '土的包容與穩定，今天讓大地色系成為你最安心的力量。'},
        6: {'element': '金', 'english': 'Metal', 'color': '#B8860B', 'bg': '#FDF8EE',
            'colors': [('#FFFFFF','白色'), ('#C9A96E','金色'), ('#C0C0C0','銀色')],
            'message': '今天穿上金屬光澤或純淨白，讓你的清醒與自信一眼可見。'},
        7: {'element': '水', 'english': 'Water', 'color': '#2C6E8A', 'bg': '#EEF5F8',
            'message': '深邃的水色系，讓你的智慧與沉靜在今天最閃耀。'},
        8: {'element': '火', 'english': 'Fire', 'color': '#A83222', 'bg': '#FDF0EE',
            'message': '今天用火的溫度點亮自己，大膽穿出你最有力量的顏色。'},
        9: {'element': '木', 'english': 'Wood', 'color': '#3E6B45', 'bg': '#EEF5EF',
            'message': '今天用自然的綠意提醒自己：紮根，才能向上生長。'},
    }

    info = DAILY_DATA[number]
    date_label = f"{today.year}年{today.month}月{today.day}日"
    return render_template('daily.html',
        today=date_label,
        number=number,
        info=info,
        noble_colors=ELEMENTS[noble_elem]['colors'],
        noble_elem=noble_elem,
        self_colors=ELEMENTS[daily_elem]['colors'],
        self_elem=daily_elem,
        drain_colors=ELEMENTS[drain_elem]['colors'],
        drain_elem=drain_elem,
    )


@app.route('/gift')
def gift():
    return render_template('gift.html')


def append_to_sheet(name, phone, email, line_id, source='風格覺醒營'):
    """將報名資料寫入 Google 試算表（背景執行）"""
    creds_json = os.environ.get('GOOGLE_CREDENTIALS_JSON', '')
    sheet_id   = os.environ.get('GOOGLE_SHEET_ID', '')
    if not creds_json or not sheet_id:
        print('[SHEET] 未設定 GOOGLE_CREDENTIALS_JSON 或 GOOGLE_SHEET_ID，略過')
        return
    try:
        import gspread
        from google.oauth2.service_account import Credentials
        creds = Credentials.from_service_account_info(
            json.loads(creds_json),
            scopes=['https://www.googleapis.com/auth/spreadsheets']
        )
        ws = gspread.authorize(creds).open_by_key(sheet_id).sheet1
        ws.append_row([
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            name, phone, email, line_id or '未填寫', source
        ])
        print(f'[SHEET] 已寫入：{name}')
    except Exception as e:
        print(f'[SHEET] 寫入失敗：{e}')


def send_registration_email(name, phone, email, line_id, source='風格覺醒營'):
    gmail_pass = os.environ.get('GMAIL_APP_PASSWORD', '')
    if not gmail_pass:
        return
    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = GMAIL_RECIPIENT
    msg['Subject'] = f'【美想道】{source}新報名：{name}'
    body = (
        f"新報名通知\n\n"
        f"姓名：{name}\n"
        f"手機：{phone}\n"
        f"Email：{email}\n"
        f"LINE ID：{line_id or '未填寫'}\n\n"
        f"報名時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    try:
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=15) as server:
            server.starttls()
            server.login(GMAIL_USER, gmail_pass)
            server.send_message(msg)
        print(f'[EMAIL] 報名通知已寄出：{name}')
    except Exception as e:
        print(f'[EMAIL] 寄信失敗：{e}')


def verify_shopline_signature(raw_body, timestamp, sign, sign_key, max_age_seconds=300):
    """驗證 Shopline Payments Webhook 簽章
    規則（見 SHOPLINE 串接文件「簽章演算法」）：
    sign = hmacSha256(f'{timestamp}.{body}', signKey)
    另外拒絕過舊的 timestamp，防止重播攻擊。
    """
    import hmac
    import hashlib
    import time
    if not timestamp or not sign:
        return False
    try:
        ts_ms = int(timestamp)
    except ValueError:
        return False
    now_ms = int(time.time() * 1000)
    if abs(now_ms - ts_ms) > max_age_seconds * 1000:
        print(f'[SHOPLINE] timestamp 過期或異常：{timestamp}')
        return False
    body_str = raw_body.decode('utf-8') if isinstance(raw_body, bytes) else raw_body
    payload = f'{timestamp}.{body_str}'
    expected = hmac.new(sign_key.encode('utf-8'), payload.encode('utf-8'), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, sign)


def harvest_ai_upsert_contact(email, phone, name):
    """在 Harvest AI (GoHighLevel) 建立/更新聯絡人，回傳 contactId"""
    import requests as req
    token = os.environ.get('HARVEST_AI_PIT_TOKEN', '')
    location_id = os.environ.get('HARVEST_AI_LOCATION_ID', '')
    if not token or not location_id:
        print('[HARVEST] 未設定 HARVEST_AI_PIT_TOKEN / HARVEST_AI_LOCATION_ID，略過同步')
        return None
    payload = {'locationId': location_id}
    if email:
        payload['email'] = email
    if phone:
        payload['phone'] = phone
    if name:
        payload['name'] = name
    try:
        r = req.post(
            'https://services.leadconnectorhq.com/contacts/upsert',
            headers={
                'Authorization': f'Bearer {token}',
                'Version': '2021-07-28',
                'Content-Type': 'application/json',
            },
            json=payload,
            timeout=15,
        )
        r.raise_for_status()
        contact_id = (r.json().get('contact') or {}).get('id')
        print(f'[HARVEST] 聯絡人已同步：{contact_id}')
        return contact_id
    except Exception as e:
        print(f'[HARVEST] upsert 聯絡人失敗：{e}')
        return None


def harvest_ai_add_tag(contact_id, tag):
    """幫 Harvest AI 聯絡人打標籤，觸發後續 Automation"""
    import requests as req
    token = os.environ.get('HARVEST_AI_PIT_TOKEN', '')
    if not contact_id or not token:
        return False
    try:
        r = req.post(
            f'https://services.leadconnectorhq.com/contacts/{contact_id}/tags',
            headers={
                'Authorization': f'Bearer {token}',
                'Version': '2021-07-28',
                'Content-Type': 'application/json',
            },
            json={'tags': [tag]},
            timeout=15,
        )
        r.raise_for_status()
        print(f'[HARVEST] 已打標籤：{tag}')
        return True
    except Exception as e:
        print(f'[HARVEST] 打標籤失敗：{e}')
        return False


def send_payment_notification_email(name, email, phone, amount, event_type):
    gmail_pass = os.environ.get('GMAIL_APP_PASSWORD', '')
    if not gmail_pass:
        return
    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = GMAIL_RECIPIENT
    msg['Subject'] = f'【美想道】收到付款通知：{name or email or phone or "未知學員"}'
    body = (
        f"Shopline 付款通知（已同步到 Harvest AI）\n\n"
        f"事件類型：{event_type}\n"
        f"姓名：{name or '未提供'}\n"
        f"Email：{email or '未提供'}\n"
        f"手機：{phone or '未提供'}\n"
        f"金額：{amount or '未提供'}\n\n"
        f"時間：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    msg.attach(MIMEText(body, 'plain', 'utf-8'))
    try:
        with smtplib.SMTP('smtp.gmail.com', 587, timeout=15) as server:
            server.starttls()
            server.login(GMAIL_USER, gmail_pass)
            server.send_message(msg)
        print('[EMAIL] 付款通知已寄出')
    except Exception as e:
        print(f'[EMAIL] 付款通知寄信失敗：{e}')


@app.route('/webhooks/shopline-payment', methods=['POST'])
def shopline_payment_webhook():
    """接收 Shopline Payments 付款成功通知，同步聯絡人與標籤到 Harvest AI。
    Webhook 名稱：五行決策系統-HarvestAI橋接（Shopline 後台 設定 > 開發者管理 > Webhook 管理）
    訂閱事件：session.succeeded, trade.succeeded
    """
    sign_key = os.environ.get('SHOPLINE_WEBHOOK_SIGN_KEY', '')
    timestamp = request.headers.get('timestamp', '')
    sign = request.headers.get('sign', '')
    raw_body = request.get_data()

    if not sign_key or not verify_shopline_signature(raw_body, timestamp, sign, sign_key):
        print('[SHOPLINE] 簽章驗證失敗，拒絕請求')
        return 'invalid signature', 401

    try:
        payload = json.loads(raw_body)
    except Exception:
        return 'invalid body', 400

    event_id = payload.get('id', '')
    event_type = payload.get('type', '')
    data = payload.get('data', {}) or {}

    if event_type not in ('session.succeeded', 'trade.succeeded'):
        return 'ignored', 200

    conn = get_db()
    existing = conn.execute(
        'SELECT id FROM shopline_payments WHERE event_id = ?', (event_id,)
    ).fetchone()
    if existing:
        conn.close()
        print(f'[SHOPLINE] 事件 {event_id} 已處理過，略過（webhook 重送）')
        return 'duplicate', 200

    order = data.get('order', {}) or {}
    customer = order.get('customer', {}) or data.get('customer', {}) or {}
    email = customer.get('email') or data.get('email') or ''
    phone = customer.get('phone') or data.get('phone') or ''
    name = customer.get('name') or data.get('name') or ''
    amount_obj = order.get('amount', {}) or data.get('amount', {}) or {}
    amount = f"{amount_obj.get('value', '')} {amount_obj.get('currency', '')}".strip()

    contact_id = None
    if email or phone:
        contact_id = harvest_ai_upsert_contact(email, phone, name)
        if contact_id:
            harvest_ai_add_tag(contact_id, '已付款-五行決策系統-首期')
    else:
        print(f'[SHOPLINE] 事件 {event_id} 沒有 email/phone，無法同步聯絡人，請人工檢查 raw_payload')

    conn.execute(
        'INSERT INTO shopline_payments '
        '(event_id, event_type, email, phone, name, amount, harvest_contact_id, raw_payload) '
        'VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
        (event_id, event_type, email, phone, name, amount, contact_id, raw_body.decode('utf-8'))
    )
    conn.commit()
    conn.close()

    threading.Thread(
        target=send_payment_notification_email,
        args=(name, email, phone, amount, event_type),
        daemon=True
    ).start()

    return 'ok', 200


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/register/submit', methods=['POST'])
def register_submit():
    name    = request.form.get('name', '').strip()
    phone   = request.form.get('phone', '').strip()
    email   = request.form.get('email', '').strip()
    line_id = request.form.get('line_id', '').strip()
    if not name or not phone or not email:
        return render_template('register.html', error='請填寫所有必填欄位')
    conn = get_db()
    conn.execute(
        'INSERT INTO registrations (name, phone, email, line_id) VALUES (?, ?, ?, ?)',
        (name, phone, email, line_id or None)
    )
    conn.commit()
    conn.close()
    threading.Thread(
        target=send_registration_email,
        args=(name, phone, email, line_id),
        daemon=True
    ).start()
    threading.Thread(
        target=append_to_sheet,
        args=(name, phone, email, line_id),
        daemon=True
    ).start()
    return redirect('/register/success')


@app.route('/register/success')
def register_success():
    return render_template('register_success.html')


@app.route('/webinar')
def webinar():
    return render_template('webinar.html', info=WEBINAR_INFO)


@app.route('/webinar/submit', methods=['POST'])
def webinar_submit():
    name    = request.form.get('name', '').strip()
    phone   = request.form.get('phone', '').strip()
    email   = request.form.get('email', '').strip()
    line_id = request.form.get('line_id', '').strip()
    if not name or not phone or not email:
        return render_template('webinar.html', info=WEBINAR_INFO, error='請填寫所有必填欄位')
    conn = get_db()
    conn.execute(
        'INSERT INTO webinar_registrations (name, phone, email, line_id) VALUES (?, ?, ?, ?)',
        (name, phone, email, line_id or None)
    )
    conn.commit()
    conn.close()
    threading.Thread(
        target=send_registration_email,
        args=(name, phone, email, line_id, '免費研討會'),
        daemon=True
    ).start()
    threading.Thread(
        target=append_to_sheet,
        args=(name, phone, email, line_id, '免費研討會'),
        daemon=True
    ).start()
    return redirect('/webinar/success')


@app.route('/webinar/success')
def webinar_success():
    return render_template('webinar_success.html', info=WEBINAR_INFO, line_link=LINE_OA_LINK)


@app.route('/broadcast', methods=['GET', 'POST'])
def broadcast_daily():
    """每日幸運色推播，讓 cron-job.org 每天早上呼叫此路由"""
    import requests as req
    from datetime import datetime
    import pytz

    CHANNEL_ID     = "2009971178"
    CHANNEL_SECRET = "1e4043dd9bd72c6ffdd5f5555714152e"
    GENERATES      = {'木':'火','火':'土','土':'金','金':'水','水':'木'}
    GENERATED_BY   = {v:k for k,v in GENERATES.items()}
    NUM_TO_ELEM    = {1:'金',2:'水',3:'火',4:'木',5:'土',6:'金',7:'水',8:'火',9:'木'}
    ELEM_EMOJI     = {'金':'⚪','水':'🔵','火':'🔴','木':'🟢','土':'🟡'}

    # 取 token
    r = req.post(
        "https://api.line.me/v2/oauth/accessToken",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data=f"grant_type=client_credentials&client_id={CHANNEL_ID}&client_secret={CHANNEL_SECRET}"
    )
    token = r.json().get("access_token")
    if not token:
        return "token error", 500

    # 計算流日（台灣時間）
    today = datetime.now(pytz.timezone('Asia/Taipei')).date()
    total = sum(int(d) for d in today.strftime('%Y%m%d'))
    while total >= 10:
        total = sum(int(d) for d in str(total))
    elem  = NUM_TO_ELEM[total]
    noble = GENERATES[elem]
    drain = GENERATED_BY[elem]

    msg = (
        f"✦ 美想道｜{today.month}月{today.day}日 每日幸運色\n\n"
        f"大環境流日【{total}】· 今日五行：{ELEM_EMOJI[elem]} {elem}\n\n"
        f"👑 貴人色：{noble}（輕鬆愉快，貴人加持）\n"
        f"💼 合作色：{elem}（商務合作，互利共贏）\n"
        f"⚠️ 消耗色：{drain}（今日不推薦）\n\n"
        f"➜ 查看完整色卡\n"
        f"https://wuxing-tool.onrender.com/daily?openExternalBrowser=1"
    )

    result = req.post(
        "https://api.line.me/v2/bot/message/broadcast",
        headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"},
        json={"messages": [{"type": "text", "text": msg}]}
    )
    status = "ok" if result.status_code == 200 else result.text
    print(f"[BROADCAST] {today} 推播：{status}")
    return f"broadcast {status}", result.status_code


init_db()

if __name__ == '__main__':
    app.run(debug=True)
