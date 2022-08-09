import tkinter
import json
from tkinter import ttk
from html_parsing import parse_html

config = json.load(open("config.json"))
main = tkinter.Tk()
main.title("CheapBrowser")
# main.state('zoomed')
w = int(config["width"])
h = int(config["height"])
main.geometry(str(w)+"x"+str(h))

frame= tkinter.Frame(main,width=w,height=h)
frame.place(x=0,y=0)

canvas = tkinter.Canvas(frame,width=w,height=h-25)
canvas.place(x=0,y=25)

scrollbar = ttk.Scrollbar(frame,orient=tkinter.VERTICAL,command=canvas.yview)
scrollbar.place(x=w-20,y=0,height=h)
scrollbar2 = ttk.Scrollbar(frame,orient=tkinter.HORIZONTAL,command=canvas.xview)
scrollbar2.place(x=0,y=h-20,height=20,width=w)

canvas.configure(yscrollcommand=scrollbar.set,xscrollcommand=scrollbar2.set)
canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
def _on_mouse_wheel(event):
    canvas.yview_scroll(-1 * int((event.delta / 120)), "units")
canvas.bind_all("<MouseWheel>", _on_mouse_wheel)

frame2 = tkinter.Frame(canvas,width=w,height=h-25)
frame2.place(x=0,y=25)
canvas.create_window((0,0),window=frame2, anchor="nw")
elements = []

def render_element(node):
    global elements
    for child in node.children:
        if(child[0]=="DOM"):
            render_element(child[1])
        else:
            elements.append(tkinter.Label(frame2,text=child[1],anchor=tkinter.W,justify=tkinter.LEFT))

def openURL():
    global elements
    if(len(elements)>0):
        for element in elements:
            element.destroy()
    current_x = 0
    current_y = 25
    elements = []
    try:
        url = urlbar.get()
        html = parse_html(url)
        render_element(html)
        for element in elements:
            element.place(x=current_x,y=current_y,height=23)
            current_y += 30
            main.update_idletasks()
            frame2.configure(height=current_y+30)
            canvas.configure(scrollregion = canvas.bbox('all'))
    except Exception as e:
        elements.append(tkinter.Label(frame2,text=str(e),anchor=tkinter.W,justify=tkinter.LEFT))
        elements[0].place(x=current_x,y=current_y)

urlbar = tkinter.Entry(frame)
urlgo = tkinter.Button(frame,text="Open URL",command= openURL)

urlbar.place(x=0,y=0,height=23,width=int(3*w/4))
urlgo.place(x=int(3*w/4),y=0,height=23,width=int(1*w/4)-20)

main.mainloop()