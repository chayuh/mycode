#!/usr/bin/python
# -*- coding: utf-8 -*-

import paramiko
import logging
import ConfigParser
import re
import csv
import os
import codecs
def opss(t):
    chan=t.open_session()
    chan.settimeout(10)
    chan.get_pty()
    chan.invoke_shell()
    return chan


def execcmd(chan):
    global username
    global id
    global sudogroup
    global f
    chan.send('sudo -i\n')
    chan.send("cat /etc/passwd|grep -v nfsnobody|awk -F: '{if($3>=500){print $1,$3}}'\n")
    buff = ''
    while not buff.endswith('# '):
        resp = chan.recv(9999).decode()
        buff +=resp
    #print(buff)
    #匹配帐号+ID
    userinfo=[]
    userinfo=re.findall(r'^\w+\s\d+',buff,re.M)

    #hosta=u'主机IP'.encode('utf-8')
    #usera=u'用户名'.encode('utf-8')
    #ida=u'ID'.encode('utf-8')
    #sudoa=u'权限'.encode('utf-8')


    filename = 'hostinfo.txt'
    if os.path.exists(filename):
        #message = 'OK, the "%s" file exists.'
        #csvfile = file('csv_test.csv', 'ab+')
        #writer = csv.writer(csvfile)
        #with codecs.open('csv_test.csv', 'ab+','cp936') as csvfile:
        #    writer = csv.writer(csvfile)
        #csvfile=codecs.open('csv_test.csv','ab','utf-8')
        #writer = csv.writer(csvfile,dialect='excel')
        f=codecs.open(filename,"a+","utf-8")
        #print message % filename
    else:
        #message = 'Sorry, I cannot find the "%s" file.'
        #csvfile = file('csv_test.csv', 'ab+')
        #writer = csv.writer(csvfile)
        #writer.writerow([hosta,usera,ida,sudoa])
        #with codecs.open('csv_test.csv', 'ab+','cp936') as csvfile:
            #writer = csv.writer(csvfile)
            #writer.writerow(['',usera,ida,sudoa])
        #csvfile=codecs.open('csv_test.csv','ab','utf-8')
        #writer = csv.writer(csvfile,dialect='excel')
        #writer.writerow([hosta,usera,ida,sudoa])
        #writer.writerow(['ip','username','id','sudo'])
        #writer.writerow(['ip','username','id','sudo'])

        f=codecs.open(filename,"a+","utf-8")
        new_context=u'主机IP,用户名,ID,权限组'+'\r\n'
        f.write(new_context)


        #print message % filename



    for a in userinfo:
        s=a.split(" ")
        #print('s=%d'%len(s))
        #print(s[0])

        username=s[0]
        id=s[1]
        chan.send('cat /etc/sudoers|grep -w '+username+'|awk \'{print $1,$2}\'\n')
        buff = ''
        while not buff.endswith('# '):
            resp = chan.recv(9999).decode()
            buff +=resp
        #print(buff)
        sudogroups = []
        sudogroups=re.findall(r'^User_Alias\s\w+',buff,re.M)
        #sudogroups=re.findall(r'[^User_Alias]\s\w+',buff,re.M)
        #print(re.findall(r'^User_Alias\s\w+',buff,re.M))
        #print(len(brr))
        #获取sudoers文件中对应用户的级权限

        for b in sudogroups:
            #print("b="+b)
            ss=b.split(" ")

            #print('b=%d'%len(ss))
            sudogroup=ss[1]
            #print('sudogroup='+sudogroup)
            print("host=%s username=%s id=%s sudogroup=%s" %(host,username,id,sudogroup) )
           # print(username)
           # print(groupname)
            f.write(host+','+username+','+id+','+sudogroup+'\r\n')
            #writer.writerow([host,username,id,sudogroup])
    #csvfile.close()
    f.close()

def sshcon(host,port,username,password):
    t=paramiko.Transport((host,port))
    t.connect(username=username,password=password)
    #print(t.accept(timeout=5))
    return t

def sshclose(t):
    t.close()
    print("=========================================")

def readcfg():
    global port
    global serip_name
    global ord_user_name
    global ord_user_pwd
    global shell_name
    global log_dir
    global sys_log_name
    global linux_path

    cf=ConfigParser.ConfigParser()
    cf.read(r"cfg\path.cfg")
    secs = cf.sections()
    opts = cf.options("path")
    port = cf.getint("path", "ssh_port")
    serip_name = cf.get("path", "serip_name")
    ord_user_name = cf.get("path", "ord_user_name")
    ord_user_pwd = cf.get("path", "ord_user_pwd")
    sys_log_name = cf.get("path", "sys_log_name")
    log_dir=cf.get("path", "log_dir")
    linux_path=cf.get("path", "linux_path")
    shell_name=cf.get("path", "shell_name")

def readserip():
    global host
    global rootuser
    global dbuser
    readcfg()
    file = open("cfg\\"+serip_name)
    for line in file:
        if '#' in line:
            continue
        host=line.rstrip()
        print(u"连接主机："+host)
        try:
            tran=sshcon(host,port,ord_user_name,ord_user_pwd)
            tran1=opss(tran)
            execcmd(tran1)
            sshclose(tran)
        except Exception as e:
            print(e)
            print(u"--------连接失败---------")
            print("=========================================")
            continue
    file.close()

if __name__ == '__main__':
    readserip()










