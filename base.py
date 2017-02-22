#
# -*- coding: utf-8 -*-
#
# Created by sunlei on 2013-03-25
# Copyright (c) 2013 MEIJIALE. All rights reserved.
#
# http://www.meijiale.com
#
import os
import datetime
import traceback
import psycopg2
import psycopg2.pool
import psycopg2.extras
# from settings import APP_SETTINGS, DB_SETTINGS
import sys
import logging

reload(sys)
sys.setdefaultencoding('utf8')

# application 配置信息
APP_SETTINGS = dict(template_path=os.path.join(os.path.dirname(__file__), "templates"),
					static_path=os.path.join(os.path.dirname(__file__), "static"),
					api_sign_key="*****",
					media_server_domain="http://222.66.2*8.89:*****",
					media_url_prefix="/media/communication",
					media_store_path="/home/media/communication",
					user_header_images_folder="user_header_images",
					picture_messages_folder="picture_messages",
					audio_messages_folder="audio_messages",
					picture_book_folder="picture_books",
					picture_bazaar_folder="picture_bazaars",
					html_messages_folder='html_messages',
					user_default_header_image_url="/media/communication/user_header_images/default/private.png",
					group_default_header_image_url="/media/communication/user_header_images/default/group.png",
					debug=True,
					gzip=True,
					# xsrf_cookies=True,
					# login_url="/web/login",
					cookie_secret='VmUl9OozTty/P/**********3tDM=')


# database 配置信息
DB_SETTINGS = dict(host="127.0.0.1",
				   port="5432",
				   dbname="ma***e",
				   user="postgres",
				   password="***",
				   minconn=1,
				   maxconn=1000)

class Error(object):
	def __init__(self, code=0, message=None):
		self.code = code
		self.message = message


class Status(object):
	def __init__(self, code=0, message=None):
		self.code = code
		self.message = message


class BaseModel(object):
	@property
	def db(self): return Database()


class DatabaseSingleton(object):
	def __new__(cls, *args, **kw):
		if not hasattr(cls, '_instance'):
			orig = super(DatabaseSingleton, cls)
			cls._instance = orig.__new__(cls, *args, **kw)

			host = DB_SETTINGS['host']
			port = DB_SETTINGS['port']
			user = DB_SETTINGS['user']
			password = DB_SETTINGS['password']
			dbname = DB_SETTINGS['dbname']
			minconn = DB_SETTINGS['minconn']
			maxconn = DB_SETTINGS['maxconn']

			dsn = 'host=%s port=%s dbname=%s user=%s password=%s' % (host, port, dbname, user, password)
			cls._instance.dbpool = psycopg2.pool.SimpleConnectionPool(minconn, maxconn, dsn=dsn)

		return cls._instance

	def __del__(self):
		self.dbpool.closeall()
		object.__del__(self)


class Database(DatabaseSingleton):
	def __init__(self):
		self.in_transaction = False

	def execute(self, operation, parameters=None):
		try:
			if not self.in_transaction:
				self.begin()

			if parameters:
				self.cursor.execute(operation, parameters)
			else:
				self.cursor.execute(operation)

			self.commit()
			self.database_log(self.cursor)
		except Exception, ex:
			print ex
			logging.error(operation)
			logging.error(parameters)
			traceback.print_exc()
			self.dbpool.putconn(self.conn, close=True)
			return False
		else:
			self.dbpool.putconn(self.conn)
			return True


	def executemany(self, operation, parameters=None):
		try:
			if not self.in_transaction:
				self.begin()

			if parameters:
				self.cursor.executemany(operation, parameters)
			else:
				self.cursor.executemany(operation)

			self.commit()
		except Exception, ex:
			print ex
			traceback.print_exc()
			self.dbpool.putconn(self.conn, close=True)
			return False
		else:
			self.dbpool.putconn(self.conn)
			return True


	def query(self, operation, parameters=None, fetchone=False):
		conn = self.dbpool.getconn()
		cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
		rows = None

		try:
			if parameters:
				cursor.execute(operation, parameters)
			else:
				cursor.execute(operation)

			if fetchone:
				rows = cursor.fetchone()
			else:
				rows = cursor.fetchall()

			self.database_log(cursor)

		except Exception, ex:
			print ex
			traceback.print_exc()
			cursor.close()
			self.dbpool.putconn(conn, close=True)

			return False
		else:
			cursor.close()
			self.dbpool.putconn(conn)

			return rows


	def begin(self):
		self.in_transaction = True
		self.conn = self.dbpool.getconn()
		self.cursor = self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor)

	def commit(self):
		if self.in_transaction and self.conn:
			try:
				self.conn.commit()
			except Exception, ex:
				self.conn.rollback()
				print ex
				traceback.print_exc()
			finally:
				self.cursor.close()
				self.in_transaction = False

	def rollback(self):
		if self.in_transaction and self.conn:
			try:
				self.conn.rollback()
			except Exception, ex:
				print ex
				traceback.print_exc()
			finally:
				self.cursor.close()
				self.in_transaction = False

	def database_log(self, cursor):
		if cursor and APP_SETTINGS.has_key('debug') and APP_SETTINGS['debug']:
			pass
			#logging.info('SQL--> ' + cursor.query)
			#logging.info('affect rows count --> ' + str(cursor.rowcount))
			#logging.info('status message -->' + str(cursor.statusmessage))
