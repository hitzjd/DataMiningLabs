# -*- coding:utf-8 -*-

l = []

f = open('DataSet/seeds.txt')
for line in f:
	l.append(','.join(line.split())+'\n')

wf = open('DataSet/seeds2.txt','w')
for s in l:
	wf.write(s)



