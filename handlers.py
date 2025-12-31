from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import ContextTypes, ConversationHandler
import database as db
from config import TRANSLATIONS, WEBHOOK_URL

# Conversation states
PHONE, FULLNAME = range(2)

def get_translation(lang, key):
    """Tarjima olish"""
    return TRANSLATIONS.get(lang, TRANSLATIONS['uz']).get(key, key)

def get_main_keyboard(lang='uz'):
    """Asosiy klaviatura"""
    t = lambda k: get_translation(lang, k)
    keyboard = [
        [KeyboardButton(f"🐄 {t('animals')}"), KeyboardButton(f"👤 {t('butchers')}")],
        [KeyboardButton(f"💰 {t('sales')}"), KeyboardButton(f"🌾 {t('feed')}")],
        [KeyboardButton(f"💉 {t('vaccinations')}"), KeyboardButton(f"📊 {t('finance')}")],
        [KeyboardButton(f"🏠 {t('dashboard')}"), KeyboardButton(f"🌐 {t('language')}")],
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def get_language_keyboard():
    """Til tanlash klaviaturasi"""
    keyboard = [
        [InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data='lang_uz')],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data='lang_ru')],
        [InlineKeyboardButton("🇬🇧 English", callback_data='lang_en')],
    ]
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start komandasi - yangi foydalanuvchi ro'yxatdan o'tishi"""
    telegram_id = update.effective_user.id
    user = db.get_user(telegram_id)
    
    if user:
        # Foydalanuvchi allaqachon ro'yxatdan o'tgan
        lang = user.get('language', 'uz')
        t = lambda k: get_translation(lang, k)
        
        web_app_url = f"{WEBHOOK_URL}/webapp?user_id={telegram_id}"
        keyboard = [
            [InlineKeyboardButton(f"🌐 {t('app_title')}", web_app=WebAppInfo(url=web_app_url))]
        ]
        
        await update.message.reply_text(
            f"👋 Xush kelibsiz, {user.get('full_name', 'Foydalanuvchi')}!\n\n"
            f"Dastur bilan ishlash uchun pastdagi tugmani bosing yoki buyruqlardan foydalaning.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        await update.message.reply_text(
            f"📱 Tanlang:",
            reply_markup=get_main_keyboard(lang)
        )
        return ConversationHandler.END
    
    # Yangi foydalanuvchi - kontakt so'rash
    contact_keyboard = [
        [KeyboardButton("📱 Telefon raqamni yuborish", request_contact=True)]
    ]
    await update.message.reply_text(
        "👋 Assalomu alaykum!\n\n"
        "🐄 CHORVA FERMERI PRO botiga xush kelibsiz!\n\n"
        "Davom etish uchun telefon raqamingizni yuboring:",
        reply_markup=ReplyKeyboardMarkup(contact_keyboard, resize_keyboard=True, one_time_keyboard=True)
    )
    return PHONE

async def receive_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Telefon raqamni qabul qilish"""
    if not update.message.contact:
        await update.message.reply_text(
            "❌ Iltimos, telefon raqamingizni yuboring (pastdagi tugmani bosing)."
        )
        return PHONE
    
    context.user_data['phone'] = update.message.contact.phone_number
    context.user_data['telegram_id'] = update.effective_user.id
    context.user_data['username'] = update.effective_user.username
    context.user_data['first_name'] = update.effective_user.first_name
    context.user_data['last_name'] = update.effective_user.last_name
    
    await update.message.reply_text(
        "✅ Telefon raqamingiz qabul qilindi!\n\n"
        "Endi ism-sharifingizni yozing:",
        reply_markup=ReplyKeyboardMarkup([[KeyboardButton("Bekor qilish")]], resize_keyboard=True)
    )
    return FULLNAME

async def receive_fullname(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ism-sharifni qabul qilish va foydalanuvchini saqlash"""
    if update.message.text == "Bekor qilish":
        await update.message.reply_text("❌ Ro'yxatdan o'tish bekor qilindi.")
        return ConversationHandler.END
    
    full_name = update.message.text.strip()
    if len(full_name) < 3:
        await update.message.reply_text("❌ Ism-sharif juda qisqa. Qaytadan kiriting:")
        return FULLNAME
    
    # Foydalanuvchini saqlash
    telegram_id = context.user_data['telegram_id']
    db.add_user(
        telegram_id=telegram_id,
        username=context.user_data.get('username'),
        first_name=context.user_data.get('first_name'),
        last_name=context.user_data.get('last_name'),
        phone=context.user_data['phone'],
        full_name=full_name
    )
    
    # Web app tugmasi
    web_app_url = f"{WEBHOOK_URL}/webapp?user_id={telegram_id}"
    keyboard = [
        [InlineKeyboardButton("🌐 Dasturni ochish", web_app=WebAppInfo(url=web_app_url))]
    ]
    
    await update.message.reply_text(
        f"✅ Tabriklaymiz, {full_name}!\n\n"
        f"Siz muvaffaqiyatli ro'yxatdan o'tdingiz.\n\n"
        f"📱 Dasturni ochish uchun pastdagi tugmani bosing:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    await update.message.reply_text(
        "📱 Asosiy menyu:",
        reply_markup=get_main_keyboard('uz')
    )
    
    # Context tozalash
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bekor qilish"""
    await update.message.reply_text("❌ Amal bekor qilindi.")
    return ConversationHandler.END

async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dashboard ma'lumotlari"""
    telegram_id = update.effective_user.id
    user = db.get_user(telegram_id)
    if not user:
        await update.message.reply_text("❌ Siz ro'yxatdan o'tmagansiz. /start buyrug'ini yuboring.")
        return
    
    lang = user.get('language', 'uz')
    t = lambda k: get_translation(lang, k)
    
    # Statistika
    animals_stats = db.get_animals_stats(telegram_id)
    finance_stats = db.get_finance_stats(telegram_id)
    
    text = f"📊 {t('dashboard')}\n\n"
    text += f"🐄 {t('total_animals')}: {animals_stats['total']}\n"
    text += f"✅ {t('active_animals')}: {animals_stats['active']}\n\n"
    text += f"💰 {t('total_income')}: {finance_stats['income']:,.0f} {t('sum')}\n"
    text += f"💸 {t('total_expense')}: {finance_stats['expense']:,.0f} {t('sum')}\n"
    text += f"📈 {t('net_profit')}: {finance_stats['profit']:,.0f} {t('sum')}\n"
    
    web_app_url = f"{WEBHOOK_URL}/webapp?user_id={telegram_id}"
    keyboard = [
        [InlineKeyboardButton(f"🌐 {t('app_title')}", web_app=WebAppInfo(url=web_app_url))]
    ]
    
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def animals_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hayvonlar ro'yxati"""
    telegram_id = update.effective_user.id
    user = db.get_user(telegram_id)
    if not user:
        await update.message.reply_text("❌ Siz ro'yxatdan o'tmagansiz. /start buyrug'ini yuboring.")
        return
    
    lang = user.get('language', 'uz')
    t = lambda k: get_translation(lang, k)
    
    animals = db.get_animals(telegram_id)
    if not animals:
        await update.message.reply_text(f"❌ {t('no_data')}")
        return
    
    text = f"🐄 {t('animals')} ({len(animals)} ta):\n\n"
    for animal in animals[:10]:  # Faqat 10 tasi
        status_emoji = "✅" if animal['status'] == 'active' else "❌"
        text += f"{status_emoji} {animal['type']} - {animal['breed']}\n"
        text += f"   💰 {animal['purchase_price']:,.0f} {t('sum')}\n"
        text += f"   📅 {animal['purchase_date']}\n\n"
    
    if len(animals) > 10:
        text += f"... va yana {len(animals) - 10} ta\n\n"
    
    text += f"To'liq ro'yxatni web dasturda ko'ring."
    
    web_app_url = f"{WEBHOOK_URL}/webapp?user_id={telegram_id}&page=animals"
    keyboard = [
        [InlineKeyboardButton(f"🌐 {t('animals')}", web_app=WebAppInfo(url=web_app_url))]
    ]
    
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def butchers_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Qassoblar ro'yxati"""
    user = db.get_user(update.effective_user.id)
    lang = user.get('language', 'uz') if user else 'uz'
    t = lambda k: get_translation(lang, k)
    
    butchers = db.get_butchers()
    if not butchers:
        await update.message.reply_text(f"❌ {t('no_data')}")
        return
    
    text = f"👤 {t('butchers')} ({len(butchers)} ta):\n\n"
    for butcher in butchers[:10]:
        text += f"👤 {butcher['name']}\n"
        text += f"   📱 {butcher['phone']}\n"
        if butcher['address']:
            text += f"   📍 {butcher['address']}\n"
        text += "\n"
    
    if len(butchers) > 10:
        text += f"... va yana {len(butchers) - 10} ta\n\n"
    
    text += f"To'liq ro'yxatni web dasturda ko'ring."
    
    telegram_id = update.effective_user.id
    web_app_url = f"{WEBHOOK_URL}/webapp?user_id={telegram_id}&page=butchers"
    keyboard = [
        [InlineKeyboardButton(f"🌐 {t('butchers')}", web_app=WebAppInfo(url=web_app_url))]
    ]
    
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def language_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tilni o'zgartirish"""
    await update.message.reply_text(
        "🌐 Tilni tanlang / Выберите язык / Choose language:",
        reply_markup=get_language_keyboard()
    )

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Til tanlash callback"""
    query = update.callback_query
    await query.answer()
    
    lang = query.data.split('_')[1]  # lang_uz -> uz
    telegram_id = update.effective_user.id
    
    db.update_user_language(telegram_id, lang)
    
    languages = {'uz': '🇺🇿 O\'zbekcha', 'ru': '🇷🇺 Русский', 'en': '🇬🇧 English'}
    await query.edit_message_text(f"✅ Til o'zgartirildi: {languages[lang]}")
    
    # Yangi klaviatura
    await context.bot.send_message(
        chat_id=telegram_id,
        text="📱 Asosiy menyu:",
        reply_markup=get_main_keyboard(lang)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yordam buyrug'i"""
    telegram_id = update.effective_user.id
    user = db.get_user(telegram_id)
    lang = user.get('language', 'uz') if user else 'uz'
    
    text = "📚 Yordam / Помощь / Help\n\n"
    text += "Buyruqlar / Команды / Commands:\n"
    text += "/start - Boshlash / Начать / Start\n"
    text += "/dashboard - Statistika / Статистика / Dashboard\n"
    text += "/animals - Hayvonlar / Животные / Animals\n"
    text += "/butchers - Qassoblar / Мясники / Butchers\n"
    text += "/language - Til / Язык / Language\n"
    text += "/help - Yordam / Помощь / Help\n\n"
    text += "📱 Web dastur tugmalarini yoki buyruqlarni ishlatishingiz mumkin."
    
    await update.message.reply_text(text)
