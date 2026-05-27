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
DATABASE = 'wuxing.db'
GMAIL_USER = 'tangyuxi1002@gmail.com'
GMAIL_RECIPIENT = 'mxd@mxdyes.com'

GAMMA_LINK = 'https://gamma.app/docs/-df8wl8nfu0ykcin?openExternalBrowser=1'

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


@app.route('/gift')
def gift():
    return render_template('gift.html')


def send_registration_email(name, phone, email, line_id):
    gmail_pass = os.environ.get('GMAIL_APP_PASSWORD', '')
    if not gmail_pass:
        return
    msg = MIMEMultipart()
    msg['From'] = GMAIL_USER
    msg['To'] = GMAIL_RECIPIENT
    msg['Subject'] = f'【美想道】風格覺醒營新報名：{name}'
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
    return redirect('/register/success')


@app.route('/register/success')
def register_success():
    return render_template('register_success.html')


init_db()

if __name__ == '__main__':
    app.run(debug=True)
