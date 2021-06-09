import os
import sys
sys.path.append('../../')


class FileReset():
    """Checks to ensure that data files exist after reboot. Use "asyncio.run(FileReset.fullReset())" to run.
    
    Includes program to manually reset individual files for testing purposes. Use "asyncio.run(FileReset.fullReset())" to run."""
    def __init__(self):
        # List of file paths
        self.__FILE_PATHS = [ 
            "/home/pi/TXISRData/flagsFile.txt" , 
            "../TXISR/data/txFile.txt" , 
            "/home/pi/TXISRData/txWindows.txt" , 
            "/home/pi/TXISRData/transmissionFlag.txt" , 
            "/home/pi/TXISRData/AX25Flag.txt",
            "/home/pi/flightLogicData/backupBootRecords.txt" , 
            "/home/pi/flightLogicData/bootRecords.txt" , 
            "/home/pi/flightLogicData/Attitude_Data.txt" , 
            "/home/pi/flightLogicData/Deploy_Data.txt" , 
            "/home/pi/flightLogicData/TTNC_Data.txt" ]
        self.__filePath = ""
        self.__windowFilePath = "/home/pi/TXISRData/txWindows.txt"
        self.fullReset()

    def __reset(self):
        """Opens and erases file, certain files are then filled with required text. If there is no file under a certain file path, it will create the file."""
        # Depending on the file path, replaces the empty file with a string of text based on what data will be written in the file
        try:
            file = open(self.__filePath, 'w')
        except:
            # Check the dir
            self.dirProtection()
            # If the file doesn't exist it creates a new one
            file = open(self.__filePath, 'w+')
            
        if self.__filePath == "/home/pi/flightLogicData/backupBootRecords.txt" or self.__filePath == "/home/pi/flightLogicData/bootRecords.txt" or self.__filePath == "../../bootRecords.txt":
            file.write("0\n0\n0\n")
            file.close()
        if self.__filePath == "/home/pi/TXISRData/flagsFile.txt" or self.__filePath == "../../flagsFile.txt":
            file.write("0\n0\n0\n0\n0\n")
            file.close()
        if self.__filePath == "/home/pi/TXISRData/transmissionFlag.txt" or self.__filePath == "../../transmissionFlag.txt":
            file.write("Enabled")
            file.close()
        if self.__filePath == "/home/pi/TXISRData/AX25Flag.txt" or self.__filePath == "../../AX25Flag.txt":
            file.write("Disabled")
            file.close()
        # This closes the file so it is no longer being edited
    
    def fullReset(self):
        """Checks to make sure that files necessary for reboot exist, if they don't, it creates them."""
        # Runs through every file in FILE_PATHS list
        for i in self.__FILE_PATHS:
            # Opens the file to see if it exists
            try:
                file = open(i)
                print("File being checked " + i)
            # If it doesn't, it runs reset to create it
            except OSError:
                print("File being reset" + i)
                self.__filePath = i
                self.__reset()
            # Otherwise it just closes the file
            else:
                file.close()

    def individualReset(self, newFile):
        self.__filePath = newFile
        """Allows the manual reset of a single file."""
        # Runs reset once for a single file
        self.__reset()
        #print("File being reset " + self.__filePath)

    # This check a single file to see if it will open or not if not it resets it 
    def checkFile(self, newFile):
        self.__filePath = newFile
        
        self.dirProtection()

        try:
            file = open(self.__filePath)
        except OSError:
            self.__reset()
            #print("File being reset " + self.__filePath)
        else:
            file.close()
            #print("File is ok " + self.__filePath)

    # This checks a single directory to see if it exists
    def checkDir(self, path):
        isdir = os.path.isdir(path)    
        return isdir

    # This makes the diretory if it files
    def dirProtection(self):  
        count = 0
        # Find the directory path
        for i in range(len(self.__filePath)):
            if self.__filePath[-i-1] == "/":
                break
            count += 1
        dirPath = self.__filePath[:len(self.__filePath) - count]
        #print(dirPath)
        
        # Check directory
        # The dir doesnt exist recreate it
        if(not self.checkDir(dirPath)):
            try:
                os.mkdir(dirPath)
            except:
                print("Error trying to make directory ", dirPath)
    
    def windowProtection(self):
        print("<Checking txWindows>")
        file = open(self.__windowFilePath, 'r')
        file.seek(0)

        TXwindows = file.readlines()
        count = 0
        for line in TXwindows:
            window = line.split(',')

            # for i in window:
            #     # if type(window[i]) is str:
            #     if 2 + 2 == 4:
            #         TXwindows[count] = ""
            #     else:
            #         continue
            #     shouldCont = False
            #     try:
            #         testVar = int(window[i])
            #     except ValueError:
            #         TXwindows[count] = ""
            #         shouldCont = True
                    
            # if shouldCont:
            #     continue

            # Check if window has five elements
            print(window, len(window))
            if len(window) != 5:
                # If not then erase it and skip current iteration
                print("Evan is testing this :)")
                TXwindows[count] = ""
                continue

            # All of these are checking if values are positive integers

            # Check if timestamp is ten characters long
            if (not isinstance(int(window[0]), int)) or int(window[0]) < 0 or len(window[0]) != 10:
                # If not then erase it and skip current iteration
                TXwindows[count] = ""
                continue

            # Check if window length is less than or equal to 3600
            if (not isinstance(int(window[1]), int)) or int(window[1]) < 0 or int(window[1]) > 3600:
                # If not then erase it and skip current iteration
                TXwindows[count] = ""
                continue

            # Check if type is less than or equal to five
            if (not isinstance(int(window[2]), int)) or int(window[2]) < 0 or int(window[2]) > 5:
                # If not then erase it and skip current iteration
                TXwindows[count] = ""
                continue

            # This is the picture number (not number of pictures), don't put limits on it
            if (not isinstance(int(window[3]), int)) or int(window[3]) < 0:
                TXwindows[count] = ""
                continue

            # This is the TX flag, don't put limits on it
            TXflagStripped = window[4].strip('\n')
            if (not isinstance(int(TXflagStripped), int)) or int(window[4]) < -1:
                TXwindows[count] = ""
                continue
            count += 1

        file = open(self.__windowFilePath, 'w')
        file.writelines(TXwindows)

        file.seek(0)

        for line in TXwindows:
            if line == "\n":
                del line
        file.close()
