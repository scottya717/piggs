import asyncio
import logging
import random
from datetime import datetime, time, timedelta
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

BOT_TOKEN = "ВСТАВЬ_СВОЙ_ТОКЕН_СЮДА"
CHAT_ID = 123456789

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# ============ КРИНЖ-БАЗА ============
MORNING_PHRASES = [
    "☀️ Доброе утро, свинопас! 🐷 Твои хрюшки уже бьются в истерике от голода. Накорми их, пока они не сожрали соседского кота!",
    "🐽 ВРЕМЯ ЗАВТРАКА ДЛЯ ПОРОСЯТ! Они смотрят на тебя грустными глазками... Или это просто они поджидают, когда ты заснёшь, чтобы захватить власть?",
    "🥓 Утро доброе, а свиньи злые! Они уже 5 минут без еды — это как 5 лет в свином измерении. БЕГИ КОРМИТЬ!",
    "🐷✨ Рассвет настал, и твои свиньи превратились в голодных монстров. Только ты можешь спасти этот мир... ну или хотя бы свой забор.",
    "🍽️ ПИКМИ-СВИНКИ ЖДУТ! Они уже написали петицию о твоём увольнении с поста кормильца. Успокой бунт, пока не поздно!",
    "🐷🔥 Твоя свинья номер 3 только что посмотрела на часы. Потом на тебя. Потом на нож. Совпадение? НЕ ДУМАЮ.",
]

EVENING_PHRASES = [
    "🌙 Вечер настал, а свиньи не наелись! Они уже строят планы по захвату холодильника. НАКОРМИ ИХ, ПОКА НЕ ПОЗДНО!",
    "🐷💀 Твои свинюшки в ярости! Они 12 часов ждали этого момента. Это их время. Это их месть. Корми, или беги.",
    "🌚 Луна взошла, и свиньи превратися в... нет, они просто останутся свиньями, но ОЧЕНЬ голодными. Кормёжка, немедленно!",
    "🍖 УЖИН ВРЕМЯ! Твои хрюндели уже разослали жалобы в Международный Суд по Правам Свиней. Ты в шаге от международного скандала!",
    "🐽🔥 ВЕЧЕРНИЙ БУНТ НАЧАЛСЯ! Свиньи отказываются хрюкать, пока ты не насыпешь им вкусняшек. Это шантаж, но ты знаешь правила игры.",
    "🌑 Тьма окутала двор. Свиньи собрались в круг. Ты слышишь шёпот? Это они обсуждают, какую часть тебя съесть первой. КОРМИ!",
]

RANDOM_PHRASES = [
    "🐷 Факт дня: свинья может есть за 3 минуты столько, сколько ты за неделю. Но твои свиньи уже 6 часов без еды. Математика простая: они СЕЙЧАС сожрут ТЕБЯ.",
    "📢 Срочные новости: твои свиньи создали TikTok-аккаунт и снимают танцы под грустную музыку, чтобы вымогать еду. Позор!",
    "🐽 Твоя свинья только что посмотрела на меня... Я чувствую её боль. Или это просто газ? В любом случае — КОРМИ!",
    "🥇 Достижение разблокировано: 'Свинопас-прокрастинатор'! Награда: голодный взгляд 5 свиней одновременно. Поздравляю?",
    "🐷💬 'Мы не злые, мы просто хотим есть' — сказала твоя свинья. А потом добавила: 'Но если через 5 минут не будет еды, мы начнём революцию'.",
    "🚨 ВНИМАНИЕ! Свиньи научились открывать двери. Твои двери. Пока ты читаешь это. БЕГИ К НИМ, ПОКА ОНИ НЕ ПРИШЛИ К ТЕБЕ.",
]

# ============ УГРОЗЫ ОТ ИМЕНИ СВИНЕЙ ============
THREATS = [
    "🐷📨 Письмо от свиньи Маши:\n\n'Привет, кормилец. Помнишь, как ты забыл покормить нас в прошлый раз? Мы помним. Мы всё помним. У нас есть список. Ты в нём. Подчёркнуто красным. Дважды.'",
    
    "🐷📨 Сообщение от свиньи Бориса:\n\n'Я знаю, где ты спишь. Я знаю, что ты ешь. Я знаю, что ты ЕЩЁ НЕ НАКОРМИЛ НАС. Последнее предупреждение. С уважением, Борис.'",
    
    "🐷📨 Записка под дверью (грязная, с копытными следами):\n\n'Мы наблюдаем. Мы ждём. Мы голодны. И у нас ОЧЕНЬ много свободного времени. — Коллективное письмо свиней'",
    
    "🐷📨 Голосовое сообщение от свиньи Пети (3:47 ночи):\n\n*хрюканье* *шорох* *звук падающего ножа* *тишина* *громкое хрюканье* \n\nПеревод: 'Завтра в 7 утра. Будь там. С едой. Или мы сами придём за тобой.'",
    
    "🐷📨 Ультиматум от старшей свиньи:\n\n'У тебя есть ровно 12 часов. Потом мы начинаем 'мирные протесты'. А потом — 'мирное' поглощение твоих запасов картошки. Выбор за тобой, мясо.'",
    
    "🐷📨 Селфи от свиньи с твоим носком в пасти:\n\n'Нашли в сушилке. Вкусно, но не то. Хотим нормальную еду. Или следующим будет твой телефон. У нас есть план. У тебя — 10 минут.'",
    
    "🐷📨 Подозрительное письмо без подписи:\n\n'Ты думаешь, забор держит нас? Забор держит ТЕБЯ. Мы просто ждём удобного момента. Корми нас — и момент откладывается. Пока что.'",
    
    "🐷📨 Групповой чат свиней (переслано 47 раз):\n\n'Кто-нибудь видел кормильца? Он опять пропал. Ребят, помните, как мы говорили про 'план Б'? Думаю, пришло время. Голосуем: 🐽 за, 🐷 против.'",
]

# ============ ДОСТИЖЕНИЯ ============
ACHIEVEMENTS = {
    "first_forget": {
        "name": "🥉 Новичок-предатель",
        "desc": "Впервые забыл покормить свиней. Они запомнят это. И тебя. Навсегда.",
        "rarity": "common"
    },
    "three_forgets": {
        "name": "🥈 Профессиональный забывальщик",
        "desc": "3 пропуска кормёжки! Свиньи уже обсуждают твою замену на робота. Или на соседа.",
        "rarity": "rare"
    },
    "week_streak": {
        "name": "🥇 Легенда прокрастинации",
        "desc": "Целая неделя без кормёжки! Свиньи выжили... каким-то чудом. Или съели соседа. Проверь забор.",
        "rarity": "epic"
    },
    "night_feed": {
        "name": "🌙 Полуночный свинопас",
        "desc": "Покормил в 3 часа ночи! Свиньи впечатлены. Они думают, что ты сошёл с ума. Они правы.",
        "rarity": "rare"
    },
    "perfect_day": {
        "name": "✨ Идеальный день",
        "desc": "Два раза вовремя! Свиньи смотрят на тебя с уважением. Это редкость. Запиши в дневник.",
        "rarity": "legendary"
    },
    "early_bird": {
        "name": "🌅 Ранняя пташка",
        "desc": "Покормил до 6 утра! Свиньи ещё спали, но ты разбудил их. Они недовольны, но накормлены. Компромисс.",
        "rarity": "common"
    },
    "late_night": {
        "name": "🦉 Сова",
        "desc": "Вечерняя кормёжка после 23:00! Свиньи уже спали и проснулись в шоке. Но еда есть еда.",
        "rarity": "common"
    },
    "panic_button": {
        "name": "😱 Паникёр",
        "desc": "Нажал /panic 5 раз! Ты либо очень тревожный, либо свиньи уже у двери. И то, и другое.",
        "rarity": "rare"
    },
    "fact_lover": {
        "name": "🤓 Свино-знаток",
        "desc": "Запросил 10 фактов про свиней! Теперь ты знаешь слишком много. Свиньи это заметили. Они нервничают.",
        "rarity": "epic"
    },
    "over feeder": {
        "name": "🍔 Перекормщик",
        "desc": "Нажал /feed 5 раз за день! Свиньи в восторге. Они думают, что это Рождество. Или конец света.",
        "rarity": "legendary"
    },
}

# ============ ФАКТЫ ПРО СВИНЕЙ ============
PIG_FACTS = [
    "🧠 ФАКТ: Свиньи умнее собак! Они могут решать головоломки быстрее, чем твой пёс. И твои свиньи уже решили головоломку 'как открыть холодильник'. Спойлер: они близки.",
    
    "🎮 ФАКТ: Свиньи умеют играть в видеоигры! Учёные научили их джойстику. Твои свиньи тоже учатся. Следующая цель — взломать твой смартфон и заказать еду.",
    
    "💬 ФАКТ: Свиньи общаются на 20 различных звуков! От 'я голоден' до 'я ОЧЕНЬ голоден' и 'если не накормишь, я расскажу всем, что ты спишь в носках'.",
    
    "🧼 ФАКТ: Свиньи чище, чем кажется! Они не потеют и купаются, чтобы охладиться. Твои свиньи купались в грязи? Нет. Они купались в ПЛАНАХ ПО ТВОЕЙ ЗАМЕНЕ.",
    
    "🏃 ФАКТ: Свинья может бегать со скоростью 17 км/ч! Это быстрее, чем ты бежишь к холодильнику ночью. Проверь замки. Серьёзно.",
    
    "🧬 ФАКТ: ДНК свиньи на 98% совпадает с человеческим! Это объясняет, почему твои свиньи так хорошо понимают твои оправдания. И почему они так злы.",
    
    "🐷 ФАКТ: Свиньи помнят лица до 2 лет! Твои свиньи помнят ТЕБЯ. И помнят каждый раз, когда ты опаздывал. У них есть архив. Он большой.",
    
    "🎨 ФАКТ: Свиньи умеют рисовать! Ну, копытом по грязи. Но всё же. Твоя свинья нарисовала твой портрет. С крестиком. И подписью 'следующий'.",
    
    "🌍 ФАКТ: В Китае свинья — символ богатства! В твоём дворе свинья — символ ТВОЕЙ головной боли. И источник кошмаров.",
    
    "🎵 ФАКТ: Свиньи распознают музыку! Они предпочитают классику. Твои свиньи предпочитают звук твоих шагов к кормушке. Или звук твоего плача.",
    
    "🛁 ФАКТ: Свиньи любят массаж! Если погладить их по спине, они расслабляются. Попробуй погладить свинью после 12 часов голода. Я посмотрю. С безопасного расстояния.",
    
    "🧮 ФАКТ: Свиньи умеют считать! Они знают, сколько раз ты кормил их сегодня. И сколько раз НЕ кормил. Итог: они злятся.",
    
    "🕵️ ФАКТ: Свиньи — мастера маскировки! В дикой природе они прячутся. В твоём дворе они прячутся... от тебя? Или ждут, пока ты заснёшь? Узнаем ночью.",
    
    "🍽️ ФАКТ: Свинья ест за день столько, сколько весит её голова. Твоя свинья весит 150 кг. Её голова — 15 кг. Сделай выводы. БЫСТРО.",
    
    "💤 ФАКТ: Свиньи спят по 8 часов, как люди! Но твои свиньи не спят. Они планируют. И ждут. И смотрят. ВСЕГДА смотрят.",
]

# ============ СТАТИСТИКА ============
user_stats = {
    "total_feeds": 0,
    "missed_feeds": 0,
    "perfect_days": 0,
    "panic_count": 0,
    "fact_count": 0,
    "last_feed_time": None,
    "achievements": set(),
    "daily_feeds": {},
}

def check_achievement(achievement_key):
    if achievement_key not in user_stats["achievements"]:
        user_stats["achievements"].add(achievement_key)
        ach = ACHIEVEMENTS[achievement_key]
        rarity_emoji = {"common": "⚪", "rare": "🔵", "epic": "🟣", "legendary": "🟡"}
        return (
            f"\n\n🏆 ДОСТИЖЕНИЕ РАЗБЛОКИРОВАНО!\n"
            f"{rarity_emoji.get(ach['rarity'], '⚪')} {ach['name']}\n"
            f"📜 {ach['desc']}\n"
            f"Редкость: {ach['rarity'].upper()}"
        )
    return ""

# ============ КОМАНДЫ ============

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🐷 О, новый свинопас!\n\n"
        "Я — бот, который будет тебя травмировать напоминалками про кормёжку.\n"
        "Два раза в день. Без права на отказ.\n\n"
        "Команды:\n"
        "/feed — 'Я покормил' (но я тебе не верю)\n"
        "/status — узнать, сколько времени прошло с последней кормёжки\n"
        "/panic — экстренная кринж-напоминалка\n"
        "/threat — получить личную угрозу от свиньи\n"
        "/fact — узнать страшный факт про свиней\n"
        "/achievements — твоя коллекция позора\n"
        "/stats — полная статистика твоих прегрешений\n\n"
        "Да прибудет с тобой сила... и еда для свиней! 🐽✨"
    )

async def feed(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    user_stats["total_feeds"] += 1
    
    today = now.strftime("%Y-%m-%d")
    if today not in user_stats["daily_feeds"]:
        user_stats["daily_feeds"][today] = 0
    user_stats["daily_feeds"][today] += 1
    
    # Проверка достижений
    extra = ""
    if user_stats["daily_feeds"][today] >= 5:
        extra += check_achievement("over feeder")
    
    if now.hour < 6:
        extra += check_achievement("early_bird")
    elif now.hour > 23:
        extra += check_achievement("late_night")
    
    # Проверка идеального дня
    feeds_today = user_stats["daily_feeds"].get(today, 0)
    if feeds_today >= 2 and (7 <= now.hour <= 9 or 18 <= now.hour <= 20):
        user_stats["perfect_days"] += 1
        if user_stats["perfect_days"] >= 1:
            extra += check_achievement("perfect_day")
    
    user_stats["last_feed_time"] = now
    
    responses = [
        f"🐷 Хрю-хрю! Свиньи довольны... ПОКА ЧТО. Увидимся через 12 часов, предатель.{extra}",
        f"✅ Записал! Но знаешь ли ты, что свинья помнит обиду 3 года? Они запомнят, если забудешь следующий раз.{extra}",
        f"🍽️ Отлично! Твои свинюшки сейчас делают тебе ментальную благодарность. Или просто жрут. Сложно различить.{extra}",
        f"🐽 Подтверждено! Статус: свиньи накормлены. Твоя совесть чиста... ненадолго.{extra}",
    ]
    await update.message.reply_text(responses[now.second % len(responses)])

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    last = user_stats["last_feed_time"]
    if last is None:
        user_stats["missed_feeds"] += 1
        extra = check_achievement("first_forget") if user_stats["missed_feeds"] == 1 else ""
        if user_stats["missed_feeds"] >= 3:
            extra += check_achievement("three_forgets")
        
        await update.message.reply_text(
            f"🐷❓ Статус: НЕИЗВЕСТНО!\n"
            f"Ты ещё ни разу не отмечал кормёжку. Свиньи уже обсуждают твою замену на автокормушку.\n"
            f"Используй /feed, если хочешь сохранить репутацию.{extra}"
        )
    else:
        diff = datetime.now() - last
        hours = diff.total_seconds() / 3600
        
        if hours > 24:
            user_stats["missed_feeds"] += 1
            extra = check_achievement("week_streak") if user_stats["missed_feeds"] >= 7 else ""
        else:
            extra = ""
        
        if hours < 6:
            msg = f"🐷✨ Последняя кормёжка: {int(diff.seconds//3600)}ч {(diff.seconds%3600)//60}м назад.\nСвиньи спокойны... НО НАДОЛГО ЛИ?"
        elif hours < 10:
            msg = f"🐷⚠️ Последняя кормёжка: {int(hours)}ч назад.\nСвиньи начинают копать. Не в землю. А планы."
        elif hours < 16:
            msg = f"🐷💀 ПОСЛЕДНЯЯ КОРМЁЖКА: {int(hours)}Ч НАЗАД!\nЭТО ЧЕРЕЗМЕРНО! СВИНЬИ УЖЕ ПОСТРОИЛИ БАРРИКАДЫ!"
        else:
            msg = f"🐷🔥🔥🔥 КРИТИЧЕСКАЯ СИТУАЦИЯ! {int(hours)}Ч БЕЗ ЕДЫ!\nСВИНЬИ УЖЕ НАПИСАЛИ ЗАВЕЩАНИЕ. ТВОЁ ЗАВЕЩАНИЕ. ПОТОМУ ЧТО ОНИ ИДУТ ЗА ТОБОЙ."
        
        await update.message.reply_text(msg + extra)

async def panic(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_stats["panic_count"] += 1
    extra = ""
    if user_stats["panic_count"] >= 5:
        extra = check_achievement("panic_button")
    
    await update.message.reply_text(
        f"🐷🔥🔥🔥 ЭКСТРЕННАЯ СИТУАЦИЯ! 🔥🔥🔥🐷\n\n"
        f"ТВОИ СВИНЬИ СЕЙЧАС СМОТРЯТ НА ТЕБЯ.\n"
        f"ОНИ ЗНАЮТ, ГДЕ ТЫ СПИШЬ.\n"
        f"ОНИ ЗНАЮТ, ГДЕ ТВОЯ ЕДА.\n"
        f"У ТЕБЯ ЕСТЬ 5 МИНУТ, ПОКА ОНИ НЕ НАЧАЛИ ПЕРЕГОВОРЫ С КОШКАМИ.\n\n"
        f"БЕГИ. КОРМИ. ВЫЖИВАЙ. 🐽⚡{extra}"
    )

async def threat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    threat_text = random.choice(THREATS)
    await update.message.reply_text(threat_text)

async def fact(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_stats["fact_count"] += 1
    extra = ""
    if user_stats["fact_count"] >= 10:
        extra = check_achievement("fact_lover")
    
    fact_text = random.choice(PIG_FACTS)
    await update.message.reply_text(fact_text + extra)

async def achievements(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not user_stats["achievements"]:
        await update.message.reply_text(
            "🏆 У тебя пока нет достижений!\n\n"
            "Свиньи разочарованы. Они ожидали хотя бы 'Новичок-предатель'.\n"
            "Попробуй забыть покормить их — это легко, и достижение гарантировано!\n"
            "Или запроси фактов: /fact"
        )
        return
    
    msg = "🏆 ТВОЯ КОЛЛЕКЦИЯ ПОЗОРА:\n\n"
    for ach_key in user_stats["achievements"]:
        ach = ACHIEVEMENTS[ach_key]
        rarity_emoji = {"common": "⚪", "rare": "🔵", "epic": "🟣", "legendary": "🟡"}
        msg += f"{rarity_emoji.get(ach['rarity'], '⚪')} {ach['name']}\n"
        msg += f"   📜 {ach['desc']}\n\n"
    
    msg += f"Всего разблокировано: {len(user_stats['achievements'])}/{len(ACHIEVEMENTS)}"
    await update.message.reply_text(msg)

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    last = user_stats["last_feed_time"]
    last_str = last.strftime("%d.%m %H:%M") if last else "НИКОГДА 😱"
    
    msg = (
        f"📊 СТАТИСТИКА СВИНОПАСА:\n\n"
        f"🍽️ Всего кормёжек: {user_stats['total_feeds']}\n"
        f"❌ Пропущено: {user_stats['missed_feeds']}\n"
        f"✨ Идеальных дней: {user_stats['perfect_days']}\n"
        f"😱 Паник нажато: {user_stats['panic_count']}\n"
        f"🤓 Фактов узнано: {user_stats['fact_count']}\n"
        f"🏆 Достижений: {len(user_stats['achievements'])}/{len(ACHIEVEMENTS)}\n"
        f"⏰ Последняя кормёжка: {last_str}\n\n"
    )
    
    if user_stats["missed_feeds"] == 0:
        msg += "🌟 Ты идеален! Свиньи в шоке. Они не верят, что такое возможно."
    elif user_stats["missed_feeds"] < 3:
        msg += "⚠️ Начинаешь сбиваться. Свиньи уже записывают."
    elif user_stats["missed_feeds"] < 7:
        msg += "💀 Свиньи разослали твою фотографию в свинячий даркнет. Осторожно."
    else:
        msg += "🔥 ТЫ В ЧЁРНОМ СПИСКЕ СВИНЕЙ. У ТЕБЯ НЕТ ШАНСОВ. БЕГИ."
    
    await update.message.reply_text(msg)

# ============ АВТОМАТИЧЕСКИЕ НАПОМИНАЛКИ ============

async def send_reminder(context: ContextTypes.DEFAULT_TYPE, phrases: list):
    phrase = phrases[datetime.now().day % len(phrases)]
    await context.bot.send_message(chat_id=CHAT_ID, text=phrase)

async def morning_reminder(context: ContextTypes.DEFAULT_TYPE):
    await send_reminder(context, MORNING_PHRASES)

async def evening_reminder(context: ContextTypes.DEFAULT_TYPE):
    await send_reminder(context, EVENING_PHRASES)

async def random_reminder(context: ContextTypes.DEFAULT_TYPE):
    await send_reminder(context, RANDOM_PHRASES)

async def daily_threat(context: ContextTypes.DEFAULT_TYPE):
    threat_text = random.choice(THREATS)
    await context.bot.send_message(
        chat_id=CHAT_ID, 
        text=f"🐷📨 ЕЖЕДНЕВНАЯ УГРОЗА ОТ СВИНЕЙ:\n\n{threat_text}"
    )

async def daily_fact(context: ContextTypes.DEFAULT_TYPE):
    fact_text = random.choice(PIG_FACTS)
    await context.bot.send_message(
        chat_id=CHAT_ID,
        text=f"🤓 СВИНО-ФАКТ ДНЯ:\n\n{fact_text}"
    )

def main():
    application = Application.builder().token(BOT_TOKEN).build()

    # Команды
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("feed", feed))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("panic", panic))
    application.add_handler(CommandHandler("threat", threat))
    application.add_handler(CommandHandler("fact", fact))
    application.add_handler(CommandHandler("achievements", achievements))
    application.add_handler(CommandHandler("stats", stats))

    # Напоминалки
    job_queue = application.job_queue
    
    job_queue.run_daily(morning_reminder, time=time(hour=7, minute=0))
    job_queue.run_daily(random_reminder, time=time(hour=14, minute=0))
    job_queue.run_daily(evening_reminder, time=time(hour=19, minute=0))
    job_queue.run_daily(daily_threat, time=time(hour=12, minute=0))
    job_queue.run_daily(daily_fact, time=time(hour=10, minute=0))

    print("🐷 Бот запущен! Свиньи под контролем... вроде.")
    application.run_polling()

if __name__ == "__main__":
    main()
