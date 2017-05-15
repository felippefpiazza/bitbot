import configparser
#import pymysql
import mysql.connector as mysql

class Handler(object):
	def __init__(self):
		config = configparser.ConfigParser()
		config.read("config/database.config")
		self.user = config["main"]["username"]
		self.passwd = config["main"]["password"]
		self.db = config["main"]["db"]
		self.host = config["main"]["host"]
		
	def connect(self):
		#self.conn = pymysql.connect(
		self.conn = mysql.connect(
			host=self.host,
			user=self.user,
			passwd=self.passwd,
			db=self.db,
			autocommit=True)
		self.cursor = self.conn.cursor(dictionary=True)

	def execute(self,query):
		self.cursor.execute(query)
		return self.cursor

	def print_response(self):
		#NOT READY YET!!!!
		for row in self.cursor.fetchall():
			print(row)
		#print("ha")

	def close_connection(self):
		self.conn.close()

	def insertIntoTable(self, table, params, timestamps=False):
		if timestamps:
			params.update({"created_at" : {"quote" : False, "value" : "NOW()"},
					"updated_at" : {"quote" : False, "value" : "NOW()"}})

		#print(params)
		query_cols = []
		query_values = []

		for key in params:
			query_cols.append(key)
			quotes = "\""
			value = params[key]
			if isinstance(value, dict):
				if not params[key]["quote"]:
					quotes = ""
				value = params[key]["value"]
			query_values.append("{}{}{}".format(quotes,value,quotes))

		query = "INSERT INTO {} ({}) values ({})".format(table , ",".join(query_cols) , ",".join(query_values))
		#print(query)
		self.execute(query)
		return self.cursor.lastrowid

	def updateRow(self, table, update_params, where_params, timestamps=False):
		if timestamps:
			update_params.update({"updated_at" : {"quote" : False, "value" : "NOW()"}})
		query = "UPDATE {} set ".format(table)

		update_array = []
		for key in update_params:
			quotes = "\""
			query += ""
			value = update_params[key]
			if isinstance(value, dict):
				if not update_params[key]["quote"]:
					quotes = ""
				value = update_params[key]["value"]
			update_array.append("{} = {}{}{} ".format(key,quotes,value,quotes))

		where_array = []
		for key in where_params:
			quotes = "\""
			query += ""
			value = where_params[key]
			if isinstance(value, dict):
				if not where_params[key]["quote"]:
					quotes = ""
				value = where_params[key]["value"]
			where_array.append("{} = {}{}{} ".format(key,quotes,value,quotes))

		query += "{} where {}".format(",".join(update_array)," and ".join(where_array))
		self.execute(query)




