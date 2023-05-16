import tkinter as tk
from tkinter.tix import *
from tkinter import filedialog
import os, shutil, time, datetime, enum, re
from datetime import datetime

"""
GUI interface for Camera Image Sorter
select a import/export directory then either select import to move files, clean to remove temporary files or import and clean to do both
"""

# enum for saveFileData array
class SaveFileItems(enum.Enum):
    origPath = 0
    finalPath = 1
    importCheckbox = 2
    cleanCheckbox = 3

# uses testing directories, only works when running via python (not once converted to EXE)
testMode = False
# whether to prompt before cleaning/removing files
confirmRemoveFiles = True
# stores origPath/finalPath/importCheckBox/CleanCheckbox values
saveFileData = ["", "", 0, 0]

# get path to resource when running in production otherwise use relative path when running in dev
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# returns the files location (current dir)
def getFileLocation():
    # return os.path.dirname(os.path.realpath(__file__))
    # returns os current working directory
    return os.getcwd()

# open data.csv read in data
if os.path.isfile(getFileLocation() + "\\" + "data.csv"):
    with open(getFileLocation() + "\\" + "data.csv", "r") as f:
        # read in data
        data = f.read()

        # make sure data is in the correct format before reading
        # equates to: any char, any char, 0 or 1, 0 or 1,
        if re.search(".*,.*,[01],[01],*", data):
            # if last char is comma, remove it
            if data[-1] == ",":
                tempData = data[:-1].split(",")
            else:
                # otherwise just split in data
                tempData = data.split(",")

            # check if enough data to store
            if len(tempData) >= len(saveFileData): 
                saveFileData = tempData
    f.close()
   
if testMode:
    # get current working directory that script is in
    CWD = os.path.dirname(os.path.realpath(__file__))
    # set origPath and finalPath
    saveFileData[SaveFileItems.origPath.value] = CWD + "\\origPath\\"
    saveFileData[SaveFileItems.finalPath.value] = CWD + "\\finalPath\\"

# modal dialog box, takes in title for title, text for message to display and type for type of box to show
def msg(title, text, type):

    if type == "info":
        tk.messagebox.showinfo(title=title, message=text)
    elif type == "yesno":
        # return true or false based on answer, select no as default
        return tk.messagebox.askyesno(title=title, message=text, default="no")

# imports and moves files into finalPath in correct folder structure
def importFiles():
    
    # original path to images 
    origPath = importEntry.get()
    # final destination where you want images
    finalPath = exportEntry.get()

    # if blank
    if origPath == "" or finalPath == "":
        statusText.set("Enter a valid directory to import")
        return

    # get all files in origPath
    try: 
        files = os.listdir(origPath)
        # after this is error handling
    except FileNotFoundError:
        statusText.set("Error: directory not found")
        return
    except NotADirectoryError:
        statusText.set("Error: not a directory")
        return
    except:
        statusText.set("Error: unknown")
        return

    # by default assume no files copied (if they are it will update this var)
    errorText = "No files were copied"
    dirFound = False
    # if no files
    if len(files) < 1:
        statusText.set("No files in directory to import")
    else:
        # check if any directories in origPath
        for file in files:
            # break if it finds a directory - only plain files allowed
            if os.path.isdir(origPath + "\\" + file):
                errorText = "Error: no directories allowed in \"Import from\""
                dirFound = True

        if not dirFound:
            # iterate over files
            for file in files:

                # record time/date meta data for categorizing
                modTimeSeconds = os.path.getmtime(origPath+"\\"+file)
                modDate = time.strftime('%Y-%m-%d', time.localtime(modTimeSeconds))
                modYear = time.strftime('%Y', time.localtime(modTimeSeconds))

                # if year directory doesn't exist
                if not os.path.isdir(finalPath+"\\"+modYear):
                    # create year folder
                    os.makedirs(finalPath+"\\"+modYear)
                
                # if date directory doesn't exist
                if not os.path.isdir(finalPath+"\\"+modYear+"\\"+modDate):
                    # create date folder
                    os.makedirs(finalPath+"\\"+modYear+"\\"+modDate)
                
                # if file doesn't exist, copy it
                if not os.path.exists(finalPath+"\\"+modYear+"\\"+modDate+"\\"+file):
                    # copy file with same year/date to that year/date folder (shutil.copy2 copies metadata also (unlike shutil.copy))
                    shutil.copy2(origPath+"\\"+file, finalPath+"\\"+modYear+"\\"+modDate+"\\"+file)
                    errorText = ""
        
        # if there is an error display it in status
        if errorText != "":
            statusText.set(errorText)
        else:
            # assumes files copied if no error message
            statusText.set("Files copied")

# removes all files in origPath folder
def cleanFiles():
    # get origPath from import entry input box
    origPath = importEntry.get()
    
    # checks that origPath input box isn't blank
    if origPath == "":
        statusText.set("Enter a valid directory to clean")
        return

    try: 
        files = os.listdir(origPath)
        # after this is error handling
    except FileNotFoundError:
        statusText.set("Error: directory not found")
        return
    except NotADirectoryError:
        statusText.set("Error: not a directory")
        return
    except:
        statusText.set("Error: unknown")
        return

    # if no files
    if len(files) < 1:
        statusText.set("No files in directory to clean")
    else:
        
        # if confirmRemoveFiles set, confirm dialog before removing
        if confirmRemoveFiles:
            # checks if user wants to remove files
            rmFiles = msg("Continue?", "This will remove all files in \"{}\", are you sure you want to continue?".format(origPath), "yesno")
        else:
            rmFiles = True
            
        if rmFiles:
            for file in files:
                # removes all files - everything in origPath
                os.remove(origPath + "/" + file)
            
            statusText.set("Files removed")
        else:
            # anything else means file remove was cancelled
            statusText.set("File removal cancelled")

def sortImages():

    # see if corresponding checkboxes checked and do action that goes with them
    # ex. import checked => do import
    if importCheckboxChecked.get():
        importFiles()
    if cleanCheckboxChecked.get():
        cleanFiles()

    # whenever run clicked update newest file status, run after import so new files are shown latest time
    mostRecentTimeText.set("Newest: " + str(getMostRecentFile(exportEntry.get(), os.getcwd())))

    # if neither checkboxes selected, alert user
    if (not importCheckboxChecked.get()) and (not cleanCheckboxChecked.get()):
        statusText.set("No action selected")

# when Browse... clicked popup file explorer and select folder, then save folder and update text box
# type is either import or export corresponding to the same input box
def addFolder(type):
    folderName = filedialog.askdirectory(title="Select Folder")
    
    # whether to update import or export text box
    if type == "import":
        # delete text
        importEntry.delete(0, tk.END)
        # add new text
        importEntry.insert(0, folderName)
        # store in save file array
        saveFileData[SaveFileItems.origPath.value] = folderName
    else:
        exportEntry.delete(0, tk.END)
        exportEntry.insert(0, folderName)
        saveFileData[SaveFileItems.finalPath.value] = folderName
        mostRecentTimeText.set("Newest: " + str(getMostRecentFile(exportEntry.get(), os.getcwd())))

# ran when checkbox is selected, saves data to save file array
def checked():

    if importCheckboxChecked.get():
        saveFileData[SaveFileItems.importCheckbox.value] = 1
    else:
        saveFileData[SaveFileItems.importCheckbox.value] = 0
        
    if cleanCheckboxChecked.get():
        saveFileData[SaveFileItems.cleanCheckbox.value] = 1
    else:
        saveFileData[SaveFileItems.cleanCheckbox.value] = 0
    
def getMostRecentFile(path, originalpath):

    # if blank
    if path == "":
        return "Invalid path"

    try: 
        files = os.listdir(path)
        # after this is error detection
    except FileNotFoundError:
        statusText.set("Error: directory not found")
        return
    except NotADirectoryError:
        statusText.set("Error: not a directory")
        return
    except:
        statusText.set("Error: unknown")
        return

    # cd into path provided
    os.chdir(path)
    
    # as long as there are files (although the loop is usually broken by break and not the condition)
    while len(files) > 0:
        # keeps track of if there is a directory in current directory
        dirFound = False
        # sort from bottom up - means high dates first, so latest will be first
        files.sort(reverse=True)
        for file in files:
            # if finds a dir
            if os.path.isdir(file):
                # cd into it
                os.chdir(file)
                dirFound = True;
                break
        
        # if dir not found, get files in current dir, sort them (in reverse again to get latest at top), get last modified time for top file (file[0]), then change
        # back dirs to be in dir where script is (so other stuff doesn't break), then return date/time in a readable format (instead of seconds since 1970 or whatever)
        if not dirFound:
            files = os.listdir(os.getcwd())
            files.sort(reverse=True)
            # makes sure most recent file time is from actual photo file not .xmp or something created after the photo was taken
            # gets latest file (file[0]) and slices last 3 characters off it ([-3:]) to get extension, if .xmp remove it and run again
            while files[0][-3:] == "xmp":
                files.pop(0)
            mostRecentTime = os.path.getmtime(os.getcwd() + "\\" + files[0])
            os.chdir(originalpath)
            return datetime.fromtimestamp(mostRecentTime).strftime('%b %d %Y %H:%M:%S')
        else:
            # otherwise make files a list of files in newly cd'd into directory
            files = os.listdir(os.getcwd())

    # make sure directory is changed back to originalPath otherwise can't access data.csv
    os.chdir(originalpath)
    
    
# root windows
root = tk.Tk()
root.title("Camera Image Sorter")
# icon
root.iconbitmap(resource_path('camera.ico'))
# can't be resized
root.resizable(False, False)

# create main frame
mainframe = tk.Frame(root)

# first input text box
importPath = tk.StringVar()
importEntry = tk.Entry(mainframe, textvariable=importPath)
importEntry.grid(column=1, row=0, columnspan=4, sticky=(tk.W, tk.E))

# second input text box
exportPath = tk.StringVar()
exportEntry = tk.Entry(mainframe, textvariable=exportPath)
exportEntry.grid(column=1, row=1, columnspan=4, sticky=(tk.W, tk.E))

# options label
tk.Label(mainframe, text="Options:").grid(column=0, row=2, sticky=tk.E)

# status label
statusText = tk.StringVar()
statusLabel = tk.Label(mainframe, textvariable=statusText).grid(column=1, row=4, columnspan=2, sticky=tk.W)

# most recent time label
mostRecentTimeText = tk.StringVar()
mostRecentTimeLabel = tk.Label(mainframe, textvariable=mostRecentTimeText).grid(column=3, row=4, columnspan=3, sticky=tk.W)

# import checkbox
importCheckboxChecked = tk.IntVar()
importCheckbox = tk.Checkbutton(mainframe, text='import',variable=importCheckboxChecked, onvalue=1, offvalue=0, command=checked)
importCheckbox.grid(column=1, row=2, sticky=(tk.W))

# clean checkbox
cleanCheckboxChecked = tk.IntVar()
cleanCheckbox = tk.Checkbutton(mainframe, text='clean',variable=cleanCheckboxChecked, onvalue=1, offvalue=0, command=checked)
cleanCheckbox.grid(column=1, row=2, sticky=(tk.E))

# labels to text boxes
tk.Label(mainframe, text="Import from:").grid(column=0, row=0, sticky=tk.E)
tk.Label(mainframe, text="Copy to:").grid(column=0, row=1, sticky=tk.E)

# file explorer buttons
tk.Button(mainframe, text="Browse...", command=lambda: addFolder("import")).grid(column=5, row=0, sticky=tk.W)
tk.Button(mainframe, text="Browse...", command=lambda: addFolder("export")).grid(column=5, row=1,  sticky=tk.W)

# import/clean action buttons
tk.Button(mainframe, text="Run", command=sortImages, width=50).grid(column=1, row=3, columnspan=4, sticky=tk.S)

# add padding to each element
for child in mainframe.winfo_children(): 
    child.grid_configure(padx=2, pady=2)

# update text boxes with saved data
importEntry.delete(0, tk.END)
importEntry.insert(0, saveFileData[0])
exportEntry.delete(0, tk.END)
exportEntry.insert(0, saveFileData[1])

# update checkbox's with saved data
# import
if int(saveFileData[SaveFileItems.importCheckbox.value]):
    importCheckbox.select()
# clean
if int(saveFileData[SaveFileItems.cleanCheckbox.value]):
    cleanCheckbox.select()

# get most recent file in "Move to" text box path
mostRecentTimeText.set("Newest: " + str(getMostRecentFile(exportEntry.get(), os.getcwd())))

# pack the mainframe
mainframe.pack()
# run tkinter mainloop
root.mainloop()

# write to data file after exited
with open(getFileLocation() + "\\" + "data.csv", "w") as f:
    for data in saveFileData:
        f.write(str(data) + ",")
f.close()