import sqlite3
from datetime import datetime
from flask import Flask, render_template, request
from calculator import calculate_wuxing

app = Flask(__name__)
DATABASE = 'wuxing.db'

GAMMA_LINK = 'https://gamma.app/docs/-df8wl8nfu0ykcin?openExternalBrowser=1'

ELEMENT_DATA = {
    '金': {
        'name': '金',
        'english': 'Metal',
        'color': '#B8860B',
        'bg_color': '#FDF8EE',
        'tagline': '清透如刃，從容綻放',
        'description': '你是一個對自我有高度要求的人，內心藏有清晰的原則與底線。你的美，在於那份不妥協的清醒——你知道自己要什麼，也敢於堅守。當你學會將內在的標準，轉化為對自己的慈悲而非批判，你的光將無可擋。',
        'advice': '練習放下「完美」的框架，讓真實的自己被看見。',
    },
    '水': {
        'name': '水',
        'english': 'Water',
        'color': '#2C6E8A',
        'bg_color': '#EEF5F8',
        'tagline': '深流無聲，智慧如淵',
        'description': '你擁有超乎常人的感知力，能感受到他人察覺不到的細微能量。你的美，在於流動的智慧——你懂得等待時機，懂得以柔克剛。當你不再壓抑內心的聲音，而是信任它，你的人生將如水，找到最美的方向。',
        'advice': '給自己安靜的時間，與內在的直覺對話。',
    },
    '火': {
        'name': '火',
        'english': 'Fire',
        'color': '#A83222',
        'bg_color': '#FDF0EE',
        'tagline': '熱烈如焰，點亮四方',
        'description': '你是天生的光源，走進一個空間就能改變氛圍。你的美，在於那份真摯的熱情——你的存在本身就是一種感染力。當你將這份能量向內滋養自己，你將從「燃燒自己」走向「持續發光」。',
        'advice': '學習在給予之前，先填滿自己的能量。',
    },
    '木': {
        'name': '木',
        'english': 'Wood',
        'color': '#3E6B45',
        'bg_color': '#EEF5EF',
        'tagline': '向陽而生，破土而長',
        'description': '你有著強烈的成長渴望與生命力，心中永遠有一個更好的自己在等待。你的美，在於那份永不停歇的向上力——你相信明天可以比今天更好。當你學會在前進中紮穩根基，你的綻放將更深遠、更持久。',
        'advice': '給自己的成長多一些耐心，根越深，花越美。',
    },
    '土': {
        'name': '土',
        'english': 'Earth',
        'color': '#7A5C1E',
        'bg_color': '#F8F3EA',
        'tagline': '厚德載物，萬物歸心',
        'description': '你是周遭人的依靠，有著天然的包容力與安定感。你的美，在於那份讓人安心的存在——你是別人生命中那塊踏實的土地。當你學會將這份愛先給自己，你將發現，你本身就是最豐盛的能量場。',
        'advice': '在照顧他人之前，記得先照顧好自己。',
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
        element_info = ELEMENT_DATA[result['element']]

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


init_db()

if __name__ == '__main__':
    app.run(debug=True)
