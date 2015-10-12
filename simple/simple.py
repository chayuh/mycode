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
        #while not buff.endswith('New password: '):
        while not buff.endswith(': '):
            resp = chan.recv(9999).decode()
            buff +=resp
        #print(buff)
        chan.send(add_user_pwd)
        chan.send('\n')
        buff=''
        #while not buff.endswith('Retype new password: '):
        while not buff.endswith(': '):
            resp = chan.recv(9999).decode()
            buff +=resp
        chan.send(add_user_pwd)
        chan.send('\n')
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
     chan.send('sudo -i')
     chan.send("\n")
     chan.send('chmod 755 '+linux_shell_path)
     chan.send('\n')
     loseR="sed -i 's/\\r$//' "+linux_shell_path
     chan.send(loseR)
     chan.send('\n')
     global log_name
     if 'alt' in shell_name:
         log_name=host+".log"
     if 'rol' in shell_name:
         log_name=host+"_rol.log"
     log_exec=linux_shell_path+" "+admins_user+" "+dba_user+">"+linux_path+"/"+log_name
     logout(u'添加用户sudo权限成功！')
     chan.send(log_exec)
     chan.send('\n')
     buff=''
     while not buff.endswith('# '):
         resp = chan.recv(9999).decode()
         buff +=resp
     #print(buff)

def sshcon(host,port,username,password):
    t=paramiko.Transport((host,port))
    try:
        t.connect(username=username,password=password)
        logout(u'主机连接成功')
        return t
    except Exception as e:
        logout(u'连接失败，错误信息：'+str(e))
        return 'false'

def upload(t):
    global linux_shell_path
    sftp = paramiko.SFTPClient.from_transport(t)
    remotepath=linux_path+"/"+shell_name
    linux_shell_path=remotepath
    localpath='sh\\'+shell_name
    #logout(u'上传脚本文件：'+shell_name)
    sftp.put(localpath,remotepath)

def download(t):
    sftp = paramiko.SFTPClient.from_transport(t)
    localpath=linux_path+'/'+log_name
    remotepath="log\\"+log_name
    #logout(u'下载日志文件：'+log_name)
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
    str="选择添加"+add_user_name+"用户至ADMINS or DBA组："
    str1=str.decode('utf-8').encode('gbk')
    user_group=raw_input(str1)
    if user_group.upper() == 'ADMINS':
        admins_user=add_user_name
        dba_user="\"\""
    elif user_group.upper() == 'DBA':
        dba_user=add_user_name
        admins_user="\"\""
    else:
        print(u'请再次输入（仅限指定组名）')
        group_select()

def readserip():
    global host
    global add_user_name
    global add_user_pwd
    readcfg()
    print("=========================================")
    print(u"程序功能：增加帐号并设置密码、添加sudo权限")
    #print(u"此程序针对redhat linux 6.5版本")
    print("=========================================")
    str='输入要创建的用户名：'.decode('utf-8').encode('gbk')
    add_user_name=raw_input(str)
    str='输入要创建的用户密码：'.decode('utf-8').encode('gbk')
    add_user_pwd=raw_input(str)
    group_select()
    logout("=========================================")
    logout(u"*************开始执行批量操作************")
    logout("=========================================")
    file = open("cfg\\"+serip_name)
    for line in file:
        if '#' in line:
            continue
        host=line.rstrip()
        flag = check_ssh(host,port)
        if flag == "true":
            logout(u"连接主机："+host)
            tran=sshcon(host,port,ord_user_name,ord_user_pwd)
            if tran != 'false':
                upload(tran)
                tran1=opss(tran)
                chgpwd(tran1)
                execcmd(tran1)
                download(tran)
                delfiles(tran1)
                sshclose(tran)
            else:
                logout("=========================================")
                continue
        else:
            logout(host+u' 连接异常,错误信息：'+flag)
            logout("=========================================")
            continue
    file.close()
    logout(u"*************批量操作执行完成************")
    logout("=========================================")

if __name__ == '__main__':
    readserip()