#!/usr/bin/python
#
###
#Feng: Oct 12 2015. Add  Find_Child_Process().
import struct, socket
import errno
import os
import re
import array


Proc_Stat_Keys=[
              "pid",
              "comm",
              "state",
              "ppid",
              "pgrp",
              "session",
              "tty_nr",
              "tpgid",
              "flags",
              "minflt",
              "cminflt",
              "majflt",
              "cmajflt",
              "utime",
              "stime",
              "cutime",
              "cstime",
              "priority",
              "nice",
              "num_threads",
              "itrealvalue",
              "starttime",
              "vsize",
              "rss",
              "rsslim",
              "startcode",
              "endcode",
              "startstack",
              "kstkesp",
              "kstkeip",
              "signal",# Obsolete,  because it does not provide information on real-time signals; use /proc/[pid]/status instead.
              "blocked",# Obsolete
              "sigignore",# Obsolete 
              "sigcatch",# Obsolete
              "wchan",
              "nswap",
              "cnswap",
              "exit_signal",
              "processor",
              "rt_priority",
              "policy",
              "delayacct_blkio_ticks",
              "guest_time",
              "cguest_time"

]
debug = 0
class ProcInfo(object):
  """
  Module for retrieving pcocess info.
  """
  def __init__(self):
    self.name = "Proc_Info"
    self.Proc_Info = []

    self.sorted_session_list = []

    self.sorted_session_dict = {}

    self.result_proc_list = []
    # Get all processes
    self.Find_tgids()


  def Find_tgids(self):
      # find all process(thread group) IDs first.
      self.arr_tgids = [int(tgid) for tgid in os.listdir('/proc') if re.match(r'[0-9]+', tgid)] 

      # find all the thread IDs
      self.tids = []
      for tgid in self.arr_tgids:
         try:
            self.tids.extend(map(int, os.listdir('/proc/' + str(tgid) + '/task')))
         except OSError:
            pass
      #Only process now
      for tgid in self.arr_tgids:
         var = self.Get_Proc_stat(tgid)
         attrs = dict(zip(Proc_Stat_Keys, var))
         self.Proc_Info.append(attrs)

      # sort the list according Session IDs     
      sortlist = sorted(self.Proc_Info, key=lambda procs: int(procs["session"]))

      last_session=0 
      for proc in sortlist:
      # build simpified proc-session list
      #  or in self.Proc_Info without sorting
         pid=int(proc["pid"])
         ppid=int(proc["ppid"])
         session=int(proc["session"])
         
         if(ppid == 0 or pid == session or session != last_session):
             last_session = session
             self.sorted_session_dict[str(session)] = [[pid,ppid,session]]
             if debug > 0: print "found new session", pid,ppid,session
         elif(session == last_session):
             self.sorted_session_dict[str(session)].append([pid,ppid,session])
             if debug > 0: print "found child processes in session", pid,ppid,session
         else:
             print "found phantom process", pid,ppid,session
             
  @staticmethod 
  def Get_Proc_stat(tid):
      # find the /proc/[pid]/stat info.
      var = []
      try:
        for line in open('/proc/%d/stat' % tid):
            var = var + line.split(" ")
      except IOError:
        var = []  
      return var

  def Find_tids(self, tgid):
      # find all the threads ids of a process/tgid.
      try:
          tids = list(map(int, os.listdir('/proc/%d/task' % tgid)))
      except OSError:
          return []
      return tids

  @staticmethod
  def Find_Process_Family(exp,session_id):
      found = -1
      mykey = "-1"
      for key in exp.sorted_session_dict:
          if((session_id) == int(key)):
             found = 1
             if debug >0: print "Found session ",key, exp.sorted_session_dict[key]
             exp.result_proc_list += exp.sorted_session_dict[key] 
             break
      # Try to find parent process using  PPID, in case PID!=SESSION ID
      if(found < 0):
        for key in exp.sorted_session_dict:
          process_session_list = exp.sorted_session_dict[key]
          for pidlist in process_session_list:
             if(session_id == (pidlist[0])):
                found = 1
                mykey = str(pidlist[2])
                if debug >0: print "Found ppid ",process_session_list
                exp.result_proc_list += process_session_list 
                break
          if(found == 1): break
      if (int(mykey)>=0): key = mykey
      # OK, no process
      if(found < 0):
         print "Cannt find process ", session_id,"!"
         exit()
      session_leader_pid = exp.sorted_session_dict[key][0][0]
      ppid = exp.sorted_session_dict[key][0][1]
      if (int(ppid) == 0):
          return
      ProcInfo.Find_Process_Family(exp,ppid)

  @staticmethod
  def Find_Child_Process(exp,process_id):
      found = -1
      for key in exp.sorted_session_dict:
        process_session_list = exp.sorted_session_dict[key]
        for pidlist in process_session_list:
          if(process_id == (pidlist[1])):
             found = 1
             mykey = str(pidlist[2])
             if debug > 0: print "Found child process ",process_session_list
             exp.result_proc_list += process_session_list
             break
        if(found == 1): break 
      if( debug > 0 and found == 1 and len(process_session_list) > 1):
         print "Fount children processes ",process_session_list
      if(found < 0): return
      pid = process_session_list[1][0]
      ProcInfo.Find_Child_Process(exp,pid)

if __name__ == '__main__':
   import sys
   process = -1
   if len(sys.argv) > 1 and sys.argv[1] > 0:
      process = sys.argv[1]
      #Find the session ID of this process
      session_id = ProcInfo.Get_Proc_stat(int(process))[5]
      if debug > 0: print "process: ",process, session_id
 
      found = -1
      #Find session leader process ID
      # Init the process list
      exp = ProcInfo()

      #Search parent processes IDs
      ProcInfo.Find_Process_Family(exp,int(session_id))
      ProcInfo.Find_Child_Process(exp,int(process))
      proc_list = ""
      for proc in exp.result_proc_list:
         proc_list = proc_list + " "+str(proc[0])

      if debug >= 0: print "proc_list ",proc_list
      os.system("ps  f -o pid,ppid,sid,pgrp,gid,tid,nice,uname,pcpu,stat,command "+proc_list)
