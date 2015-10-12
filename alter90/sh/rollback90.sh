#!/bin/bash
sshconfig=/etc/ssh/sshd_config
passwdconfig=/etc/login.defs
sshpamconfig=/etc/pam.d/sshd
systemauthconfig=/etc/pam.d/system-auth
linux_path=$1
linux_shell_name=$2

mv -f $sshconfig.bak $sshconfig
mv -f $passwdconfig.bak $passwdconfig
mv -f $sshpamconfig.bak $sshpamconfig
mv -f $systemauthconfig.bak $systemauthconfig

#匹配/etc/passwd文件与用户列表中相同的用户
cat /etc/passwd|awk -F ":" '{print $1}' > $linux_path/passwd.cfg
grep -Ff $linux_path/passwd.cfg $linux_path/$linux_shell_name > $linux_path/comm.cfg
sed -i 's/.$//' $linux_path/comm.cfg
list=`cat $linux_path/comm.cfg|awk '{print $1}'`
for user90 in $list
do
	chage -d `date +%Y-%m-%d` -M 9999 -E never -W 7 $user90
done

service sshd restart

#print modify log
echo "======================================================================"
echo "                         1 $sshconfig                                 "
echo "======================================================================"
cat $sshconfig |grep "MaxAuthTries"
echo "======================================================================"
echo "                         2 $sshpamconfig                              "
echo "======================================================================"
cat $sshpamconfig|grep "pam_tally"
echo "======================================================================"
echo "                         3 $passwdconfig                              "
echo "======================================================================"
cat $passwdconfig|grep -e "^PASS_MAX_DAYS"
cat $passwdconfig|grep -e "^PASS_MIN_DAYS"
cat $passwdconfig|grep -e "^PASS_MIN_LEN"
cat $passwdconfig|grep -e "^PASS_WARN_AGE"
echo "======================================================================"
echo "                         4 $systemauthconfig                          "
echo "======================================================================"
cat $systemauthconfig|grep "pam_cracklib.so"
cat $systemauthconfig|grep "shadow"
cat $systemauthconfig|grep "pam_tally"
echo "======================================================================"
echo "                         5 90 days expires                           "
echo "======================================================================"
list=`cat $linux_path/comm.cfg|awk '{print $1}'`
for user90 in $list
do
	echo "chage -l "$user90
	echo "----------------------------------------------------------------------"
	chage -l $user90
	echo "----------------------------------------------------------------------"
done
echo "======================================================================"