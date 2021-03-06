import xml.etree.ElementTree as ET
from PIL import ImageTk, Image

import tkinter as tk
from tkinter import ttk
from typing import List

class Empty:
    pass

def generate_window(path):
    mytree = ET.parse(path)
    myroot = mytree.getroot()

    if myroot.tag != "root":
        return "NO ROOT FOUND"
    else:
        title = "Window"
        if "title" in myroot.attrib:
            title = myroot.attrib["title"]
        root_window = tk.Tk()
        root_window.a = {}
        root_window.title(title)
        width = root_window.winfo_width()
        height = root_window.winfo_height()
        if "width" in myroot.attrib:
            width = int(myroot.attrib["width"])
        if "height" in myroot.attrib:
            height = int(myroot.attrib["height"])
        root_window.geometry("%dx%d" % (width, height))
        
        pack_msg = pack_children(root_window, root_window, list(myroot), myroot)
        if pack_msg != "OK":
            return pack_msg
        else:
            return root_window

def jack(master_elem, grand_elem, widget, child_counter, sticky=None):
    if master_elem is not None:
        if "grid" in master_elem.attrib:
            if master_elem.attrib["grid"] == "col":
                cols = int(master_elem.attrib["count"])
                coln = child_counter % cols 
                if coln == 0:
                    coln = cols
                rown = child_counter // cols + int(child_counter % cols > 0) 
            elif master_elem.attrib["grid"] == "row":
                rows = int(master_elem.attrib["count"])
                rown = child_counter % rows 
                if rown == 0:
                    rown = rows
                coln = child_counter // rows + int(child_counter % rows > 0) 
            # print(widget, rown, coln, "#" + str(child_counter))
            if sticky:
                widget.grid(row=rown-1, column=coln-1, sticky=sticky)
            else:
                widget.grid(row=rown-1, column=coln-1)
        else:
            widget.pack()

def identify_widget(elem, widget, grand_elem):
    if "id" in elem.attrib:
        id = elem.attrib["id"]
        grand_elem.a[id] = widget

def pack_children(master, grand_elem, children: List[ET.Element], master_elem: ET.Element = None):
    child_counter = 0
    for elem in children:
        child_counter += 1
        if elem.tag == "pass":
            pass

        if elem.tag == "button":
            button_text = elem.text
            button = tk.Button(master, text=button_text)
            jack(master_elem, grand_elem, button, child_counter)
            identify_widget(elem, button, grand_elem)

        if elem.tag == "label":
            label_text = elem.text
            label = tk.Label(master, text=label_text)
            jack(master_elem, grand_elem, label, child_counter)
            identify_widget(elem, label, grand_elem)

        if elem.tag == "entry":
            entry = tk.Entry(master)
            jack(master_elem, grand_elem, entry, child_counter)
            identify_widget(elem, entry, grand_elem)

        if elem.tag == "progressbar":
            pbar = ttk.Progressbar(master)
            jack(master_elem, grand_elem, pbar, child_counter)
            identify_widget(elem, pbar, grand_elem)

        if elem.tag == "checkbutton":
            text = elem.text
            var = tk.IntVar()
            checkbutton = tk.Checkbutton(master, text=text, variable=var)
            checkbutton.value = var
            jack(master_elem, grand_elem, checkbutton, child_counter)
            identify_widget(elem, checkbutton, grand_elem)

        if elem.tag == "combobox":
            var = tk.StringVar()
            values = []
            for option in list(elem):
                if option.tag != "option":
                    return "NON OPTION INSIDE COMBOBOX"
                values.append(option.text)
            combobox = ttk.Combobox(master, values=values, textvariable=var)
            combobox.selected_text = var
            jack(master_elem, grand_elem, combobox, child_counter)
            identify_widget(elem, combobox, grand_elem)

        if elem.tag == "listbox":
            values = []
            for item in list(elem):
                if item.tag != "item":
                    return "NON OPTION INSIDE COMBOBOX"
                values.append(item.text)
            var = tk.StringVar(value=values)
            listbox = tk.Listbox(master, listvariable=var)
            listbox.items = var
            jack(master_elem, grand_elem, listbox, child_counter)
            identify_widget(elem, listbox, grand_elem)

        if elem.tag == "select":
            if "id" not in elem.attrib:
                return "ID NOT SPECIFIED FOR SELECT"
            id = elem.attrib["id"]
            var = tk.IntVar()
            grand_elem.a[id] = Empty()
            grand_elem.a[id].a = {}
            grand_elem.a[id].value = var
            for option in list(elem):
                if option.tag != "radiobutton":
                    return "NON RADIOBUTTON INSIDE SELECT"
                button_text = option.text
                if "value" not in option.attrib:
                    return "NO VALUE SPECIFIED FOR RADIOBUTTON"
                value = int(option.attrib["value"])
                if "key" not in option.attrib:
                    return "NO KEY SPECIFIED FOR RADIOBUTTON"
                key = option.attrib["key"]
                radiobutton = tk.Radiobutton(master, text=button_text, value=value)
                jack(master_elem, grand_elem, radiobutton, child_counter)
                grand_elem.a[id].a[key] = radiobutton

        if elem.tag == "frame":
            sticky = ""
            if "sticky" in elem.attrib:
                sticky = elem.attrib["sticky"]
            padx=None; pady=None
            if "padx" in elem.attrib:
                padx=int(elem.attrib["padx"])
            if "pady" in elem.attrib:
                pady=int(elem.attrib["pady"])
            
            frame = tk.Frame(master, padx=padx, pady=pady)
            
            jack(master_elem, grand_elem, frame, child_counter, sticky=sticky)
            pack_msg = pack_children(frame, grand_elem, list(elem), elem)
            if pack_msg != "OK":
                return pack_msg
            identify_widget(elem, frame, grand_elem)

        if elem.tag == "labelframe":
            sticky = ""
            if "sticky" in elem.attrib:
                sticky = elem.attrib["sticky"]
            sticky = ""
            if not "text" in elem.attrib:
                return "LABELFRAME TITLE NOT SPECIFIED"
            text = elem.attrib["text"]
            labelframe = tk.LabelFrame(master, text=text)
            
            jack(master_elem, grand_elem, labelframe, child_counter, sticky=sticky)
            pack_children(labelframe, grand_elem, list(elem), elem)
            identify_widget(elem, labelframe, grand_elem)

        if elem.tag == "canvas":
            canvas = tk.Canvas(master)
            if "img" in elem.attrib:
                img = elem.attrib["img"]
                import os
                # print(os.getcwd())
                pilimg = Image.open(r"assets/" + img)
                image = ImageTk.PhotoImage(pilimg)
                canvas.create_image(0,0, anchor=tk.NW, image=image)
                canvas.image = image
                canvas.update_idletasks()
            jack(master_elem, grand_elem, canvas, child_counter)
            identify_widget(elem, canvas, grand_elem)
    return "OK"