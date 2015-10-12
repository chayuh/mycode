#!/usr/bin/python
# -*- coding: utf-8 -*-

import paramiko
import logging
import ConfigParser
import socket

def logout(msg):
    logger=logging.getLogger()
    fh=logging.FileHandler(sys_log_name)
    fh.setLevel(logging.CRITICAL)
    ch = logging.StreamHandler()
    ch.setLevel(logging.CRITICAL)
    #formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    formatter = logging.Formatter('%(asctime)s - %(message)s')
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    #logger.error(msg)
    #logger.info(msg)
    #logger.debug(msg)
    logger.critical(msg)
    logger.removeHandler(fh)
    logger.removeHandler(ch)
    logging.shutdown()

def execcmd(t):
    chan=t.open_session()
    chan.settimeout(10)
    chan.get_pty()
    chan.invoke_shell()
    #if ord_user_name != 'root':
    chan.send('sudo -i')
    chan.send("\n")
    buff = ''
    while not buff.endswith('# '):
        resp = chan.recv(9999).decode()
        buff +=resp
    chan.send('passwd '+alt_user_name)
    chan.send('\n')
    buff=''
    #while not buff.endswith('New password: '):
    while not buff.endswith(': '):
        resp = chan.recv(9999).decode()
        buff +=resp
    #print(buff)
    #logout(u"输入新密码")
    chan.send(alt_user_pwd)
    chan.send('\n')
    buff=''
    #while not buff.endswith('Retype new password: '):
    while not buff.endswith(': '):
        resp = chan.recv(9999).decode()
        buff +=resp
    #print(buff)
    #logout(u"再次输入新密码")
    chan.send(alt_user_pwd)
    chan.send('\n')
    #print(buff)
    buff=''
    while not buff.endswith('# '):
        resp = chan.recv(9999).decode()
        buff +=resp
    #print(buff)
    if 'successfully' in buff:
        logout(alt_user_name+u"用户密码修改成功！")
    else:
        logout(alt_user_name+u"用户密码修改失败！")

def sshcon(host,port,username,password):
    t=paramiko.Transport((host,port))
    try:
        t.connect(username=username,password=password)
        logout(u'主机连接成功')
        return t
    except Exception as e:
        logout(u'连接失败，错误信息：'+str(e))
        return 'false'

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
    #global root_pwd
    cf=ConfigParser.ConfigParser()
    cf.read(r"cfg\path.cfg")
    secs = cf.sections()
    #print('sections:', secs)
    opts = cf.options("path")
    #print('options:', opts)
    #read by type
    #shell_name = cf.get("path", "shell_name")
    port = cf.getint("path", "ssh_port")
    serip_name = cf.get("path", "serip_name")
    ord_user_name = cf.get("path", "ord_user_name")
    ord_user_pwd = cf.get("path", "ord_user_pwd")
    alt_user_pwd = cf.get("path", "alt_user_pwd")
    alt_user_name = cf.get("path", "alt_user_name")
    sys_log_name = cf.get("path", "sys_log_name")

def readserip():
    global host
    readcfg()
    file = open("cfg\\"+serip_name)
    for line in file:
        if '#' in line:
            continue
        #delete end space
        host=line.rstrip()
        flag = check_ssh(host,port)
        if flag == "true":
            logout(u"连接主机："+host)
            #try:
            tran=sshcon(host,port,ord_user_name,ord_user_pwd)
            if tran != 'false':
                execcmd(tran)
                sshclose(tran)
            else:
                logout("=========================================")
                continue
        else:
            logout(host+u' 连接失败,错误信息：'+flag)
            logout("=========================================")
            continue
    file.close()

if __name__ == '__main__':
    readserip()









