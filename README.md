# nodeSetupBrowser

Python Panel in houdini to copy/paste houdini nodes and setup between users

## Demo
Here is a short demo showing the tool and how it's working:
https://vimeo.com/777696262

## Installation
1. Clone the repository and put it into a folder called "python3.9libs" located in your preference directory.
If you don't have one, you can create one.
2. Set the PATH variable in the utils.py to where you want the files to be stored. It can be a network location or a 
local one
3. Then, inside of Houdini, go to windows -> python panel editor, create a new panel and type this code in the script window:
```
from NodesBrowser import nodesbrowser, utils, treemodel, filtering
from PySide2 import QtWidgets

def createInterface():
    return nodesbrowser.NodesBrowser()
```
4. You should now get a new pythonPanel which will show you the interface as shown in the video.
