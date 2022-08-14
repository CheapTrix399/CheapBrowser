import tkinter
import json
from tkinter import ttk
from html_parsing import parse_html
import urllib

config = json.load(open("config.json"))
main = tkinter.Tk()
main.title("CheapBrowser")
main.state('zoomed')
# w = int(config["width"])
# h = int(config["height"])
main.update()
w = main.winfo_width()
h = main.winfo_height()
urlbar_height = int(config["urlbar_height"])
urlbar_width_scale = float(config["urlbar_width_scale"])
font = config["font"]
scrollbar_width = int(config["scrollbar_width"])
element_padding = config["element_padding"]
main.geometry(str(w)+"x"+str(h))

frame= tkinter.Frame(main,width=w,height=h)
frame.place(x=0,y=0)

canvas = tkinter.Canvas(frame,width=w,height=h-urlbar_height)
canvas.place(x=0,y=urlbar_height)

scrollbar = ttk.Scrollbar(frame,orient=tkinter.VERTICAL,command=canvas.yview)
scrollbar.place(x=w-scrollbar_width,y=0,height=h,width=scrollbar_width)
scrollbar2 = ttk.Scrollbar(frame,orient=tkinter.HORIZONTAL,command=canvas.xview)
scrollbar2.place(x=0,y=h-20,height=20,width=w)

canvas.configure(yscrollcommand=scrollbar.set,xscrollcommand=scrollbar2.set)
canvas.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
def _on_mouse_wheel(event):
    canvas.yview_scroll(-1 * int((event.delta / 120)), "units")
canvas.bind_all("<MouseWheel>", _on_mouse_wheel)

frame2 = tkinter.Frame(canvas,width=w,height=h-urlbar_height)
frame2.place(x=0,y=urlbar_height)
canvas.create_window((0,0),window=frame2, anchor="nw")
elements = []
max_width = 0
url = tkinter.StringVar()
tag_attr = {
    "h1": (font,config["h1_size"]),
    "h2": (font,config["h2_size"]),
    "h3": (font,config["h3_size"]),
    "h4": (font,config["h4_size"]),
    "h5": (font,config["h5_size"]),
    "h6": (font,config["h6_size"]),
    "p": (font,config["p_size"])
}

def base_url(url, with_path=False):
    parsed = urllib.parse.urlparse(url)
    path   = '/'.join(parsed.path.split('/')[:-1]) if with_path else ''
    parsed = parsed._replace(path=path)
    parsed = parsed._replace(params='')
    parsed = parsed._replace(query='')
    parsed = parsed._replace(fragment='')
    return parsed.geturl()

def open_a_href(href):
    url.set(href)
    openURL()

def render_element(node):
    global elements, max_width
    for child in node.children:
        if(child[0]=="DOM"):
            if(child[1].tag in ["div","body","html"]):
                render_element(child[1])
            elif(child[1].tag in ["h1","h2","h3","h4","h5","h6","p"]):
                for mini_child in child[1].children:
                    if(mini_child[0]=="text"):
                        elements.append(tkinter.Label(frame2,text=mini_child[1],font=tag_attr[child[1].tag],anchor=tkinter.W,justify=tkinter.LEFT))
                    else:
                        render_element(mini_child[1])
            elif(child[1].tag == "a"):
                href = child[1].attributes["href"]
                if(href[:4]=="http"):
                    pass
                else:
                    href = base_url(url.get()) + "/" + href
                for mini_child in child[1].children:
                    if(mini_child[0]=="text"):
                        elements.append(tkinter.Button(frame2,text=mini_child[1],command=lambda:open_a_href(href)))
            elif(child[1].tag == "img"):
                src = child[1].attributes["src"]
                if(src[:4]=="http"):
                    pass
                elif(src[0]=="/"):
                    src = base_url(url.get()) + "/" + src               
                else:
                    src = url.get() + "/" + src
                image_name = src.split("/")[-1]
                urllib.request.urlretrieve(src,"cache/img/"+image_name)
                img = tkinter.PhotoImage(file="cache/img/"+image_name)
                image = tkinter.Canvas(frame2,width=img.width(),height=img.height())
                image.create_image(0,0,anchor=tkinter.NW,image=img)
                image.image = img
                elements.append(image)
        else:
            elements.append(tkinter.Label(frame2,text=child[1],font=(font,10),anchor=tkinter.W,justify=tkinter.LEFT))

def openURL():
    global elements, max_width
    max_width = 0
    if(len(elements)>0):
        for element in elements:
            element.destroy()
    current_x = 0
    current_y = urlbar_height
    elements = []
    try:
        get_url = url.get()
        html = parse_html(get_url)
        render_element(html)
        for element in elements:
            element.place(x=current_x,y=current_y)
            element.update()
            if(element.winfo_class()=="Canvas"):
                current_y += element.winfo_height()
            current_y += element_padding
            if(element.winfo_width()>max_width):
                max_width = element.winfo_width()
            main.update_idletasks()
            frame2.configure(height=current_y+element_padding,width=max_width+scrollbar_width)
            canvas.configure(scrollregion = canvas.bbox('all'))
    except Exception as e:
        elements.append(tkinter.Label(frame2,text="Error: "+str(e),anchor=tkinter.W,justify=tkinter.LEFT))
        elements[0].place(x=current_x,y=current_y)

urlbar = tkinter.Entry(frame,textvariable=url)
urlgo = tkinter.Button(frame,text="Open URL",command= openURL)

urlbar.place(x=0,y=0,height=urlbar_height,width=int(urlbar_width_scale*(w)))
urlgo.place(x=int(urlbar_width_scale*w),y=0,height=urlbar_height,width=(w-int(urlbar_width_scale*w)-scrollbar_width))

main.mainloop()