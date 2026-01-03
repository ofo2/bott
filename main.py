import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
import os
from datetime import datetime
import requests
import logging
from pathlib import Path

# إعداد البوت
TOKEN = "7610806578:AAH1DUUk_JaEGO5fh13r3HuQOV9siarQYOM"
bot = telebot.TeleBot(TOKEN, threaded=False)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# قوائم المنتجات
purchase_options = ["🎮 60 شدة", "🎮 325 شدة", "🎮 660 شدة", "🎮 1800 شدة", "🎮 3800 شدة", "🎮 8100 شدة"]
codes_options = ["🎮 60 كود", "🎮 325 كود", "🎮 660 كود", "🎮 1800 كود", "🎮 3800 كود", "🎮 8100 كود"]

payment_methods = {
    "شام كاش": "sirtel_cash.jpg",
    "سيرتيل كاش": "sham_cash.jpg"
}

currencies = {
    "💵 دولار أمريكي": "usd",
    "🇸🇾 ليرة سورية": "syp"
}

# قائمة الأسعار
prices = {
    "🎮 60 شدة": {"usd": "1 $", "syp": "11,000 ل.س"},
    "🎮 325 شدة": {"usd": "4 $", "syp": "42,000 ل.س"},
    "🎮 660 شدة": {"usd": "8 $", "syp": "85,000 ل.س"},
    "🎮 1800 شدة": {"usd": "20 $", "syp": "170,000 ل.س"},
    "🎮 3800 شدة": {"usd": "38 $", "syp": "350,000 ل.س"},
    "🎮 8100 شدة": {"usd": "75 $", "syp": "720,000 ل.س"},
    "🎮 60 كود": {"usd": "1 $", "syp": "11,000 ل.س"},
    "🎮 325 كود": {"usd": "4 $", "syp": "42,000 ل.س"},
    "🎮 660 كود": {"usd": "8 $", "syp": "85,000 ل.س"},
    "🎮 1800 كود": {"usd": "20 $", "syp": "170,000 ل.س"},
    "🎮 3800 كود": {"usd": "38 $", "syp": "350,000 ل.س"},
    "🎮 8100 كود": {"usd": "75 $", "syp": "720,000 ل.س"}
}

# Helper functions
def get_or_create_user(telegram_id, first_name, last_name, username):
    """Get or create user via API"""
    try:
        response = requests.post(f"{BACKEND_URL}/users/", json={
            "telegram_id": telegram_id,
            "first_name": first_name,
            "last_name": last_name,
            "username": username
        }, timeout=5)

        if response.status_code in [200, 201]:
            return response.json()
        else:
            logger.error(f"Failed to create/get user: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error in get_or_create_user: {e}")
        return None

def create_order(order_data):
    """Create order via API"""
    try:
        response = requests.post(f"{BACKEND_URL}/orders/", json=order_data, timeout=5)
        if response.status_code in [200, 201]:
            return response.json()
        else:
            logger.error(f"Failed to create order: {response.status_code}")
            return None
    except Exception as e:
        logger.error(f"Error in create_order: {e}")
        return None

def notify_admin(order_data):
    """Send notification to admin about new order"""
    try:
        # Get admin telegram ID from settings
        response = requests.get(f"{BACKEND_URL}/settings/", timeout=5)
        if response.status_code == 200:
            settings = response.json()
            admin_id = settings.get("admin_telegram_id")

            if admin_id:
                message = f"🔔 طلب جديد!\n\n"
                message += f"👤 العميل: {order_data.get('user_name')}\n"
                message += f"🎮 المنتج: {order_data.get('product_type')} {order_data.get('quantity')}\n"
                message += f"💰 السعر: {order_data.get('price')}\n"
                message += f"💳 طريقة الدفع: {order_data.get('payment_method')}\n"
                message += f"🔐 رمز الطلب: {order_data.get('transaction_code')}\n"

                bot.send_message(admin_id, message)
    except Exception as e:
        logger.error(f"Error notifying admin: {e}")

# رسالة البداية
@bot.message_handler(commands=['start', 'menu'])
def start_menu(message):
    # Create/get user
    user = message.from_user
    get_or_create_user(user.id, user.first_name, user.last_name, user.username)

    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        KeyboardButton("💰 الشراء"),
        KeyboardButton("🔑 اكواد الشدات"),
        KeyboardButton("📦 أقسام أخرى")
    )
    bot.send_message(message.chat.id, "مرحبًا! اختر القسم:", reply_markup=markup)

# قسم الشراء
@bot.message_handler(func=lambda msg: msg.text == "💰 الشراء")
def buy_section(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for item in purchase_options:
        markup.add(KeyboardButton(item))
    markup.add(KeyboardButton("🔙 العودة"))
    bot.send_message(message.chat.id, "اختر كمية الشدة للشراء:", reply_markup=markup)

# قسم الأكواد
@bot.message_handler(func=lambda msg: msg.text == "🔑 اكواد الشدات")
def codes_section(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for item in codes_options:
        markup.add(KeyboardButton(item))
    markup.add(KeyboardButton("🔙 العودة"))
    bot.send_message(message.chat.id, "اختر كمية الاكواد:", reply_markup=markup)

# أقسام أخرى
@bot.message_handler(func=lambda msg: msg.text == "📦 أقسام أخرى")
def other_sections(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(
        KeyboardButton("📄 معلومات"),
        KeyboardButton("🆘 الدعم"),
        KeyboardButton("🔙 العودة")
    )
    bot.send_message(message.chat.id, "اختر القسم:", reply_markup=markup)

# العودة للقائمة الرئيسية
@bot.message_handler(func=lambda msg: msg.text == "🔙 العودة")
def back_to_menu(message):
    start_menu(message)

# اختيار كمية
@bot.message_handler(func=lambda msg: msg.text in purchase_options + codes_options)
def choose_currency(message):
    selected_amount = message.text
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    for currency in currencies.keys():
        markup.add(KeyboardButton(currency))
    markup.add(KeyboardButton("🔙 العودة"))
    bot.send_message(message.chat.id, f"لقد اخترت: {selected_amount}\nاختر العملة:", reply_markup=markup)
    bot.register_next_step_handler(message, choose_payment_method, selected_amount)

# اختيار طريقة الدفع
def choose_payment_method(message, amount):
    if message.text in currencies:
        selected_currency = currencies[message.text]
        markup = ReplyKeyboardMarkup(resize_keyboard=True)
        for method in payment_methods.keys():
            markup.add(KeyboardButton(method))
        markup.add(KeyboardButton("🔙 العودة"))
        bot.send_message(message.chat.id, f"اختر طريقة الدفع:", reply_markup=markup)
        bot.register_next_step_handler(message, send_payment_image, amount, message.text, selected_currency)
    elif message.text == "🔙 العودة":
        start_menu(message)
    else:
        bot.send_message(message.chat.id, "خيار غير صحيح. حاول مرة أخرى.")
        choose_currency(message)

# إرسال صورة الدفع
def send_payment_image(message, amount, currency_name, currency_type):
    if message.text in payment_methods:
        photo_file = Path(__file__).parent / payment_methods[message.text]
        price = prices.get(amount, {}).get(currency_type, "غير متوفر")

        try:
            with open(photo_file, "rb") as photo:
                caption = f"✅ تم تأكيد الطلب\n\n📦 الكمية: {amount}\n💳 طريقة الدفع: {message.text}\n💷 العملة: {currency_name}\n💰 السعر: {price}"
                bot.send_photo(message.chat.id, photo, caption=caption)

            bot.send_message(message.chat.id, "ارسل صورة او رمز او عملية التحويل الى هنا @rnxxe ✅🌹")
            bot.register_next_step_handler(message, verify_transaction, amount, message.text, currency_name, currency_type, price)
        except FileNotFoundError:
            bot.send_message(message.chat.id, f"الصورة الخاصة ب{message.text} غير موجودة.")
            start_menu(message)
    elif message.text == "🔙 العودة":
        start_menu(message)
    else:
        bot.send_message(message.chat.id, "تم الإلغاء أو الخيار غير صحيح.")
        start_menu(message)

# التحقق من رمز العملية
def verify_transaction(message, amount, payment_method, currency_name, currency_type, price):
    import uuid

    transaction_id = str(uuid.uuid4())[:8].upper()
    user = message.from_user

    # Get user data
    user_data = get_or_create_user(user.id, user.first_name, user.last_name, user.username)

    if not user_data:
        bot.send_message(message.chat.id, "حدث خطأ. يرجى المحاولة مرة أخرى.")
        start_menu(message)
        return

    # Extract product info
    product_type = "شدة" if "شدة" in amount else "كود"
    quantity = amount.split()[1]

    # Prepare order data
    order_data = {
        "user_id": user_data.get("id"),
        "user_telegram_id": user.id,
        "user_name": f"{user.first_name} {user.last_name or ''}".strip(),
        "product_type": product_type,
        "quantity": quantity,
        "currency": currency_type,
        "currency_display": currency_name,
        "payment_method": payment_method,
        "price": price,
        "transaction_code": transaction_id
    }

    # Handle photo or text
    if message.content_type == 'photo':
        file_info = bot.get_file(message.photo[-1].file_id)
        order_data["payment_proof"] = f"photo:{file_info.file_id}"
    elif message.content_type == 'text':
        order_data["payment_proof"] = f"text:{message.text}"

    # Create order
    order = create_order(order_data)

    if order:
        # Send confirmation to user
        confirmation_msg = f"✅ تم استقبال طلبك بنجاح!\n\n"
        confirmation_msg += f"📋 بيانات الطلب:\n"
        confirmation_msg += f"━━━━━━━━━━━━━━━━━\n"
        confirmation_msg += f"🎮 المنتج: {amount}\n"
        confirmation_msg += f"💳 طريقة الدفع: {payment_method}\n"
        confirmation_msg += f"💷 العملة: {currency_name}\n"
        confirmation_msg += f"💰 السعر: {price}\n"
        confirmation_msg += f"🔐 رمز الطلب: {transaction_id}\n"
        confirmation_msg += f"━━━━━━━━━━━━━━━━━\n\n"
        confirmation_msg += f"سيتم معالجة طلبك قريباً 🚀"
        bot.send_message(message.chat.id, confirmation_msg)

        # Notify admin
        notify_admin(order_data)
    else:
        bot.send_message(message.chat.id, "حدث خطأ في حفظ الطلب. يرجى المحاولة مرة أخرى.")

    start_menu(message)

# معلومات
@bot.message_handler(func=lambda msg: msg.text in ["📄 معلومات", "🆘 الدعم"])
def other_info(message):
    if message.text == "📄 معلومات":
        bot.send_message(message.chat.id, "بوت الشراء والبيع.\nيمكنك شراء الشدات والأكواد بسهولة.")
    elif message.text == "🆘 الدعم":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("💬 واتس أب", url="https://wa.me/963982597773"))
        bot.send_message(message.chat.id,
                        "للدعم اتصل بنا:\n📱 الهاتف: +963982597773\n📧 البريد: abodshoiep1@gmail.com\n\nأو اضغط على الزر أدناه للتواصل عبر واتس أب 👇",
                        reply_markup=markup)

def run_bot():
    """Run the bot"""
    logger.info("Starting bot...")
    try:
        bot.delete_webhook()
        logger.info("Webhook deleted")
        bot.infinity_polling(timeout=10, long_polling_timeout=5)
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise

if __name__ == "__main__":
    run_bot()
