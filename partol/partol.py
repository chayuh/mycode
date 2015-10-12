#!/usr/bin/python
# -*- coding: utf-8 -*-

import paramiko
import logging
import ConfigParser

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

def opss(t):
    chan=t.open_session()
    chan.settimeout(10)
    chan.get_pty()
    chan.invoke_shell()
    return chan

def delfiles(chan):
    #if ord_user_name != 'root':
    chan.send('sudo -i')
    chan.send("\n")
    buff = ''
    while not buff.endswith('# '):
        resp = chan.recv(9999).decode()
        buff +=resp
    chan.send("rm -f "+linux_shell_path+" "+linux_path+"/"+log_name )
    chan.send('\n')
    buff = ''
    while not buff.endswith('# '):
        resp = chan.recv(9999).decode()
        buff +=resp
    #print(buff)


def execcmd(chan):
    #if ord_user_name != 'root':
    chan.send('sudo -i')
    chan.send("\n")
    buff = ''
    while not buff.endswith('# '):
        resp = chan.recv(9999).decode()
        buff +=resp
    #print(buff)
    chan.send('chmod 755 '+linux_shell_path)
    chan.send('\n')
    buff=''
    while not buff.endswith('# '):
        resp = chan.recv(9999).decode()
        buff +=resp
    #print(buff)
    loseR="sed -i 's/\\r$//' "+linux_shell_path
    chan.send(loseR)
    chan.send('\n')
    buff=''
    while not buff.endswith('# '):
        resp = chan.recv(9999).decode()
        buff +=resp
    #print(buff)
    global log_name
    if 'alt' in shell_name:
        log_name=host+".log"
    if 'rol' in shell_name:
        log_name=host+"_rol.log"
    log_exec=linux_shell_path+" "+host+">"+linux_path+"/"+log_name
    logout(u'执行脚本文件：'+shell_name)
    chan.send(log_exec)
    chan.send('\n')
    buff=''
    while not buff.endswith('# '):
        resp = chan.recv(9999).decode()
        buff +=resp
    #print(buff)

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
    logout(u'上传脚本文件：'+shell_name)
    sftp.put(localpath,remotepath)

def download(t):
    sftp = paramiko.SFTPClient.from_transport(t)
    localpath=linux_path+'/'+log_name
    remotepath="log\\"+log_name
    logout(u'下载日志文件：'+log_name)
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
        logout(u"连接主机："+host)
        try:
            tran=sshcon(host,port,ord_user_name,ord_user_pwd)
            upload(tran)
            tran1=opss(tran)
            execcmd(tran1)
            download(tran)
            delfiles(tran1)
            sshclose(tran)
        except Exception as e:
            print(e)
            logout(u"--------连接失败---------")
            logout("=========================================")
            continue
    file.close()

if __name__ == '__main__':
    readserip()










