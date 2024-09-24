#!/usr/bin/env python

import os
import sys
import subprocess

from tempfile import mktemp


def interpretCore(corefile):
    """
    Interprets the core file to extract stack trace information.
    Args:
        corefile: The path to the core file.
    """
    if os.path.getsize(corefile) == 0:
        details = "Core file of zero size written - Stack trace not produced for crash\nCheck your coredumpsize limit"
        return "Empty core file", details, None
    
    binary = getBinary(corefile)
    if not os.path.isfile(binary):
        details = "Could not find binary name '" + binary + "' from core file : Stack trace not produced for crash"
        return "No binary found from core", details, None

    summary, details = writeGdbStackTrace(corefile, binary)
    if "Parse failure" in summary:
        try:
            dbxSummary, dbxDetails = writeDbxStackTrace(corefile, binary)
            if "Parse failure" in dbxSummary:
                return "Parse failure from both GDB and DBX", details + dbxDetails, binary
            else:
                return dbxSummary, dbxDetails, binary
        except OSError:
            pass  # If DBX isn't installed, just return the GDB details anyway
    return summary, details, binary


def getLocalName(corefile):
    """
    Determine the binary file name from the core file.
    Args:
        corefile: The path to the core file.
    """
    data = os.popen("file " + corefile).readline()
    parts = data.split("'")
    if len(parts) == 3:
        return parts[1].split()[0]  # don't pass arguments along, only want program name
    else:
        newParts = data.split()
        if len(newParts) > 2 and newParts[-2].endswith(","):
            # AIX...
            return newParts[-1]
        else:
            return ""


def getLastFileName(corefile):
    """
    Extracts the last valid binary file name.
    Args:
        corefile: The path to the core file.
    """
    # Yes, we know this is horrible. Does anyone know a better way of getting the binary out of a core file???
    # Unfortunately running gdb is not the answer, because it truncates the data...
    localName = getLocalName(corefile)
    if os.path.isfile(localName):
        return localName

    localRegexp = localName 
    if not os.path.isabs(localName):
        localRegexp = "/.*/" + localName

    possibleNames = os.popen("strings " + corefile + " | grep '^" + localRegexp + "'").readlines()
    possibleNames.reverse()
    for name in possibleNames:
        name = name.strip()
        if os.path.isfile(name):
            return name
    # If none of them exist, return the first one anyway for error printout
    if len(possibleNames) > 0:
        return possibleNames[0].strip()
    else:
        return ""
    

def getBinary(corefile):
    """
    Retrieves the binary associated with the core file.
    Args:
        corefile: The path to the core file.
    """
    binary = getLastFileName(corefile)
    if os.path.isfile(binary):
        return binary
    dirname, local = os.path.split(binary)
    parts = local.split(".")
    # pick up temporary binaries (Jeppesen-hack, should not be here...)
    if len(parts) > 2 and len(parts[0]) == 0:
        user = os.getenv("USER")
        try:
            pos = parts.index(user)
            return os.path.join(dirname, ".".join(parts[1:pos]))
        except ValueError:
            pass
    return binary


def writeCmdFile():
    """
    Creates a temporary GDB command file.
    """
    fileName = mktemp("coreCommands.gdb")
    file = open(fileName, "w")
    file.write("bt\n")
    file.close()
    return fileName


def parseGdbOutput(output):
    """
    Parses the output from GDB to extract stack trace information.
    Args:
        output (str): The output from GDB.
    """
    summaryLine = ""
    signalDesc = ""
    stackLines = []
    prevLine = ""
    stackStarted = False
    for line in output.splitlines():
        if line.find("Program terminated") != -1:
            summaryLine = line.strip()
            signalDesc = summaryLine.split(",")[-1].strip().replace(".", "")
        if line.startswith("#"):
            stackStarted = True
        if stackStarted and line != prevLine:
            methodName = line.rstrip()
            startPos = methodName.find("in ")
            if startPos != -1:
                methodName = methodName[startPos + 3:]
                stackLines.append(methodName)
            else:
                stackLines.append(methodName)
        prevLine = line
        
    if len(stackLines) > 1:
        signalDesc += " in " + getGdbMethodName(stackLines[0])
    return signalDesc, summaryLine, stackLines    


def parseDbxOutput(output):
    """
    Parses the output from DBX to extract stack trace information.
    Args:
        output (str): The output from DBX.
    """
    summaryLine = ""
    signalDesc = ""
    stackLines = []
    prevLine = ""
    for line in output.splitlines():
        stripLine = line.strip()
        if line.find("program terminated") != -1:
            summaryLine = stripLine
            signalDesc = summaryLine.split("(")[-1].replace(")", "")
        if (stripLine.startswith("[") or stripLine.startswith("=>[")) and line != prevLine:
            startPos = line.find("]") + 2
            endPos = line.rfind("(")
            methodName = line[startPos:endPos]
            stackLines.append(methodName)
        prevLine = line

    if len(stackLines) > 1:    
        signalDesc += " in " + stackLines[0].strip()
    return signalDesc, summaryLine, stackLines    


def getGdbMethodName(line):
    """
    Extracts the method name from a GDB stack trace line.
    Args:
        line (str): A line from the GDB stack trace.
    """
    endPos = line.rfind("(")
    methodName = line[:endPos]
    pointerPos = methodName.find("+0")
    if pointerPos != -1:
        methodName = methodName[:pointerPos]
    return methodName.strip()


def parseFailure(errMsg, debugger):
    """
    Handles the parsing failure of GDB or DBX output.
    Args:
        errMsg (str): The error message from the debugger.
        debugger (str): The debugger being used (GDB or DBX).
    """
    summary = "Parse failure on " + debugger + " output"
    if len(errMsg) > 50000:
        return summary, "Over 50000 error characters printed - suspecting binary output"
    else:
        return summary, debugger + " backtrace command failed : Stack trace not produced for crash\nErrors from " + debugger + ":\n" + errMsg


def assembleInfo(signalDesc, summaryLine, stackLines, debugger):
    """
    Assembles the stack trace information into a formatted summary and details.
    Args:
        signalDesc (str): The signal description.
        summaryLine (str): The summary line from the debugger.
        stackLines (list): The list of stack trace lines.
        debugger (str): The debugger used (GDB or DBX).
    """
    summary = signalDesc
    details = summaryLine + "\nStack trace from " + debugger + " :\n" + \
              "\n".join(stackLines[:100])
    # Sometimes you get enormous stacktraces from GDB, for example, if you have
    # an infinite recursive loop.
    if len(stackLines) > 100:
        details += "\nStack trace print-out aborted after 100 function calls"
    return summary, details


def writeGdbStackTrace(corefile, binary):
    """
    Generates the stack trace using GDB.
    Args:
        corefile (str): The path to the core file.
        binary (str): The path to the binary file.
    """
    fileName = writeCmdFile()
    cmdArgs = [ "gdb", "-q", "-batch", "-x", fileName, binary, corefile ]
    proc = subprocess.Popen(cmdArgs, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, errors = proc.communicate()
    signalDesc, summaryLine, stackLines = parseGdbOutput(output)
    os.remove(fileName)
    if summaryLine:
        return assembleInfo(signalDesc, summaryLine, stackLines, "GDB")
    else:
        return parseFailure(errors, "GDB")


def writeDbxStackTrace(corefile, binary):
    """
    Generates the stack trace using DBX.
    Args:
        corefile (str): The path to the core file.
        binary (str): The path to the binary file.
    """
    cmdArgs = [ "dbx", "-f", "-q", "-c", "where; quit", binary, corefile ]
    proc = subprocess.Popen(cmdArgs, 
                            stdin=open(os.devnull), 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE)
    output, errors = proc.communicate()
    signalDesc, summaryLine, stackLines = parseDbxOutput(output)
    if summaryLine:
        return assembleInfo(signalDesc, summaryLine, stackLines, "DBX")
    else:
        return parseFailure(errors, "DBX")


def printCoreInfo(corefile):
    """
    Prints the core file information and stack trace.
    Args:
        corefile (str): The path to the core file.
    """
    compression = corefile.endswith(".Z")
    if compression:
        os.system("uncompress " + corefile)
        corefile = corefile[:-2]
    summary, details, binary = interpretCore(corefile)
    print summary
    print "-" * len(summary)
    print "(Core file at", corefile + ")"
    if binary:
        print "(Created by binary", binary + ")"
    print details
    if compression:
        os.system("compress " + corefile)


if len(sys.argv) != 2:
    print "Usage: interpretcore.py <corefile>"
else:
    corefile = sys.argv[1]
    if os.path.isfile(corefile):
        printCoreInfo(corefile)
    else:    
        sys.stderr.write("File not found : " + corefile + "\n")