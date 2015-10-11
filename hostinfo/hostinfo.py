#!/usr/bin/python
# -*- coding: utf-8 -*-

import paramiko
import ConfigParser
import re
import os
import xlrd
import xlwt
import socket
import datetime
import codecs
from xlutils.copy import copy

def logout(msg):
    filename=sys_log_name
    #print "%s %s" %(datetime.datetime.now(),msg)
    print(str(datetime.datetime.now())+' == '+msg)
    #print('%s host=%s hostname=%s  username=%s id=%s sudogroup=%s release=%s' %(datetime.datetime.now(),host,hostname,username,id,sudogroup,release))
    f=codecs.open(filename,"ab+","utf-8")
    f.write(str(datetime.datetime.now())+' == '+msg+'\r\n')
    f.close()

def create_xls(filename):
    style1 = xlwt.XFStyle()
    font1 = xlwt.Font()   #创建font1
    font1.name = u'宋体'  #字体为'Times New Roman'
    font1.bold = True   #加粗
    style1 = xlwt.XFStyle()
    borders = xlwt.Borders()
    alignment = xlwt.Alignment()
    alignment.vert = xlwt.Alignment.VERT_CENTER
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top =  xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN
    style1.alignment=alignment
    style1.borders = borders
    style1.font = font1

    file = xlwt.Workbook()
    table = file.add_sheet(u'主机信息',cell_overwrite_ok=True)
    table.write(0,0,u'序号',style1)
    table.write(0,1,u'主机IP',style1)
    table.write(0,2,u'主机名',style1)
    table.write(0,3,u'用户名',style1)
    table.write(0,4,u'ID',style1)
    table.write(0,5,u'权限组',style1)
    table.write(0,6,u'系统版本',style1)
    file.save(filename)

def write_xls(filename,host,hostname,username,id,sudogroup,release):
    oldWb = xlrd.open_workbook(filename,formatting_info=True)
    newWb = copy(oldWb)
    newWs = newWb.get_sheet(0)
    sheet2 = oldWb.sheet_by_index(0)
    global initcol
    col=sheet2.ncols
    row=sheet2.nrows
    #print('row=%d col=%d' %(row,col))
    newWs.write(row, 1, host,style())
    newWs.write(row, 2, hostname,style())
    newWs.write(row, 3, username,style())
    newWs.write(row, 4, id,style())
    newWs.write(row, 5, sudogroup,style())
    newWs.write(row, 6, release,style())
    newWb.save(filename)

def style():
    style1 = xlwt.XFStyle()
    borders = xlwt.Borders()
    alignment = xlwt.Alignment()
    alignment.vert = xlwt.Alignment.VERT_CENTER
    borders.left = xlwt.Borders.THIN
    borders.right = xlwt.Borders.THIN
    borders.top =  xlwt.Borders.THIN
    borders.bottom = xlwt.Borders.THIN
    style1.alignment=alignment
    style1.borders = borders
    return style1

def merge_xls(filename,host,hostname,release,mem_row):
    oldWb = xlrd.open_workbook(filename,formatting_info=True)
    newWb = copy(oldWb)
    newWs = newWb.get_sheet(0)
    sheet2 = oldWb.sheet_by_index(0)
    #print(sheet2.merged_cells)
    order=len(sheet2.merged_cells)/4
    col=sheet2.ncols
    row=sheet2.nrows
    #print(mem_row,row-1)
    newWs.write_merge(mem_row,row-1, 1, 1, host,style())
    newWs.write_merge(mem_row,row-1, 2, 2, hostname,style())
    newWs.write_merge(mem_row,row-1, 6, 6, release,style())
    #newWs.write_merge(mem_row,row-1, 0, 0, xlwt.Formula("COUNTA(b2"+":b"+str(row)+")"),style())
    newWs.write_merge(mem_row,row-1, 0, 0, str(order+1),style())
    #newWs.write_merge(mem_row,row-1, 0, 0, host,style())
    #newWs.write_merge(mem_row,row-1, 1, 1, hostname,style())
    #newWs.write_merge(mem_row,row-1, 5, 5, release,style())
    newWb.save(filename)

def memcr_xls(filename):
    oldWb = xlrd.open_workbook(filename,formatting_info=True)
    newWb = copy(oldWb)
    #newWs = newWb.get_sheet(0)
    sheet2 = oldWb.sheet_by_index(0)
    global mem_col
    global mem_row
    mem_col=sheet2.ncols
    mem_row=sheet2.nrows

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
    #判断文件是否存在，如果不存在就创建文件并输出标题，如果存在则只是打开
    global filename
    filename = out_xls_name
    if not os.path.exists(filename):
        #创建标题
        create_xls(filename)
        #记录col,row初始值
        memcr_xls(filename)
    else:
        memcr_xls(filename)
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
        #当前用户对应在sudoers中一个或者多个组权限

        for b in sudogroups:
            ss=b.split(" ")
            #获取权限组名称
            sudogroup=ss[1]
            #output="host=%s hostname=%s username=%s id=%s sudogroup=%s release=%s" %(host,hostname,username,id,sudogroup,release)
            #logout(output)
            write_xls(filename,host,hostname,username,id,sudogroup,release)
    logout(u'主机信息采集完成，生成Excel文件成功')
    merge_xls(filename,host,hostname,release,mem_row)

def sshcon(host,port,username,password):
    t=paramiko.Transport((host,port))
    try:
        t.connect(username=username,password=password)
        logout(u'主机连接成功')
    except Exception as e:
        logout(e)
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
    global out_xls_name

    cf=ConfigParser.ConfigParser()
    cf.readfp(codecs.open(r"cfg\path.cfg", "r", "utf-8-sig"))
    #cf.read(r"cfg\path.cfg")
    secs = cf.sections()
    opts = cf.options("path")
    port = cf.getint("path", "ssh_port")
    serip_name = cf.get("path", "serip_name")
    ord_user_name = cf.get("path", "ord_user_name")
    ord_user_pwd = cf.get("path", "ord_user_pwd")
    sys_log_name = cf.get("path", "sys_log_name")
    out_xls_name = cf.get("path", "out_xls_name")

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
        flag = check_ssh(host,port)
        if flag == "true":
            logout(u"连接主机："+host)
            try:
                tran=sshcon(host,port,ord_user_name,ord_user_pwd)
                tran1=opss(tran)
                execcmd(tran1)
                sshclose(tran)
            except Exception as e:
                logout(e)
                logout("=========================================")
                continue
        else:
            logout(host+u' 连接异常,错误信息：'+flag)
            logout("=========================================")
            continue
    file.close()

if __name__ == '__main__':
    readserip()










