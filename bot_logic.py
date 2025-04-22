import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import supabase
from openai import OpenAI

# Настройка логгирования
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация клиентов
supabase_client = supabase.create_client(os.getenv('https://qcvralbhkfbmqohjhcni.supabase.co'), os.getenv(''))
openai_client = OpenAI(api_key=os.getenv(''))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    referrer_id = context.args[0] if context.args else None
    
    # Проверяем, есть ли пользователь в базе
    user_data = supabase_client.table('users').select('*').eq('telegram_id', user.id).execute()
    
    if not user_data.data:
        # Регистрация нового пользователя
        user_data = {
            'telegram_id': user.id,
            'username': user.username,
            'full_name': user.full_name,
            'referrer_id': int(referrer_id) if referrer_id and referrer_id.isdigit() else None
        }
        supabase_client.table('users').insert(user_data).execute()
        
        # Начисление бонуса рефереру
        if referrer_id and referrer_id.isdigit():
            referrer_bonus = 100  # Примерная сумма бонуса
            supabase_client.rpc('increment_balance', {'user_id': int(referrer_id), 'amount': referrer_bonus}).execute()
            supabase_client.table('referral_payments').insert({
                'referrer_id': int(referrer_id),
                'referred_id': user.id,
                'amount': referrer_bonus
            }).execute()
    
    await update.message.reply_text(
        f"Привет, {user.full_name}! Я помогу тебе учитывать расходы.\n\n"
        "Отправь мне сообщение с суммой и категорией, например:\n"
        "• '500 руб продукты' (текстом)\n"
        "• или голосовое сообщение 'потратил 500 рублей на продукты'\n\n"
        "Доступные команды:\n"
        "/report - получить отчет\n"
        "/referral - получить реферальную ссылку\n"
        "/export - экспорт данных"
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    
    # Используем ИИ для разбора текста
    response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Извлеки сумму, категорию и описание из текста о расходах. Ответь в формате JSON: {'amount': число, 'category': строка, 'description': строка}"},
            {"role": "user", "content": text}
        ],
        response_format={ "type": "json_object" }
    )
    
    try:
        data = json.loads(response.choices[0].message.content)
        amount = float(data['amount'])
        category = data['category']
        description = data.get('description', '')
        
        # Сохраняем транзакцию
        supabase_client.table('transactions').insert({
            'user_id': user_id,
            'amount': amount,
            'category': category,
            'description': description
        }).execute()
        
        await update.message.reply_text(f"Записал: {amount} руб на {category}")
    except Exception as e:
        logger.error(f"Error processing text: {e}")
        await update.message.reply_text("Не смог разобрать сообщение. Попробуй в формате: '500 руб продукты'")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = update.message.voice
    user_id = update.effective_user.id
    
    # Скачиваем голосовое сообщение
    voice_file = await context.bot.get_file(voice.file_id)
    voice_path = f"voice_{user_id}.ogg"
    await voice_file.download_to_drive(voice_path)
    
    # Преобразуем голос в текст
    with open(voice_path, "rb") as audio_file:
        transcript = openai_client.audio.transcriptions.create(
            file=audio_file,
            model="whisper-1",
            response_format="json"
        )
    
    text = transcript.text
    os.remove(voice_path)
    
    # Обрабатываем текст как обычное сообщение
    await handle_text(update.message.reply_text(text), context)

async def generate_report(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    period = context.args[0] if context.args else 'month'
    
    # Получаем данные из Supabase
    if period == 'week':
        query = supabase_client.table('transactions').select('*').eq('user_id', user_id).gte('transaction_date', 'now()::date - interval \'7 days\'').execute()
    else:  # month
        query = supabase_client.table('transactions').select('*').eq('user_id', user_id).gte('transaction_date', 'now()::date - interval \'1 month\'').execute()
    
    transactions = query.data
    
    if not transactions:
        await update.message.reply_text("Нет данных за выбранный период")
        return
    
    # Анализ расходов
    total = sum(t['amount'] for t in transactions)
    by_category = {}
    for t in transactions:
        by_category[t['category']] = by_category.get(t['category'], 0) + t['amount']
    
    # Формируем отчет
    report = f"Отчет за {'неделю' if period == 'week' else 'месяц'}:\n"
    report += f"Всего потрачено: {total} руб\n\n"
    report += "По категориям:\n"
    for category, amount in by_category.items():
        report += f"- {category}: {amount} руб ({amount/total*100:.1f}%)\n"
    
    # Добавляем рекомендации от ИИ
    ai_response = openai_client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Дай краткие рекомендации по оптимизации расходов на основе данных. Будь дружелюбным и конкретным."},
            {"role": "user", "content": str(by_category)}
        ]
    )
    
    report += "\nРекомендации:\n" + ai_response.choices[0].message.content
    
    await update.message.reply_text(report)

async def referral_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    referral_link = f"https://t.me/your_bot?start={user_id}"
    
    # Получаем статистику по рефералам
    referrals = supabase_client.table('users').select('count(*)').eq('referrer_id', user_id).execute()
    earnings = supabase_client.table('referral_payments').select('sum(amount)').eq('referrer_id', user_id).execute()
    
    await update.message.reply_text(
        f"Ваша реферальная ссылка: {referral_link}\n\n"
        f"Приглашено пользователей: {referrals.data[0]['count'] or 0}\n"
        f"Заработано: {earnings.data[0]['sum'] or 0} руб"
    )

async def export_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Получаем все транзакции пользователя
    transactions = supabase_client.table('transactions').select('*').eq('user_id', user_id).execute().data
    
    if not transactions:
        await update.message.reply_text("Нет данных для экспорта")
        return
    
    # Создаем CSV файл
    csv_file = f"transactions_{user_id}.csv"
    with open(csv_file, 'w') as f:
        f.write("Дата,Сумма,Категория,Описание\n")
        for t in transactions:
            f.write(f"{t['transaction_date']},{t['amount']},{t['category']},{t['description']}\n")
    
    # Отправляем файл пользователю
    with open(csv_file, 'rb') as f:
        await update.message.reply_document(document=f, filename="transactions.csv")
    
    os.remove(csv_file)

def main():
    application = Application.builder().token(os.getenv('TELEGRAM_TOKEN')).build()
    
    # Обработчики команд
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("report", generate_report))
    application.add_handler(CommandHandler("referral", referral_info))
    application.add_handler(CommandHandler("export", export_data))
    
    # Обработчики сообщений
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.VOICE, handle_voice))
    
    application.run_polling()

if __name__ == '__main__':
    main()
