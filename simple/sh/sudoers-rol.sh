#!/bin/bash
sudofile=/etc/sudoers
bakdir=/tmp/bak

mv -f $sudofile.bak $sudofile

#print modify log
echo "======================================================================"
echo "                         modified $sudofile                           "
echo "======================================================================"
cat $sudofile |grep -e "User_Alias ADMINS"
cat $sudofile |grep -e "ADMINS.*ALL=(ALL).*NOPASSWD:ALL"
cat $sudofile |grep -e "User_Alias DBA"
cat $sudofile |grep -e "DBA.*ALL=NOPASSWD"
echo "======================================================================"