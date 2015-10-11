import paramiko


def ssh2(ip,username,passwd,cmd):
    try:
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(ip,22,username,passwd,timeout=5)
        for m in cmd:
            stdin, stdout, stderr = ssh.exec_command(m)
            #stdin.write("Y")
            out = stdout.readlines()
            for o in out:
                print o,
        print('%s\tOK\n'%(ip))
        ssh.close()
    except :
        print('%s\tError\n'%(ip))


if __name__=='__main__':
    cmd = ['sudo -i','id','sudo -i','id']
    username = "manager"
    passwd = "123456"
    ip="192.168.68.210"
    ssh2(ip,username,passwd,cmd)
