import json 
import requests
import time
import urllib
import re
from db_telegram import TDBHelper



db = TDBHelper()

f = open('config.txt', 'r')
x = f.read().splitlines()
f.close()

token = x[1]
MASTER_CHAT_ID = x[3]

URL = "https://api.telegram.org/bot{}/".format(token)
headers = {
	'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
	}

regex_oglas = r"<li class=\"EntityList-item EntityList-item--(Regular|VauVau) (.*\s*)data-href=\"(.*?)\"\s*.*\s*.*\s*.*\">(.*)<\/a>"
regex_next_page = r"Pagination-item--next"


def get_url(url):
	response = requests.get(url, headers = headers)
	response = response.content.decode("utf8")
	return response

def url_to_json(url):
	response = get_url(url) 
	js = json.loads(response)
	return js

def get_updates(offset = None, timeout = 100):

	url_updates = URL + "getUpdates?timeout={}".format(timeout)
	if offset:
		url_updates += "&offset={}".format(offset)
	js = url_to_json(url_updates)
	return js

def get_last_update_id(updates):

	return int(updates["result"][-1]["update_id"])

def send_msg(msg, chat_id, reply_markup=None):
	msg = urllib.parse.quote_plus(msg)
	url = URL + "sendMessage?text={}&chat_id={}".format(msg, chat_id)
	if reply_markup:
		url += "&reply_markup={}".format(reply_markup)
	
	return get_url(url)

def build_keyboard(items):
	keyboard = [[urllib.parse.quote(item)] for item in items]
	reply_markup = {"keyboard": keyboard, "one_time_keyboard":True, "resize_keyboard":True}
	return json.dumps(reply_markup)



def check_valid_url(url):

	if not "njuskalo.hr" in url:
		print("ne pronalazi njuskalo")
		return False
	try:
		print(url)
		response = requests.get(url, headers=headers)
		bien = response.status_code < 400
		print("dobar response code")
	except:
		bien = False
		print("request faila")

	return bien

def check_valid_url2(url):
	url += "?"
	if not "njuskalo.hr" in url:
		print("ne pronalazi njuskalo")
		return False
	try:
		print(url)
		response = requests.get(url, headers=headers)
		bien = response.status_code < 400
		print("dobar response code")
	except:
		bien = False
		print("request faila")

	return bien	

def period_passed(minutes, oldepoch):
	#print( "proslo je ", time.time() - oldepoch )

	return time.time() - oldepoch >= 60*minutes

	#TODO
#save feature as a reply
#bugs, improval  command



def handle_updates(updates):

	for update in updates["result"]:

		try:
			text = update["message"]["text"]
			chat = update["message"]["chat"]["id"]

			if text == "/start":

				send_msg("OLA KOMO ESTA' JEL TI SE NJUSKA NESTA??", chat )
				if not db.check_user_in_db(chat):
					db.add_user(chat, "NEW")

			elif text.startswith("/sub"):
				#_, sub_url = text.split(" ", 1)
				#if check_valid_url(sub_url):
				#	db.add_sub(chat, sub_url)
				#	send_msg(  "You are now subscribed to the given url!", chat)
				#else:
				send_msg("Send me a link you wish to subscribe to!", chat)
				db.update_user_status(chat, "sub")


			elif text.startswith("/unsub"):

				active_subs = db.get_subs_from_user(chat)
				if len(active_subs) == 0:
					send_msg("You dont have any active subscriptions!", chat)
					continue

				kb = build_keyboard(["all"] + active_subs)

				user_exists = db.check_user_in_db(chat)
				if user_exists: 
					db.update_user_status(chat, "unsub")

				else:
					db.add_user(chat, "unsub")
					#TODO user bi trebao vec postojati
					send_msg("nema te u userima", chat)

				#ovo ne radi, ne vrati kb koji treba
				rsp = send_msg("Select url you want to unsubscribe from: ", chat, reply_markup=kb )


			elif text.startswith("/filter"):
				send_msg("Additional filters not supported yet, sorry :(", chat)

			elif text.startswith("/active"):
				active_subs = db.get_subs_from_user(chat)
				if len(active_subs)==0:
					send_msg("You don't have any active subscriptions", chat)
				else:
					out = "\n".join(active_subs)
					send_msg(out, chat)


			elif text.startswith("/"):
				send_msg('Invalid command or use of, check valid commands by typing "/"', chat)

			else:

				status = db.get_user_status(chat)

				if status == "unsub":

					if text == "all":
						subbovi = db.get_subs_from_user(chat)
						for sub in subbovi:
							db.delete_subscription(chat, sub)
					else:
						db.delete_subscription(chat, text)
						send_msg("You are unsubscribed from:\n"+text,chat)
					
					db.update_user_status(chat, "nada")

				elif status == "sub":

					if not text.startswith("http"):
						text = "https://"+text
					if check_valid_url(text):
						db.add_sub(chat, text)
						send_msg("You are now subscribed to the given njuskalo search!:\n"+text, chat)
					else:
						send_msg("Invalid link, please start again using /sub command", chat)
					db.update_user_status(chat, "nada")

				else:
					send_msg("I'm sorry, I'm not sure what to do with: "+text, chat)

		except KeyError:
			pass


def get_additional_filters(chat):
	dicto = {}
	dicto["words"] = ["smart","twingo","citigo","up!"]
	return dicto

def fitler(naslov, filter):

	naslov = naslov.lower()
	word_filteri = filter["words"]
	for word in word_filteri:
		if word in naslov:
			#print(naslov)
			return True
	return False



def scrape_sub(url):

	naslov_group = 4
	url_group = 3

	current_page = 1
	oglasi = set()

	while current_page>0:

		url_fix = url + "&page=" + str(current_page)
		response = requests.get(url_fix, headers=headers)
		html = response.text

		if response.status_code != 200:
			#handlaj error
			#TODO
			pass				

		else:

			matches = re.finditer(regex_oglas, html, re.MULTILINE)

			for match_num, match in enumerate(matches, start=1):

				naslov_oglasa = match.group(naslov_group)				
				ad = "https://www.njuskalo.hr"+match.group(url_group)
				oglasi.add(ad)

			more_pages = re.search(regex_next_page, html)

			if more_pages:
				current_page += 1

			else:
				current_page = -1

	return oglasi





def process_results(user, sub, results):
	
	#ucitaj viđene oglase
	seen_ads = db.get_seen_ads(user, sub)
	#pronadi koji su novi
	new_ads = set(results) - set(seen_ads)

	
	for new_ad in new_ads:
		#posalji useru nove oglase
		send_msg(new_ad, user)
		#dodaj nove oglase u videne oglase
		db.add_seen_ad(user, sub, new_ad)
	


def scrape_data():
	
	users = db.get_all_chats()
	for user in users:

		subs = db.get_subs_from_user(user)
		for sub in subs:

			results = scrape_sub(sub)
			process_results(user, sub, results)



def main():

	old_epoch = time.time()

	db.setup()
	last_id = None
	while True:
		updates = get_updates(offset = last_id)
		#print("gettin updates")
		if len(updates["result"]) > 0:
			last_id = get_last_update_id(updates) + 1
			handle_updates(updates)

		if period_passed(15, old_epoch):
			#ovo idealno odvojiti i pokrenuti u zasebnoj dretvi/procesu
			scrape_data()
			old_epoch = time.time()


if __name__ == '__main__':

    main()

