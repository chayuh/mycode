#!/bin/bash
#create path
sshconfig=/etc/ssh/sshd_config
passwdconfig=/etc/login.defs
sshpamconfig=/etc/pam.d/sshd
systemauthconfig=/etc/pam.d/system-auth
linux_path=$1
linux_shell_name=$2
bakdir=/tmp/bak
mkdir -p $bakdir

#backup configure files
cp -p $sshconfig $sshconfig.bak
cp -p $passwdconfig $passwdconfig.bak
cp -p $sshpamconfig $sshpamconfig.bak
cp -p $systemauthconfig $systemauthconfig.bak
#bakcup to another dir
cp -p $sshconfig $bakdir/.
cp -p $passwdconfig $bakdir/.
cp -p $sshpamconfig $bakdir/.
cp -p $systemauthconfig $bakdir/.

#1 modify ssh config
sed -i -e '/#MaxAuthTries/s/[0-9]\+/5/' -i -e '/^#MaxAuthTries/s/#//' $sshconfig

#2 modify ssh pam config
pam_tally=`find /lib* -iname "pam_tally.so"`
pam_tally2=`find /lib* -iname "pam_tally2.so"`
if [ -n "$pam_tally2" ];then
	sed -i '2 a auth       required     pam_tally2.so onerr=fail deny=5 unlock_time=120' $sshpamconfig
	sed -i '/auth.*pam_env.so/a\auth        required      pam_tally2.so onerr=fail deny=5 unlock_time=120' $systemauthconfig
	sed -i '/account.*pam_unix.so/a\account     required      pam_tally2.so' $systemauthconfig
elif [ -n "$pam_tally" ];then
	sed -i '2 a auth       required     pam_tally.so onerr=fail deny=5 unlock_time=120' $sshpamconfig
	sed -i '/auth.*pam_env.so/a\auth        required      pam_tally.so onerr=fail deny=5 unlock_time=120' $systemauthconfig
	sed -i '/account.*pam_unix.so/a\account     required      pam_tally.so' $systemauthconfig
fi

#3 modify passwd config"
sed -i '/PASS_MAX_DAYS/s/[0-9]\+/90/' $passwdconfig
sed -i '/PASS_MIN_DAYS/s/[0-9]\+/0/' $passwdconfig
sed -i '/PASS_MIN_LEN/s/[0-9]\+/8/' $passwdconfig
sed -i '/PASS_WARN_AGE/s/[0-9]\+/7/' $passwdconfig

#4 modify system-auth config
sed -i -e'/password.*pam_cracklib.so/a\password    requisite     pam_cracklib.so try_first_pass retry=5 difok=5 minlen=8 dcredit=-1 lcredit=-1 ocredit=-1 ucredit=-1' -i -e '/password.*pam_cracklib.so/{/try_first_pass/d}' $systemauthconfig

#5 modify system-auth config
sed -i -e '/password.*pam_unix.so/a\password    sufficient    pam_unix.so sha512 shadow nullok try_first_pass use_authtok  remember=3' -i -e '/password.*pam_unix.so/{/try_first_pass/d}' $systemauthconfig 

#6 匹配/etc/passwd文件与用户列表中相同的用户
cat /etc/passwd|awk -F ":" '{print $1}' > $linux_path/passwd.cfg
#对比两个文件，将相同内容输出到指定文件
grep -Ff $linux_path/passwd.cfg $linux_path/$linux_shell_name > $linux_path/comm.cfg
#去除文本中每行自带的换行符^M
sed -i 's/.$//' $linux_path/comm.cfg
#获取通过系统用户与列表中对比后相同的用户，然后执行登陆后修改密码，相隔90天后再次修改，提前一周进行提醒
list=`cat $linux_path/comm.cfg|awk '{print $1}'`
for user90 in $list
do
	chage -d 0 -m 0 -M 90 -W 7 $user90
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
rm -f $linux_path/comm.cfg