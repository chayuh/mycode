#!/bin/bash
rc_local=/etc/rc.d/rc.local
bakdir=/tmp/bak

mv -f $rc_local.bak $rc_local

#print modify log
echo "======================================================================"
echo "                         modified $rc_local                           "
echo "======================================================================"
cat $rc_local |grep -e "/bin/sh /home/patrol/Patrol3/PatrolAgent -id $ip"
echo "======================================================================"