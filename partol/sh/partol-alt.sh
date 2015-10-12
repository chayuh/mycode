#!/bin/bash
rc_local=/etc/rc.d/rc.local
bakdir=/tmp/bak
if [ ! -d "$bakdir" ]; then 
	mkdir -p $bakdir
fi 
ip=$1
#backup configure files
if [ ! -f "$rc_local.bak" ];then
	cp -p $rc_local $rc_local.bak
fi
#bakcup to another dir
if [ ! -f "$bakdir/rc.local" ];then
	cp -p $rc_local $bakdir/.
fi
#add shell script to rc.local
flag=`cat $rc_local |grep -e "/bin/sh /home/patrol/Patrol3/PatrolAgent -id $ip"`
if [[ ! -n "$flag" ]];then
	sed -i '$a /bin/sh /home/patrol/Patrol3/PatrolAgent -id '$ip'' $rc_local
fi
#print modify log
echo "======================================================================"
echo "                         modified $rc_local                           "
echo "======================================================================"
cat $rc_local |grep -e "/bin/sh /home/patrol/Patrol3/PatrolAgent -id $ip"
echo "======================================================================"

