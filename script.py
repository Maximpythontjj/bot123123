import telebot
from telebot import types
import sqlite3
from db import *




@bot.message_handler(commands = ['start'])
def start(message):

	# Проверка наличия пользователя
	ie = is_exist(message.chat.id)
	irl = True if len(message.text.split(' ')) == 2 else False

	if ie == False:
		# bot.send_message(message.chat.id, message.text)
		registration(message, message.text.split(' ')[1] if irl else None)
		captcha(message)

	else:
		category = get_user_data(message.chat.id)['category']
		if category == 'captcha':
			captcha(message)

		elif category == 'sponsors':
			sponsors(message)


@bot.message_handler(commands = ['profile'])
def profile_command(message):
	if is_exist(message.chat.id) == True:
		profile(message)


@bot.message_handler(commands = ['refsystem'])
def refprogram_command(message):
	if is_exist(message.chat.id) == True:
		refprogram(message)


@bot.message_handler(commands = ['info'])
def info_command(message):
	if is_exist(message.chat.id) == True:
		info(message)


@bot.message_handler(content_types = ['text'])
def text(message):
	if is_exist(message.chat.id) == True:
		category = get_user_data(message.chat.id)['category']
		if category == 'captcha':
			if message.text == get_user_data(message.chat.id)['captcha_code']:
				sponsors(message)
			else:
				bot.send_message(message.chat.id, 'Неверно')

		elif category == 'withdrawn':
			summ = message.text
			try:
				summ = float(summ)
			except:
				bot.send_message(message.chat.id, '<b>❌  Неправильный ввод!</b>', parse_mode = 'html')
				return None

			if summ < 4:
				bot.send_message(message.chat.id, '<b>❌  Минимальная сумма вывода - 4 TRX!</b>', parse_mode = 'html')
				return None

			available = (get_all_referals_amount_and_sum(message.chat.id)[1] + get_user_data(message.chat.id)['balance'] - get_user_data(message.chat.id)['withdrawn']) * 0.0001
			if summ > available:
				bot.send_message(message.chat.id, f'<b>❌  Недостаточно баланса для вывода {summ} TRX!</b>\nДоступный баланс для вывода: <code>{available} TRX</code>', parse_mode = 'html')
				return None

			number = make_withdrawn(message, summ)

		elif message.chat.id == 5658727360:
			telegram_id = message.text.split('_')[0]
			summ = message.text.split('_')[1]
			withdrawn_number = message.text.split('_')[2]
			link = message.text.split('_')[3]

			bot.send_message(int(telegram_id), f'<b>📤  Выплата</b>\n\nВаша заявка на вывод #{withdrawn_number} одобрена!\n\n<b>Сумма: </b><code>{summ} TRX</code>\n<b>Ссылка: </b>{link}', parse_mode = 'html')
			disactivate_withdraw(withdrawn_number)




@bot.callback_query_handler(func=lambda call: True)
def call(call):
	if is_exist(call.message.chat.id) == True:
		category = get_user_data(call.message.chat.id)['category']
		data = call.data
		if data == 'subscribed':
			if category == 'sponsors':
				result = check_subscription(call.message)
				if result == False:
					bot.answer_callback_query(callback_query_id = call.id, text = 'Вы не подписаны на все ресурсы!', show_alert = True)
				else:
					bot.send_message(call.message.chat.id, '✅  <b>Регистрация прошла успешно!</b>', parse_mode = 'html')
					activate_user(call.message.chat.id)
					profile(call.message)

		if data == 'withdraw':
			if category == 'profile':
				balance, withwrawn = get_all_referals_amount_and_sum(call.message.chat.id)[1] + get_user_data(call.message.chat.id)['balance'], get_user_data(call.message.chat.id)['withdrawn']
				if balance - withwrawn < 40000:
					bot.answer_callback_query(callback_query_id = call.id, text = 'Минимальная сумма вывода: 4 TRX', show_alert = True)

				else:
					withdrawn(call.message)


@bot.inline_handler(lambda query: len(query.query) >= 0)
def query_text(query):
	telegram_id = query.from_user.id
	if is_exist(telegram_id) not in [None, False]:
		results = []
		request = query.query
		if get_referrer_by_refcode(request) != None:
			content = content = f'<b>Тут ты можешь приглашать пользователей и зарабатывать TRX!\n\n5️⃣ - уровневая реферальная система!</b>\n\nРегистрируйся и зарабатывай TRX уже сейчас!'
			results.append(types.InlineQueryResultArticle(id = random.randint(10000, 999999), title = 'Реферальное приглашение', description = 'Нажмите, чтобы поделиться приглашением', input_message_content = types.InputTextMessageContent(message_text = content, parse_mode='html'), reply_markup = inline_mode_buttons(request)))

	try:
		if len(results) != 0:
			bot.answer_inline_query(inline_query_id = query.id, results = results,  cache_time = 0)
	except:
		pass

# bot.polling(none_stop = True)


while True:
	try:
		bot.polling(none_stop = True)
	except:
		pass


