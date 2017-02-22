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
		filename=os.path.join(prog_path, 'article2.log'),
		filemode='w')
logger = logging.getLogger('mylogger')

km_server = SessionServer(os.path.join(servers_path, 'pubmed170131'))
db = dal().db
stopwords = set([line.rstrip().decode('utf-8') for line in open(os.path.join(os.path.dirname(__file__), 'stopwords.txt'))]) #--停用词 对停用词处理

db.execute('update pubmed170131 set weight_punish=0,similarity_punish=0') #initial

#matrix

for a in range(1,275):  #1--55+1 number of seeds
	#print('----------',a,'---------')
	print(a)
	logger.info(a)
	question_db=db.query('select title,abstract from seed1_2 where id=%s',(a,))
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
	#for x in range(0,len(res)): #print found article 
		#print(res[x])

	#print(res)
	
	
	for r in res:
		ids=r[0][4:] 
		similarity=r[1]
		weight_db=db.query('select weight_punish from pubmed170131 where id=%s',(ids,))
		#print(weight_db)
		weight_list=weight_db[0]
		weight=weight_list['weight_punish']
		
		weight_upgrade=similarity+weight #weight upgrade
		
		db.execute('update pubmed170131 set similarity_punish=%s,weight_punish=%s where id=%s',(similarity,weight_upgrade,ids))

	



