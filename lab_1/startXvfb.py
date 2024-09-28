#!/usr/bin/env python

# Wrapper for Xvfb. Works on UNIX only. Main points are as follows :
# - Provide a unique display ID by using our own process ID
# - Get Xvfb to ignore job control signals properly 
# - Handle Xvfb's weird mechanism whereby it sends SIGUSR1 to its parent process
#   every time a process disconnects. If the parent process is TextTest there is no
#   way to tell these signals from ordinary job control
# - Clean up after Xvfb as it leaks lock files from time to time.

import os
import signal
import subprocess
import sys
from socket import gethostname

MAX_DISPLAY = 32768
Xvfb_ready = False


class ConnectionComplete:
    pass


class ConnectionTimeout:
    pass
    

def setReadyFlag(self, *args):  # pragma: no cover - only here to deal with pathological and probably impossible race condition
    """
    Sets the global Xvfb_ready flag when the SIGUSR1 signal is received.
    """
    global Xvfb_ready
    Xvfb_ready = True


def connectionComplete(self, *args):
    """
    Signal handler to raise a ConnectionComplete exception.
    """
    raise ConnectionComplete()


def connectionFailed(self, *args):
    """
    Signal handler to raise a ConnectionTimeout exception when the SIGALRM signal is received.
    """
    raise ConnectionTimeout()


def ignoreSignals():
    """
    Ignores specific signals (SIGUSR1, SIGUSR2, SIGXCPU) to prevent Xvfb from interfering with the parent process when it sends signals during its lifetime.
    """
    for signum in [ signal.SIGUSR1, signal.SIGUSR2, signal.SIGXCPU ]:
        signal.signal(signum, signal.SIG_IGN)


def getDisplayNumber():
    """
    Generates a display number for Xvfb using the process ID modulo 32768.
    """
    # We use the device of making the display number match our process ID (mod 32768)!
    # And we hope that works :) Should prevent clashes with others using the same strategy anyway
    # Display numbers up to 32768 seem to be allowed, which is less than most process IDs on systems I've observed...
    return str(os.getpid() % MAX_DISPLAY)


def getLockFiles(num):
    """
    Constructs paths to lock files associated with a given display number.
    Args:
        num (str): The display number.
    """
    lockFile = "/tmp/.X" + num + "-lock"
    xFile = "/tmp/.X11-unix/X" + num
    return [ lockFile, xFile ]


def cleanLeakedLockFiles(displayNum):
    """
    Cleans up any lock files left behind by Xvfb, which sometimes fails to remove them.
    Args:
        displayNum (str): The display number whose lock files need to be cleaned.
    """
    # Xvfb sometimes leaves lock files lying around, clean up
    for lockFile in getLockFiles(displayNum):
        if os.path.isfile(lockFile):
            try:
                os.remove(lockFile)
            except:  # pragma: no cover - pathological case of ending up in race condition with Xvfb
                pass


def writeAndWait(text, proc, displayNum):
    """
    Writes output to stdout and waits for the Xvfb process to finish, then cleans up.
    Args:
        text (str): The text to write to stdout.
        proc (Popen): The Xvfb subprocess.
        displayNum (str): The display number associated with the Xvfb instance.
    """
    ignoreSignals()
    sys.stdout.write(text + "\n")
    sys.stdout.flush()
    proc.wait()
    cleanLeakedLockFiles(displayNum)


def runXvfb(logDir, extraArgs):
    """
    Runs the Xvfb process with the specified arguments and handles signal-based readiness.
    Args:
        logDir: The directory where the Xvfb log file will be stored.
        extraArgs: Additional arguments to pass to the Xvfb command.
    """
    ignoreSignals()
    signal.signal(signal.SIGUSR1, setReadyFlag)
    displayNum = getDisplayNumber()
    logFile = os.path.join(logDir, "Xvfb." + displayNum + "." + gethostname())
    startArgs = [ "Xvfb", "-ac" ] + extraArgs + [ "-audit", "2", ":" + displayNum ]
    proc = subprocess.Popen(startArgs, 
                            preexec_fn=ignoreSignals,
                            stdout=open(logFile, "w"), 
                            stderr=subprocess.STDOUT, 
                            stdin=open(os.devnull))
    try:
        signal.signal(signal.SIGUSR1, connectionComplete)
        signal.signal(signal.SIGALRM, connectionFailed)
        if not Xvfb_ready:
            signal.alarm(int(os.getenv("TEXTTEST_XVFB_WAIT", 15)))  # Time to wait for Xvfb to set up connections
            signal.pause() 
    except ConnectionTimeout:
        # Kill it and tell TextTest we timed out. It will then start a new startXvfb.py process, with a new process ID
        # that will hopefully work better
        os.kill(proc.pid, signal.SIGTERM)
        return writeAndWait("Time Out!", proc, displayNum)
    except ConnectionComplete:
        signal.alarm(0)  # cancel any alarms that were previously set up!

    writeAndWait(displayNum + "," + str(proc.pid), proc, displayNum)
    
    
if __name__ == "__main__":
    """
    Main entry point for running the Xvfb wrapper script.
    """
    runXvfb(sys.argv[1], sys.argv[2:])