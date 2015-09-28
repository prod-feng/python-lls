# python-lls

This is tool that can retrive all the related processes that one want to list.

With use's input of a process id, it will find all the child and parent processes, include processes in the same sessions.

The output format uses command "ps", shows in tree mode, which looks as following.

$./lls.py 24283 
  PID  PPID   SID  PGRP   GID   TID  NI USER     %CPU STAT COMMAND
    1     0     1     1     0     1   0 root      0.0 Ss   /sbin/init
20766     1 20766 20766     0 20766   0 root      0.0 Ss   /usr/sbin/sshd -4
24278 20766 24278 24278     0 24278   0 root      0.0 Ss    \_ sshd: xxx [priv]   
24282 24278 24278 24278  1008 24282   0 xxx      0.0 S         \_ sshd: xxx@pts/0    
24283 24282 24283 24283  1008 24283   0 xxx      0.0 Ss            \_ -bash
25602 24283 24283 25602  1008 25602   0 xxx      0.2 S+                \_ vim lls.py
$ 

Developed on CentOS 6.2, Kernel 2.6.32-220.2.1.el6.x86_64, Python 2.6.6.
