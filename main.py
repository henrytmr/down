from pyrogram import Client
from pyrogram.types import Message
import extras
import moodleclient
import os

API_ID = 18233797
API_HASH = "6cad012cd66ba62e1b7d49f1f84742d1"
BOT_TOKEN = "7279915670:AAHOPZhjXd-KBq9bUICQj-jdqI-edi0XXYQ"

bot = Client("moodle", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)
data = {"moodle": "", "token": "", "ws": True, "upec": False}

@bot.on_message()
async def messages_handler(client: Client, message: Message):
	msg = message.text
	username = message.from_user.username
	#info = "Moodle: " + data["moodle"] + "\nToken: " + data["token"]
	info = "😏 𝐈'𝐦 𝐚𝐥𝐢𝐯𝐞 👻"
	if not username in ["yordante", "nakigeplayer"]:
		#await message.reply("Ke tu ase")
		return
	if msg.startswith("/start"):
		await message.reply("😏 𝐈'𝐦 𝐚𝐥𝐢𝐯𝐞 👻")
	elif msg.startswith("/config"):
		try:
			m = msg.split(" ")
			data["moodle"] = m[1]
			data["token"] = m[2]
			await message.reply("Moodle: " + data["moodle"] + "\nToken: " + data["token"])
			print(data)
		except Exception as ex:
			await message.reply(ex)
	elif msg.startswith("/ws"):
		if msg.split(" ")[1] == "on":
			data["ws"] = True
		elif msg.split(" ")[1] == "off":
			data["ws"] = False
		await message.reply("WebService: " + str(data["ws"]))
	elif msg.startswith("/upec"):
		if msg.split(" ")[1] == "on":
			data["upec"] = True
		elif msg.split(" ")[1] == "off":
			data["upec"] = False
		await message.reply("Upec: " + str(data["upec"]))
	elif msg.startswith("http"):
		try:
			print(data)
			#await message.reply("Procesando...")
			file = extras.download_file(msg)
			link = moodleclient.upload_token(file, data["token"], data["moodle"], data["ws"], data["upec"])
			await message.reply(link)
			os.remove(file)
		except Exception as ex:
			await message.reply(ex)

bot.run()
