from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import database as db
from config import SECRET_KEY, TRANSLATIONS
from datetime import datetime
import threading
import bot  # Botni ishga tushirish uchun bot.py faylini import qilamiz
import os

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Context processor - barcha template uchun
@app.context_processor
def inject_translation():
    def t(key):
        lang = session.get('language', 'uz')
        return TRANSLATIONS.get(lang, {}).get(key, key)
    return dict(t=t)

# ==================== WEB APP ROUTES ====================

@app.route('/')
@app.route('/dashboard')
def dashboard():
    """Bosh sahifa"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
    # Statistika
    animals_stats = db.get_animals_stats(int(user_id))
    finance_stats = db.get_finance_stats(int(user_id))
    
    return render_template('dashboard.html', 
                         animals_stats=animals_stats,
                         finance_stats=finance_stats)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login sahifasi"""
    if request.method == 'POST':
        telegram_id = request.form.get('telegram_id')
        if telegram_id:
            user = db.get_user(int(telegram_id))
            if user:
                session['user_id'] = telegram_id
                session['language'] = user.get('language', 'uz')
                return redirect(url_for('dashboard'))
            else:
                return render_template('login.html', error='Foydalanuvchi topilmadi. Telegram botda /start bosing.')
    return render_template('login.html')

# app.py ichida namuna
@app.route('/delete-animal/<int:id>')
def delete_animal_simple_route(id):
    user_id = session.get('user_id')
    if user_id:
        db.delete_animal(id))
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))
@app.route('/logout')
def logout():
    """Logout"""
    session.clear()
    return redirect(url_for('login'))

@app.route('/webapp')
def webapp():
    """Telegram Web App - AVTOMATIK LOGIN"""
    # Telegram dan user_id olish
    user_id = request.args.get('user_id')
    
    # Agar user_id URL da bo'lmasa, Telegram Web App initData dan olishga harakat qilamiz
    if not user_id:
        # Bu yerda frontend initData dan user_id ni olishi kerak
        # Hozircha xato qaytaramiz
        return render_template('webapp_init.html')
    
    # Foydalanuvchini tekshirish
    user = db.get_user(int(user_id))
    if not user:
        return f"Foydalanuvchi topilmadi (ID: {user_id}). Telegram botda /start bosing.", 404
    
    # AVTOMATIK LOGIN
    session['user_id'] = user_id
    session['language'] = user.get('language', 'uz')
    
    # Oxirgi faollikni yangilash
    db.update_user_last_active(int(user_id))
    
    # Dashboard ga yo'naltirish
    page = request.args.get('page', 'dashboard')
    return redirect(url_for(page))

@app.route('/animals')
def animals():
    """Hayvonlar sahifasi"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    return render_template('animals.html')

@app.route('/butchers')
def butchers():
    """Qassoblar sahifasi"""
    if not session.get('user_id'):
        return redirect(url_for('login'))
    return render_template('butchers.html')

@app.route('/sales')
def sales():
    """Sotuvlar sahifasi"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    return render_template('sales.html')

@app.route('/feed')
def feed():
    """Ozuqa sahifasi"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    return render_template('feed.html')

@app.route('/vaccinations')
def vaccinations():
    """Vaksinatsiya sahifasi"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    return render_template('vaccinations.html')

@app.route('/finance')
def finance():
    """Moliya sahifasi"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    return render_template('finance.html')

# ==================== API ENDPOINTS ====================

@app.route('/api/language', methods=['POST'])
def set_language():
    """Tilni o'zgartirish"""
    data = request.json
    lang = data.get('language', 'uz')
    session['language'] = lang
    
    user_id = session.get('user_id')
    if user_id:
        db.update_user_language(int(user_id), lang)
    
    return jsonify({'success': True})

# ==================== ANIMALS API ====================

@app.route('/api/animals', methods=['GET'])
def get_animals():
    """Hayvonlarni olish"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    animals = db.get_animals(int(user_id))
    return jsonify(animals)

@app.route('/api/animals', methods=['POST'])
def create_animal():
    """Hayvon qo'shish"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    animal_id = db.add_animal(
        user_id=int(user_id),
        animal_type=data['type'],
        breed=data['breed'],
        gender=data['gender'],
        birth_date=data.get('birth_date'),
        weight=float(data['weight']) if data.get('weight') else None,
        purchase_price=float(data['purchase_price']),
        purchase_date=data['purchase_date']
    )
    return jsonify({'success': True, 'id': animal_id})

@app.route('/api/animals/<int:animal_id>', methods=['PUT'])
def update_animal(animal_id):
    """Hayvonni yangilash"""
    data = request.json
    db.update_animal(animal_id, **data)
    return jsonify({'success': True})

@app.route('/api/animals/<int:animal_id>', methods=['DELETE'])
def api_delete_animal_route(animal_id):
    """Hayvonni o'chirish"""
    db.delete_animal(animal_id)
    return jsonify({'success': True})

@app.route('/api/animals/stats', methods=['GET'])
def get_animals_stats():
    """Hayvonlar statistikasi"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    stats = db.get_animals_stats(int(user_id))
    return jsonify(stats)

# ==================== BUTCHERS API ====================

@app.route('/api/butchers', methods=['GET'])
def get_butchers_route():
    """Qassoblarni olish"""
    search = request.args.get('search')
    butchers = db.get_butchers(search)
    return jsonify(butchers)

@app.route('/api/butchers', methods=['POST'])
def create_butcher():
    """Qassob qo'shish"""
    data = request.json
    butcher_id = db.add_butcher(
        name=data['name'],
        phone=data['phone'],
        address=data.get('address'),
        experience=int(data['experience']) if data.get('experience') else None,
        notes=data.get('notes')
    )
    return jsonify({'success': True, 'id': butcher_id})

@app.route('/api/butchers/<int:butcher_id>', methods=['PUT'])
def update_butcher_route(butcher_id):
    """Qassobni yangilash"""
    data = request.json
    db.update_butcher(butcher_id, **data)
    return jsonify({'success': True})

@app.route('/api/butchers/<int:butcher_id>', methods=['DELETE'])
def delete_butcher_route(butcher_id):
    """Qassobni o'chirish"""
    db.delete_butcher(butcher_id)
    return jsonify({'success': True})

# ==================== SALES API ====================

@app.route('/api/sales', methods=['GET'])
def get_sales_route():
    """Sotuvlarni olish"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    sales = db.get_sales(int(user_id))
    return jsonify(sales)

@app.route('/api/sales', methods=['POST'])
def create_sale():
    """Sotuv qo'shish"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    sale_id = db.add_sale(
        user_id=int(user_id),
        animal_id=int(data['animal_id']),
        butcher_id=int(data['butcher_id']) if data.get('butcher_id') else None,
        sale_date=data['sale_date'],
        sale_price=float(data['sale_price']),
        buyer_name=data.get('buyer_name'),
        buyer_phone=data.get('buyer_phone'),
        payment_type=data.get('payment_type', 'cash')
    )
    
    if sale_id:
        return jsonify({'success': True, 'id': sale_id})
    else:
        return jsonify({'error': 'Animal not found'}), 404

@app.route('/api/sales/<int:sale_id>', methods=['DELETE'])
def delete_sale_route(sale_id):
    """Sotuvni o'chirish"""
    db.delete_sale(sale_id)
    return jsonify({'success': True})

@app.route('/api/animals/<int:animal_id>/details', methods=['GET'])
def get_animal_details(animal_id):
    """Hayvon ma'lumotlari"""
    animal = db.get_animal(animal_id)
    if animal:
        return jsonify(animal)
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/butchers/<int:butcher_id>/details', methods=['GET'])
def get_butcher_details(butcher_id):
    """Qassob ma'lumotlari"""
    butcher = db.get_butcher(butcher_id)
    if butcher:
        return jsonify(butcher)
    return jsonify({'error': 'Not found'}), 404

# ==================== FEED API ====================

@app.route('/api/feed', methods=['GET'])
def get_feed_route():
    """Ozuqalarni olish"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    feed = db.get_feed(int(user_id))
    return jsonify(feed)

@app.route('/api/feed', methods=['POST'])
def create_feed():
    """Ozuqa qo'shish"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    feed_id = db.add_feed(
        user_id=int(user_id),
        name=data['name'],
        quantity=float(data['quantity']),
        unit_price=float(data['unit_price']),
        supplier=data.get('supplier'),
        feed_date=data['feed_date']
    )
    return jsonify({'success': True, 'id': feed_id})

@app.route('/api/feed/<int:feed_id>', methods=['DELETE'])
def delete_feed_route(feed_id):
    """Ozuqani o'chirish"""
    db.delete_feed(feed_id)
    return jsonify({'success': True})

# ==================== VACCINATIONS API ====================

@app.route('/api/vaccinations', methods=['GET'])
def get_vaccinations_route():
    """Vaksinatsiyalarni olish"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    vaccinations = db.get_vaccinations(int(user_id))
    return jsonify(vaccinations)

@app.route('/api/vaccinations', methods=['POST'])
def create_vaccination():
    """Vaksinatsiya qo'shish"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    vaccination_id = db.add_vaccination(
        user_id=int(user_id),
        animal_id=int(data['animal_id']),
        vaccine_name=data['vaccine_name'],
        vaccination_date=data['vaccination_date'],
        next_date=data.get('next_date'),
        veterinarian=data.get('veterinarian'),
        cost=float(data['cost']) if data.get('cost') else None
    )
    return jsonify({'success': True, 'id': vaccination_id})

@app.route('/api/vaccinations/<int:vaccination_id>', methods=['DELETE'])
def delete_vaccination_route(vaccination_id):
    """Vaksinatsiyani o'chirish"""
    db.delete_vaccination(vaccination_id)
    return jsonify({'success': True})

# ==================== FINANCE API ====================

@app.route('/api/finance', methods=['GET'])
def get_finance_route():
    """Moliyalarni olish"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    finance = db.get_finance(int(user_id))
    return jsonify(finance)

@app.route('/api/finance', methods=['POST'])
def create_finance():
    """Moliya qo'shish"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.json
    finance_id = db.add_finance(
        user_id=int(user_id),
        finance_type=data['type'],
        amount=float(data['amount']),
        category=data['category'],
        description=data.get('description'),
        date=data['date']
    )
    return jsonify({'success': True, 'id': finance_id})

@app.route('/api/finance/<int:finance_id>', methods=['DELETE'])
def delete_finance_route(finance_id):
    """Moliyani o'chirish"""
    db.delete_finance(finance_id)
    return jsonify({'success': True})

@app.route('/api/finance/stats', methods=['GET'])
def get_finance_stats_route():
    """Moliya statistikasi"""
    user_id = session.get('user_id')
    if not user_id:
        return jsonify({'error': 'Unauthorized'}), 401
    
    stats = db.get_finance_stats(int(user_id))
    return jsonify(stats)

@app.route('/ping')
def ping():
    return "Bot is alive!", 200
    
if __name__ == '__main__':
    # 1. Ma'lumotlar bazasini tekshirish
    db.init_db()
    
    # 2. Telegram Botni alohida Thread (oqim) ichida ishga tushirish
    # Bu orqali Flask va Bot bir vaqtda ishlaydi
    def run_bot():
        print("🤖 Telegram bot ishga tushmoqda...")
        bot.main() # bot.py ichidagi main() funksiyasini chaqiradi

    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True # Flask to'xtasa, bot ham to'xtaydi
    bot_thread.start()

    print("=" * 50)
    print("🌐 CHORVA FERMERI PRO WEB SERVER")
    print("=" * 50)
    
    # 3. Render portini aniqlash va Flaskni yurgizish
    # Render avtomatik PORT beradi, agar bermasa 5000 ishlatiladi
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
