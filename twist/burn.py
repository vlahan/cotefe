#
# Copyright (c) 2006, Technische Universitaet Berlin
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# - Redistributions of source code must retain the above copyright notice,
#   this list of conditions and the following disclaimer.
# - Redistributions in binary form must reproduce the above copyright
#   notice, this list of conditions and the following disclaimer in the
#   documentation and/or other materials provided with the distribution.
# - Neither the name of the Technische Universitaet Berlin nor the names
#   of its contributors may be used to endorse or promote products derived
#   from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED
# TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
# OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE
# USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# Author: Andreas Koepke (koepke at tkn.tu-berlin.de)

import sys
import os
import re
import time

import pexpect
import difflib
import ConfigParser

from twisted.python import log, failure, util as tutil

config=ConfigParser.SafeConfigParser()
config.read(['/etc/twist/twist.cfg',
             os.path.expanduser('~/.twist/twist.cfg'),
             tutil.sibpath(__file__, '../twist.cfg'),
             tutil.sibpath(__file__, 'twist.cfg')])

wpath = config.get('web','tools_path')
lpath = config.get('web','temp_path')
nlist = config.get('web','node_list')
slist = config.get('web','slug_list')
ilist = config.get('web','image_list')
tuser = config.get('web','user') 
thost = config.get('web','host')
brlog = config.get('web','burn_log')

ruser = config.get('server','user')
if config.has_option('server','passphrase'):
    rpassph = config.get('server','passphrase')
else:
    rpassph=None
if config.has_option('server','password'):
    rpasswd = config.get('server','password')
else:
    rpasswd=None
rhost = config.get('server','host')
rpath = config.get('server','tools_path')
rconf = config.get('server','python_path')
rfile = config.get('server','result_file')
rtimeout = config.getint('server', 'timeout')

def timedCommand(cmd, timeout, successMsg, errorMsg, passph=None, passwd=None):
    try:
        child = pexpect.spawn(cmd)
        child.timeout=timeout
        while True:
            index=child.expect(['connecting (yes/no)?',
                                r'passphrase for key(.*):',
                                '[P|p]assword:'])
            if index==0: # accepting new RSA host keys
                child.sendline('yes') 
            elif index==1: # handling passphrase-based authentication
                if passph is not None:
                        child.sendline(passph)
                        break
                else:
                        child.sendline('\n') # move to password-based authentication
            elif index==2: # handling password based authentication
                if passwd is not None:
                    child.sendline(passwd)
                else:
                    break
    except pexpect.EOF:
        lines = child.before + successMsg + "\n"
        child.terminate(True)
        return lines, True
    except pexpect.TIMEOUT:   
        lines = child.before + errorMsg + " (time  out) \n"
        child.terminate(True)
        return lines, False
    except pexpect.ExceptionPexpect, exc:
        lines = child.before + errorMsg + exc + "\n"
        child.terminate(True)
        return lines, False

def copyFile(cfile):
    return timedCommand('scp ' + cfile + ' %s@%s' % (ruser, rhost) + ':' + rpath, 20, \
                        "copied " + cfile, "could not copy " + cfile, passwd=rpasswd)
        
def remoteBurn(rburncmd, action):
    return timedCommand('ssh -nxTA' + ' %s@%s ' % (ruser, rhost)  + rconf + \
                        " 'python "  + rpath + "/" + rburncmd + "'",
                        1.5*rtimeout, action + " done", action + " failed", passwd=rpasswd)
def checkSilentNodes():
    action = "Checking for silent nodes"
    return timedCommand('ssh -nxTA' + ' %s@%s ' % (ruser, rhost) + rconf + \
                        " 'python "  + rpath + "/silentFailure.py'",
                        60, action + " done", action + " failed", passwd=rpasswd)
def matchLine(line):
    sfRe = re.compile(r'(\d+) (\S+):(\d+)')
    sfMa = sfRe.match(line)
    match = False
    lport = 0
    rport = ""
    rhost = ""
    node = ''
    if sfMa:
        node = sfMa.group(1)
        lport = 9000 + int(sfMa.group(1))
        rhost = sfMa.group(2)
        rport = sfMa.group(3)
        match = True
    return match, node, lport, rhost, rport;

def tunnelUserLine(node, lport):
    return  'To forward SF e.g. for node ' + node + \
           ' use: ssh -nNxTL ' + str(lport) + \
           ':localhost:' +  str(lport) + ' %s@%s' % (tuser, thost)

def tunnelCmdLine(lport, rport, rhost):
    return wpath+'/tunnel.py ' + str(lport) + ' ' + rhost +  ' ' + rport

def createTunnels(mappedLines, tCreate):
    lines = ''
    try:
        for line in tCreate:
            (match, node, lport, rhost, rport) = matchLine(line)
            if(match):
                sshcmd = tunnelCmdLine(lport, rport, rhost)
                os.popen("nohup " + sshcmd + " &" )
                lines = lines + tunnelUserLine(node, lport) + ' # tunnel created\n'
    except OSError:
        lines = lines + 'OSError opening tunnels'
        return lines, False
    return lines, True

def readProcFS():
    matchPID = re.compile(r'/proc/(\d+)/cmdline')

    processes = []
    mappedLines = {}
    
    for entry in os.listdir("/proc"):
        pLine = "/proc/" + entry + "/cmdline"
        if os.path.exists(pLine):
            processes.append(pLine)

    for file in processes:
        consider = True
        try:
            pLine = open(file).readline()
        except IOError:
            consider = False

        if consider:
            pidm = matchPID.match(file)
            if(pidm):
                pid = pidm.group(1)
                mappedLines[pLine] = pid
            else:
                pid = ""
    return mappedLines

def findPID(mappedLines, sshcmd):
    found = False
    pid = 0    
    matchSfstr = sshcmd.replace(' ', '.*')
    matchSf = re.compile(matchSfstr)
    for pLine in mappedLines.keys():
        sfm = matchSf.search(pLine)
        if sfm:
            found = True
            pid = mappedLines[pLine]
    return found, pid

def keepTunnels(mappedLines, tKeep):
    lines = ''
    tCreate = []
    for line in tKeep:
        (match, node, lport, rhost, rport) = matchLine(line)
        if(match):
            (found, pid) = findPID(mappedLines, tunnelCmdLine(lport, rport, rhost))
            if(found):
                lines = lines + tunnelUserLine(node, lport) + ' # tunnel kept\n'
            else:
                tCreate.append(line)
    li, res = createTunnels(mappedLines, tCreate)
    return lines + li, True

def killTunnels(mappedLines, tKill):
    lines = ''
    for line in tKill:
        (match, node, lport, rhost, rport) = matchLine(line)
        if(match):
            (found, pid) = findPID(mappedLines, tunnelCmdLine(lport, rport, rhost))
            if(found):
                try:
                    kill = os.popen("kill %s 1>/dev/null 2>/dev/null" % pid)
                    kill.close()
                    lines = lines + tunnelUserLine(node, lport) + ' # tunnel killed\n'
                except OSError:
                    lines = lines + "trouble killing SF tunnel "  + tunnelUserLine(node, lport)

    return lines, True
    
def getTunnelFile():
    return timedCommand('scp ' + ' %s@%s' % (ruser, rhost) + ':' + rpath + '/' + rfile + ' .', 20, \
                        "retrieved information on tunnels", \
                        "could not retrieve information on tunnels")

def openTunnels():
    rNew = ""
    rOld = ""
    tKill = []
    tCreate = []
    tKeep = []
    result = ""
    lines = ""
    try:
        if os.path.exists(rfile):
            resfileOld = open(rfile)
        else:
            resfileOld = open(rfile, 'w+')
        rOld = resfileOld.readlines()
        resfileOld.close()
    except IOError:
        lines = lines + 'IOError opening ssh tunnels'
        return lines, False
    except OSError:
        lines = lines + 'OSError opening ssh tunnels'
        return lines, False
    
    li, res = getTunnelFile()
    if res == False:
        return li, res
    
    d = difflib.Differ()
    try:
        resfile = open(rfile,'r')
        rNew = resfile.readlines()
        resfile.close()
    except IOError:
        lines = lines + 'IOError opening ssh tunnels'
        return lines, False
    except OSError:
        lines = lines + 'OSError opening ssh tunnels'
        return lines, False
    
    for line in d.compare(rOld, rNew):
        if line[:2] == '- ':
            tKill.append(line[2:])
        elif line[:2] == '  ':
            tKeep.append(line[2:])
        elif line[:2] == '+ ':
            tCreate.append(line[2:])

    mappedLines = readProcFS()

    li, res = killTunnels(mappedLines, tKill)
    if(res == False):
        return lines+li, res
    else:
        lines = lines + li

    li, res = keepTunnels(mappedLines, tKeep)
    if(res == False):
        return lines+li, res
    else:
        lines = lines + li

    li, res = createTunnels(mappedLines, tCreate)
    if(res == False):
        return lines + li, res
    else:
        lines = lines + li
        
    return lines, True

def convertAction(action):
    rburncmd = 'zerokit.py '
    if action == 'Install':
        rburncmd = rburncmd + ' install '
    elif action == 'Reset':
        rburncmd = rburncmd + ' reset '
    elif action == 'Erase':
        rburncmd = rburncmd + ' erase '
    elif action == 'Power down':
        rburncmd = rburncmd + ' power_off '
    elif action == 'Power up':
        rburncmd = rburncmd + ' power_on '
    elif action == 'Start SF':
        rburncmd = rburncmd + ' start_sforwarders '
    elif action == 'Stop SF':
        rburncmd = rburncmd + ' stop_sforwarders '
    else:
        rburncmd = rburncmd + ' default '
    return rburncmd

def countInstalled(lines):
    stageRe = re.compile(r'.*installed.*')
    count = 0
    for line in lines.splitlines():
        stageMa = stageRe.search(line)
        if(stageMa):
            count = count + 1
    return 'Action "install" has been performed on %s nodes \n' % str(count)

def burn(action, credentials=None):
    imLineRe = re.compile(r'ELF 32-bit LSB executable')
    lines = ""
    logfile=open(brlog,'a')
    tstart = time.time()    
    
    logfile.write(time.strftime("%Y/%m/%d %H:%M")+' Will copy files\n')
    logfile.flush()
    for i in range(1,6):
        nl = lpath + '/' + nlist + str(i)
        im = lpath + '/' + ilist + str(i)
        
        if os.path.exists(im):
            try:
                check = os.popen('file ' + im)
                for line in check:
                    imLineMa = imLineRe.search(line)
                    if imLineMa:
                        li, res = copyFile(im)
                        if res == False:
                            logfile.write(time.strftime("%Y/%m/%d %H:%M")+' Copy files failed\n' +  li)
                            logfile.flush()
                            print 'Copying image files...\n'
                            print li
                check.close()
            except OSError:
                print 'Could not check file ' + im

        if os.path.exists(nl) and os.stat(nl)[6] > 5:
            li, res = copyFile(nl)
            if res == False:
                logfile.write(time.strftime("%Y/%m/%d %H:%M")+' Copy files failed\n' +  li)
                logfile.flush()
                print 'Copying node job files...\n'
                print li

    slugFile = lpath + '/' + slist
    if os.path.exists(slugFile) and os.stat(slugFile)[6] > 1:
        li, res = copyFile(slugFile)
        if res == False:
            logfile.write(time.strftime("%Y/%m/%d %H:%M")+' Copy files failed\n' +  li)
            logfile.flush()
            print 'Copying supernode job files...\n'
            print li
            
    logfile.write(time.strftime("%Y/%m/%d %H:%M")+' Copied Files\n')
    logfile.flush()

    li, res = remoteBurn(convertAction(action), action)
    lines = lines + li
    if res == False:
        logfile.write(time.strftime("%Y/%m/%d %H:%M")+' remote %s failed\n' %action + li)
        logfile.close()
        print 'Executing remote actions...\n'
        print li
        return lines

    lines = lines + countInstalled(lines)
        
    logfile.write(time.strftime("%Y/%m/%d %H:%M")+' remote %s done\n' %action + li)
    logfile.flush()

    li, res = checkSilentNodes()
    lines = lines + li
    if res == False:
        logfile.write(time.strftime("%Y/%m/%d %H:%M")+' check for silent nodes failed\n'  + li)
        logfile.close()
        print 'Executing silent node check...\n'
        print li
        return lines
    logfile.write(time.strftime("%Y/%m/%d %H:%M")+' done check for silent nodes \n')
    logfile.flush()
    lines = lines + tunnelUserLine(str(10), 9010) + "\nElapsed Time: "+str(time.time()-tstart)+" [s]\n"
#   li, res = openTunnels()
#     lines = lines + li
#     if res == False:
#         logfile.write(time.strftime("%Y/%m/%d %H:%M")+' tunnels failed\n'  + li)
#         logfile.close()
#         print 'Executing data tunnel opening...\n'
#         print li
#         return lines
#     logfile.write(time.strftime("%Y/%m/%d %H:%M")+' Done open Tunnels\n')
#     logfile.flush()
    logfile.close()
    return lines

if __name__ == "__main__":
    print burn(sys.argv[1])
