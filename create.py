# -*- coding: utf-8 -*-
#!/usr/bin/python
import logging
import sys
import os
from gensim import utils
from simserver import SessionServer
from base import BaseModel
import nltk
def dal():
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
	

'''
def stop(words_all):  
	stopwords2=list(stopwords)
	words_all_nrpt=list(set(words_all))
	for i in range(0,len(words_all_nrpt)):
		for w in words_all_nrpt:
			for s in stopwords2:
				if w==s:
					words_all_nrpt.remove(w)
		words_nrpt=words_all_nrpt
	return words_nrpt

'''

prog_path = os.path.abspath(os.path.dirname(__file__))
db = dal().db
stopwords = set([line.rstrip().decode('utf-8') for line in open(os.path.join(os.path.dirname(__file__), 'stopwords.txt'))]) #--停用词 对停用词处理
#print(type(stopwords))

logging.basicConfig(level=logging.INFO,   #--设置日志等级 CRITICAL > ERROR > WARNING > INFO > DEBUG > NOTSET
		format='%(asctime)s %(filename)s:%(lineno)d %(levelname)s %(message)s',
		filename=os.path.join(prog_path, 'article.log'),
		filemode='a')
logger = logging.getLogger('mylogger')

#server_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'servers', table_name)  
server_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'servers/pubmed170131',)  #--model path
server = SessionServer(server_path)  

ta_db=db.query('select id, title, abstract from pubmed170131')
ta_list=[]
x=1
for row in ta_db:
	title=row['title']
	abstract=row['abstract']
	ta=title+'. '+abstract+'. '
	#ta=row['title_abstract']
	ta2=cut(ta)
	ta_list.append({'id': 'doc_%i' % row['id'], 'tokens': stop(ta2), 'payload': ta})	
	#print row
	#logger.info(row)
	logger.info(x)
	x=x+1


server.drop_index()  #--删除所有索引
utils.upload_chunked(server, ta_list, chunksize=1000) #--simserver分块处理
server.train(ta_list, method='lsi')  #--训练已处理后的问题
server.index(ta_list)  #--建立索引文件
print(server.status())

#UnicodeDecodeError: 'utf8' codec can't decode byte 0xc2 in position 9: unexpected end of data