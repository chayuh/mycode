#!/usr/bin/python
# -*- coding: utf-8 -*-

import paramiko
import ConfigParser
import re
import os
import codecs
import datetime
import socket

def logout(msg):
    filename=sys_log_name
    print(str(datetime.datetime.now())+' == '+msg)
    f=codecs.open(filename,"ab+","utf-8")
    f.write(str(datetime.datetime.now())+' == '+msg+'\r\n')
    f.close()

def opss(t):
    chan=t.open_session()
    chan.settimeout(10)
    chan.get_pty()
    chan.invoke_shell()
    return chan

def execcmd(chan):
    global release
    global hostname
    global username
    global id
    global sudogroup
    global f
    logout(u'开始采集主机信息......')
    chan.send('sudo -i\n')
    chan.send('cat /etc/redhat-release\n')
    buff = ''
    while not buff.endswith('# '):
        resp = chan.recv(9999).decode()
        buff +=resp
    #print(buff)
	#获取系统版本，使用re.findall匹配到的结果必须放到数组中，否则会带回车、中括号等符号
    release1=[]
    #release1=re.findall(r'^[\w+\s]+\d+\.\d\s\(\w+\)',buff,re.M)
    release1=re.findall(r'^[\w+\s]+[\d.]+\s\(\w+\)',buff,re.M)
    #print(release1)
    for i in release1:
        release=i
    #print(release)
	#获取主机名，使用sysctl命令时以=为分隔左右来获取主机名
    chan.send('sysctl kernel.hostname\n')
    buff = ''
    while not buff.endswith('# '):
        resp = chan.recv(9999).decode()
        buff +=resp
    #print(buff)
    hostname1=[]
    hostname1=re.findall(r'^\w+.\w+\s\=\s.+',buff,re.M)
    for i in hostname1:
		#注意去除首尾的空格，否则打印时会出意外
        aaa=str(i).split("=")
        hostname=aaa[1].strip()
	#查询ID为500以后的用户名
    chan.send("cat /etc/passwd|grep -v nfsnobody|awk -F: '{if($3>=500){print $1,$3}}'\n")
    buff = ''
    while not buff.endswith('# '):
        resp = chan.recv(9999).decode()
        buff +=resp
    #print(buff)
    #匹配帐号+ID
    userinfo=[]
	#匹配字母开头中间为空格后为数字，即匹配帐号加ID
    userinfo=re.findall(r'^\w+\s\d+',buff,re.M)
    #print(re.findall(r'^\w+\s\d+',buff,re.M))

	#判断文件是否存在，如果不存在就创建文件并输出标题，如果存在则只是打开
    filename = 'hostinfo.txt'
    if os.path.exists(filename):
        f=codecs.open(filename,"a+","utf-8")
    else:
        f=codecs.open(filename,"a+","utf-8")
        title=u'主机IP,主机名,用户名,ID,权限组,系统版本'+'\r\n'
        f.write(title)
	#遍历用户
    for a in userinfo:
        s=a.split(" ")
        username=s[0]
        id=s[1]
		#当前用户在sudoers中是否存在权限组中
        chan.send('cat /etc/sudoers|grep -w '+username+'|awk \'{print $1,$2}\'\n')
        buff = ''
        while not buff.endswith('# '):
            resp = chan.recv(9999).decode()
            buff +=resp
        #print(buff)
        sudogroups = []
		#匹配权限组,可能是一个，也可能是多个，也可能为空
        sudogroups=re.findall(r'^User_Alias\s\w+',buff,re.M)
        #当匹配User_Alias开头的数据时，没有任何数据返回的时候，赋值为NULL
        if len(sudogroups)==0:
            sudogroups.append('User_Alias NULL')
        #获取sudoers文件中对应用户的级权限
		#当前用户对应在sudoers中一个或者多个组权限
        for b in sudogroups:
            ss=b.split(" ")
			#获取权限组名称
            sudogroup=ss[1]
            #print('host=%s hostname=%s  username=%s id=%s sudogroup=%s release=%s' %(host,hostname,username,id,sudogroup,release) )
            f.write(host+','+hostname+','+username+','+id+','+sudogroup+','+release+'\r\n')
    logout(u'主机信息采集完成，生成文本文件成功')
    f.close()

def sshcon(host,port,username,password):
    t=paramiko.Transport((host,port))
    try:
        t.connect(username=username,password=password)
        logout(u'主机连接成功')
    except Exception as e:
        logout(str(e))
    return t

def check_ssh(ip, port):
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk.settimeout(1)
    try:
        sk.connect((ip,port))
        return "true"
    except Exception as e:
        return str(e)
    finally:
        sk.close()

def sshclose(t):
    t.close()
    logout(u'关闭主机连接')
    logout("=========================================")

def readcfg():
    global port
    global serip_name
    global ord_user_name
    global ord_user_pwd
    global sys_log_name

    cf=ConfigParser.ConfigParser()
    cf.read(r"cfg\path.cfg")
    secs = cf.sections()
    opts = cf.options("path")
    port = cf.getint("path", "ssh_port")
    serip_name = cf.get("path", "serip_name")
    ord_user_name = cf.get("path", "ord_user_name")
    ord_user_pwd = cf.get("path", "ord_user_pwd")
    sys_log_name = cf.get("path", "sys_log_name")

def readserip():
    global host
    readcfg()
    file = open("cfg\\"+serip_name)
    for line in file:
        if '#' in line:
            continue
        host=line.rstrip()
        flag = check_ssh(host,port)
        if flag == "true":
            logout(u"连接主机："+host)
            try:
                tran=sshcon(host,port,ord_user_name,ord_user_pwd)
                tran1=opss(tran)
                execcmd(tran1)
                sshclose(tran)
            except Exception as e:
                logout(str(e))
                logout("=========================================")
                continue
        else:
            logout(host+u' 连接异常,错误信息：'+flag)
            logout("=========================================")
            continue
    file.close()

if __name__ == '__main__':
    readserip()










