import sqlite3

class TDBHelper:

	def __init__(self, dbname="telegram_njuskalo.sqlite"):
		self.dbname = dbname
		self.conn = sqlite3.connect(dbname)

	def setup(self):

		sql_users = """ CREATE TABLE IF NOT EXISTS users (
										chat_id integer PRIMARY KEY,
										status text
									); """

		sql_subs = """ CREATE TABLE IF NOT EXISTS sub_ads (
								chat_id integer,
								sub_url text,

								PRIMARY KEY (chat_id, sub_url),
								FOREIGN KEY (chat_id) REFERENCES sql_users (chat_id) 

							); """

		sql_seen_ads = """ CREATE TABLE IF NOT EXISTS seen_ads (
								chat_id integer,
								sub_url text,
								ad_url text,
								PRIMARY KEY (chat_id, sub_url, ad_url),
								FOREIGN KEY (chat_id) REFERENCES sql_users (chat_id) 
							); """

		sql_filters = """ CREATE TABLE IF NOT EXISTS filters (
								chat_id integer,
								sub_url text,
								filter text,
								PRIMARY KEY (chat_id, sub_url, filter),
								FOREIGN KEY (chat_id) REFERENCES sql_users (chat_id) 
							); """

		#itemidx = "CREATE INDEX IF NOT EXISTS itemIndex ON items (description ASC)" 
		#ownidx = "CREATE INDEX IF NOT EXISTS ownIndex ON items (owner ASC)"
		self.conn.execute(sql_users)
		self.conn.execute(sql_subs)
		self.conn.execute(sql_seen_ads)
		self.conn.execute(sql_filters)
		self.conn.commit()

	def add_user(self, chat_id, status):
		stmt = "INSERT INTO users (chat_id, status) VALUES (?, ?)"
		args = (chat_id, status)
		self.conn.execute(stmt, args)
		self.conn.commit()

	def check_user_in_db(self, chat_id):
		stmt = "SELECT 1 FROM users WHERE chat_id = ?;"
		args = (chat_id,)
		print(len([x for x in self.conn.execute(stmt, args)]) == 1)
		return len([x for x in self.conn.execute(stmt, args)]) == 1

	def update_user_status(self, chat_id, new_status):
		stmt = '''UPDATE users
				  SET status = ?
				  WHERE chat_id = ?'''
		args = (new_status, chat_id)
		self.conn.execute(stmt, args)
		self.conn.commit()

	def add_sub(self, chat_id, sub_url):
		stmt = "INSERT INTO sub_ads (chat_id, sub_url) VALUES (?, ?)"
		args = (chat_id, sub_url)
		self.conn.execute(stmt, args)
		self.conn.commit()

	def add_seen_ad(self, chat_id, sub_url, ad_url):
		stmt = "INSERT INTO seen_ads (chat_id, sub_url, ad_url) VALUES (?, ?, ?)"
		args = (chat_id, sub_url, ad_url)
		self.conn.execute(stmt, args)
		self.conn.commit()

	def add_filter(self, chat_id, sub_url, filter):
		stmt = "INSERT INTO filters (chat_id, sub_url, filter) VALUES (?, ?, ?)"
		args = (chat_id, sub_url, filter)
		self.conn.execute(stmt, args)
		self.conn.commit()


	def delete_user(self, chat_id):
		stmt = "DELETE FROM users WHERE chat_id = (?) "
		args = (chat_id )
		self.conn.execute(stmt, args)
		self.conn.commit()

	def delete_subscription(self, chat_id, sub_url):
		stmt = "DELETE FROM sub_ads WHERE chat_id = (?) AND sub_url = (?)"
		args = (chat_id, sub_url )
		#todo one kaskade il kaj vec ili manual
		#pobrisi onda i sve seen adsove!
		self.conn.execute(stmt, args)
		self.conn.commit()

	def delete_seen_ad(self, chat_id, sub_url, ad_url):
		stmt = "DELETE FROM seen_ads WHERE chat_id = (?) AND sub_url = (?) AND ad_url = (?)"
		args = (chat_id, sub_url, ad_url )
		self.conn.execute(stmt, args)
		self.conn.commit()

	def delete_filter(self, chat_id, sub_url, filter):
		stmt = "DELETE FROM filters WHERE chat_id = (?) AND sub_url = (?) AND filter = (?)"
		args = (chat_id, sub_url, filter)
		self.conn.execute(stmt, args)
		self.conn.commit()

	def get_all_chats(self):
		stmt = "SELECT chat_id FROM users"
		return [x[0] for x in self.conn.execute(stmt)]

	def get_user_status(self, chat_id):
		stmt = "SELECT status FROM users WHERE chat_id = ?"
		args = (chat_id,)
		tmp = [x[0] for x in self.conn.execute(stmt, args)]
		return tmp[0]

	def get_subs_from_user(self, chat_id):
		stmt = "SELECT sub_url FROM sub_ads WHERE chat_id = (?)"
		args = (chat_id, )
		return [x[0] for x in self.conn.execute(stmt, args)]

	def get_seen_ads(self, chat_id, sub_url):
		stmt = "SELECT ad_url FROM seen_ads WHERE chat_id = (?) AND sub_url = (?)"
		args = (chat_id, sub_url)
		return [x[0] for x in self.conn.execute(stmt, args)]

	def get_filters(self, chat_id, sub_url):
		stmt = "SELECT filter FROM filters WHERE chat_id = (?) AND sub_url = (?)"
		args = (chat_id, sub_url)
		return [x[0] for x in self.conn.execute(stmt, args)]

	def delete_all(self):
		#"DELETE FROM users; DELETE FROM sub_ads; DELETE FROM seen_ads; DELETE FROM filters"
		stmt = "DELETE FROM users; DELETE FROM sub_ads; DELETE FROM seen_ads; DELETE FROM filters"
		self.conn.executescript(stmt)
		self.conn.commit()


def adding_test(db):
	
	db.add_user(55)
	db.add_user(38)
	db.add_sub(55, "https:www.google//dadasd//")
	db.add_sub(55, "https:www.gofsfefogle//dadasd//")
	db.add_seen_ad(55, "https:www.google//dadasd//", "prva")
	db.add_seen_ad(55, "https:www.google//dadasd//", "druga")
	db.add_seen_ad(55, "https:www.google//dadasd//", "treca")
	db.add_filter(55, "https:www.google//dadasd//", "jos ne znam kako ovo urediti")


def fetch_test(db):

	print(db.get_all_chats())
	print(db.get_subs_from_user(55))
	print(db.get_subs_from_user(38))
	print(db.get_seen_ads(55, "https:www.google//dadasd//"))
	print(db.get_filters(55, "https:www.google//dadasd//"))


if __name__ == "__main__":

	ab = TDBHelper()
	ab.setup()
#	adding_test(ab)
#	fetch_test(ab)
#	ab.delete_all()
	ab.delete_seen_ad(450673401, "https://www.njuskalo.hr/?ctl=search_ads&keywords=paperwhite&price%5Bmin%5D=500", "https://www.njuskalo.hr/informatika-sve-ostalo/kindle-paperwhite-2018-waterproof-najnovije-neotvoren-e-book-e-reader-oglas-27220076")