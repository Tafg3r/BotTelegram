import telebot
from telebot import types
from rentals import load_rental_items, add_renter
from datetime import datetime

#токен
TOKEN = 'your token'

# Создание бота
bot = telebot.TeleBot(TOKEN)


# Словарь для хранения товаров в корзине
cart = []


# Функция для приветствия пользователя по имени
def greet_user(message):
    user_name = message.from_user.first_name
    greeting_message = f"Привет, {user_name}! Я рад видеть тебя здесь."
    bot.send_message(message.chat.id, greeting_message)

# Обработчик команды /start и приветствие пользователя по имени
@bot.message_handler(commands=['start'])
def start(message):
    greet_user(message)
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    item1 = types.KeyboardButton('Я хочу арендовать')
    item2 = types.KeyboardButton('Я хочу сдать в аренду')
    markup.add(item1, item2)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)


# Обработчик кнопки "Я хочу арендовать"
@bot.message_handler(func=lambda message: message.text.lower() == 'я хочу арендовать')
def rent_handler(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    item1 = types.KeyboardButton('Список всех товаров')
    item2 = types.KeyboardButton('Корзина')
    item3 = types.KeyboardButton('Поиск товаров')
    item4 = types.KeyboardButton('Изменить дату аренды')
    item5 = types.KeyboardButton('Назад')
    markup.add(item1, item2, item3, item4, item5)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

# Обработчик кнопки "Изменить дату аренды"
@bot.message_handler(func=lambda message: message.text.lower() == 'изменить дату аренды')
def change_rental_date_handler(message):
    bot.send_message(message.chat.id, "Введите новую дату начала аренды в формате ДД.ММ.ГГГГ:")
    bot.register_next_step_handler(message, change_start_date)

# Функция для изменения даты начала аренды
def change_start_date(message):
    try:
        start_date = datetime.strptime(message.text, "%d.%m.%Y")
        bot.send_message(message.chat.id, "Введите новую дату окончания аренды в формате ДД.ММ.ГГГГ:")
        bot.register_next_step_handler(message, change_end_date, start_date)
    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат даты. Пожалуйста, введите дату в указанном формате.")

# Функция для изменения даты окончания аренды и вывода информации о заказе
def change_end_date(message, start_date):
    try:
        end_date = datetime.strptime(message.text, "%d.%m.%Y")
        if end_date > start_date:
            total_days = (end_date - start_date).days
            total_price = sum(item['price_per_day'] for item in cart) * total_days
            cart_text = "\n".join(f"Название: {item['name']}, Цена за день: {item['price_per_day']}" for item in cart)
            order_info = f"Товары в корзине:\n{cart_text}\nДата начала аренды: {start_date.strftime('%d.%m.%Y')}\nДата окончания аренды: {end_date.strftime('%d.%m.%Y')}\nОбщее количество дней: {total_days}\nОбщая стоимость: {total_price}"
            bot.send_message(message.chat.id, order_info)
        else:
            bot.send_message(message.chat.id, "Дата окончания аренды должна быть позже даты начала аренды.")
    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат даты. Пожалуйста, введите дату в указанном формате.")


# Обработчик кнопки "Я хочу арендовать"
@bot.message_handler(func=lambda message: message.text.lower() == 'я хочу арендовать')
def rent_handler(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    item1 = types.KeyboardButton('Список всех товаров')
    item2 = types.KeyboardButton('Корзина')
    item3 = types.KeyboardButton('Поиск товаров')
    item4 = types.KeyboardButton('Назад')
    markup.add(item1, item2, item3, item4)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

# Обработчик команды /search_items
@bot.message_handler(func=lambda message: message.text.lower() == 'поиск товаров')
def search_items_handler(message):
    bot.send_message(message.chat.id, "Введите название товара для поиска:")
    bot.register_next_step_handler(message, search_items)


def search_items(message):
    search_query = message.text.strip().lower()
    found_items = []
    rental_items = load_rental_items("rental_items.json")
    for renter in rental_items:
        for item in renter['rented_items']:
            if search_query in item['name'].lower():
                found_items.append(item)
    if found_items:
        response = "Результаты поиска:\n"
        for item in found_items:
            response += f"\nНазвание: {item['name']}\nОписание: {item['description']}\nЦена за день: {item['price_per_day']}\n\n"
        bot.send_message(message.chat.id, response)
    else:
        bot.send_message(message.chat.id, "Товары по вашему запросу не найдены.")
# Обработчик команды /list_items
@bot.message_handler(func=lambda message: message.text.lower() == 'список всех товаров')
def list_items_handler(message):
    rental_items = load_rental_items("rental_items.json")
    if rental_items:
        for renter in rental_items:
            bot.send_message(message.chat.id, f"Рентодатель: *{renter['name']}*", parse_mode='Markdown')
            items_info = ""
            for item in renter['rented_items']:
                items_info += f"\nНазвание: *{item['name']}*\nОписание: {item['description']}\nЦена за день: *{item['price_per_day']}*\n"
            bot.send_message(message.chat.id, f"Арендуемые товары:{items_info}", parse_mode='Markdown')
        # Запрашиваем у пользователя название товара для добавления в корзину
        bot.send_message(message.chat.id, "Введите название товара, который хотите добавить в корзину:")
        bot.register_next_step_handler(message, add_to_cart_from_input)
    else:
        bot.send_message(message.chat.id, "Список товаров пока пуст.")

# Функция добавления товара в корзину по введенному пользователем названию
def add_to_cart_from_input(message):
    item_name = message.text.strip().lower()  # Преобразование в нижний регистр
    rental_items = load_rental_items("rental_items.json")
    while item_name != 'готово':  # Продолжаем цикл, пока пользователь не введет "готово"
        found = False
        for renter in rental_items:
            for item in renter['rented_items']:
                if item['name'].lower() == item_name:  # Преобразование в нижний регистр
                    cart.append(item)
                    bot.send_message(message.chat.id, f"Товар '{item['name']}' добавлен в корзину.")
                    found = True
                    break
            if found:
                break
        if not found:
            bot.send_message(message.chat.id, "Такой товар не найден.")
        bot.send_message(message.chat.id, "Введите следующий товар для добавления или отправьте 'готово', чтобы закончить:")
        bot.register_next_step_handler(message, add_to_cart_from_input)  # Ждем следующего сообщения пользователя
        return  # Возвращаемся, чтобы не продолжать выполнение кода до получения следующего сообщения
    bot.send_message(message.chat.id, "Добавление товаров в корзину завершено.")


# Обработчик команды /cart
@bot.message_handler(func=lambda message: message.text.lower() == 'корзина')
def cart_handler(message):
    if cart:
        total_price = sum(item['price_per_day'] for item in cart)
        cart_text = "\n".join(f"Название: {item['name']}, Цена за день: {item['price_per_day']}" for item in cart)
        bot.send_message(message.chat.id, f"Товары в корзине:\n{cart_text}\nОбщая стоимость: {total_price}")
        markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
        item_remove = types.KeyboardButton('Удалить товар')
        item_order = types.KeyboardButton('Оформить заказ')
        item_back = types.KeyboardButton('Назад')
        markup.add(item_remove, item_order, item_back)
        bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)
    else:
        bot.send_message(message.chat.id, "Корзина пуста.")

# Обработчик кнопки "Удалить товар"
@bot.message_handler(func=lambda message: message.text.lower() == 'удалить товар')
def remove_item_handler(message):
    bot.send_message(message.chat.id, "Введите название товара, который хотите удалить из корзины:")
    bot.register_next_step_handler(message, remove_item)

# Функция удаления товара из корзины
def remove_item(message):
    item_name = message.text.strip().lower()
    removed = False
    for item in cart:
        if item['name'].lower() == item_name:
            cart.remove(item)
            removed = True
            bot.send_message(message.chat.id, f"Товар '{item['name']}' удален из корзины.")
            break
    if not removed:
        bot.send_message(message.chat.id, "Такой товар не найден в корзине.")

# Обработчик кнопки "Оформить заказ"
@bot.message_handler(func=lambda message: message.text.lower() == 'оформить заказ')
def order_handler(message):
    bot.send_message(message.chat.id, "Введите дату начала аренды в формате ДД.ММ.ГГГГ:")
    bot.register_next_step_handler(message, get_start_date)

# Функция для получения даты начала аренды
def get_start_date(message):
    try:
        start_date = datetime.strptime(message.text, "%d.%m.%Y")
        bot.send_message(message.chat.id, "Введите дату окончания аренды в формате ДД.ММ.ГГГГ:")
        bot.register_next_step_handler(message, get_end_date, start_date)
    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат даты. Пожалуйста, введите дату в указанном формате.")

# Функция для получения даты окончания аренды и вывода информации о заказе
def get_end_date(message, start_date):
    try:
        end_date = datetime.strptime(message.text, "%d.%m.%Y")
        if end_date > start_date:
            total_days = (end_date - start_date).days
            total_price = sum(item['price_per_day'] for item in cart) * total_days
            cart_text = "\n".join(f"Название: {item['name']}, Цена за день: {item['price_per_day']}" for item in cart)
            order_info = f"Товары в корзине:\n{cart_text}\nДата начала аренды: {start_date.strftime('%d.%m.%Y')}\nДата окончания аренды: {end_date.strftime('%d.%m.%Y')}\nОбщее количество дней: {total_days}\nОбщая стоимость: {total_price}"
            bot.send_message(message.chat.id, order_info)
        else:
            bot.send_message(message.chat.id, "Дата окончания аренды должна быть позже даты начала аренды.")
    except ValueError:
        bot.send_message(message.chat.id, "Неверный формат даты. Пожалуйста, введите дату в указанном формате.")



# Обработчик кнопки "Я хочу сдать в аренду"
@bot.message_handler(func=lambda message: message.text.lower() == 'я хочу сдать в аренду')
def rent_out_handler(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    item1 = types.KeyboardButton('Список товаров')
    item2 = types.KeyboardButton('Добавить арендатора')
    item3 = types.KeyboardButton('Назад')
    markup.add(item1, item2, item3)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup)

# Обработчик команды /list_items
@bot.message_handler(func=lambda message: message.text.lower() == 'список товаров')
def list_items_handler(message):
    rental_items = load_rental_items("rental_items.json")
    if rental_items:
        for renter in rental_items:
            bot.send_message(message.chat.id, f"Рентодатель: *{renter['name']}*", parse_mode='Markdown')
            items_info = ""
            for item in renter['rented_items']:
                items_info += f"\nНазвание: *{item['name']}*\nОписание: {item['description']}\nЦена за день: *{item['price_per_day']}*\n"
            bot.send_message(message.chat.id, f"Арендуемые товары:{items_info}", parse_mode='Markdown')
        # Запрашиваем у пользователя название товара для добавления в корзину
        bot.send_message(message.chat.id, "Введите название товара, который хотите добавить в корзину:")
        bot.register_next_step_handler(message, add_to_cart_from_input)
    else:
        bot.send_message(message.chat.id, "Список товаров пока пуст.")

# Обработчик команды /add_renter
@bot.message_handler(func=lambda message: message.text.lower() == 'добавить арендатора')
def add_renter_handler(message):
    markup = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    item_back = types.KeyboardButton('Назад')
    markup.add(item_back)
    bot.send_message(message.chat.id, "Введите информацию о новом арендаторе в формате:\n\n"
                                      "Имя арендатора: [Имя арендатора]\n"
                                      "Контактная информация: [Контактная информация]\n"
                                      "Название товара: [Название товара]\n"
                                      "Описание товара: [Описание товара]\n"
                                      "Цена за день: [Цена за день аренды]", reply_markup=markup)
    bot.register_next_step_handler(message, process_renter_info)

# Обработчик для получения информации о новом арендаторе
def process_renter_info(message):
    if message.text.lower() == 'назад':
        start(message)
        return
    try:
        renter_info = message.text.split('\n')
        new_renter = {
            "name": renter_info[0].split(':')[1].strip(),
            "contact_info": renter_info[1].split(':')[1].strip(),
            "rented_items": [{
                "name": renter_info[2].split(':')[1].strip(),
                "description": renter_info[3].split(':')[1].strip(),
                "price_per_day": float(renter_info[4].split(':')[1].strip())
            }]
        }
        add_renter(new_renter, "rental_items.json")
        bot.send_message(message.chat.id, "Новый арендатор успешно добавлен.")
    except (IndexError, ValueError):
        bot.send_message(message.chat.id,
                         "Неверный формат ввода. Попробуйте снова или нажмите 'Назад' для возвращения к основному меню.")

# Обработчик кнопки "Назад"
@bot.message_handler(func=lambda message: message.text.lower() == 'назад')
def back_handler(message):
    start(message)





# Запуск бота
bot.polling(none_stop=True, interval=0)




