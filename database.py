import sqlite3
from datetime import datetime

DB_NAME = 'chorva_fermeri.db'

def get_db():
    """Database connection"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Database yaratish"""
    conn = get_db()
    cursor = conn.cursor()

def init_db():
    """Database jadvallarini yaratish (PostgreSQL sintaksisida)"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Users table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            telegram_id INTEGER UNIQUE NOT NULL,
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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            animal_id INTEGER NOT NULL,
            butcher_id INTEGER,
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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            animal_id INTEGER NOT NULL,
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
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
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
    conn.close()

# ==================== USERS ====================

def get_user(telegram_id):
    """Foydalanuvchini olish"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE telegram_id = ?', (telegram_id,))
    user = cursor.fetchone()
    conn.close()
    return dict(user) if user else None

def add_user(telegram_id, username, first_name, last_name, phone, full_name, language='uz'):
    """Foydalanuvchi qo'shish"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (telegram_id, username, first_name, last_name, phone, full_name, language)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (telegram_id, username, first_name, last_name, phone, full_name, language))
    conn.commit()
    user_id = cursor.lastrowid
    conn.close()
    return user_id

def update_user_language(telegram_id, language):
    """Tilni yangilash"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET language = ? WHERE telegram_id = ?', (language, telegram_id))
    conn.commit()
    conn.close()

def update_user_last_active(telegram_id):
    """Oxirgi faollikni yangilash"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE telegram_id = ?', (telegram_id,))
    conn.commit()
    conn.close()

# ==================== ANIMALS ====================

def get_animals(user_id):
    """Hayvonlarni olish"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM animals WHERE user_id = ? ORDER BY created_date DESC', (user_id,))
    animals = cursor.fetchall()
    conn.close()
    return [dict(animal) for animal in animals]

def get_animal(animal_id):
    """Hayvonni olish"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM animals WHERE id = ?', (animal_id,))
    animal = cursor.fetchone()
    conn.close()
    return dict(animal) if animal else None

def add_animal(user_id, animal_type, breed, gender, birth_date, weight, purchase_price, purchase_date):
    """Hayvon qo'shish"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO animals (user_id, type, breed, gender, birth_date, weight, purchase_price, purchase_date)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, animal_type, breed, gender, birth_date, weight, purchase_price, purchase_date))
    conn.commit()
    animal_id = cursor.lastrowid
    
    # Moliya qo'shish - hayvon xaridi
    cursor.execute('''
        INSERT INTO finance (user_id, type, amount, category, description, date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, 'expense', purchase_price, 'animal_purchase', f'{animal_type} - {breed}', purchase_date))
    
    conn.commit()
    conn.close()
    return animal_id

def update_animal(animal_id, **kwargs):
    """Hayvonni yangilash"""
    conn = get_db()
    cursor = conn.cursor()
    
    fields = []
    values = []
    for key, value in kwargs.items():
        if value is not None:
            fields.append(f"{key} = ?")
            values.append(value)
    
    if fields:
        values.append(animal_id)
        query = f"UPDATE animals SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
    
    conn.close()

def delete_animal(animal_id):
    """Hayvonni o'chirish"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM animals WHERE id = ?', (animal_id,))
    conn.commit()
    conn.close()

def get_animals_stats(user_id):
    """Hayvonlar statistikasi"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Total animals
    cursor.execute('SELECT COUNT(*) FROM animals WHERE user_id = ?', (user_id,))
    result = cursor.fetchone()
    total = result[0] if result else 0
    
    # Active animals
    cursor.execute('SELECT COUNT(*) FROM animals WHERE user_id = ? AND status = ?', (user_id, 'active'))
    result = cursor.fetchone()
    active = result[0] if result else 0
    
    conn.close()
    return {'total': total, 'active': active}

# ==================== BUTCHERS ====================

def get_butchers(search=None):
    """Qassoblarni olish"""
    conn = get_db()
    cursor = conn.cursor()
    
    if search:
        search_pattern = f'%{search}%'
        cursor.execute('''
            SELECT * FROM butchers 
            WHERE name LIKE ? OR phone LIKE ? OR address LIKE ?
            ORDER BY created_date DESC
        ''', (search_pattern, search_pattern, search_pattern))
    else:
        cursor.execute('SELECT * FROM butchers ORDER BY created_date DESC')
    
    butchers = cursor.fetchall()
    conn.close()
    return [dict(butcher) for butcher in butchers]

def get_butcher(butcher_id):
    """Qassobni olish"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM butchers WHERE id = ?', (butcher_id,))
    butcher = cursor.fetchone()
    conn.close()
    return dict(butcher) if butcher else None

def add_butcher(name, phone, address=None, experience=None, notes=None):
    """Qassob qo'shish"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO butchers (name, phone, address, experience, notes)
        VALUES (?, ?, ?, ?, ?)
    ''', (name, phone, address, experience, notes))
    conn.commit()
    butcher_id = cursor.lastrowid
    conn.close()
    return butcher_id

def update_butcher(butcher_id, **kwargs):
    """Qassobni yangilash"""
    conn = get_db()
    cursor = conn.cursor()
    
    fields = []
    values = []
    for key, value in kwargs.items():
        if value is not None:
            fields.append(f"{key} = ?")
            values.append(value)
    
    if fields:
        values.append(butcher_id)
        query = f"UPDATE butchers SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
    
    conn.close()

def delete_butcher(butcher_id):
    """Qassobni o'chirish"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM butchers WHERE id = ?', (butcher_id,))
    conn.commit()
    conn.close()

# ==================== SALES ====================

def get_sales(user_id):
    """Sotuvlarni olish"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.*, a.type as animal_type, a.breed, a.purchase_price, b.name as butcher_name
        FROM sales s
        LEFT JOIN animals a ON s.animal_id = a.id
        LEFT JOIN butchers b ON s.butcher_id = b.id
        WHERE s.user_id = ?
        ORDER BY s.sale_date DESC
    ''', (user_id,))
    sales = cursor.fetchall()
    conn.close()
    return [dict(sale) for sale in sales]

def add_sale(user_id, animal_id, butcher_id, sale_date, sale_price, buyer_name=None, buyer_phone=None, payment_type='cash'):
    """Sotuv qo'shish"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Hayvonni tekshirish
    cursor.execute('SELECT * FROM animals WHERE id = ? AND user_id = ?', (animal_id, user_id))
    animal = cursor.fetchone()
    if not animal:
        conn.close()
        return None
    
    # Sotuvni saqlash
    cursor.execute('''
        INSERT INTO sales (user_id, animal_id, butcher_id, sale_date, sale_price, buyer_name, buyer_phone, payment_type)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, animal_id, butcher_id, sale_date, sale_price, buyer_name, buyer_phone, payment_type))
    sale_id = cursor.lastrowid
    
    # Hayvon statusini yangilash
    cursor.execute('UPDATE animals SET status = ? WHERE id = ?', ('sold', animal_id))
    
    # Moliya qo'shish - sotuv
    profit = sale_price - dict(animal)['purchase_price']
    cursor.execute('''
        INSERT INTO finance (user_id, type, amount, category, description, date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, 'income', sale_price, 'animal_sale', f'Sotuv (Foyda: {profit:,.0f})', sale_date))
    
    conn.commit()
    conn.close()
    return sale_id

def delete_sale(sale_id):
    """Sotuvni o'chirish"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Sotuv ma'lumotlarini olish
    cursor.execute('SELECT animal_id FROM sales WHERE id = ?', (sale_id,))
    sale = cursor.fetchone()
    
    if sale:
        # Hayvon statusini qaytarish
        cursor.execute('UPDATE animals SET status = ? WHERE id = ?', ('active', dict(sale)['animal_id']))
    
    cursor.execute('DELETE FROM sales WHERE id = ?', (sale_id,))
    conn.commit()
    conn.close()

# ==================== FEED ====================

def get_feed(user_id):
    """Ozuqalarni olish"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM feed WHERE user_id = ? ORDER BY feed_date DESC', (user_id,))
    feed = cursor.fetchall()
    conn.close()
    return [dict(f) for f in feed]

def add_feed(user_id, name, quantity, unit_price, supplier=None, feed_date=None):
    """Ozuqa qo'shish"""
    if not feed_date:
        feed_date = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_db()
    cursor = conn.cursor()
    
    total_cost = quantity * unit_price
    
    cursor.execute('''
        INSERT INTO feed (user_id, name, quantity, unit_price, supplier, feed_date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, name, quantity, unit_price, supplier, feed_date))
    feed_id = cursor.lastrowid
    
    # Moliya qo'shish
    cursor.execute('''
        INSERT INTO finance (user_id, type, amount, category, description, date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, 'expense', total_cost, 'feed_purchase', f'{name} ({quantity} kg)', feed_date))
    
    conn.commit()
    conn.close()
    return feed_id

def delete_feed(feed_id):
    """Ozuqani o'chirish"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM feed WHERE id = ?', (feed_id,))
    conn.commit()
    conn.close()

# ==================== VACCINATIONS ====================

def get_vaccinations(user_id):
    """Vaksinatsiyalarni olish"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT v.*, a.type as animal_type, a.breed
        FROM vaccinations v
        LEFT JOIN animals a ON v.animal_id = a.id
        WHERE v.user_id = ?
        ORDER BY v.vaccination_date DESC
    ''', (user_id,))
    vaccinations = cursor.fetchall()
    conn.close()
    return [dict(v) for v in vaccinations]

def add_vaccination(user_id, animal_id, vaccine_name, vaccination_date, next_date=None, veterinarian=None, cost=None):
    """Vaksinatsiya qo'shish"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO vaccinations (user_id, animal_id, vaccine_name, vaccination_date, next_date, veterinarian, cost)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (user_id, animal_id, vaccine_name, vaccination_date, next_date, veterinarian, cost))
    vaccination_id = cursor.lastrowid
    
    # Agar narx kiritilgan bo'lsa moliya qo'shish
    if cost:
        cursor.execute('''
            INSERT INTO finance (user_id, type, amount, category, description, date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, 'expense', cost, 'medicine', f'{vaccine_name}', vaccination_date))
    
    conn.commit()
    conn.close()
    return vaccination_id

def delete_vaccination(vaccination_id):
    """Vaksinatsiyani o'chirish"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM vaccinations WHERE id = ?', (vaccination_id,))
    conn.commit()
    conn.close()

# ==================== FINANCE ====================

def get_finance(user_id):
    """Moliyalarni olish"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM finance WHERE user_id = ? ORDER BY date DESC', (user_id,))
    finance = cursor.fetchall()
    conn.close()
    return [dict(f) for f in finance]

def add_finance(user_id, finance_type, amount, category, description=None, date=None):
    """Moliya qo'shish"""
    if not date:
        date = datetime.now().strftime('%Y-%m-%d')
    
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO finance (user_id, type, amount, category, description, date)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, finance_type, amount, category, description, date))
    conn.commit()
    finance_id = cursor.lastrowid
    conn.close()
    return finance_id

def delete_finance(finance_id):
    """Moliyani o'chirish"""
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM finance WHERE id = ?', (finance_id,))
    conn.commit()
    conn.close()

def get_finance_stats(user_id):
    """Moliya statistikasi"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Income
    cursor.execute('SELECT SUM(amount) FROM finance WHERE user_id = ? AND type = ?', (user_id, 'income'))
    result = cursor.fetchone()
    income = result[0] if result and result[0] else 0
    
    # Expense
    cursor.execute('SELECT SUM(amount) FROM finance WHERE user_id = ? AND type = ?', (user_id, 'expense'))
    result = cursor.fetchone()
    expense = result[0] if result and result[0] else 0
    
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
