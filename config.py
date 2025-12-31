import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_IDS = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '').split(',') if id.strip()]
SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
WEBHOOK_URL = os.getenv('WEBHOOK_URL', '')
PORT = int(os.getenv('PORT', 10000))

# Database
DATABASE_PATH = 'chorva_fermeri.db'

# Translations
TRANSLATIONS = {
    'uz': {
        # Navigation
        'app_title': 'CHORVA FERMERI PRO v2.0',
        'dashboard': 'Bosh sahifa',
        'animals': 'Hayvonlar',
        'butchers': 'Qassoblar',
        'sales': 'Sotuvlar',
        'feed': 'Ozuqa',
        'vaccinations': 'Vaksinatsiya',
        'finance': 'Moliya',
        'language': 'Til',
        
        # Dashboard
        'total_animals': 'Jami hayvonlar',
        'active_animals': 'Faol hayvonlar',
        'total_income': 'Jami kirim',
        'total_expense': 'Jami chiqim',
        'net_profit': 'Sof foyda',
        'animals_by_type': 'Hayvonlar turi bo\'yicha',
        'financial_overview': 'Moliyaviy ko\'rsatkichlar',
        'monthly_trend': 'Oylik dinamika',
        
        # Animals
        'add_animal': 'Hayvon qo\'shish',
        'animal_type': 'Turi',
        'breed': 'Zoti',
        'gender': 'Jinsi',
        'birth_date': 'Tug\'ilgan sana',
        'weight': 'Og\'irligi (kg)',
        'purchase_price': 'Xarid narxi',
        'purchase_date': 'Xarid sanasi',
        'status': 'Holati',
        'male': 'Erkak',
        'female': 'Urg\'ochi',
        'active': 'Faol',
        'sold': 'Sotilgan',
        'deceased': 'O\'lgan',
        'cow': 'Sigir',
        'sheep': 'Qo\'y',
        'goat': 'Echki',
        'actions': 'Amallar',
        'edit': 'Tahrirlash',
        'delete': 'O\'chirish',
        
        # Butchers
        'add_butcher': 'Qassob qo\'shish',
        'butcher_name': 'Ismi',
        'phone': 'Telefon',
        'address': 'Manzil',
        'experience': 'Tajriba (yil)',
        'notes': 'Izohlar',
        'search': 'Qidirish',
        'search_placeholder': 'Ism, telefon yoki manzil bo\'yicha qidiring...',
        
        # Sales
        'add_sale': 'Sotuv qo\'shish',
        'select_animal': 'Hayvonni tanlang',
        'select_butcher': 'Qassobni tanlang',
        'sale_date': 'Sotuv sanasi',
        'sale_price': 'Sotuv narxi',
        'buyer_name': 'Xaridor ismi',
        'buyer_phone': 'Xaridor telefoni',
        'payment_type': 'To\'lov turi',
        'cash': 'Naqd',
        'card': 'Karta',
        'transfer': 'O\'tkazma',
        'profit': 'Foyda',
        'animal_info': 'Hayvon ma\'lumoti',
        'butcher_info': 'Qassob ma\'lumoti',
        
        # Feed
        'add_feed': 'Ozuqa qo\'shish',
        'feed_name': 'Nomi',
        'quantity': 'Miqdori (kg)',
        'unit_price': 'Birlik narxi',
        'total_price': 'Jami narx',
        'supplier': 'Ta\'minotchi',
        'feed_date': 'Sana',
        
        # Vaccinations
        'add_vaccination': 'Vaksinatsiya qo\'shish',
        'vaccine_name': 'Vaksina nomi',
        'vaccination_date': 'Vaksinatsiya sanasi',
        'next_date': 'Keyingi sana',
        'veterinarian': 'Veterinar',
        'cost': 'Narxi',
        
        # Finance
        'add_finance': 'Moliya qo\'shish',
        'type': 'Turi',
        'income': 'Kirim',
        'expense': 'Chiqim',
        'amount': 'Miqdori',
        'category': 'Kategoriya',
        'description': 'Tavsif',
        'date': 'Sana',
        'animal_purchase': 'Hayvon xaridi',
        'animal_sale': 'Hayvon sotuvi',
        'feed_purchase': 'Ozuqa xaridi',
        'medicine': 'Dori-darmon',
        'other': 'Boshqa',
        
        # Common
        'save': 'Saqlash',
        'cancel': 'Bekor qilish',
        'close': 'Yopish',
        'submit': 'Jo\'natish',
        'success': 'Muvaffaqiyatli!',
        'error': 'Xatolik!',
        'confirm_delete': 'O\'chirishni tasdiqlaysizmi?',
        'no_data': 'Ma\'lumot yo\'q',
        'required': 'Majburiy',
        'sum': 'so\'m',
    },
    'ru': {
        # Navigation
        'app_title': 'CHORVA FERMERI PRO v2.0',
        'dashboard': 'Главная',
        'animals': 'Животные',
        'butchers': 'Мясники',
        'sales': 'Продажи',
        'feed': 'Корм',
        'vaccinations': 'Вакцинация',
        'finance': 'Финансы',
        'language': 'Язык',
        
        # Dashboard
        'total_animals': 'Всего животных',
        'active_animals': 'Активных животных',
        'total_income': 'Общий доход',
        'total_expense': 'Общий расход',
        'net_profit': 'Чистая прибыль',
        'animals_by_type': 'Животные по типам',
        'financial_overview': 'Финансовый обзор',
        'monthly_trend': 'Месячная динамика',
        
        # Animals
        'add_animal': 'Добавить животное',
        'animal_type': 'Тип',
        'breed': 'Порода',
        'gender': 'Пол',
        'birth_date': 'Дата рождения',
        'weight': 'Вес (кг)',
        'purchase_price': 'Цена покупки',
        'purchase_date': 'Дата покупки',
        'status': 'Статус',
        'male': 'Самец',
        'female': 'Самка',
        'active': 'Активный',
        'sold': 'Продан',
        'deceased': 'Умер',
        'cow': 'Корова',
        'sheep': 'Овца',
        'goat': 'Коза',
        'actions': 'Действия',
        'edit': 'Редактировать',
        'delete': 'Удалить',
        
        # Butchers
        'add_butcher': 'Добавить мясника',
        'butcher_name': 'Имя',
        'phone': 'Телефон',
        'address': 'Адрес',
        'experience': 'Опыт (лет)',
        'notes': 'Заметки',
        'search': 'Поиск',
        'search_placeholder': 'Поиск по имени, телефону или адресу...',
        
        # Sales
        'add_sale': 'Добавить продажу',
        'select_animal': 'Выберите животное',
        'select_butcher': 'Выберите мясника',
        'sale_date': 'Дата продажи',
        'sale_price': 'Цена продажи',
        'buyer_name': 'Имя покупателя',
        'buyer_phone': 'Телефон покупателя',
        'payment_type': 'Тип оплаты',
        'cash': 'Наличные',
        'card': 'Карта',
        'transfer': 'Перевод',
        'profit': 'Прибыль',
        'animal_info': 'Информация о животном',
        'butcher_info': 'Информация о мяснике',
        
        # Feed
        'add_feed': 'Добавить корм',
        'feed_name': 'Название',
        'quantity': 'Количество (кг)',
        'unit_price': 'Цена за единицу',
        'total_price': 'Общая цена',
        'supplier': 'Поставщик',
        'feed_date': 'Дата',
        
        # Vaccinations
        'add_vaccination': 'Добавить вакцинацию',
        'vaccine_name': 'Название вакцины',
        'vaccination_date': 'Дата вакцинации',
        'next_date': 'Следующая дата',
        'veterinarian': 'Ветеринар',
        'cost': 'Стоимость',
        
        # Finance
        'add_finance': 'Добавить финансы',
        'type': 'Тип',
        'income': 'Доход',
        'expense': 'Расход',
        'amount': 'Сумма',
        'category': 'Категория',
        'description': 'Описание',
        'date': 'Дата',
        'animal_purchase': 'Покупка животного',
        'animal_sale': 'Продажа животного',
        'feed_purchase': 'Покупка корма',
        'medicine': 'Лекарства',
        'other': 'Другое',
        
        # Common
        'save': 'Сохранить',
        'cancel': 'Отменить',
        'close': 'Закрыть',
        'submit': 'Отправить',
        'success': 'Успешно!',
        'error': 'Ошибка!',
        'confirm_delete': 'Подтвердить удаление?',
        'no_data': 'Нет данных',
        'required': 'Обязательно',
        'sum': 'сум',
    },
    'en': {
        # Navigation
        'app_title': 'CHORVA FERMERI PRO v2.0',
        'dashboard': 'Dashboard',
        'animals': 'Animals',
        'butchers': 'Butchers',
        'sales': 'Sales',
        'feed': 'Feed',
        'vaccinations': 'Vaccinations',
        'finance': 'Finance',
        'language': 'Language',
        
        # Dashboard
        'total_animals': 'Total Animals',
        'active_animals': 'Active Animals',
        'total_income': 'Total Income',
        'total_expense': 'Total Expense',
        'net_profit': 'Net Profit',
        'animals_by_type': 'Animals by Type',
        'financial_overview': 'Financial Overview',
        'monthly_trend': 'Monthly Trend',
        
        # Animals
        'add_animal': 'Add Animal',
        'animal_type': 'Type',
        'breed': 'Breed',
        'gender': 'Gender',
        'birth_date': 'Birth Date',
        'weight': 'Weight (kg)',
        'purchase_price': 'Purchase Price',
        'purchase_date': 'Purchase Date',
        'status': 'Status',
        'male': 'Male',
        'female': 'Female',
        'active': 'Active',
        'sold': 'Sold',
        'deceased': 'Deceased',
        'cow': 'Cow',
        'sheep': 'Sheep',
        'goat': 'Goat',
        'actions': 'Actions',
        'edit': 'Edit',
        'delete': 'Delete',
        
        # Butchers
        'add_butcher': 'Add Butcher',
        'butcher_name': 'Name',
        'phone': 'Phone',
        'address': 'Address',
        'experience': 'Experience (years)',
        'notes': 'Notes',
        'search': 'Search',
        'search_placeholder': 'Search by name, phone or address...',
        
        # Sales
        'add_sale': 'Add Sale',
        'select_animal': 'Select Animal',
        'select_butcher': 'Select Butcher',
        'sale_date': 'Sale Date',
        'sale_price': 'Sale Price',
        'buyer_name': 'Buyer Name',
        'buyer_phone': 'Buyer Phone',
        'payment_type': 'Payment Type',
        'cash': 'Cash',
        'card': 'Card',
        'transfer': 'Transfer',
        'profit': 'Profit',
        'animal_info': 'Animal Information',
        'butcher_info': 'Butcher Information',
        
        # Feed
        'add_feed': 'Add Feed',
        'feed_name': 'Name',
        'quantity': 'Quantity (kg)',
        'unit_price': 'Unit Price',
        'total_price': 'Total Price',
        'supplier': 'Supplier',
        'feed_date': 'Date',
        
        # Vaccinations
        'add_vaccination': 'Add Vaccination',
        'vaccine_name': 'Vaccine Name',
        'vaccination_date': 'Vaccination Date',
        'next_date': 'Next Date',
        'veterinarian': 'Veterinarian',
        'cost': 'Cost',
        
        # Finance
        'add_finance': 'Add Finance',
        'type': 'Type',
        'income': 'Income',
        'expense': 'Expense',
        'amount': 'Amount',
        'category': 'Category',
        'description': 'Description',
        'date': 'Date',
        'animal_purchase': 'Animal Purchase',
        'animal_sale': 'Animal Sale',
        'feed_purchase': 'Feed Purchase',
        'medicine': 'Medicine',
        'other': 'Other',
        
        # Common
        'save': 'Save',
        'cancel': 'Cancel',
        'close': 'Close',
        'submit': 'Submit',
        'success': 'Success!',
        'error': 'Error!',
        'confirm_delete': 'Confirm deletion?',
        'no_data': 'No data',
        'required': 'Required',
        'sum': 'sum',
    }
}
