# -*- coding: utf-8 -*-
#!/usr/bin/python

import os
import time
import datetime
import cPickle
import datetime
import logging
import flask
import optparse
import tornado.wsgi
import tornado.httpserver
import urllib
import hashlib
import cStringIO as StringIO
#import caffe
import sys
import numpy as np
import pandas as pd
from gensim import utils
from simserver import SessionServer
from base import BaseModel
from random import Random
from json import JSONEncoder
#----------------------
from pprint import pprint
import urllib
import urllib2
import json

import nltk


prog_path = os.path.abspath(os.path.dirname(__file__))
servers_path = os.path.join(prog_path, 'servers') #--注意servers路径问题


def dal():#数据源
	return BaseModel()

#separate
def cut(text):
	text = unicode(text, errors='ignore')  #ignore the 'utf8' codec can't decode byte 0xc2 in position 13
	words_all=(nltk.word_tokenize(text))	
	return words_all

#stopword
def stop(words_all):
	stopwords2=list(stopwords)
	words_all_nrpt=list(set(words_all))
	for i in range(0,len(words_all_nrpt)):
		for w in words_all_nrpt:
			if w in stopwords2:
				words_all_nrpt.remove(w)
		words_nrpt=words_all_nrpt
	return words_nrpt

#find simimlar article
def find_answer(question,min_score,max_results):
	#logger.info("Question: %s" % question)
	#--ta_db=db.query('select id, title_abstract from tanda')
	question2=cut(question)
	question3=stop(question2)
	#logger.info("Question3: %s" %question3)
	doc = {'tokens': question3}
	#for d in doc['tokens']:
		#logger.info(d) 
	res = km_server.find_similar(doc, min_score, max_results)#智能搜索  #--serve.find_similar服务find_similar(doc, min_score=0.0, max_results=100) doc索引要用指定tokens 或之前的索引   最小相似度  最大输出篇数                                
	#logger.info(len(doc['tokens']))   #--显示数字 分词个数 即 字典中list分词个数
	#logger.info(res)  #--数据库ID 相似度 有效载荷=数据库中km_qa问题  根据相似度降序排列
	return res


logging.basicConfig(level=logging.INFO,   #--设置日志等级 CRITICAL > ERROR > WARNING > INFO > DEBUG > NOTSET
		format='%(asctime)s %(filename)s:%(lineno)d %(levelname)s %(message)s',
		filename=os.path.join(prog_path, 'article.log'),
		filemode='w')
logger = logging.getLogger('mylogger')

km_server = SessionServer(os.path.join(servers_path, 'pubmed170131'))
db = dal().db
stopwords = set([line.rstrip().decode('utf-8') for line in open(os.path.join(os.path.dirname(__file__), 'stopwords.txt'))]) #--停用词 对停用词处理

db.execute('update pubmed170131 set similarity=0,weight=0') #initial

#matrix

for a in range(1,148):  #1--55+1 number of seeds
	print(a)
	logger.info(a)
	question_db=db.query('select title,abstract from seed where id=%s',(a,))
	question_list=question_db[0]
	question_title=question_list['title']
	#print(question_title)
	question_abstract=question_list['abstract']
	question=question_title+' .'+question_abstract
	#question=question_list['title_abstract']

	#question='Phylogenetic analyses place the enigmatic orthonectids within Spiralia'
	min_score=0.1  #similarity of articles
	max_results=100  #number of articles
	res=find_answer(question,min_score,max_results)
	

	for r in res:
		ids=r[0][4:] 
		similarity=r[1]
		weight_db=db.query('select weight from pubmed170131 where id=%s',(ids,))
		weight_list=weight_db[0]
		weight=weight_list['weight']
		
		weight_upgrade=similarity+weight #weight upgrade
		
		db.execute('update pubmed170131 set similarity=%s,weight=%s where id=%s',(similarity,weight_upgrade,ids))

	


'''

#----------------------

ta_list=[]
for row in ta_db:
	ta=row['title_abstract']
	ta2=cut(ta)
	ta_list.append({'id': 'doc_%i' % row['id'], 'tokens': stop(ta2), 'payload': row['title_abstract']})	
	print row


	return 0



#-------
pre_similar=[]  #初始化
global pre_similar
again=0  #global again初始化

#global again




@app.route('/', methods=['POST'])
def qa(api = False):
	#logger.info("Begin.")
	question = flask.request.form.get('q', '')  #--网页输入的问题获取  类型Unicode
	#-------------------
	min_answer_score = flask.request.form.get('min_score', 0.713)#给出答案（answer）的最低分值，不是相关问题的最低分值
	max_results = flask.request.form.get('max_results', 5)
	#-------------------
	if not question:
		if api:
			return "您好！有什么可以帮您？"
		else:
			return flask.render_template('index2.html', has_result=False)  #index
	#global I_DONT_KNOW
	
	#answer, res = find_answer(question, knowledge_server, table_name='knowledge')#搜索答案

	#-----------
	user_buy=flask.request.form.get('user_buy', '')
	user_id=flask.request.form.get('user_id', '')
	user_id=0
	logger.info('zzzzzzzzzzz')
	logger.info(user_buy)
	logger.info(user_id)
	#-----------
	#answer, res = find_answer(question, km_server, table_name='km_qa_2')  #-- 问题 km_qa_2服务 数据库table名字  返回answer和 res
	
	#---
	question_multi=multi(question)
	logger.info(question)
	if question_multi==[]:
		logger.info(question)

		answer, res,tuling_code = find_answer(question, km_server, table_name='km2_1', min_answer_score=min_answer_score, max_results=max_results, user_id=user_id)#搜索答案
		remember_question(question,tuling_code)

		
		#res=[]
	else:
	#---
		answer, res,tuling_code = find_answer(question_multi, km_server, table_name='km2_1', min_answer_score=min_answer_score, max_results=max_results, user_id=user_id)#搜索答案
		remember_question(question,tuling_code)

	#-----
	
	print('1111111111')
	

		
	if api:
		#logger.info("API answer: %s" % answer)
		return answer
	else:
		return flask.render_template('index1.html', has_result=True, question=question, result=answer, list=res)  #pfb
			
'''