#!/usr/bin/env python2.7

import os
import subprocess
import sys
from glob import glob

# ---------------------------------------
# ---------------- PATHS ----------------
# ---------------------------------------

# Set data and executables paths
dataPath = r"/buildserver/data/XB1"
exePath = r"/buildserver/executables/XB1"

# Set location of 7-zip and check it exists, otherwise error
loc7Zip = r"/Program Files/7-zip/7z.exe" # Check for normal location
if not os.path.isfile(os.path.normpath(loc7Zip)):
    loc7Zip = r"/Program Files (x86)/7-zip/7z.exe" # Check for other version on 64 bit systems
    if not os.path.isfile(os.path.normpath(loc7Zip)):
        sys.exit("Cannot find 7-zip at " + os.path.normpath(loc7Zip))

# Set output path of script
outputPath = r"/buildserver/builds/XB1"

# ----------------------------------------
# ---------------- INPUTS ----------------
# ----------------------------------------

if len(sys.argv) >= 3: # If input is already supplied
    # Branch and Changelist
    branch = sys.argv[1]
    print("Branch: " + branch)
    changelist = sys.argv[2]
    print("Changelist: " + changelist)
    if len(sys.argv) >= 7: # If additional arguments are supplied for FTP transfer
        ftpServer = sys.argv[3]
        ftpPort = sys.argv[4]
        ftpUser = sys.argv[5]
        ftpPassword = sys.argv[6]
else: # If input is required
    branch = raw_input("Please enter branch: ")
    changelist = raw_input("Please enter changelist: ")
    ftpTransfer = raw_input("FTP Transfer? (1 or 0):")
    if ftpTransfer == "1": # If FTP transfer is desired
        ftpServer = raw_input("FTP Server:")
        ftpPort = raw_input("FTP Port:")
        ftpUser = raw_input("FTP User:")
        ftpPassword = raw_input("FTP Password:")

# Set specified build paths
dataPath = dataPath + "/" + branch + "/" + changelist + "/"
exePath = exePath + "/" + branch + "/" + changelist + "/"

# ----------------------------------------
# ---------------- CHECKS ----------------
# ----------------------------------------

# Check if paths exist, if not then output error
if not os.path.exists(dataPath):
    sys.exit("Specified data path does not exist: " + dataPath)

if not os.path.exists(exePath):
    sys.exit("Specified executables path does not exist: " + exePath)

# Check if output path exists, otherwise error. Check if output folder exists, if not create it.
if not os.path.exists(outputPath):
    sys.exit("Specified output path does not exist: " + outputPath)
else:
    outputPath += "/" + branch + "/" + changelist + "/"
    if not os.path.exists(outputPath):
        print("Specified output path did not exist: " + outputPath)
        print("Creating path now...")
        os.makedirs(outputPath)
        print(outputPath + " created.")

# Check if minimum number of build files exist
# Data
if not len(glob(os.path.normpath(dataPath) + r"\*.data")) > 0:
    sys.exit("Could not find a .data file in " + os.path.normpath(dataPath))

# Executable and Symbol
if not len(glob(os.path.normpath(exePath) + r"\*.exe")) > 0 and len(glob(os.path.normpath(exePath) + r"\*.adb")) > 0:
    sys.exit("Could not find a .exe file in " + os.path.normpath(exePath))
else:
    # Check if each executable has a symbol file
    exeFiles = glob(os.path.normpath(exePath) + r"\*.exe")
    for exeFile in exeFiles:
        exeName = os.path.splitext(os.path.basename(exeFile))[0]
        pdbFile = glob(os.path.normpath(exePath + "/" + exeName + r".pdb"))
        if not len(pdbFile) == 1:
            print("Could not find pdb file " + os.path.normpath(exePath + "/" + exeName + r".pdb"))
            # Replace ^ with this line if pdb files are required --> sys.exit("Could not find pdb file " + os.path.normpath(exePath + "/" + exeName + r".pdb"))

# -------------------------------------------
# ---------------- ZIP FILES ----------------
# -------------------------------------------

# Set full output path and name
outputName = "XboxBuild-" + branch + "-" + changelist
outputFull = outputPath + outputName

# Run zip on files
# Data
dataFiles = glob(os.path.normpath(dataPath) + r"\*.data")
for dataFile in dataFiles:
    print("Zipping " + dataFile + " to " + outputFull)

    # Zip data file
    archive_command = r'"{}" a "{}" "{}" -p{} {} -mhe=on'.format(loc7Zip, outputFull, dataFile, "XboxBuild", ">nul")
    subprocess.call(archive_command, shell=True)

# Executables and Symbol
exeFiles = glob(os.path.normpath(exePath) + r"\*.exe")
for exeFile in exeFiles:
    print("Zipping " + exeFile + " to " + outputFull)

    # Zip executable file
    archive_command = r'"{}" a "{}" "{}" -p{} {} -mhe=on'.format(loc7Zip, outputFull, exeFile, "XboxBuild", ">nul")
    subprocess.call(archive_command, shell=True)

    # if pdb file exists zip it too
    exeName = os.path.splitext(os.path.basename(exeFile))[0]
    pdbFile = glob(os.path.normpath(exePath + "/" + exeName + r".pdb"))
    if len(pdbFile) == 1:
        archive_command = r'"{}" a "{}" "{}" -p{} {} -mhe=on'.format(loc7Zip, outputFull, pdbFile[0], "XboxBuild", ">nul")
        subprocess.call(archive_command, shell=True)


print("Zip completed successfully.")

# ----------------------------------------------
# ---------------- FTP TRANSFER ----------------
# ----------------------------------------------

if 'ftpServer' in locals() and 'ftpPort' in locals() and 'ftpUser' in locals() and 'ftpPassword' in locals(): # If FTP server arguments were supplied

    print("Attempting to connect to FTP server...")

    # Check installation of WinSCP
    locWinSCP = r"/Program Files/WinSCP/WinSCP.com" # Check for 32-bit version
    if not os.path.isfile(os.path.normpath(locWinSCP)):
        locWinSCP = r"/Program Files (x86)/WinSCP/WinSCP.com" # Check for other version on 64 bit systems
        if not os.path.isfile(os.path.normpath(locWinSCP)):
            sys.exit("Cannot find WinSCP at " + os.path.normpath(locWinSCP))

    # Attempt to open connection and send file to FTP server
    outputFileName = outputFull + ".7z"
    winscp_command = r'"{}" /command "open ftp://{}:{}@{}:{}" "put "{}" "{}"" "exit"'.format(locWinSCP,ftpUser,ftpPassword,ftpServer,ftpPort,os.path.normpath(outputFileName),"/")
    subprocess.call(winscp_command, shell=True)

    print("FTP transfer attempt finished.")
