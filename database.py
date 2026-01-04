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
    """Database jadvallarini yaratish"""
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
            registered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
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
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Sales table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            animal_id INTEGER NOT NULL,
            butcher_id INTEGER,
            sale_date TEXT NOT NULL,
            sale_price REAL NOT NULL,
            buyer_name TEXT,
            buyer_phone TEXT,
            payment_type TEXT DEFAULT 'cash',
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(telegram_id),
            FOREIGN KEY (animal_id) REFERENCES animals(id) ON DELETE CASCADE,
            FOREIGN KEY (butcher_id) REFERENCES butchers(id) ON DELETE SET NULL
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
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(telegram_id)
        )
    ''')
    
    # Vaccinations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vaccinations (
            id SERIAL PRIMARY KEY,
            user_id BIGINT NOT NULL,
            animal_id INTEGER NOT NULL,
            vaccine_name TEXT NOT NULL,
            vaccination_date TEXT NOT NULL,
            next_date TEXT,
            veterinarian TEXT,
            cost REAL,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(telegram_id),
            FOREIGN KEY (animal_id) REFERENCES animals(id) ON DELETE CASCADE
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
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(telegram_id)
        )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()

# ==================== USERS ====================

def get_user(telegram_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE telegram_id = %s', (telegram_id,))
    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return dict(user) if user else None

def add_user(telegram_id, username, first_name, last_name, phone, full_name, language='uz'):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (telegram_id, username, first_name, last_name, phone, full_name, language)
        VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
    ''', (telegram_id, username, first_name, last_name, phone, full_name, language))
    user_id = cursor.fetchone()['id']
    conn.commit()
    cursor.close()
    conn.close()
    return user_id

def update_user_language(telegram_id, language):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET language = %s WHERE telegram_id = %s', (language, telegram_id))
    conn.commit()
    cursor.close()
    conn.close()

def update_user_last_active(telegram_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET last_active = CURRENT_TIMESTAMP WHERE telegram_id = %s', (telegram_id,))
    conn.commit()
    cursor.close()
    conn.close()

# ==================== ANIMALS ====================

def get_animals(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM animals WHERE user_id = %s ORDER BY created_date DESC', (user_id,))
    animals = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(animal) for animal in animals]

def get_animal(animal_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM animals WHERE id = %s', (animal_id,))
    animal = cursor.fetchone()
    cursor.close()
    conn.close()
    return dict(animal) if animal else None

def add_animal(user_id, animal_type, breed, gender, birth_date, weight, purchase_price, purchase_date):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO animals (user_id, type, breed, gender, birth_date, weight, purchase_price, purchase_date)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
    ''', (user_id, animal_type, breed, gender, birth_date, weight, purchase_price, purchase_date))
    animal_id = cursor.fetchone()['id']
    
    cursor.execute('''
        INSERT INTO finance (user_id, type, amount, category, description, date)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (user_id, 'expense', purchase_price, 'animal_purchase', f'{animal_type} - {breed}', purchase_date))
    
    conn.commit()
    cursor.close()
    conn.close()
    return animal_id

def update_animal(animal_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    fields = []
    values = []
    for key, value in data.items():
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
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT user_id, type, breed, purchase_price FROM animals WHERE id = %s', (animal_id,))
        animal = cursor.fetchone()
        if animal:
            desc_pattern = f"%{animal['type']} - {animal['breed']}%"
            cursor.execute('''
                DELETE FROM finance 
                WHERE user_id = %s AND amount = %s AND category = 'animal_purchase' 
                AND description LIKE %s
            ''', (animal['user_id'], animal['purchase_price'], desc_pattern))

        cursor.execute('DELETE FROM animals WHERE id = %s', (animal_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        cursor.close()
        conn.close()

def get_animals_stats(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) as total FROM animals WHERE user_id = %s', (user_id,))
    total = cursor.fetchone()['total']
    cursor.execute("SELECT COUNT(*) as active FROM animals WHERE user_id = %s AND status = 'active'", (user_id,))
    active = cursor.fetchone()['active']
    cursor.close()
    conn.close()
    return {'total': total, 'active': active}

# ==================== BUTCHERS ====================

def get_butchers(search=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if search:
        pattern = f'%{search}%'
        cursor.execute('SELECT * FROM butchers WHERE name LIKE %s OR phone LIKE %s ORDER BY created_date DESC', (pattern, pattern))
    else:
        cursor.execute('SELECT * FROM butchers ORDER BY created_date DESC')
    butchers = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(b) for b in butchers]

def add_butcher(name, phone, address=None, experience=None, notes=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO butchers (name, phone, address, experience, notes)
        VALUES (%s, %s, %s, %s, %s) RETURNING id
    ''', (name, phone, address, experience, notes))
    bid = cursor.fetchone()['id']
    conn.commit()
    cursor.close()
    conn.close()
    return bid

def update_butcher(butcher_id, **kwargs):
    conn = get_db_connection()
    cursor = conn.cursor()
    fields = [f"{k} = %s" for k in kwargs.keys()]
    values = list(kwargs.values())
    values.append(butcher_id)
    cursor.execute(f"UPDATE butchers SET {', '.join(fields)} WHERE id = %s", values)
    conn.commit()
    cursor.close()
    conn.close()

def delete_butcher(butcher_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM butchers WHERE id = %s', (butcher_id,))
    conn.commit()
    cursor.close()
    conn.close()

# ==================== SALES ====================

def get_sales(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT s.*, a.type as animal_type, a.breed, b.name as butcher_name
        FROM sales s
        LEFT JOIN animals a ON s.animal_id = a.id
        LEFT JOIN butchers b ON s.butcher_id = b.id
        WHERE s.user_id = %s ORDER BY s.sale_date DESC
    ''', (user_id,))
    sales = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(s) for s in sales]

def add_sale(user_id, animal_id, butcher_id, sale_date, sale_price, buyer_name=None, buyer_phone=None, payment_type='cash'):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT purchase_price FROM animals WHERE id = %s', (animal_id,))
    animal = cursor.fetchone()
    if not animal:
        return None
    
    cursor.execute('''
        INSERT INTO sales (user_id, animal_id, butcher_id, sale_date, sale_price, buyer_name, buyer_phone, payment_type)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
    ''', (user_id, animal_id, butcher_id, sale_date, sale_price, buyer_name, buyer_phone, payment_type))
    sale_id = cursor.fetchone()['id']
    
    cursor.execute("UPDATE animals SET status = 'sold' WHERE id = %s", (animal_id,))
    
    profit = sale_price - animal['purchase_price']
    cursor.execute('''
        INSERT INTO finance (user_id, type, amount, category, description, date)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (user_id, 'income', sale_price, 'animal_sale', f'Sotuv (Foyda: {profit})', sale_date))
    
    conn.commit()
    cursor.close()
    conn.close()
    return sale_id

def delete_sale(sale_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT animal_id FROM sales WHERE id = %s', (sale_id,))
    sale = cursor.fetchone()
    if sale:
        cursor.execute("UPDATE animals SET status = 'active' WHERE id = %s", (sale['animal_id'],))
    cursor.execute('DELETE FROM sales WHERE id = %s', (sale_id,))
    conn.commit()
    cursor.close()
    conn.close()

# ==================== FEED ====================

def get_feed(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM feed WHERE user_id = %s ORDER BY feed_date DESC', (user_id,))
    feeds = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(f) for f in feeds]

def add_feed(user_id, name, quantity, unit_price, supplier=None, feed_date=None):
    if not feed_date: feed_date = datetime.now().strftime('%Y-%m-%d')
    total = quantity * unit_price
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO feed (user_id, name, quantity, unit_price, supplier, feed_date)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
    ''', (user_id, name, quantity, unit_price, supplier, feed_date))
    fid = cursor.fetchone()['id']
    
    cursor.execute('''
        INSERT INTO finance (user_id, type, amount, category, description, date)
        VALUES (%s, %s, %s, %s, %s, %s)
    ''', (user_id, 'expense', total, 'feed_purchase', f'{name} ({quantity} kg)', feed_date))
    
    conn.commit()
    cursor.close()
    conn.close()
    return fid

def update_feed(feed_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE feed SET name=%s, quantity=%s, unit_price=%s, supplier=%s, feed_date=%s 
        WHERE id=%s''', (data['name'], data['quantity'], data['unit_price'], data['supplier'], data['feed_date'], feed_id))
    conn.commit()
    cursor.close()
    conn.close()

def delete_feed(feed_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT user_id, name, (quantity * unit_price) as total FROM feed WHERE id = %s', (feed_id,))
        feed = cursor.fetchone()
        if feed:
            cursor.execute('''
                DELETE FROM finance WHERE user_id = %s AND amount = %s AND category = 'feed_purchase' 
                AND description LIKE %s
            ''', (feed['user_id'], feed['total'], f"%{feed['name']}%"))
        cursor.execute('DELETE FROM feed WHERE id = %s', (feed_id,))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

# ==================== VACCINATIONS ====================

def get_vaccinations(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT v.*, a.type as animal_type, a.breed FROM vaccinations v
        LEFT JOIN animals a ON v.animal_id = a.id
        WHERE v.user_id = %s ORDER BY v.vaccination_date DESC
    ''', (user_id,))
    vax = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(v) for v in vax]

def add_vaccination(user_id, animal_id, vaccine_name, vaccination_date, next_date=None, veterinarian=None, cost=0):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO vaccinations (user_id, animal_id, vaccine_name, vaccination_date, next_date, veterinarian, cost)
        VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id
    ''', (user_id, animal_id, vaccine_name, vaccination_date, next_date, veterinarian, cost))
    vid = cursor.fetchone()['id']
    if cost and cost > 0:
        cursor.execute('''
            INSERT INTO finance (user_id, type, amount, category, description, date)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (user_id, 'expense', cost, 'medicine', f'Vaksina: {vaccine_name}', vaccination_date))
    conn.commit()
    cursor.close()
    conn.close()
    return vid

def update_vaccination(vac_id, data):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE vaccinations SET vaccine_name=%s, vaccination_date=%s, next_date=%s, veterinarian=%s, cost=%s 
        WHERE id=%s''', (data['vaccine_name'], data['vaccination_date'], data.get('next_date'), data.get('veterinarian'), data.get('cost'), vac_id))
    conn.commit()
    cursor.close()
    conn.close()

def delete_vaccination(vac_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM vaccinations WHERE id = %s', (vac_id,))
    conn.commit()
    cursor.close()
    conn.close()

# ==================== FINANCE ====================

def get_finance(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM finance WHERE user_id = %s ORDER BY date DESC', (user_id,))
    fin = cursor.fetchall()
    cursor.close()
    conn.close()
    return [dict(f) for f in fin]

def add_finance(user_id, finance_type, amount, category, description=None, date=None):
    if not date: date = datetime.now().strftime('%Y-%m-%d')
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO finance (user_id, type, amount, category, description, date)
        VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
    ''', (user_id, finance_type, amount, category, description, date))
    fid = cursor.fetchone()['id']
    conn.commit()
    cursor.close()
    conn.close()
    return fid

def delete_finance(fid):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM finance WHERE id = %s', (fid,))
    conn.commit()
    cursor.close()
    conn.close()

def get_finance_stats(user_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT SUM(amount) as total FROM finance WHERE user_id = %s AND type = 'income'", (user_id,))
    inc = cursor.fetchone()['total'] or 0
    cursor.execute("SELECT SUM(amount) as total FROM finance WHERE user_id = %s AND type = 'expense'", (user_id,))
    exp = cursor.fetchone()['total'] or 0
    cursor.close()
    conn.close()
    return {'income': inc, 'expense': exp, 'profit': inc - exp}

def delete_user_completely(telegram_id):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute('DELETE FROM finance WHERE user_id = %s', (telegram_id,))
        cursor.execute('DELETE FROM vaccinations WHERE user_id = %s', (telegram_id,))
        cursor.execute('DELETE FROM feed WHERE user_id = %s', (telegram_id,))
        cursor.execute('DELETE FROM sales WHERE user_id = %s', (telegram_id,))
        cursor.execute('DELETE FROM animals WHERE user_id = %s', (telegram_id,))
        cursor.execute('DELETE FROM users WHERE telegram_id = %s', (telegram_id,))
        conn.commit()
    except Exception as e:
        conn.rollback()
        print(f"Error: {e}")
    finally:
        cursor.close()
        conn.close()
