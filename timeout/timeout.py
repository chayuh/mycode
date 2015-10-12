#!/usr/bin/python
# -*- coding: utf-8 -*-
__author__ = 'chayuh'
import os
import os.path
import codecs
import re
import datetime

def logout(msg):
    filename='output.log'
    #print(str(datetime.datetime.now())+' == '+msg)
    print(msg)
    f=codecs.open(filename,"ab+","utf-8")
    f.write(str(datetime.datetime.now())+' == '+msg+'\r\n')
    f.close()

if __name__ == '__main__':
    global rootdir
    global dn
    global end
    global fns
    rootdir = r"D:\Database\Traffica"
    dn=[]
    end=[]
    fns=[]
    for parent,dirnames,filenames in os.walk(rootdir):
        for dirname in  dirnames:
            dn.append(dirname)
        for filename in filenames:                        #输出文件信息
            fns.append(filename)

    if len(fns)!=0:
        fn=str(dn[len(dn)-1])
        filename =r'%s\%s\%s' %(rootdir,fn,'solmsg.out')
        f=codecs.open(filename,"r+","utf-8")
        logout(u'文件：'+filename)
        logout( '========================================================================================')
        for eachLine in f:
            end+=re.findall(r'^[\d+-]+\s+[\d:]+\s+\w+\s\'\w+\'\s\w+\stimed out[\w\s\,]+',eachLine,re.M)
        for b in end:
            print logout(b)
        logout( '========================================================================================')



