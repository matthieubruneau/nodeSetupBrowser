# nodeSetupBrowser

Python Panel in houdini to copy/paste houdini nodes and setup between users

## Demo
Here is a short demo showing the tool and how it's working:
https://vimeo.com/777696262

## Installation
1. Clone the repository and put it into a folder called "python3.9libs" located in your preference directory.
If you don't have one, you can create one.

2. Then, go to python_panel, create a new panel and type this code in the script window:
```
from NodesBrowser import nodesbrowser, utils, treemodel, filtering
from PySide2 import QtWidgets

def createInterface():
    return nodesbrowser.NodesBrowser()
```


