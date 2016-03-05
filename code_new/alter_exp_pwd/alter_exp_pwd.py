#!/usr/bin/python
# -*- coding: utf-8 -*-

##################################################
#alter_exp_pwd.py
#date:2016.3.5
#功能概述
#检测用户登陆时密码是否过期，如过期则重设新密码并在更改密码后尝试登陆，未过期则直接退出（针对密码策略生效后的批量密码重置)
##################################################

import paramiko
import ConfigParser
import socket
import re
import datetime
import codecs

class ExpireException(Exception):
	'''你定义的异常类。'''
	def __init__(self, msg):
		Exception.__init__(self)
		self.msg = msg

def logout(msg):
    print(str(datetime.datetime.now())+' == '+msg)
    f=codecs.open(sys_log_name,"ab+","utf-8")
    f.write(str(datetime.datetime.now())+' == '+msg+'\r\n')
    f.close()

def errout(msg):
    f=codecs.open(err_log_name,"ab+","utf-8")
    f.write(msg+'\r\n')
    f.close()

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
    global alt_user_pwd
    global log_dir
    global alt_user_name
    global sys_log_name
    global err_log_name
    global key
    key=77
    filter()
    #global root_pwd
    cf=ConfigParser.ConfigParser()
    cf.read(r"cfg\path.cfg")
    secs = cf.sections()
    opts = cf.options("path")
    port = cf.get("path", "ssh_port")
    serip_name = cf.get("path", "serip_name")
    ord_user_name = cf.get("path", "ord_user_name")
    ord_user_pwd = cf.get("path", "ord_user_pwd")
    alt_user_pwd = decrypt(key,cf.get("path", "alt_user_pwd"))
    #alt_user_name = cf.get("path", "alt_user_name")
    sys_log_name = cf.get("path", "sys_log_name")
    err_log_name = cf.get("path", "err_log_name")

def decrypt(key, s):
    c = bytearray(str(s).encode("gbk"))
    n = len(c) # 计算 b 的字节数
    if n % 2 != 0 :
        return ""
    n = n // 2
    b = bytearray(n)
    j = 0
    for i in range(0, n):
        c1 = c[j]
        c2 = c[j+1]
        j = j+2
        c1 = c1 - 40
        c2 = c2 - 40
        b2 = c2*16 + c1
        b1 = b2^ key
        b[i]= b1
    try:
        return b.decode("gbk")
    except:
        return "failed"

def filter():
    content = open(r'cfg\path.cfg').read()
    content = re.sub(r"\xfe\xff","", content)
    content = re.sub(r"\xff\xfe","", content)
    content = re.sub(r"\xef\xbb\xbf","", content)
    open(r'cfg\path.cfg', 'w').write(content)

def expire(chan,pwd):
    #chan.send('\n')
    buff=''
    resp=chan.recv(9999).decode()
    buff+=resp
    #print buff
    if 'password' in buff:
        logout(u'检测到当前用户密码已经过期！')
        logout(u"开始修改密码")
        buff=''
        while not buff.endswith(': '):
            resp = chan.recv(9999).decode()
            buff +=resp
        #print(buff)
        #输入当前用户密码
        chan.send(pwd)
        chan.send('\n')
        buff=''
        while not buff.endswith(': '):
            resp = chan.recv(9999).decode()
            buff +=resp
        #print(buff)
        #输入修改密码
        chan.send(alt_user_pwd)
        chan.send('\n')
        buff=''
        while not buff.endswith(': '):
            resp = chan.recv(9999).decode()
            buff +=resp
        #print(buff)
        chan.send(alt_user_pwd)
        chan.send('\n')
    else:
        raise ExpireException(u'错误信息：当前用户密码未过期')


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
        port1=port.split(' ')#以空格分隔多个端口
        name=ord_user_name.split(' ')#以空格分隔多个用户
        pwd=ord_user_pwd.split(' ')#以空格分隔多个密码
        i=0
        global flag
        while i<len(port1):
           p=int(port1[i])
           #logout(u"检测 "+str(p)+u" 端口状态")
           flag = check_ssh(host,p)
           if flag== "true":
                logout(str(p)+u" 端口正常")
                break
           else:
                logout(u"检测到 "+str(p)+u" 端口异常,尝试其他端口")
                errout(host+" "+str(p))
           i=i+1
        if flag == "true":
            j=0
            while j<len(name):
                n1=name[j]#获取用户名
                p1=decrypt(key,pwd[j])#获取解密后的密码
                logout(u"连接主机："+host)
                #print j,n1,p1
                try:
                    t=paramiko.Transport((host,p))
                    t.connect(username=n1,password=p1)
                    chan=t.open_session()
                    chan.settimeout(10)
                    chan.get_pty()
                    chan.invoke_shell()
                    logout(u'主机连接成功')
                    try :
                        expire(chan,p1)
                        t=paramiko.Transport((host,p))
                        t.connect(username=n1,password=alt_user_pwd)
                        if 'isAlive' in str(t.is_alive):
                            logout(u"密码更改成功，尝试登陆成功！")
                        else:
                            logout(u"密码修改失败！")
                        sshclose(t)
                        break
                    except socket.timeout :
                        logout(u'错误信息：连接超时')
                        errout(host+" "+str(p)+" "+n1)
                        sshclose(t)
                        #continue
                    except ExpireException,x:
                        logout(x.msg)
                        errout(host+" "+str(p)+" "+n1)
                        sshclose(t)
                        #continue
                except Exception as e:
                    logout(u'使用 '+n1+u' 登陆失败'+u'错误信息：'+str(e))
                    #logout(u'错误信息：'+str(e))
                    errout(host+" "+str(p)+" "+n1)
                    logout("=========================================")
                    #continue
                j=j+1
        else:
            logout(host+u' 连接异常,错误信息：'+flag)
            errout(host)
            logout("=========================================")
            continue
    file.close()

if __name__ == '__main__':
    readserip()









