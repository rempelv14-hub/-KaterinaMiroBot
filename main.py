import asyncio
import html
import os
import sqlite3
from datetime import datetime
from pathlib import Path

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import FSInputFile, Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv


load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
ADMIN_ID_RAW = os.getenv("ADMIN_ID", "").strip()
START_PHOTO = os.getenv("START_PHOTO", "start.jpg").strip() or "start.jpg"
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "").strip()
PROTECT_CONTENT = os.getenv("PROTECT_CONTENT", "true").lower() in {"1", "true", "yes", "on"}
DB_PATH = os.getenv("DB_PATH", "katya_bot.db").strip()

if not BOT_TOKEN:
    raise RuntimeError("Заполните BOT_TOKEN в .env или Railway Variables")

ADMIN_ID = int(ADMIN_ID_RAW) if ADMIN_ID_RAW.isdigit() else 779528794


WELCOME_TEXT = """<b>Добро пожаловать 🫶🏻</b>

Хорошо, что ты здесь. Значит, ты уже ищешь способ зарабатывать.

Меня зовут Катя. 4 года назад я начала бизнес на брендовом стоке с 60 000 рублей — в декрете, с ребёнком на руках и без опыта в продажах.

Сегодня мой доход минимум 200 тысяч рублей в месяц. И это не случайность — это система.
В найм я уже не вернулась.

<b>Почему тебе нужен этот бот?</b>

Потому что большинство теряют деньги на старте. Покупают не тот товар. Идут к «левым» поставщикам. Сливают бюджет и разочаровываются.

Здесь ты получаешь сразу готовую базу:
✔️ Проверенные поставщики из России
✔️ Прямые фабрики Европы
✔️ Надёжная логистика
✔️ Контакты оригинальной люксовой косметики
✔️ Базу для запуска магазина с брендами
✔️ Моё личное сопровождение

Без ошибок, которые стоят десятки тысяч.
Без «серых» схем.
Без риска нарваться на обман.

<b>Что ты будешь продавать?</b>

Стоковые оригинальные бренды.
Не «дешёвку», а ликвидный брендовый товар, который покупают снова и снова:

Sandro, Pinko, Maje, COS, Arket, Guess, Tommy Hilfiger, Calvin Klein, Max Mara, Simone Perele и другие известные бренды.

Это товар с низкой закупкой и высоким спросом. То, на чём реально зарабатывают.

<b>Кому это подойдёт:</b>
— хочешь открыть свой магазин
— уже продаёшь и хочешь масштабироваться
— ищешь прибыльную нишу
— хочешь работать из дома
— устал(а) терять деньги на ошибках

Сейчас у тебя есть два варианта: оставить всё как есть или зайти в систему, которая уже приносит результат.

Я прошла этот путь сама — и ты можешь пройти его быстрее, без потерь.

Внутри бота — все инструменты и возможность пойти со мной в наставничество.

<b>Выбирай направление и начинай со мной 😊</b>"""


SECTION_TEXTS = {
    "cosmetics_suppliers": """<b>💄 База поставщиков оригинальной косметики</b>

Создай канал, размести ассортимент с собственной наценкой и привлекай аудиторию.

Твоя задача — просто брать готовый контент и публиковать его в своих соцсетях.

Далее — собираешь заказы, оформляешь поставку и получаешь свою прибыль.

Это не массовая база из интернета.
Только проверенные контакты, которые передаются в узком кругу.

Я собрала для вас 50+ поставщиков оригинальной косметики — Россия и Казахстан. Без рисков, лишних тестов и потери времени.

В ассортименте — культовые и востребованные бренды:
Dior, Chanel, Charlotte Tilbury, Gucci, Valentino, Rare Beauty и другие.

Также доступны современные бьюти-девайсы, включая AGE-R Booster 6-в-1 от Medicube.

👉 Ознакомиться с ассортиментом можно тут:
https://t.me/+CZn1DOBxmV9iZWEy

<b>Для кого это решение:</b>
— для действующего бизнеса, который готов выйти в сегмент люкс
— для запуска с нуля с сильной продуктовой базой
— для тех, кто выбирает скорость, качество и готовые решения

<b>Бонусы от меня 🎁:</b>
— контакт поставщика оригинальной парфюмерии, включая редкие позиции и отливанты
— контакт байера из США: Sephora, выкуп от 15 единиц, доставка до Москвы бесплатно

Вы получаете не просто базу, а готовое решение для запуска бизнеса. Без риска, с проверенными поставщиками.""",

    "brand_suppliers_rf": """<b>👗 Поставщики в России</b>

Первые закупки — всегда риск: легко потерять деньги и сложно понять, кому доверять.

Поэтому я собрала для вас базу из 14 проверенных поставщиков брендового стока по России — всех тестировала лично, на своих закупках.

Никаких случайных контактов — только те, с кем я реально работаю.

Весь товар уже в России — доставка до вас всего 7–14 дней после закупа. Это быстрый реальный старт вашего бизнеса.

И бонус: на стоке можно не только зарабатывать, но и выгодно одевать себя и свою семью.

<b>Посмотреть ассортимент и цены:</b>
https://t.me/+aBk00zrOeYcwOTky

<b>🎁 Бонусы к базе:</b>

<b>1. Сообщество продавцов стока</b>
— обмен и продажа товара
— чёрный список поставщиков
— живое общение селлеров
— доступ к мелкому опту
— поддержка на старте

<b>2. Личная консультация</b>
После покупки:
— изучаете базу
— готовите вопросы
— созваниваемся

Разберём, что закупать, с чего начать и как быстрее выйти в прибыль.""",

    "factories_europe": """<b>🇪🇺 Поставщики Европа — прямые фабрики без посредников</b>

Это не просто база, а инструмент для роста действующих предпринимателей.

Если у тебя уже есть магазин — ты можешь расширить ассортимент, зайти в более сильный сегмент и увеличить средний чек.

Внутри — 3 крупные фабрики из Германии и Польши, работающие напрямую, без перекупов и лишних наценок.

<b>Посмотреть пример ассортимента и цен:</b>
https://t.me/+R8s3vQ_Mcms0NmJi

<b>Что ты получаешь:</b>
✔️ прямые контакты менеджеров фабрик
✔️ доступ к закрытым группам с ассортиментом
✔️ регулярные обновления складов

<b>И ключевое:</b>
✔️ проверенный перевозчик, который доставляет товар напрямую от фабрик и сопровождает поставки до получения

<b>Преимущества для бизнеса:</b>
— закупка без посредников и переплат
— доступ к новинкам раньше рынка
— ниже себестоимость = выше маржа
— усиление ассортимента и рост чека

<b>Подходит для:</b>
— действующих предпринимателей, которые хотят увеличить прибыль
— магазинов, которые ищут новый ассортимент
— тех, кто устал от перекупов и хочет прямые закупки
— новичков, которые хотят стартовать сразу правильно

<b>🎁 Бонус: личная консультация со мной</b>

После покупки:
— получаешь материалы
— изучаешь
— готовишь вопросы
— и мы созваниваемся

Разберём, что выгодно закупать, какие бренды дают прибыль и как быстрее выйти в плюс.

Это не просто контакты — это выход на прямые фабрики Европы и возможность масштабировать свой бизнес.""",

    "shop_turnkey": """<b>🚀 Личное сопровождение под ключ</b>

Если вы хотите:
— открыть магазин брендового стока
— выйти из «потолка» по доходу
— расширить ассортимент и увеличить чек
— работать без хаоса и лишних рисков

Тогда сопровождение — это самый быстрый путь к результату.

<b>Почему этого мало — просто контакты?</b>

Контакты без опыта не дают результата.

Важно понимать:
— с чего начать
— что закупать
— как масштабироваться без потерь

Я даю не просто контакты — я даю систему и веду за руку.

<b>Что входит:</b>
✔️ 1,5 месяца сопровождения
✔️ 7 личных созвонов: ниша, ассортимент, поставщики, стратегия, масштабирование
✔️ чат-поддержка
✔️ все мои базы: поставщики РФ, фабрики Европы, люкс-косметика
✔️ индивидуальная стратегия под ваш магазин и город

<b>Важно:</b>
В стоимость уже входят все мои собранные базы поставщиков + мой 5-летний опыт работы в этой нише.

<b>Результат:</b>
— первая прибыль уже с первой закупки
— понятная модель бизнеса без хаоса
— безопасные закупки и меньше ошибок
— чёткий план действий
— возможность масштабироваться и расти в доходе

<b>Почему со мной:</b>
✔️ 5 лет в товарном бизнесе
✔️ 2 действующих онлайн-магазина
✔️ проверенные поставщики и фабрики Европы
✔️ знаю все ошибки и риски на практике

Это не «обучение сверху», а работа рядом с человеком, который уже прошёл этот путь и помогает пройти его быстрее.""",

    "tariffs": """<b>💰 Тарифы</b>

<b>1. База поставщиков оригинальной косметики — 4 990 ₽</b>
Входит:
— 50+ поставщиков оригинальной косметики: Россия и Казахстан
— проверенные контакты
— бонус: поставщик оригинальной парфюмерии
— бонус: байер из США

<b>2. База поставщиков брендов РФ — 19 500 ₽</b>
Входит:
— 14 проверенных поставщиков брендового стока по России
— сообщество продавцов стока
— чёрный список поставщиков
— доступ к мелкому опту
— личная консультация

<b>3. Фабрики Европы — 29 900 ₽</b>
Входит:
— 3 прямые фабрики из Германии и Польши
— контакты менеджеров
— закрытые группы с ассортиментом
— регулярные обновления складов
— проверенный перевозчик
— личная консультация

<b>4. Личное сопровождение под ключ — 95 000 ₽</b>
Входит:
— 1,5 месяца сопровождения
— 7 личных созвонов
— чат-поддержка
— все базы поставщиков
— индивидуальная стратегия под ваш магазин и город

<b>💳 Оплата:</b>
Банк: ВТБ
Карта: <code>2200 2418 5353 3812</code>

Чтобы купить тариф, выберите нужную кнопку ниже. Бот покажет карту для оплаты и попросит отправить чек.

После проверки оплаты Катерина подтвердит доступ, и PDF откроется автоматически.""",
}



DOCUMENTS = {
    "cosmetics_suppliers": "cosmetics.pdf",
    "brand_suppliers_rf": "russia_suppliers.pdf",
    "factories_europe": "europe_factories.pdf",
}


TARIFFS = {
    "cosmetics_suppliers": {
        "title": "База поставщиков оригинальной косметики",
        "price": "4 990 ₽",
    },
    "brand_suppliers_rf": {
        "title": "База поставщиков брендов РФ",
        "price": "19 500 ₽",
    },
    "factories_europe": {
        "title": "Фабрики Европы",
        "price": "29 900 ₽",
    },
    "shop_turnkey": {
        "title": "Личное сопровождение под ключ",
        "price": "95 000 ₽",
    },
}


PAYMENT_BANK = "ВТБ"
PAYMENT_CARD = "2200 2418 5353 3812"


class QuestionState(StatesGroup):
    waiting_for_question = State()


class PaymentState(StatesGroup):
    waiting_for_receipt = State()


router = Router()


def db() -> sqlite3.Connection:
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            last_name TEXT,
            created_at TEXT,
            last_seen_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS questions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            question TEXT,
            created_at TEXT
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS paid_access (
            user_id INTEGER,
            section_key TEXT,
            approved_at TEXT,
            PRIMARY KEY (user_id, section_key)
        )
    """)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS payment_requests (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            first_name TEXT,
            section_key TEXT,
            amount TEXT,
            receipt_text TEXT,
            status TEXT,
            created_at TEXT
        )
    """)
    conn.commit()
    return conn


def save_user(message: Message) -> None:
    user = message.from_user
    if not user:
        return

    now = datetime.now().isoformat(timespec="seconds")
    conn = db()
    conn.execute(
        """
        INSERT INTO users (user_id, username, first_name, last_name, created_at, last_seen_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            username = excluded.username,
            first_name = excluded.first_name,
            last_name = excluded.last_name,
            last_seen_at = excluded.last_seen_at
        """,
        (user.id, user.username, user.first_name, user.last_name, now, now),
    )
    conn.commit()
    conn.close()



def has_access(user_id: int, section_key: str) -> bool:
    conn = db()
    row = conn.execute(
        "SELECT 1 FROM paid_access WHERE user_id = ? AND section_key = ?",
        (user_id, section_key),
    ).fetchone()
    conn.close()
    return row is not None


def grant_access(user_id: int, section_key: str) -> None:
    conn = db()
    conn.execute(
        """
        INSERT OR REPLACE INTO paid_access (user_id, section_key, approved_at)
        VALUES (?, ?, ?)
        """,
        (user_id, section_key, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()


def save_payment_request(message: Message, section_key: str, receipt_text: str) -> None:
    user = message.from_user
    tariff = TARIFFS.get(section_key, {})
    conn = db()
    conn.execute(
        """
        INSERT INTO payment_requests
        (user_id, username, first_name, section_key, amount, receipt_text, status, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user.id if user else 0,
            f"@{user.username}" if user and user.username else "без username",
            user.first_name if user else "Пользователь",
            section_key,
            tariff.get("price", ""),
            receipt_text,
            "waiting",
            datetime.now().isoformat(timespec="seconds"),
        ),
    )
    conn.commit()
    conn.close()


def payment_text(section_key: str) -> str:
    tariff = TARIFFS.get(section_key)
    if not tariff:
        return "Тариф не найден."

    return (
        "<b>💳 Оплата тарифа</b>\n\n"
        f"<b>Тариф:</b> {html.escape(tariff['title'])}\n"
        f"<b>Сумма:</b> {html.escape(tariff['price'])}\n\n"
        f"<b>Банк:</b> {html.escape(PAYMENT_BANK)}\n"
        f"<b>Карта:</b> <code>{html.escape(PAYMENT_CARD)}</code>\n\n"
        "1. Переведите сумму на карту.\n"
        "2. После оплаты нажмите кнопку «📎 Я оплатил(а), отправить чек».\n"
        "3. Отправьте чек или скриншот перевода одним сообщением.\n\n"
        "После проверки оплаты Катерина подтвердит доступ, и бот автоматически выдаст материал."
    )


def payment_keyboard(section_key: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="💳 Реквизиты для оплаты", callback_data=f"pay_info:{section_key}")
    kb.button(text="📎 Я оплатил(а), отправить чек", callback_data=f"receipt:{section_key}")
    kb.button(text="⬅️ К тарифам", callback_data="section:tariffs")
    kb.adjust(1)
    return kb.as_markup()


def payment_admin_keyboard(user_id: int, section_key: str):
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Подтвердить оплату", callback_data=f"approve:{section_key}:{user_id}")
    kb.button(text="❌ Отклонить", callback_data=f"decline:{section_key}:{user_id}")
    kb.adjust(1)
    return kb.as_markup()


def main_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="База поставщиков оригинальной косметики (РФ, КЗ)", callback_data="section:cosmetics_suppliers")
    kb.button(text="База поставщиков брендов (РФ)", callback_data="section:brand_suppliers_rf")
    kb.button(text="Фабрики Европы", callback_data="section:factories_europe")
    kb.button(text="Запуск магазина под ключ", callback_data="section:shop_turnkey")
    kb.button(text="💰 Тарифы", callback_data="section:tariffs")
    kb.button(text="💬 Связь со мной", callback_data="ask_question")
    kb.adjust(1)
    return kb.as_markup()


def back_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="⬅️ Назад в меню", callback_data="back_to_menu")
    kb.adjust(1)
    return kb.as_markup()


def tariffs_keyboard():
    kb = InlineKeyboardBuilder()
    kb.button(text="Купить: косметика — 4 990 ₽", callback_data="pay:cosmetics_suppliers")
    kb.button(text="Купить: поставщики РФ — 19 500 ₽", callback_data="pay:brand_suppliers_rf")
    kb.button(text="Купить: фабрики Европы — 29 900 ₽", callback_data="pay:factories_europe")
    kb.button(text="Купить: сопровождение — 95 000 ₽", callback_data="pay:shop_turnkey")
    kb.button(text="⬅️ Назад в меню", callback_data="back_to_menu")
    kb.adjust(1)
    return kb.as_markup()


def section_keyboard(section_key: str, user_id: int | None = None):
    kb = InlineKeyboardBuilder()

    if section_key in DOCUMENTS:
        if user_id and has_access(user_id, section_key):
            kb.button(text="📄 Открыть PDF", callback_data=f"pdf:{section_key}")
        else:
            kb.button(text="💳 Оплатить и получить PDF", callback_data=f"pay:{section_key}")
    elif section_key in TARIFFS:
        kb.button(text="💳 Оплатить / записаться", callback_data=f"pay:{section_key}")

    kb.button(text="⬅️ Назад в меню", callback_data="back_to_menu")
    kb.adjust(1)
    return kb.as_markup()

async def send_main_menu(message: Message) -> None:
    if START_PHOTO:
        try:
            photo = FSInputFile(START_PHOTO) if Path(START_PHOTO).exists() else START_PHOTO
            await message.answer_photo(photo=photo, protect_content=PROTECT_CONTENT)
        except Exception:
            await message.answer("Фото не отправилось. Проверь START_PHOTO в переменных.", protect_content=PROTECT_CONTENT)

    await message.answer(
        WELCOME_TEXT,
        reply_markup=main_keyboard(),
        protect_content=PROTECT_CONTENT,
    )


@router.message(CommandStart())
async def start(message: Message, state: FSMContext):
    await state.clear()
    save_user(message)
    await send_main_menu(message)


@router.message(Command("menu"))
async def menu(message: Message, state: FSMContext):
    await state.clear()
    save_user(message)
    await send_main_menu(message)


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer(
        WELCOME_TEXT,
        reply_markup=main_keyboard(),
        protect_content=PROTECT_CONTENT,
    )
    await callback.answer()


@router.callback_query(F.data.startswith("section:"))
async def show_section(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    key = callback.data.split(":", 1)[1]
    text = SECTION_TEXTS.get(key, "Раздел скоро будет заполнен.")

    reply_markup = tariffs_keyboard() if key == "tariffs" else section_keyboard(key, callback.from_user.id)

    await callback.message.answer(
        text,
        reply_markup=reply_markup,
        protect_content=PROTECT_CONTENT,
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pdf:"))
async def send_pdf(callback: CallbackQuery, state: FSMContext):
    key = callback.data.split(":", 1)[1]

    if not has_access(callback.from_user.id, key):
        await start_payment_flow(callback, state, key)
        return

    pdf_path = DOCUMENTS.get(key)

    if not pdf_path:
        await callback.message.answer("PDF для этого раздела пока не добавлен.")
        await callback.answer()
        return

    path = Path(pdf_path)
    if not path.exists():
        await callback.message.answer("PDF-файл не найден. Проверь, что PDF загружен рядом с main.py.")
        await callback.answer()
        return

    await callback.message.answer_document(
        document=FSInputFile(path),
        caption="📄 Доступ подтверждён. Ваш PDF-файл открыт.",
        protect_content=PROTECT_CONTENT,
    )
    await callback.answer()


async def start_payment_flow(callback: CallbackQuery, state: FSMContext, section_key: str):
    if section_key not in TARIFFS:
        await callback.message.answer("Тариф не найден.")
        await callback.answer()
        return

    await state.clear()
    await callback.message.answer(
        payment_text(section_key),
        reply_markup=payment_keyboard(section_key),
        protect_content=PROTECT_CONTENT,
    )
    await callback.answer()


@router.callback_query(F.data.startswith("pay:"))
async def start_payment(callback: CallbackQuery, state: FSMContext):
    section_key = callback.data.split(":", 1)[1]
    await start_payment_flow(callback, state, section_key)


@router.callback_query(F.data.startswith("pay_info:"))
async def show_payment_requisites(callback: CallbackQuery):
    section_key = callback.data.split(":", 1)[1]
    tariff = TARIFFS.get(section_key)

    if not tariff:
        await callback.answer("Тариф не найден", show_alert=True)
        return

    await callback.answer(
        f"Банк: {PAYMENT_BANK}\nКарта: {PAYMENT_CARD}\nСумма: {tariff['price']}",
        show_alert=True,
    )


@router.callback_query(F.data.startswith("receipt:"))
async def ask_for_payment_receipt(callback: CallbackQuery, state: FSMContext):
    section_key = callback.data.split(":", 1)[1]
    tariff = TARIFFS.get(section_key)

    if not tariff:
        await callback.answer("Тариф не найден", show_alert=True)
        return

    await state.set_state(PaymentState.waiting_for_receipt)
    await state.update_data(section_key=section_key)

    await callback.message.answer(
        "📎 Отправьте чек или скриншот перевода одним сообщением.\n\n"
        f"Тариф: <b>{html.escape(tariff['title'])}</b>\n"
        f"Сумма: <b>{html.escape(tariff['price'])}</b>\n\n"
        "После проверки Катерина нажмёт подтверждение, и бот автоматически выдаст доступ.",
        reply_markup=payment_keyboard(section_key),
        protect_content=PROTECT_CONTENT,
    )
    await callback.answer()


@router.message(PaymentState.waiting_for_receipt)
async def receive_payment_receipt(message: Message, state: FSMContext):
    save_user(message)

    data = await state.get_data()
    section_key = data.get("section_key", "")
    tariff = TARIFFS.get(section_key)

    if not tariff:
        await message.answer("Тариф не найден. Откройте меню и попробуйте ещё раз.", reply_markup=main_keyboard())
        await state.clear()
        return

    user = message.from_user
    username = f"@{user.username}" if user and user.username else "без username"
    first_name = user.first_name if user else "Пользователь"
    receipt_text = message.text or message.caption or "Чек отправлен файлом/фото без текста"

    save_payment_request(message, section_key, receipt_text)

    await message.answer(
        "Чек отправлен Катерине на проверку ✅\nПосле подтверждения бот автоматически выдаст доступ.",
        reply_markup=main_keyboard(),
        protect_content=PROTECT_CONTENT,
    )
    await state.clear()

    if ADMIN_ID:
        try:
            await message.bot.forward_message(
                chat_id=ADMIN_ID,
                from_chat_id=message.chat.id,
                message_id=message.message_id,
            )
        except Exception:
            pass

        admin_text = (
            "<b>💳 Новая оплата на проверку</b>\n\n"
            f"<b>Тариф:</b> {html.escape(tariff['title'])}\n"
            f"<b>Сумма:</b> {html.escape(tariff['price'])}\n\n"
            f"<b>От:</b> {html.escape(first_name)}\n"
            f"<b>Username:</b> {html.escape(username)}\n"
            f"<b>ID:</b> <code>{user.id if user else 0}</code>\n\n"
            f"<b>Комментарий/чек:</b>\n{html.escape(receipt_text)}"
        )

        await message.bot.send_message(
            ADMIN_ID,
            admin_text,
            reply_markup=payment_admin_keyboard(user.id if user else 0, section_key),
        )


@router.callback_query(F.data.startswith("approve:"))
async def approve_payment(callback: CallbackQuery):
    if not ADMIN_ID or not callback.from_user or callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа", show_alert=True)
        return

    parts = callback.data.split(":")
    if len(parts) != 3 or not parts[2].isdigit():
        await callback.answer("Некорректные данные", show_alert=True)
        return

    section_key = parts[1]
    user_id = int(parts[2])
    tariff = TARIFFS.get(section_key)

    if not tariff:
        await callback.answer("Тариф не найден", show_alert=True)
        return

    grant_access(user_id, section_key)

    if section_key in DOCUMENTS:
        path = Path(DOCUMENTS[section_key])
        await callback.bot.send_message(
            user_id,
            f"✅ Оплата подтверждена!\n\nДоступ открыт: <b>{html.escape(tariff['title'])}</b>",
            protect_content=PROTECT_CONTENT,
        )
        if path.exists():
            await callback.bot.send_document(
                user_id,
                FSInputFile(path),
                caption="📄 Ваш PDF-файл.",
                protect_content=PROTECT_CONTENT,
            )
    else:
        await callback.bot.send_message(
            user_id,
            "✅ Оплата подтверждена!\n\nКатерина свяжется с вами по сопровождению.",
            protect_content=PROTECT_CONTENT,
        )

    await callback.message.answer("Оплата подтверждена, доступ выдан ✅")
    await callback.answer("Готово")


@router.callback_query(F.data.startswith("decline:"))
async def decline_payment(callback: CallbackQuery):
    if not ADMIN_ID or not callback.from_user or callback.from_user.id != ADMIN_ID:
        await callback.answer("Нет доступа", show_alert=True)
        return

    parts = callback.data.split(":")
    if len(parts) != 3 or not parts[2].isdigit():
        await callback.answer("Некорректные данные", show_alert=True)
        return

    section_key = parts[1]
    user_id = int(parts[2])
    tariff = TARIFFS.get(section_key, {"title": "тариф"})

    await callback.bot.send_message(
        user_id,
        f"❌ Оплата по тарифу «{html.escape(tariff['title'])}» не подтверждена.\nПожалуйста, свяжитесь с Катериной через кнопку вопросов.",
        reply_markup=main_keyboard(),
        protect_content=PROTECT_CONTENT,
    )
    await callback.message.answer("Пользователю отправлено сообщение об отклонении ❌")
    await callback.answer("Отклонено")


@router.callback_query(F.data == "ask_question")
async def ask_question(callback: CallbackQuery, state: FSMContext):
    await state.set_state(QuestionState.waiting_for_question)
    support_line = f"\n\nТакже можно написать напрямую: @{SUPPORT_USERNAME}" if SUPPORT_USERNAME else ""
    await callback.message.answer(
        "Напиши свой вопрос одним сообщением. Я передам его Катерине 💬" + support_line,
        protect_content=PROTECT_CONTENT,
    )
    await callback.answer()


@router.message(QuestionState.waiting_for_question)
async def receive_question(message: Message, state: FSMContext):
    save_user(message)

    user = message.from_user
    question = message.text or message.caption or ""
    username = f"@{user.username}" if user and user.username else "без username"
    first_name = user.first_name if user else "Пользователь"

    conn = db()
    conn.execute(
        "INSERT INTO questions (user_id, username, question, created_at) VALUES (?, ?, ?, ?)",
        (user.id if user else 0, username, question, datetime.now().isoformat(timespec="seconds")),
    )
    conn.commit()
    conn.close()

    await message.answer(
        "Спасибо! Вопрос отправлен. Катерина ответит тебе здесь или свяжется лично 🫶🏻",
        reply_markup=main_keyboard(),
        protect_content=PROTECT_CONTENT,
    )
    await state.clear()

    if ADMIN_ID:
        admin_text = (
            "<b>❓ Новый вопрос в боте</b>\n\n"
            f"<b>От:</b> {html.escape(first_name)}\n"
            f"<b>Username:</b> {html.escape(username)}\n"
            f"<b>ID:</b> <code>{user.id if user else 0}</code>\n\n"
            f"<b>Вопрос:</b>\n{html.escape(question)}\n\n"
            f"Ответить пользователю:\n<code>/reply {user.id if user else 0} текст ответа</code>"
        )
        await message.bot.send_message(ADMIN_ID, admin_text)


@router.message(Command("reply"))
async def admin_reply(message: Message):
    if not ADMIN_ID or not message.from_user or message.from_user.id != ADMIN_ID:
        return

    parts = (message.text or "").split(maxsplit=2)
    if len(parts) < 3 or not parts[1].isdigit():
        await message.answer("Формат ответа: /reply USER_ID текст ответа")
        return

    user_id = int(parts[1])
    answer = parts[2].strip()

    try:
        await message.bot.send_message(
            user_id,
            f"<b>💬 Ответ от Катерины:</b>\n\n{html.escape(answer)}",
            protect_content=PROTECT_CONTENT,
        )
        await message.answer("Ответ отправлен ✅")
    except Exception as e:
        await message.answer(f"Не получилось отправить ответ. Ошибка: {e}")


@router.message(Command("grant"))
async def admin_grant_access(message: Message):
    if not ADMIN_ID or not message.from_user or message.from_user.id != ADMIN_ID:
        return

    parts = (message.text or "").split(maxsplit=2)
    if len(parts) < 3 or not parts[1].isdigit():
        await message.answer(
            "Формат:\n"
            "/grant USER_ID cosmetics_suppliers\n"
            "/grant USER_ID brand_suppliers_rf\n"
            "/grant USER_ID factories_europe"
        )
        return

    user_id = int(parts[1])
    section_key = parts[2].strip()

    if section_key not in TARIFFS:
        await message.answer("Такого тарифа нет.")
        return

    grant_access(user_id, section_key)

    await message.answer("Доступ выдан вручную ✅")

    if section_key in DOCUMENTS:
        path = Path(DOCUMENTS[section_key])
        if path.exists():
            await message.bot.send_document(
                user_id,
                FSInputFile(path),
                caption="✅ Доступ выдан. Ваш PDF-файл.",
                protect_content=PROTECT_CONTENT,
            )
    else:
        await message.bot.send_message(
            user_id,
            "✅ Доступ/заявка подтверждены. Катерина свяжется с вами.",
            protect_content=PROTECT_CONTENT,
        )


@router.message(Command("users"))
async def users_count(message: Message):
    if not ADMIN_ID or not message.from_user or message.from_user.id != ADMIN_ID:
        return

    conn = db()
    count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()
    await message.answer(f"Пользователей в базе: {count}")


@router.message(Command("broadcast"))
async def broadcast(message: Message):
    if not ADMIN_ID or not message.from_user or message.from_user.id != ADMIN_ID:
        return

    text = (message.text or "").replace("/broadcast", "", 1).strip()
    if not text:
        await message.answer("Формат рассылки: /broadcast текст рассылки")
        return

    conn = db()
    user_ids = [row[0] for row in conn.execute("SELECT user_id FROM users").fetchall()]
    conn.close()

    sent = 0
    failed = 0
    for user_id in user_ids:
        try:
            await message.bot.send_message(user_id, text, protect_content=PROTECT_CONTENT)
            sent += 1
            await asyncio.sleep(0.05)
        except Exception:
            failed += 1

    await message.answer(f"Рассылка завершена.\nОтправлено: {sent}\nОшибок: {failed}")


@router.message()
async def any_message(message: Message):
    save_user(message)
    await message.answer(
        "Выбери нужный раздел в меню ниже 👇",
        reply_markup=main_keyboard(),
        protect_content=PROTECT_CONTENT,
    )


async def main():
    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    db()
    print("Bot started")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
