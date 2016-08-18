import telebot
from local_settings import tgbot_token
from local_settings import allowed_users
from threading import Thread
from time import sleep

class TGCoffeeBot:
	def __init__(self, receiver):
		self.uid = allowed_users[0]
		self.bot = telebot.TeleBot(tgbot_token)
		self.bot.send_message(self.uid, "This is your coffee machine speaking. I am awake!")
		
		@self.bot.message_handler(func=lambda message: True)
		def msghandler(message):
			if message.from_user.id not in allowed_users:
				print message.from_user.first_name,message.from_user.last_name,message.from_user.id,"is unknown"
				return
			if message.text.lower() == 'hi' or message.text.lower() == 'hello':
				self.sender("Hi! I'm a teapot!",1)
				self.sender("I mean... HTTP 418 I'm a teapot.",1)
				self.sender("Look:",1)
				self.bot.send_photo(self.uid, open('/var/www/pot.jpg', 'rb'))
				self.sender("But by NO means that means that I cannot brew coffee.",2)
				self.sender("So, what can I do for you?",1)
			if 'tea' in message.text.lower():
				self.sender("Sorry. While I am a teapot",1)
				self.sender("While I AM a teapot, I cannot as of yet brew tea.",2)
				self.sender("Really sorry.",1)
				self.sender("Anything else?",0)
			receiver(message)

		thread = Thread(target = self.bot.polling)
		thread.start()
		
	def sender(self,msg,sleeptime):
		if sleeptime > 0:
			self.bot.send_chat_action(self.uid, 'typing')
			sleep(sleeptime)
		self.bot.send_message(self.uid, msg)
	def stop_polling(self):
		self.bot.stop_polling()