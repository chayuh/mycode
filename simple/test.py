#!/usr/bin/python
# -*- coding: utf-8 -*-

import paramiko
import logging
import ConfigParser
import socket
import datetime
import os
import threading
import sys

"""
def logout(msg):
    logger=logging.getLogger()
    fh=logging.FileHandler(sys_log_name)
    fh.setLevel(logging.CRITICAL)
    ch = logging.StreamHandler()
    ch.setLevel(logging.CRITICAL)
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    logger.critical(msg)
    logger.removeHandler(fh)
    logger.removeHandler(ch)
    logging.shutdown()
"""
def logout(msg):
    #print(datetime.datetime.now()+msg)
    print "%s %s" %(datetime.datetime.now(),msg)


def opss(t):
    chan=t.open_session()
    chan.settimeout(10)
    chan.get_pty()
    chan.invoke_shell()
    return chan

def delfiles(chan):
     chan.send('sudo -i')
     chan.send("\n")
     chan.send("rm -f "+linux_shell_path+" "+linux_path+"/"+log_name )
     chan.send('\n')
     buff = ''
     while not buff.endswith('# '):
         resp = chan.recv(9999).decode()
         buff +=resp
     #print(buff)

def chgpwd(chan):
    chan.send('sudo -i')
    chan.send("\n")
    buff = ''
    while not buff.endswith('# '):
        resp = chan.recv(9999).decode()
        buff +=resp
    chan.send('cat /etc/passwd|grep '+add_user_name)
    chan.send('\n')
    buff=''
    while not buff.endswith('# '):
        resp = chan.recv(9999).decode()
        buff +=resp
    #print(buff)
    if '/bin/bash' in buff:
        logout(u'检测'+add_user_name+u"用户是否已存在：yes")
    else:
        logout(u'检测'+add_user_name+u"用户是否已存在：no")
        logout(u'创建'+add_user_name+u"用户")
        chan.send('useradd '+add_user_name)
        chan.send('\n')
        buff=''
        while not buff.endswith('# '):
            resp = chan.recv(9999).decode()
            buff +=resp
        #print(buff)
        logout(u'设置'+add_user_name+u"用户密码")
        chan.send('passwd '+add_user_name)
        chan.send('\n')
        buff=''
        while not buff.endswith('New password: '):
            resp = chan.recv(9999).decode()
            buff +=resp
        #print(buff)
        chan.send(add_user_pwd)
        chan.send('\n')
        buff=''
        while not buff.endswith('Retype new password: '):
            resp = chan.recv(9999).decode()
            buff +=resp
        #print(buff)
        chan.send(add_user_pwd)
        chan.send('\n')
        #print(buff)
        buff=''
        while not buff.endswith('# '):
            resp = chan.recv(9999).decode()
            buff +=resp
        #print(buff)
        if 'successfully' in buff:
            logout(add_user_name+u"用户密码设置成功！")
        else:
            logout(add_user_name+u"用户密码设置失败！")

def execcmd(chan):
     chan.send('sudo -i\n')
     chan.send('hostname\n')
     buff=''
     while not buff.endswith('# '):
         resp = chan.recv(9999).decode()
         buff +=resp
     print(buff)

def sshcon(host,port,username,password):
    t=paramiko.Transport((host,port))
    t.connect(username=username,password=password)
    return t

def upload(t):
    global linux_shell_path
    sftp = paramiko.SFTPClient.from_transport(t)
    remotepath=linux_path+"/"+shell_name
    linux_shell_path=remotepath
    localpath='sh\\'+shell_name
    #logout(sys_log_name,u'上传脚本文件：'+shell_name)
    sftp.put(localpath,remotepath)

def download(t):
    sftp = paramiko.SFTPClient.from_transport(t)
    localpath=linux_path+'/'+log_name
    remotepath="log\\"+log_name
    #logout(sys_log_name,u'下载日志文件：'+log_name)
    sftp.get(localpath,remotepath)

def sshclose(t):
    t.close()
    logout("=========================================")

def readcfg():
    global port
    global serip_name
    global ord_user_name
    global ord_user_pwd
    global shell_name
    global log_dir
    global sys_log_name
    global linux_path
    global add_user_name
    global add_user_pwd
    global user_group

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
    add_user_name=cf.get("path", "add_user_name")
    add_user_pwd=cf.get("path", "add_user_pwd")
    user_group=cf.get("path", "user_group")

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

def group_select():
    global admins_user
    global dba_user
    #str="选择添加"+add_user_name+"用户至ADMINS or DBA组："
    #str1=str.decode('utf-8').encode('gbk')
    #user_group=raw_input(str1)
    if user_group.upper() == 'ADMINS':
        admins_user=add_user_name
        dba_user="\"\""
    elif user_group.upper() == 'DBA':
        dba_user=add_user_name
        admins_user="\"\""
    else:
        print(u'请再次输入（仅限指定组名）')
        group_select()

def readserip(host):
    #global host
    global add_user_name
    global add_user_pwd
    #readcfg()

    #str='输入要创建的用户名：'.decode('utf-8').encode('gbk')
    #add_user_name=raw_input(str)
    #str='输入要创建的用户密码：'.decode('utf-8').encode('gbk')
    #add_user_pwd=raw_input(str)
    group_select()

    #file = open("cfg\\"+serip_name)
    #for line in file:
        #if '#' in line:
            #continue
        #host=line.rstrip()
    #flag = check_ssh(host,port)
    #if flag == "true":
    logout(u"连接主机："+host)
    try:
        tran=sshcon(host,port,ord_user_name,ord_user_pwd)
        upload(tran)
        tran1=opss(tran)
        #chgpwd(tran1)
        execcmd(tran1)
        #download(tran)
        #delfiles(tran1)
        sshclose(tran)
    except Exception as e:
        logout(e)
        logout("=========================================")
        #continue
        return
   # else:
       # logout(host+u' 连接异常,错误信息：'+flag)
       # logout("=========================================")
        #continue
       # return
    #logout(u"*************批量操作执行完成************")
    #logout("=========================================")

if __name__ == '__main__':
    global host
    readcfg()
    #print("=========================================")
    #print(u"程序功能：增加帐号并设置密码、添加sudo权限")
    #print("=========================================")
    logout("=========================================")
    logout(u"*************开始执行批量操作************")
    logout("=========================================")

    threads = []
    #print "程序开始运行%s" % datetime.datetime.now()
    file = open("cfg\\"+serip_name)
    for line in file:
        if '#' in line:
            continue
        host=line.rstrip()
        flag = check_ssh(host,port)
        if flag == "true":
        #readserip(host)
            th = threading.Thread(target=readserip, args=(host,))
            th.start()
            threads.append(th)
        else:
            logout(host+u' 连接异常,错误信息：'+flag)
            logout("=========================================")
            continue

    file.close()
    # 等待线程运行完毕
    for th in threads:
        th.join()
    #print "程序结束运行%s" % datetime.datetime.now()

