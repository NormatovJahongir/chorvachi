from flask import Flask, render_template, request, jsonify, session, redirect, url_for
import database as db
from config import SECRET_KEY, TRANSLATIONS
from datetime import datetime
import threading
import bot  # Botni ishga tushirish uchun bot.py faylini import qilamiz
import os

app = Flask(__name__)
app.secret_key = SECRET_KEY

# Context processor - barcha template uchun tarjima funksiyasi
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
    """Bosh sahifa statistika bilan"""
    user_id = session.get('user_id')
    if not user_id:
        return redirect(url_for('login'))
    
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

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/webapp')
def webapp():
    user_id = request.args.get('user_id')
    if not user_id:
        return render_template('webapp_init.html')
    
    user = db.get_user(int(user_id))
    if not user:
        return f"Foydalanuvchi topilmadi. Botda /start bosing.", 404
    
    session['user_id'] = user_id
    session['language'] = user.get('language', 'uz')
    db.update_user_last_active(int(user_id))
    
    page = request.args.get('page', 'dashboard')
    return redirect(url_for(page))

# Sahifalar uchun routelar
@app.route('/animals')
def animals(): return render_template('animals.html') if session.get('user_id') else redirect(url_for('login'))

@app.route('/butchers')
def butchers(): return render_template('butchers.html') if session.get('user_id') else redirect(url_for('login'))

@app.route('/sales')
def sales(): return render_template('sales.html') if session.get('user_id') else redirect(url_for('login'))

@app.route('/feed')
def feed(): return render_template('feed.html') if session.get('user_id') else redirect(url_for('login'))

@app.route('/vaccinations')
def vaccinations(): return render_template('vaccinations.html') if session.get('user_id') else redirect(url_for('login'))

@app.route('/finance')
def finance(): return render_template('finance.html') if session.get('user_id') else redirect(url_for('login'))

# ==================== API ENDPOINTS ====================

@app.route('/api/language', methods=['POST'])
def set_language():
    data = request.json
    lang = data.get('language', 'uz')
    session['language'] = lang
    user_id = session.get('user_id')
    if user_id:
        db.update_user_language(int(user_id), lang)
    return jsonify({'success': True})

# --- ANIMALS API ---
@app.route('/api/animals', methods=['GET', 'POST'])
def handle_animals():
    user_id = session.get('user_id')
    if not user_id: return jsonify({'error': 'Unauthorized'}), 401
    
    if request.method == 'GET':
        return jsonify(db.get_animals(int(user_id)))
    
    data = request.json
    animal_id = db.add_animal(
        user_id=int(user_id), animal_type=data['type'], breed=data['breed'],
        gender=data['gender'], birth_date=data.get('birth_date'),
        weight=float(data['weight']) if data.get('weight') else None,
        purchase_price=float(data['purchase_price']), purchase_date=data['purchase_date']
    )
    return jsonify({'success': True, 'id': animal_id})

@app.route('/api/animals/<int:animal_id>', methods=['PUT', 'DELETE'])
def manage_animal(animal_id):
    if request.method == 'DELETE':
        db.delete_animal(animal_id)
        return jsonify({'success': True})
    db.update_animal(animal_id, request.json)
    return jsonify({'success': True})

# --- BUTCHERS API ---
@app.route('/api/butchers', methods=['GET', 'POST'])
def handle_butchers():
    if request.method == 'GET':
        return jsonify(db.get_butchers(request.args.get('search')))
    data = request.json
    bid = db.add_butcher(name=data['name'], phone=data['phone'], address=data.get('address'))
    return jsonify({'success': True, 'id': bid})

# --- FINANCE API (MOLIYA QISMI TUZATILDI) ---
@app.route('/api/finance', methods=['GET', 'POST'])
def handle_finance():
    user_id = session.get('user_id')
    if not user_id: return jsonify({'error': 'Unauthorized'}), 401
    
    if request.method == 'GET':
        return jsonify(db.get_finance(int(user_id)))
    
    data = request.json
    db.add_finance(
        user_id=int(user_id), finance_type=data['type'], amount=float(data['amount']),
        category=data['category'], description=data.get('description'), date=data['date']
    )
    return jsonify({'success': True})

@app.route('/api/finance/stats', methods=['GET'])
def get_finance_stats_api():
    """Grafiklar uchun statistika ma'lumotlarini olish"""
    user_id = session.get('user_id')
    if not user_id: return jsonify({'income': 0, 'expense': 0, 'profit': 0})
    return jsonify(db.get_finance_stats(int(user_id)))

@app.route('/api/finance/<int:finance_id>', methods=['DELETE'])
def delete_finance(finance_id):
    db.delete_finance(finance_id)
    return jsonify({'success': True})

# --- FEED API ---
@app.route('/api/feed', methods=['GET', 'POST'])
def handle_feed():
    user_id = session.get('user_id')
    if not user_id: return jsonify({'error': 'Unauthorized'}), 401
    if request.method == 'GET':
        return jsonify(db.get_feed(int(user_id)))
    data = request.json
    fid = db.add_feed(
        user_id=int(user_id), name=data['name'], quantity=float(data['quantity']),
        unit_price=float(data['unit_price']), supplier=data.get('supplier'), feed_date=data['feed_date']
    )
    return jsonify({'success': True, 'id': fid})

@app.route('/api/feed/<int:feed_id>', methods=['PUT', 'DELETE'])
def manage_feed(feed_id):
    if request.method == 'DELETE':
        db.delete_feed(feed_id)
    else:
        db.update_feed(feed_id, request.json)
    return jsonify({'success': True})

# --- VACCINATIONS API ---
@app.route('/api/vaccinations', methods=['GET', 'POST'])
def handle_vaccinations():
    user_id = session.get('user_id')
    if not user_id: return jsonify({'error': 'Unauthorized'}), 401
    if request.method == 'GET':
        return jsonify(db.get_vaccinations(int(user_id)))
    data = request.json
    vid = db.add_vaccination(
        user_id=int(user_id), animal_id=int(data['animal_id']),
        vaccine_name=data['vaccine_name'], vaccination_date=data['vaccination_date'],
        next_date=data.get('next_date'), veterinarian=data.get('veterinarian'),
        cost=float(data['cost']) if data.get('cost') else 0
    )
    return jsonify({'success': True, 'id': vid})

@app.route('/api/vaccinations/<int:vac_id>', methods=['PUT', 'DELETE'])
def manage_vaccination(vac_id):
    if request.method == 'DELETE':
        db.delete_vaccination(vac_id)
    else:
        db.update_vaccination(vac_id, request.json)
    return jsonify({'success': True})

@app.route('/ping')
def ping(): return "Bot is alive!", 200

# ==================== MAIN ====================

if __name__ == '__main__':
    db.init_db()
    
    def run_bot():
        print("🤖 Telegram bot ishga tushmoqda...")
        try:
            bot.main()
        except Exception as e:
            print(f"Botda xatolik: {e}")

    bot_thread = threading.Thread(target=run_bot)
    bot_thread.daemon = True
    bot_thread.start()

    print("🌐 CHORVA FERMERI PRO WEB SERVER ISHLAYAPTI")
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
