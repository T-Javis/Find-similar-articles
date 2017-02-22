# -*- coding: utf-8 -*-
#!/usr/bin/python
from base import BaseModel


def dal():#数据源
	return BaseModel()

db = dal().db

number=db.query('select id,weight,weight_punish from pubmed170131')

for i in range(len(number)):	
	n=number[i]
	ids=n['id']
	weight=n['weight']
	weight_punish=n['weight_punish']
	total=weight-weight_punish
	db.execute('update pubmed170131 set total=%s where id=%s',(total,ids))
	print(i)
	#print(ids,weight,weight_punish,total)












