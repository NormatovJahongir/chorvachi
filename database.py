import psycopg2
from psycopg2.extras import RealDictCursor
from datetime import datetime
import os

# Render'dagi Database URL'ni muhit o'zgaruvchisidan olish
DATABASE_URL = os.environ.get('DATABASE_URL')

def get_db_connection():
    """PostgreSQL bazasiga ulanish yaratish"""
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor, sslmode='require')
    return conn

def init_db():
    """Database jadvallarini yaratish (PostgreSQL sintaksisida)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            telegram_id BIGINT UNIQUE NOT NULL,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            full_name TEXT,
            language TEXT DEFAULT 'uz',
            registered_date TEXT DEFAULT CURRENT_TIMESTAMP,
            last_active TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Animals table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS animals (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            type TEXT NOT NULL,
            breed TEXT,
            gender TEXT,
            birth_date TEXT,
            weight REAL,
            purchase_price REAL NOT NULL,
            purchase_date TEXT NOT NULL,
            status TEXT DEFAULT 'active',
            created_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(telegram_id)
        )
    ''')
    
    # Butchers table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS butchers (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            address TEXT,
            experience INTEGER,
            notes TEXT,
            created_date TEXT DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Sales table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            animal_id BIGINT NOT NULL,
            butcher_id BIGINT,
            sale_date TEXT NOT NULL,
            sale_price REAL NOT NULL,
            buyer_name TEXT,
            buyer_phone TEXT,
            payment_type TEXT DEFAULT 'cash',
            created_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(telegram_id),
            FOREIGN KEY (animal_id) REFERENCES animals(id),
            FOREIGN KEY (butcher_id) REFERENCES butchers(id)
        )
    ''')
    
    # Feed table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS feed (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            name TEXT NOT NULL,
            quantity REAL NOT NULL,
            unit_price REAL NOT NULL,
            supplier TEXT,
            feed_date TEXT NOT NULL,
            created_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(telegram_id)
        )
    ''')
    
    # Vaccinations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vaccinations (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            animal_id BIGINT NOT NULL,
            vaccine_name TEXT NOT NULL,
            vaccination_date TEXT NOT NULL,
            next_date TEXT,
            veterinarian TEXT,
            cost REAL,
            created_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(telegram_id),
            FOREIGN KEY (animal_id) REFERENCES animals(id)
        )
    ''')
    
    # Finance table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS finance (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            type TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL,
            created_date TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(telegram_id)
        )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()

# ==================== USERS ====================

def get_user(telegram_id):
    """Foydalanuvchini olish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE telegram_id = %s', (telegram_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return dict(user) if user else None

def add_user(telegram_id, username, first_name, last_name, phone, full_name, language='uz'):
    """Foydalanuvchi qo'shish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (telegram_id, username, first_name, last_name, phone, full_name, language)
        VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
    ''', (telegram_id, username, first_name, last_name, phone, full_name, language))
    conn.commit()
    user_id = cursor.fetchone()['id']
    cursor.close()
    conn.close()
    return user_id

def update_user_language(telegram_id, language):
    """Tilni yangilash"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET language = %s WHERE telegram_id = %s', (language, telegram_id))
    conn.commit()
    cursor.close()
    conn.close()

def update_user_last_active(telegram_id):
    """Oxirgi faollikni yangilash"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE telegram_id = %s', (telegram_id,))
    conn.commit()
    cursor.close()
    conn.close()

# ==================== ANIMALS ====================

def get_animals(user_id):
    """Hayvonlarni olish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM animals WHERE user_id = %s ORDER BY created_date DESC', (user_id,))
    animals = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(animal) for animal in animals]

def get_animal(animal_id):
    """Hayvonni olish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM animals WHERE id = %s', (animal_id,))
    animal = cursor.fetchone()
    cursor.close()
    conn.close()
    return dict(animal) if animal else None

def add_animal(user_id, animal_type, breed, gender, birth_date, weight, purchase_price, purchase_date):
    """Hayvon qo'shish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO animals (user_id, type, breed, gender, birth_date, weight, purchase_price, purchase_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
    ''', (user_id, animal_type, breed, gender, birth_date, weight, purchase_price, purchase_date))
    conn.commit()
    animal_id = cursor.fetchone()['id']
    
    # Moliya qo'shish - hayvon xaridi
    cursor.execute('''
        INSERT INTO finance (user_id, type, amount, category, description, date)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (user_id, 'expense', purchase_price, 'animal_purchase', f'{animal_type} - {breed}', purchase_date))
    
    conn.commit()
    cursor.close()
    conn.close()
    return animal_id

def update_animal(animal_id, **kwargs):
    """Hayvonni yangilash"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    fields = []
    values = []
    for key, value in kwargs.items():
        if value is not None:
            fields.append(f"{key} = %s")
            values.append(value)
    
    if fields:
        values.append(animal_id)
        query = f"UPDATE animals SET {', '.join(fields)} WHERE id = %s"
        cursor.execute(query, values)
        conn.commit()

    cursor.close()
    conn.close()

def delete_animal(animal_id):
    """Hayvonni o'chirish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM animals WHERE id = %s', (animal_id,))
    conn.commit()
    cursor.close()
    conn.close()

def get_animals_stats(user_id):
    """Hayvonlar statistikasi"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Total animals
    cursor.execute('SELECT COUNT(*) FROM animals WHERE user_id = %s', (user_id,))
    result = cursor.fetchone()
    total = result['count'] if result else 0
    
    # Active animals
    cursor.execute('SELECT COUNT(*) FROM animals WHERE user_id = %s AND status = %s', (user_id, 'active'))
    result = cursor.fetchone()
    active = result['count'] if result else 0
    cursor.close()
    
    conn.close()
    return {'total': total, 'active': active}

# ==================== BUTCHERS ====================

def get_butchers(search=None):
    """Qassoblarni olish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if search:
        search_pattern = f'%{search}%'
        cursor.execute('''
            SELECT * FROM butchers 
            WHERE name LIKE %s OR phone LIKE %s OR address LIKE %s
            ORDER BY created_date DESC
        ''', (search_pattern, search_pattern, search_pattern))
    else:
        cursor.execute('SELECT * FROM butchers ORDER BY created_date DESC')
    
    butchers = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(butcher) for butcher in butchers]

def get_butcher(butcher_id):
    """Qassobni olish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM butchers WHERE id = %s', (butcher_id,))
    butcher = cursor.fetchone()
    cursor.close()
    conn.close()
    return dict(butcher) if butcher else None

def add_butcher(name, phone, address=None, experience=None, notes=None):
    """Qassob qo'shish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO butchers (name, phone, address, experience, notes)
        VALUES (%s, %s, %s, %s, %s) RETURNING id
    ''', (name, phone, address, experience, notes))
    conn.commit()
    butcher_id = cursor.fetchone()['id']
    cursor.close()
    conn.close()
    return butcher_id

def update_butcher(butcher_id, **kwargs):
    """Qassobni yangilash"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    fields = []
    values = []
    for key, value in kwargs.items():
        if value is not None:
            fields.append(f"{key} = %s")
            values.append(value)
    
    if fields:
        values.append(butcher_id)
        query = f"UPDATE butchers SET {', '.join(fields)} WHERE id = %s"
        cursor.execute(query, values)
        conn.commit()
        cursor.close()
    
    conn.close()

def delete_butcher(butcher_id):
    """Qassobni o'chirish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM butchers WHERE id = %s', (butcher_id,))
    conn.commit()
    cursor.close()
    conn.close()

# ==================== SALES ====================

def get_sales(user_id):
    """Sotuvlarni olish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.*, a.type as animal_type, a.breed, a.purchase_price, b.name as butcher_name
        FROM sales s
        LEFT JOIN animals a ON s.animal_id = a.id
        LEFT JOIN butchers b ON s.butcher_id = b.id
        WHERE s.user_id = %s
        ORDER BY s.sale_date DESC
    ''', (user_id,))
    sales = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(sale) for sale in sales]

def add_sale(user_id, animal_id, butcher_id, sale_date, sale_price, buyer_name=None, buyer_phone=None, payment_type='cash'):
    """Sotuv qo'shish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Hayvonni tekshirish
    cursor.execute('SELECT * FROM animals WHERE id = %s AND user_id = %s', (animal_id, user_id))
    animal = cursor.fetchone()
    if not animal:
        cursor.close()
        conn.close()
        return None
    
    # Sotuvni saqlash
    cursor.execute('''
        INSERT INTO sales (user_id, animal_id, butcher_id, sale_date, sale_price, buyer_name, buyer_phone, payment_type)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
    ''', (user_id, animal_id, butcher_id, sale_date, sale_price, buyer_name, buyer_phone, payment_type))
    sale_id = cursor.fetchone()['id']
    
    # Hayvon statusini yangilash
    cursor.execute('UPDATE animals SET status = %s WHERE id = %s', ('sold', animal_id))
    
    # Moliya qo'shish - sotuv
    profit = sale_price - dict(animal)['purchase_price']
    cursor.execute('''
        INSERT INTO finance (user_id, type, amount, category, description, date)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (user_id, 'income', sale_price, 'animal_sale', f'Sotuv (Foyda: {profit:,.0f})', sale_date))
    
    conn.commit()
    cursor.close()
    conn.close()
    return sale_id

def delete_sale(sale_id):
    """Sotuvni o'chirish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Sotuv ma'lumotlarini olish
    cursor.execute('SELECT animal_id FROM sales WHERE id = %s', (sale_id,))
    sale = cursor.fetchone()
    
    if sale:
        # Hayvon statusini qaytarish
        cursor.execute('UPDATE animals SET status = %s WHERE id = %s', ('active', dict(sale)['animal_id']))
    
    cursor.execute('DELETE FROM sales WHERE id = %s', (sale_id,))
    conn.commit()
    cursor.close()
    conn.close()

# ==================== FEED ====================

def get_feed(user_id):
    """Ozuqalarni olish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM feed WHERE user_id = %s ORDER BY feed_date DESC', (user_id,))
    feed = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(f) for f in feed]

def add_feed(user_id, name, quantity, unit_price, supplier=None, feed_date=None):
    """Ozuqa qo'shish"""
    if not feed_date:
        feed_date = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    total_cost = quantity * unit_price
    
    cursor.execute('''
        INSERT INTO feed (user_id, name, quantity, unit_price, supplier, feed_date)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
    ''', (user_id, name, quantity, unit_price, supplier, feed_date))
    feed_id = cursor.fetchone()['id']
    
    # Moliya qo'shish
    cursor.execute('''
        INSERT INTO finance (user_id, type, amount, category, description, date)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (user_id, 'expense', total_cost, 'feed_purchase', f'{name} ({quantity} kg)', feed_date))
    
    conn.commit()
    cursor.close()
    conn.close()
    return feed_id

def delete_feed(feed_id):
    """Ozuqani o'chirish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM feed WHERE id = %s', (feed_id,))
    conn.commit()
    cursor.close()
    conn.close()

# ==================== VACCINATIONS ====================

def get_vaccinations(user_id):
    """Vaksinatsiyalarni olish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT v.*, a.type as animal_type, a.breed
        FROM vaccinations v
        LEFT JOIN animals a ON v.animal_id = a.id
        WHERE v.user_id = %s
        ORDER BY v.vaccination_date DESC
    ''', (user_id,))
    vaccinations = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(v) for v in vaccinations]

def add_vaccination(user_id, animal_id, vaccine_name, vaccination_date, next_date=None, veterinarian=None, cost=None):
    """Vaksinatsiya qo'shish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO vaccinations (user_id, animal_id, vaccine_name, vaccination_date, next_date, veterinarian, cost)
        VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
    ''', (user_id, animal_id, vaccine_name, vaccination_date, next_date, veterinarian, cost))
    vaccination_id = cursor.fetchone()['id']
    
    # Agar narx kiritilgan bo'lsa moliya qo'shish
    if cost:
        cursor.execute('''
            INSERT INTO finance (user_id, type, amount, category, description, date)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (user_id, 'expense', cost, 'medicine', f'{vaccine_name}', vaccination_date))
    
    conn.commit()
    cursor.close()
    conn.close()
    return vaccination_id

def delete_vaccination(vaccination_id):
    """Vaksinatsiyani o'chirish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM vaccinations WHERE id = %s', (vaccination_id,))
    conn.commit()
    cursor.close()
    conn.close()

# ==================== FINANCE ====================

def get_finance(user_id):
    """Moliyalarni olish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM finance WHERE user_id = %s ORDER BY date DESC', (user_id,))
    finance = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(f) for f in finance]

def add_finance(user_id, finance_type, amount, category, description=None, date=None):
    """Moliya qo'shish"""
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO finance (user_id, type, amount, category, description, date)
        VALUES (%s, %s, %s, %s, %s, %s)RETURNING id
    ''', (user_id, finance_type, amount, category, description, date))
    conn.commit()
    finance_id = cursor.fetchone()['id']
    cursor.close()
    conn.close()
    return finance_id

def delete_finance(finance_id):
    """Moliyani o'chirish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM finance WHERE id = %s', (finance_id,))
    conn.commit()
    cursor.close()
    conn.close()

def get_finance_stats(user_id):
    """Moliya statistikasi"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Income
    cursor.execute('SELECT SUM(amount) FROM finance WHERE user_id = %s AND type = %s', (user_id, 'income'))
    result = cursor.fetchone()
    income = result['sum'] if result and result['sum'] else 0
    
    # Expense
    cursor.execute('SELECT SUM(amount) FROM finance WHERE user_id = %s AND type = %s', (user_id, 'expense'))
    result = cursor.fetchone()
    expense = result['sum'] if result and result['sum'] else 0
    
    cursor.close()
    conn.close()
    return {
        'income': income,
        'expense': expense,
        'profit': income - expense
    }
    
def delete_user_completely(telegram_id):
    """Foydalanuvchi va unga tegishli barcha ma'lumotlarni o'chirish"""
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        # Avval moliya va hayvonlarni o'chiramiz
        cursor.execute('DELETE FROM finance WHERE user_id = %s', (telegram_id,))
        cursor.execute('DELETE FROM animals WHERE user_id = %s', (telegram_id,))
        # Keyin foydalanuvchining o'zini
        cursor.execute('DELETE FROM users WHERE telegram_id = %s', (telegram_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"O'chirishda xato: {e}")
    finally:
        cursor.close()
        conn.close()
