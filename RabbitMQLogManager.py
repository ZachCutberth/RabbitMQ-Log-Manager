#! python3
# RabbitMQLogManager
# Version 1.0
# By Zach Cutberth

# Rotates and deletes RabbitMQ log files before they become too large and impact system performance.

from time import sleep
from subprocess import Popen
from os import stat
from os import remove
from glob import glob
from sys import exit
import winreg
import datetime

# Setup timestamp for later use.
timestamp = datetime.datetime.now().strftime("%D %H:%M:%S")

# Open the key and return the handle object.
rabbitMQLogHKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                          "Software\\Wow6432Node\\Ericsson\\Erlang\\ErlSrv\\1.1\\RabbitMQ")
                          
# Read the value.                      
rabbitMQLogInstallDir = winreg.QueryValueEx(rabbitMQLogHKey, "WorkDir")
winreg.CloseKey(rabbitMQLogHKey)

# Open the key and return the handle object.
rabbitMQServerHKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, 
                          "Software\\Wow6432Node\\VMware, Inc.\\RabbitMQ Server")
                          
# Read the value.                      
rabbitMQServerInstallDir = winreg.QueryValueEx(rabbitMQServerHKey, "Install_Dir")
winreg.CloseKey(rabbitMQServerHKey)
        
# Get the size of the log file and see if it's over 10 mb.
def checkLogSize():
    for file in glob(rabbitMQLogInstallDir[0] + '\log\*.log'):
        logFileSize = stat(file)
        logFileSizeMB = logFileSize.st_size / 1000000 
        print(timestamp + ' Log file size is ' + str(logFileSizeMB) + ' megabytes.', flush=True)
        if logFileSize.st_size > 10000000:
            return logFileSize.st_size / 1000000

# Run the RabbitMQ batch file to rotate the log file.
def rotateLog():
    sbinDir = glob(rabbitMQServerInstallDir[0] + '\\rabbitmq_server*' + '\\sbin\\')
    Popen('rabbitmqctl rotate_logs .old', cwd=sbinDir[0], shell=True).communicate()

# Delete the rotated log file with the *.old extention.
def deleteRotatedLog():
    for filename in glob(rabbitMQLogInstallDir[0] + '\log\*.old'):
        remove(filename)

if __name__ == '__main__':
    try:
        while True:
            # Clean up any rotated log files that were not deleted for some reason.
            deleteRotatedLog()

            # Check if logSize is None. If it is set it to 0, so we don't get a type error later.
            logSize = checkLogSize()
            if logSize is None:
                logSize = 0

            # If the log size is > 10mb rotate and delete the log files.
            if logSize > 10:
                print(timestamp + ' Log files need to be rotated.', flush=True)
                rotateLog()
                print(timestamp + ' Log files rotated.', flush=True)
                deleteRotatedLog()
                print(timestamp + ' Old log files deleted.', flush=True)
                print(timestamp + ' Sleeping for one hour.', flush=True)
                # Sleep for 1 hour.
                sleep(3600)
            else:
                print(timestamp + ' Logs do not need to be rotated.', flush=True)
                print(timestamp + ' Sleeping for one hour.', flush=True)
                # Sleep for 1 hour.
                sleep(3600)

    # If there is a keyboard interrupt (ctrl-c) exit the script.
    except KeyboardInterrupt:
        print(timestamp + ' Keyboard Interrupt Signaled!', flush=True)
        exit()
