#!/bin/bash
sudofile=/etc/sudoers
bakdir=/tmp/bak
if [ ! -d "$bakdir" ]; then 
	mkdir -p $bakdir
fi 
add_admin_user=$1
add_db_user=$2
#backup configure files
if [ ! -f "$sudofile.bak" ];then
	cp -p $sudofile $sudofile.bak
else 
	rm -f $sudofile.bak
	cp -p $sudofile $sudofile.bak
fi
#bakcup to another dir
if [ ! -f "$bakdir/sudoers" ];then
	cp -p $sudofile $bakdir/.
else
	rm -f $bakdir/sudoers
	cp -p $sudofile $bakdir/.
fi
#Declare Variable
user=`cat $sudofile |grep -i "^User_Alias ADMINS"`
group=`cat $sudofile |grep -i "^User_Alias DBA"`
admins=`cat $sudofile |grep -i "^ADMINS.*ALL=(ALL).*NOPASSWD:ALL"`
dba=`cat $sudofile |grep -i "^DBA.*ALL=NOPASSWD:"`
admin_user_sum=`cat $sudofile |grep "^User_Alias ADMINS"|awk -F"=" '{print NF}'`
admin_user_name=`cat $sudofile |grep "^User_Alias ADMINS"|awk -F"=" '{print $2}'`
db_user_sum=`cat $sudofile |grep "^User_Alias DBA"|awk -F"=" '{print NF}'`
db_user_name=`cat $sudofile |grep "^User_Alias DBA"|awk -F"=" '{print $2}'`	
a=`cat $sudofile|grep '^User_Alias ADMINS'|grep -o "$add_admin_user"|wc -l`
if [ $a -eq 0 ];then
	if [[ -n $add_admin_user ]];then
		if [[ ! -n $user ]];then
			sed -i '$a User_Alias ADMINS = ' $sudofile
			sed -i '/^User_Alias ADMINS/s/$/'$add_admin_user'/' $sudofile
		elif [[ $admin_user_sum -eq 2 ]];then
				if [[ -n $admin_user_name ]];then
					sed -i '/^User_Alias ADMINS/s/$/,'$add_admin_user'/' $sudofile
				else
					sed -i '/^User_Alias ADMINS/s/$/'$add_admin_user'/' $sudofile
				fi
		elif [[ $admin_user_sum -gt 2 ]];then 
				sed -i '/^User_Alias ADMINS/s/$/,'$add_admin_user'/' $sudofile
		fi
		if [[ ! -n $admins ]];then
			sed -i '/^User_Alias ADMINS/a\ADMINS    ALL=(ALL)	NOPASSWD:ALL' $sudofile	 
		fi
	fi
fi
b=`cat $sudofile|grep '^User_Alias DBA'|grep -o "$add_db_user"|wc -l`
if [ $b -eq 0 ];then
	if [[ -n $add_db_user ]];then
		if [[ ! -n $group ]];then
			sed -i '$a User_Alias DBA = ' $sudofile
			sed -i '/^User_Alias DBA/s/$/'$add_db_user'/' $sudofile
		elif [[ $db_user_sum -eq 2 ]];then
				if [[  -n $db_user_name ]];then
					sed -i '/^User_Alias DBA/s/$/,'$add_db_user'/' $sudofile
				else
					sed -i '/^User_Alias DBA/s/$/'$add_db_user'/' $sudofile
				fi
		elif [[ $db_user_sum -gt 2 ]];then 
				sed -i '/^User_Alias DBA/s/$/,'$add_db_user'/' $sudofile
		fi	
		if [[ ! -n $dba ]];then
			sed -i '/^User_Alias DBA/a\DBA      ALL=NOPASSWD:/bin/su *oracle*,/bin/su *grid*' $sudofile	 
		fi
	fi
fi
#print modify log
echo "======================================================================"
echo "                         show /etc/passwd                           "
echo "======================================================================"
cat /etc/passwd
echo "======================================================================"
echo "                         modified $sudofile                           "
echo "======================================================================"
cat $sudofile |grep -e "^User_Alias ADMINS"
cat $sudofile |grep -e "^ADMINS.*ALL=(ALL).*NOPASSWD:ALL"
cat $sudofile |grep -e "^User_Alias DBA"
cat $sudofile |grep -e "^DBA.*ALL=NOPASSWD"
echo "======================================================================"

