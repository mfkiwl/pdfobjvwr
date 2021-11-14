"""
Copyright (C) Shelby Tucker 2021

This file is part of 'Droid Assistant Bot', which is released under the MIT license.
Please see the license file that was included with this software.
"""

import PySimpleGUI as sg
from PyPDF2 import PdfFileReader
from PyPDF2.generic import IndirectObject

#Default to start with
MAX_LEVELS = 4

def loadData(fileName):
    """Is given a file name and returns a new treeData."""
    global treeData; treeData = sg.TreeData()

    if fileName == '':
        treeData.Insert('','1','No file selected...', values=[])
        return treeData, 0

    try:
        file = open(fileName, 'rb')
        pdf = PdfFileReader(file)
        fields = pdf.getFields()
    except Exception as error:
        treeData.Insert('','1',f"Error loading file {fileName}...", values=[])
        treeData.Insert('','1',f"{error}", values=[])
        return treeData, 0

    #Reset these counters to 0 before we start processing data.
    global level; level = 0
    global keyNum; keyNum = 0

    def add_data(data, itemName, parentKey):
        """
        This function is called for each member that is inserted into the tree.
        When it encounters a new dict or list of enteries, it inserts a tile for it
        then calls this function recursively for each sub-item. We keep a count
        of how deep we go using 'level' so we don't get stuck in loops, because
        PDFs will have IndirectObjects having children that are their parents.
        """
        global level
        global keyNum; keyNum += 1

        #If it's an IndirectObject then get it and continue processing.
        if isinstance(data, IndirectObject):
            data = data.getObject()
        #We've reached our max depth, add an item without going any deeper and go back.
        if level > MAX_LEVELS:
            treeData.Insert(parentKey, keyNum, itemName, values=[data])
            return
        level += 1
        if isinstance(data, dict):
            #Insert an entry for this parent dict then process the kids after
            treeData.Insert(parentKey, keyNum, itemName, values=[])
            #Save the current keyNum counter ID and use it for the parentKey for the items under it
            currentParentNum = keyNum
            for key, value in data.items():
                add_data(value, key, currentParentNum)
        elif isinstance(data, list):
            #Insert an entry for this parent list then process the kids after
            treeData.Insert(parentKey, keyNum, itemName, values=[])
            #Save the current keyNum counter ID and use it for the parentKey for the items under it
            currentParentNum = keyNum
            for item in data:
                    add_data(item, str(item), currentParentNum)
        #It's not a dict or list, so just insert it as an item and move on.
        else:
            treeData.Insert(parentKey, keyNum, itemName, values=[data])
        #We've finished this iteration so subtract one as we return and go up a level.
        level -= 1
    add_data(fields, fileName, '')
    return treeData, keyNum

layout = [[sg.Text('File:'), sg.InputText(key='fileInput'), sg.FileBrowse(target='fileInput'), sg.Button('Load')],
            [sg.Text("Children:"), sg.Spin([i for i in range(1,11)], initial_value=MAX_LEVELS, key='levels', tooltip="Layers of children to process recursively")],
            [sg.Text("", key='status')], 
            [sg.Tree(data = sg.TreeData(),
                    headings=['Value', ],
                    auto_size_columns=True,
                    num_rows=25,
                    col0_width=40,
                    key='tree',
                    show_expanded=False,
                    enable_events=True)],
            [sg.Button('Close')]]

window = sg.Window(f"PDF Object Viewer", layout, resizable=True)

while True:
    event, values = window.read()
    if event in (sg.WIN_CLOSED, 'Close'):
        break
    if event == 'Load':
        sg.popup_quick_message("Loading... Please Wait...")
        newTree, numOfItems = loadData(values['fileInput'])
        window['tree'](newTree)
        window['status'](f"Finished. Loaded {numOfItems} items.")
    if event == 'levels':
        MAX_LEVELS = values['levels']
    print(event, values)
window.close()
