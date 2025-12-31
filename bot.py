import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, ContextTypes, filters
import database as db
from config import TRANSLATIONS, BOT_TOKEN

# Logging sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# WEBAPP URL - RENDER.COM
WEBAPP_URL = "https://chorvachi.onrender.com"

# Conversation states
PHONE, FULLNAME = range(2)

# ==================== HELPER FUNCTIONS ====================

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

# ==================== BOT HANDLERS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start komandasi"""
    telegram_id = update.effective_user.id
    user = db.get_user(telegram_id)
    
    if user:
        # Foydalanuvchi ro'yxatdan o'tgan
        lang = user.get('language', 'uz')
        
        # WEB APP TUGMASI
        web_app_url = f"{WEBAPP_URL}/webapp?user_id={telegram_id}"
        keyboard = [
            [InlineKeyboardButton("🌐 Dasturni ochish", web_app=WebAppInfo(url=web_app_url))]
        ]
        
        await update.message.reply_text(
            f"👋 Xush kelibsiz, {user.get('full_name', 'Foydalanuvchi')}!\n\n"
            f"🆔 Telegram ID: <code>{telegram_id}</code>\n\n"
            f"📱 Buyruqlar:\n"
            f"• /dashboard - Statistika\n"
            f"• /animals - Hayvonlar\n"
            f"• /butchers - Qassoblar\n"
            f"• /help - Yordam\n\n"
            f"💻 Web dastur: {WEBAPP_URL}\n"
            f"Pastdagi tugmani bosing va avtomatik kirish:",
            parse_mode='HTML',
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        await update.message.reply_text(
            f"📱 Yoki klaviaturadan foydalaning:",
            reply_markup=get_main_keyboard(lang)
        )
        return ConversationHandler.END
    
    # Yangi foydalanuvchi
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
    """Telefon qabul qilish"""
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
    """Ism-sharif qabul qilish"""
    if update.message.text == "Bekor qilish":
        await update.message.reply_text("❌ Ro'yxatdan o'tish bekor qilindi.")
        return ConversationHandler.END
    
    full_name = update.message.text.strip()
    if len(full_name) < 3:
        await update.message.reply_text("❌ Ism-sharif juda qisqa. Qaytadan kiriting:")
        return FULLNAME
    
    # Saqlash
    telegram_id = context.user_data['telegram_id']
    db.add_user(
        telegram_id=telegram_id,
        username=context.user_data.get('username'),
        first_name=context.user_data.get('first_name'),
        last_name=context.user_data.get('last_name'),
        phone=context.user_data['phone'],
        full_name=full_name
    )
    
    # WEB APP TUGMASI
    web_app_url = f"{WEBAPP_URL}/webapp?user_id={telegram_id}"
    keyboard = [
        [InlineKeyboardButton("🌐 Dasturni ochish", web_app=WebAppInfo(url=web_app_url))]
    ]
    
    await update.message.reply_text(
        f"✅ Tabriklaymiz, {full_name}!\n\n"
        f"Ro'yxatdan muvaffaqiyatli o'tdingiz.\n\n"
        f"🆔 Telegram ID: <code>{telegram_id}</code>\n\n"
        f"💻 Web dastur: {WEBAPP_URL}\n"
        f"Pastdagi tugmani bosing va avtomatik kirish:",
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    await update.message.reply_text(
        "📱 Asosiy menyu:",
        reply_markup=get_main_keyboard('uz')
    )
    
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bekor qilish"""
    await update.message.reply_text("❌ Amal bekor qilindi.")
    return ConversationHandler.END

async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Dashboard"""
    telegram_id = update.effective_user.id
    user = db.get_user(telegram_id)
    if not user:
        await update.message.reply_text("❌ Siz ro'yxatdan o'tmagansiz. /start bosing.")
        return
    
    lang = user.get('language', 'uz')
    t = lambda k: get_translation(lang, k)
    
    animals_stats = db.get_animals_stats(telegram_id)
    finance_stats = db.get_finance_stats(telegram_id)
    
    text = f"📊 {t('dashboard')}\n\n"
    text += f"🐄 {t('total_animals')}: {animals_stats['total']}\n"
    text += f"✅ {t('active_animals')}: {animals_stats['active']}\n\n"
    text += f"💰 {t('total_income')}: {finance_stats['income']:,.0f} {t('sum')}\n"
    text += f"💸 {t('total_expense')}: {finance_stats['expense']:,.0f} {t('sum')}\n"
    text += f"📈 {t('net_profit')}: {finance_stats['profit']:,.0f} {t('sum')}\n\n"
    
    # WEB APP TUGMASI
    web_app_url = f"{WEBAPP_URL}/webapp?user_id={telegram_id}"
    keyboard = [
        [InlineKeyboardButton("🌐 Batafsil ko'rish", web_app=WebAppInfo(url=web_app_url))]
    ]
    
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def animals_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Hayvonlar"""
    telegram_id = update.effective_user.id
    user = db.get_user(telegram_id)
    if not user:
        await update.message.reply_text("❌ Siz ro'yxatdan o'tmagansiz. /start bosing.")
        return
    
    lang = user.get('language', 'uz')
    t = lambda k: get_translation(lang, k)
    
    animals = db.get_animals(telegram_id)
    if not animals:
        await update.message.reply_text(f"❌ {t('no_data')}")
        return
    
    text = f"🐄 {t('animals')} ({len(animals)} ta):\n\n"
    for animal in animals[:10]:
        status_emoji = "✅" if animal['status'] == 'active' else "❌"
        text += f"{status_emoji} {animal['type']} - {animal['breed']}\n"
        text += f"   💰 {animal['purchase_price']:,.0f} {t('sum')}\n"
        text += f"   📅 {animal['purchase_date']}\n\n"
    
    if len(animals) > 10:
        text += f"... va yana {len(animals) - 10} ta\n\n"
    
    # WEB APP TUGMASI
    web_app_url = f"{WEBAPP_URL}/webapp?user_id={telegram_id}&page=animals"
    keyboard = [
        [InlineKeyboardButton("🌐 Barchasini ko'rish", web_app=WebAppInfo(url=web_app_url))]
    ]
    
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def butchers_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Qassoblar"""
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
    
    # WEB APP TUGMASI
    telegram_id = update.effective_user.id
    web_app_url = f"{WEBAPP_URL}/webapp?user_id={telegram_id}&page=butchers"
    keyboard = [
        [InlineKeyboardButton("🌐 Barchasini ko'rish", web_app=WebAppInfo(url=web_app_url))]
    ]
    
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

async def language_change(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Tilni o'zgartirish"""
    await update.message.reply_text(
        "🌐 Tilni tanlang / Выберите язык / Choose language:",
        reply_markup=get_language_keyboard()
    )

async def language_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Til callback"""
    query = update.callback_query
    await query.answer()
    
    lang = query.data.split('_')[1]
    telegram_id = update.effective_user.id
    
    db.update_user_language(telegram_id, lang)
    
    languages = {'uz': '🇺🇿 O\'zbekcha', 'ru': '🇷🇺 Русский', 'en': '🇬🇧 English'}
    await query.edit_message_text(f"✅ Til o'zgartirildi: {languages[lang]}")
    
    await context.bot.send_message(
        chat_id=telegram_id,
        text="📱 Asosiy menyu:",
        reply_markup=get_main_keyboard(lang)
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Yordam"""
    text = "📚 CHORVA FERMERI PRO v2.0\n\n"
    text += "🤖 Buyruqlar:\n"
    text += "• /start - Boshlash\n"
    text += "• /dashboard - Statistika\n"
    text += "• /animals - Hayvonlar\n"
    text += "• /butchers - Qassoblar\n"
    text += "• /language - Til\n"
    text += "• /help - Yordam\n\n"
    text += f"💻 Web dastur: {WEBAPP_URL}\n\n"
    text += "📱 Klaviatura tugmalari ham mavjud."
    
    await update.message.reply_text(text)

# ==================== MAIN ====================

def main():
    """Bot ishga tushirish"""
    db.init_db()
    logger.info("Database initialized")
    
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PHONE: [MessageHandler(filters.CONTACT, receive_phone)],
            FULLNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_fullname)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    # Handlerlar
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler('dashboard', dashboard))
    application.add_handler(CommandHandler('animals', animals_list))
    application.add_handler(CommandHandler('butchers', butchers_list))
    application.add_handler(CommandHandler('language', language_change))
    application.add_handler(CommandHandler('help', help_command))
    
    # Callback
    application.add_handler(CallbackQueryHandler(language_callback, pattern='^lang_'))
    
    # Klaviatura
    application.add_handler(MessageHandler(filters.Regex('🏠'), dashboard))
    application.add_handler(MessageHandler(filters.Regex('🐄'), animals_list))
    application.add_handler(MessageHandler(filters.Regex('👤'), butchers_list))
    application.add_handler(MessageHandler(filters.Regex('🌐'), language_change))
    application.add_handler(MessageHandler(filters.Regex('💰|🌾|💉|📊'), dashboard))
    
    logger.info("=" * 60)
    logger.info("🤖 CHORVA FERMERI PRO BOT - NGROK BILAN")
    logger.info("=" * 60)
    logger.info(f"🌍 Web App URL: {WEBAPP_URL}")
    logger.info("📱 Telegram botga /start yuboring!")
    logger.info("🌐 'Dasturni ochish' tugmasini bosing")
    logger.info("✅ Avtomatik login bo'ladi!")
    logger.info("=" * 60)
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
