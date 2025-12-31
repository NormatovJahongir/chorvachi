# CHORVA FERMERI PRO v2.0 - Telegram Bot + Web App

Cho'rvachilik fermalarini boshqarish uchun zamonaviy dastur - Telegram bot va Web App integratsiyasi bilan.

## Xususiyatlar

### 🤖 Telegram Bot
- Avtomatik ro'yxatdan o'tish (kontakt va ism-sharif)
- Asosiy statistika va ma'lumotlar
- Telegram Web App integratsiyasi
- 3 tilni qo'llab-quvvatlash (O'zbekcha, Ruscha, Inglizcha)

### 🌐 Web App
- **Hayvonlar**: Hayvonlarni qo'shish, tahrirlash, o'chirish
- **Qassoblar**: Qassoblar ma'lumotlar bazasi (ommaviy qidiruv)
- **Sotuvlar**: Hayvonlarni sotish va avtomatik foyda hisoblash
- **Ozuqa**: Ozuqa xaridlari va avtomatik moliya qo'shish
- **Vaksinatsiya**: Vaksinatsiya jadvali va xarajatlar
- **Moliya**: To'liq moliya nazorati va statistika
- **Diagrammalar**: Chart.js bilan vizualizatsiya

### 💰 Narx kiritish muammosi to'liq hal qilingan!
- Input type="text" bilan raqamlar
- Avtomatik formatlash (1,000,000)
- Focus/blur da to'g'ri konvertatsiya
- Barcha narxlar uchun ishlaydi

## O'rnatish

### 1. Lokal ishga tushirish

```bash
# Loyihani yuklab olish
cd chorva_fermeri_bot

# Virtual environment yaratish (ixtiyoriy)
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Kutubxonalarni o'rnatish
pip install -r requirements.txt

# .env faylni sozlash
cp .env.example .env
# .env faylda BOT_TOKEN va ADMIN_IDS ni to'ldiring

# Database yaratish va Flask ishga tushirish
python app.py

# Boshqa terminalda bot ishga tushirish
python telegram_bot.py
```

### 2. Render.com orqali bepul deploy qilish

#### Bosqich 1: GitHub repositoriya yaratish

1. GitHub.com ga kiring
2. Yangi repository yarating (masalan: `chorva-fermeri-bot`)
3. Loyihani repositoriyaga yuklang:

```bash
cd chorva_fermeri_bot
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/USERNAME/chorva-fermeri-bot.git
git push -u origin main
```

#### Bosqich 2: Render.com sozlash

1. **Render.com** ga kiring: https://render.com
2. GitHub akkaunt bilan ro'yxatdan o'ting
3. **New +** tugmasini bosing va **Web Service** tanlang
4. GitHub repositoriyangizni ulang
5. Quyidagi sozlamalarni kiriting:

**Basic Settings:**
- **Name**: `chorva-fermeri-bot` (yoki o'zingiz xohlagan nom)
- **Region**: `Oregon` (bepul)
- **Branch**: `main`
- **Root Directory**: bo'sh qoldiring
- **Runtime**: `Python 3`

**Build & Deploy:**
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app & python bot.py`

**Environment Variables (muhim!):**
1. `BOT_TOKEN` = @BotFather dan olgan token
2. `ADMIN_IDS` = Telegram ID laringiz (vergul bilan ajratilgan)
3. `SECRET_KEY` = Avtomatik generatsiya qilinadi
4. `WEBHOOK_URL` = https://YOUR-APP-NAME.onrender.com
5. `PORT` = 10000

6. **Create Web Service** tugmasini bosing

#### Bosqich 3: Telegram bot tokenni olish

1. Telegram da **@BotFather** ga yozing
2. `/newbot` buyrug'ini yuboring
3. Bot nomi va username kiriting
4. Token olasiz (masalan: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`)
5. Tokenni Render.com dagi `BOT_TOKEN` ga qo'ying

#### Bosqich 4: Telegram ID ni olish

1. Telegram da **@userinfobot** ga yozing
2. Start bosing
3. Sizning ID ni ko'rsatadi (masalan: `123456789`)
4. ID ni Render.com dagi `ADMIN_IDS` ga qo'ying

#### Bosqich 5: Webhook URL ni sozlash

1. Render.com sizga URL beradi: `https://your-app-name.onrender.com`
2. Ushbu URL ni `WEBHOOK_URL` environmentga qo'ying
3. Deploy qilishni kuting (3-5 daqiqa)

### Muhim eslatmalar

⚠️ **Render.com bepul rejasida:**
- 15 daqiqa aktivlik bo'lmasa, dastur o'chadi
- Har safar birinchi so'rovda 50 sekund kutish kerak
- Oyiga 750 soat bepul

✅ **Doimiy ishlashi uchun:**
- UptimeRobot.com dan foydalaning (bepul ping xizmati)
- Har 5 daqiqada ping qiladi va dasturni uyg'otadi

## Foydalanish

### Telegram Bot

1. Botni toping va `/start` bosing
2. Telefon raqamingizni yuboring
3. Ism-sharifingizni kiriting
4. "Dasturni ochish" tugmasini bosing - Web App ochiladi!

### Buyruqlar

- `/start` - Boshlovchi
- `/dashboard` - Statistika
- `/animals` - Hayvonlar ro'yxati
- `/butchers` - Qassoblar ro'yxati
- `/language` - Tilni o'zgartirish
- `/help` - Yordam

## Texnologiyalar

### Backend
- Python 3.11+
- Flask 3.0 (Web framework)
- python-telegram-bot 20.7 (Bot)
- SQLite (Database)

### Frontend
- HTML5, CSS3 (Yashil dizayn)
- JavaScript (Vanilla JS)
- Chart.js 4.0 (Diagrammalar)
- Font Awesome 6.4 (Ikonkalar)
- Telegram Web App SDK

### Deployment
- Gunicorn (WSGI server)
- Render.com (Hosting)

## Fayl tuzilishi

```
chorva_fermeri_bot/
├── app.py              # Flask web application
├── telegram_bot.py     # Telegram bot
├── config.py           # Konfiguratsiya va tarjimalar
├── database.py         # Database operatsiyalar
├── requirements.txt    # Python kutubxonalar
├── render.yaml         # Render.com sozlamalari
├── .env.example        # Muhit o'zgaruvchilari namunasi
├── bot/
│   └── handlers.py     # Bot handlerlar
├── static/
│   ├── css/
│   │   └── style.css   # Yashil dizayn CSS
│   └── js/
│       └── main.js     # JavaScript funksiyalar
└── templates/
    ├── base.html       # Asosiy shablon
    ├── dashboard.html  # Bosh sahifa
    ├── animals.html    # Hayvonlar
    ├── butchers.html   # Qassoblar
    ├── sales.html      # Sotuvlar
    ├── feed.html       # Ozuqa
    ├── vaccinations.html # Vaksinatsiya
    └── finance.html    # Moliya
```

## Muammolarni hal qilish

### Bot javob bermayapti
- BOT_TOKEN to'g'ri kiritilganligini tekshiring
- Render.com deploy muvaffaqiyatli o'tganligini tekshiring
- Logs ni ko'ring: Render.com > Logs

### Web App ochilmayapti
- WEBHOOK_URL to'g'riligini tekshiring
- Browser console da xatolarni tekshiring
- Flask server ishlab turganligini tekshiring

### Narx kiritishda xatolik
- Faqat raqamlar kiriting (vergul avtomatik qo'shiladi)
- Focus qilganingizda oddiy raqam ko'rsatiladi
- Blur qilganingizda formatlangan raqam (1,000,000)

## Muallif

**CHORVA FERMERI PRO v2.0**
© 2025 - Barcha huquqlar himoyalangan

## Litsenziya

Ushbu dastur shaxsiy foydalanish uchun bepul.

---

📱 Telegram: @YOUR_TELEGRAM
🌐 Web: https://your-app-name.onrender.com
