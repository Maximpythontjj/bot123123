import sqlite3
import random
import os
import telebot
from telebot import types
import time


token = '6039673649:AAEm3zU2042SlCCGK5ZRSU1nwsSrPkobQT4'
bot = telebot.TeleBot(token)
CHARS = 'QWERTYUIOPLKJHGFDSAZXCVBNM1234567890qwertyuioplkjhgfdsazxcvbnm'


def sponsors_buttons():
	kb = types.InlineKeyboardMarkup()
	kb.add(types.InlineKeyboardButton(text = '🔗  Канал', url = 'https://t.me/sharkprogect'))
	kb.add(types.InlineKeyboardButton(text = '🔗  Спонсор 1', url = 'https://t.me/sr_garfield'))
	kb.add(types.InlineKeyboardButton(text = '✅  Подписался', callback_data = 'subscribed'))
	return kb


def info_buttons():
	kb = types.InlineKeyboardMarkup()
	kb.add(types.InlineKeyboardButton(text = '👤  Связь с админом', url = 'https://t.me/crypton_g24'))
	kb.add(types.InlineKeyboardButton(text = '🤖  Хочу такого бота', url = 'https://t.me/sr_garfield_27'))
	return kb

def refprogram_buttons(telegram_id):
	kb = types.InlineKeyboardMarkup()
	kb.add(types.InlineKeyboardButton(text = '🔗  Поделиться ссылкой', switch_inline_query = f'{get_user_data(telegram_id)["refcode"]}'))
	return kb


def inline_mode_buttons(req):
	kb = types.InlineKeyboardMarkup()
	kb.add(types.InlineKeyboardButton(text = 'Получить TRX', url = f'https://t.me/TronTrxBot?start={req}'))
	return kb


def get_total_users():
	con = sqlite3.connect("data.db")
	cur = con.cursor()
	query = "SELECT COUNT(telegram_id) FROM users WHERE status = 1"
	cur.execute(query)
	return cur.fetchone()[0]



def profile_buttons():
	kb = types.InlineKeyboardMarkup()
	kb.add(types.InlineKeyboardButton(text = '📤  Вывести', callback_data = 'withdraw'))
	return kb


def set_captcha(telegram_id, code):
	con = sqlite3.connect("data.db")
	cur = con.cursor()
	query = "UPDATE users SET captcha_code = ? WHERE telegram_id = ?"
	cur.execute(query, (code, telegram_id))
	con.commit()


def set_category(telegram_id, category):
	con = sqlite3.connect("data.db")
	cur = con.cursor()
	query = "UPDATE users SET category = ? WHERE telegram_id = ?"
	cur.execute(query, (category, telegram_id))
	con.commit()


def update_withdrawn(telegram_id, amount):
	con = sqlite3.connect("data.db")
	cur = con.cursor()
	query = "UPDATE users SET withdrawn = ? WHERE telegram_id = ?"
	cur.execute(query, (get_user_data(telegram_id)["withdrawn"] + amount * 10000, telegram_id))
	con.commit()	


def get_random_sample():
	png_files = [f for f in os.listdir('samples') if f.endswith('.png')]
	if not png_files:
		return None
	return os.path.join('samples', random.choice(png_files))


def get_user_data(telegram_id):
	con = sqlite3.connect("data.db")
	cur = con.cursor()
	query = "SELECT * FROM users WHERE telegram_id=?"
	cur.execute(query, (telegram_id,))
	data = cur.fetchone()
	return {
		'telegram_id' : data[0],
		'useraname' : data[1],
		'firstname' : data[2],
		'lastname' : data[3],
		'balance' : data[4],
		'refcode' : data[5],
		'referrer' : data[6],
		'status' : data[7],
		'category' : data[8],
		'captcha_code': data[9],
		'regtime': data[10],
		'withdrawn' : data[11]
	}




def get_referrer_by_refcode(refcode):
	con = sqlite3.connect("data.db")
	cur = con.cursor()
	query = "SELECT telegram_id FROM users WHERE refcode=?"
	cur.execute(query, (refcode,))
	data = cur.fetchone()
	if data == None:
		return None
	return data[0]

def is_exist(telegram_id):
	con = sqlite3.connect("data.db")
	cur = con.cursor()
	query = "SELECT telegram_id FROM users WHERE telegram_id=?"
	cur.execute(query, (telegram_id,))
	if cur.fetchone() == None:
		return False
	return True


def registration(message, is_ref_link):
	refcode = ''
	for i in range(10):
		refcode += random.choice(CHARS)

	referrer = get_referrer_by_refcode(is_ref_link) if is_ref_link else None

	con = sqlite3.connect("data.db")
	cur = con.cursor()

	query = "INSERT INTO users (telegram_id, username, firstname, lastname, balance, refcode, referrer, status, category, captcha_code, regtime) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"
	cur.execute(query, (message.chat.id, message.from_user.username, message.from_user.first_name, message.from_user.last_name, 0, refcode, referrer, 0, 'captcha', None, None))
	con.commit()

	return refcode


def sponsors(message):
	text = '<b>⏳  Регистрация почти завершена!</b>\n\nДля завершения регистрации Вам необходимо подписаться на мой канал, а также на спонсоров:'
	bot.send_message(message.chat.id, text, parse_mode = 'html', reply_markup = sponsors_buttons())
	set_category(message.chat.id, 'sponsors')



def captcha(message):
	random_sample_path = get_random_sample()
	code = ((random_sample_path.split('\\'))[1].split('.'))[0]
	with open(random_sample_path, 'rb') as f:
		bot.send_photo(message.chat.id, f, caption = '<b>✍️  Введите капчу:</b>', parse_mode = 'html')

	set_captcha(message.chat.id, code)


def set_regtime(telegram_id):
	con = sqlite3.connect("data.db")
	cur = con.cursor()
	query = "UPDATE users SET regtime = ? WHERE telegram_id = ?"
	cur.execute(query, (int(time.time()), telegram_id))
	con.commit()


def check_subscription(message):
	telegram_id = message.chat.id
	# -1001734204714
	result = bot.get_chat_member(-1001537310587, telegram_id).status in ['member', 'administrator', 'creator'] and bot.get_chat_member(-1001734204714, telegram_id).status in ['member', 'administrator', 'creator']
	print(result)
	return result

def activate_user(telegram_id):
	con = sqlite3.connect("data.db")
	cur = con.cursor()
	query = "UPDATE users SET status = ? WHERE telegram_id = ?"
	cur.execute(query, (1, telegram_id))
	con.commit()
	set_regtime(telegram_id)

def disactivate_withdraw(withdrawn_number):
	con = sqlite3.connect("data.db")
	cur = con.cursor()
	query = "UPDATE withdrawns SET status = ? WHERE withdrawn_number = ?"
	cur.execute(query, (0, withdrawn_number))
	con.commit()


def get_referrals_by_telegram_id(telegram_id):
	con = sqlite3.connect("data.db")
	cur = con.cursor()
	query = "SELECT telegram_id FROM users WHERE referrer=? AND status = 1"
	cur.execute(query, (telegram_id,))
	data = cur.fetchall()
	list = []
	for i in range(len(data)):
		list.append(data[i][0])

	return list


def get_all_referals_amount_and_sum(telegram_id):
	first_level, second_level, third_level, forth_level, fifth_level = get_referrals(telegram_id)
	fl = len(first_level)
	sl = len(second_level)
	tl = len(third_level)
	frl = len(forth_level)
	fil = len(fifth_level)
	amount = fl + sl + tl + frl + fil
	sum = fl*1000 + sl*700 + tl*300 + frl*200 + fil*100
	return [amount, sum] 



def get_referrals(telegram_id, level = None):
	first_level = []
	second_level = []
	third_level = []
	forth_level = []
	fifth_level = []

	first_level += get_referrals_by_telegram_id(telegram_id)

	for i in range(len(first_level)):
		second_level += get_referrals_by_telegram_id(first_level[i])

	for i in range(len(second_level)):
		third_level += get_referrals_by_telegram_id(second_level[i])

	for i in range(len(third_level)):
		forth_level += get_referrals_by_telegram_id(third_level[i])

	for i in range(len(forth_level)):
		fifth_level += get_referrals_by_telegram_id(forth_level[i])

	if level == None:
		return first_level, second_level, third_level, forth_level, fifth_level 

	if level == 1:
		return first_level
	if level == 2:
		return second_level
	if level == 3:
		return third_level
	if level == 4:
		return forth_level
	if level == 5:
		return fifth_level


def tf_hours_users():
	con = sqlite3.connect("data.db")
	cur = con.cursor()
	query = "SELECT COUNT(telegram_id) FROM users WHERE regtime > ? and status = 1"
	cur.execute(query, (int(time.time() - 86400),))
	return cur.fetchone()[0]


def total_withdrawn():
	con = sqlite3.connect("data.db")
	cur = con.cursor()
	query = "SELECT SUM(withdrawn) FROM users"
	cur.execute(query)
	return cur.fetchone()[0]

def profile(message):
	data = get_user_data(message.chat.id)
	days = ((int(time.time()) - data['regtime']) // 86400) + 1
	referrals = get_referrals(message.chat.id)
	all_referals_amount_and_sum = get_all_referals_amount_and_sum(message.chat.id)
	text = f'🆔  <b>Профиль</b>  <code>{data["firstname"]} {data["lastname"] if data["lastname"] else ""}</code>\n\n<b>💰  Баланс: </b>{((all_referals_amount_and_sum[1]) - data["withdrawn"] + data["balance"]) * 0.0001} TRX\n<b>👨‍👩‍👧‍👦  Рефералов на всех уровнях: </b> {all_referals_amount_and_sum[0]}\n<b>💵  Заработано с рефералки: </b>{round((all_referals_amount_and_sum[1]) * 0.0001, 4)} TRX\n<b>🎁  Бонусы: </b>{round((get_user_data(message.chat.id)["balance"]) * 0.0001, 4)} TRX\n<b>📤  Выведено: </b>{(data["withdrawn"]) * 0.0001} TRX\n\n<b>⏳  Вы с нами: </b><code>{days} {"день" if days == 1 else "дня" if days in [2, 3, 4] else "дней"}</code>'
	bot.send_message(message.chat.id, text, parse_mode = 'html', reply_markup = profile_buttons())
	set_category(message.chat.id, 'profile')


def refprogram(message):
	first_level, second_level, third_level, forth_level, fifth_level = get_referrals(message.chat.id)
	reflink = f'http://t.me/TronTrxBot?start={get_user_data(message.chat.id)["refcode"]}'
	text = f'<b>👨‍👩‍👧‍👦  Реферальная программа</b>\n\n<code><b>1️⃣ уровень: </b>{len(first_level)} | {round((len(first_level) * 1000) * 0.0001, 4)} TRX\n<b>2️⃣ уровень: </b>{len(second_level)} | {round((len(second_level) * 700) * 0.0001, 4)} TRX\n<b>3️⃣ уровень: </b>{len(third_level)} | {round((len(third_level) * 300) * 0.0001, 4)} TRX\n<b>4️⃣ уровень: </b>{len(forth_level)} | {round((len(forth_level) * 200) * 0.0001, 4)} TRX\n<b>5️⃣ уровень: </b>{len(fifth_level)} | {round((len(fifth_level) * 100) * 0.0001, 4)} TRX</code>\n\nПриглашайте пользователей по своей реферальной ссылке и получайте за реферала:\n\n<code>0.1 TRX за 1 уровень\n0.07 TRX за 2 уровень\n0.03 TRX за 3 уровень\n0.02 TRX за 4 уровень\n0.01 TRX за 5 уровень</code>\n\n<b>Ваша реферальная ссылка: </b>\n{reflink}'
	bot.send_message(message.chat.id, text, parse_mode = 'html', reply_markup = refprogram_buttons(message.chat.id))
	set_category(message.chat.id, 'refprogram')


def info(message):
	text = f'<b>ℹ️  Информация о проекте</b>\n\n<b>👨‍👩‍👧‍👦  Всего пользователей:</b> {get_total_users()}\n<b>🆕  Новых за 24 часа: </b>{tf_hours_users()}\n<b>📤  Всего выплачено: </b><code>{total_withdrawn() * 0.0001} TRX</code>'
	bot.send_message(message.chat.id, text, parse_mode = 'html', reply_markup = info_buttons())
	set_category(message.chat.id, 'info')


def withdrawn(message):
	withdrawn = get_user_data(message.chat.id)['withdrawn']
	all_referals_amount_and_sum = get_all_referals_amount_and_sum(message.chat.id)[1]
	available = all_referals_amount_and_sum + get_user_data(message.chat.id)['balance'] - withdrawn

	text = f'<b>📤  Вывод</b>\n\n<b>Доступно для вывода: </b><code>{(available) * 0.0001} TRX</code>\nВведите сумму вывода:'
	bot.send_message(message.chat.id, text, parse_mode = 'html')
	set_category(message.chat.id, 'withdrawn')


def make_withdrawn(message, summ):
	withdrawn_number = ''
	for i in range(10):
		withdrawn_number += random.choice(CHARS) 

	update_withdrawn(message.chat.id, summ)
	withdrawn_making(message, summ, withdrawn_number)
	text = f'<b>📤  Выплата сформирована!</b>\n\nВаша выплата успешно сформирована и передана администрации, и будет рассмотрена в срок от 1 часа до 48 часов.\n\n<b>Номер выплаты: </b>{withdrawn_number}\n<b>Сумма: </b><code>{summ} TRX</code>\n\n<b>Внимание! Убедительная просьба сохранить данное сообщение!</b>'
	bot.send_message(message.chat.id, text, parse_mode = 'html')
	bot.send_message(5658727360, f'<b>📤  Выплата</b>\n\n<b>Telegram ID: </b>{message.chat.id}\n<b>Имя / Фамилия: </b>{message.from_user.first_name} {message.from_user.last_name if message.from_user.last_name != None else ""}\n<b>Юзернейм: </b>{message.from_user.username}\n<b>Сумма: </b><code>{summ}</code>\n<b>Номер выплаты: </b>{withdrawn_number}\n\n<code>{message.chat.id}_{summ}_{withdrawn_number}_</code>', parse_mode = 'html')
	set_category(message.chat.id, 'profile')


def withdrawn_making(message, summ, number):
	con = sqlite3.connect("data.db")
	cur = con.cursor()

	query = "INSERT INTO withdrawns (telegram_id, username, summ, withdrawn_time, withdrawn_number) VALUES (?, ?, ?, ?, ?)"
	cur.execute(query, (message.chat.id, message.from_user.username, summ, int(time.time()), number))
	con.commit()




