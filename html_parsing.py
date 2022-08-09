import requests

class Stack:
    def __init__(self):
        self.stack = []
    def peek(self):
        return self.stack[-1]
    def push(self,val):
        self.stack.append(val)
    def pop(self):
        pop = self.stack[-1]
        self.stack = self.stack[:-1]
        return pop

class DOM:
    def __init__(self,tag):
        tag_split = self.split_tag(tag)
        self.tag = tag_split[0][0]
        self.attributes = {}
        if(len(tag_split)>1):
            for attr in tag_split[1:]:
                if(len(attr)>1):
                    self.attributes[attr[0]] = attr[1]
                else:
                    self.attributes[attr[0]] = True
        self.children = []
    def split_tag(self,tag):
        result = []
        pointer = 0
        tag_len = len(tag)
        current = ""
        mini_param_mode = False
        ignore_space_mode = False
        param = []
        while(pointer < tag_len):
            if(not mini_param_mode):
                if(tag[pointer]==" "):
                    result.append([current])
                    current = ""
                    param = []
                elif(tag[pointer]=="="):
                    mini_param_mode = True
                    param.append(current)
                    current = ""
                else:
                    current += tag[pointer]
                if(pointer == (tag_len-1)):
                    result.append([current])
            else:
                if(not ignore_space_mode):
                    if(tag[pointer]=="\""):
                        ignore_space_mode = True
                    elif(tag[pointer] == " "):
                        param.append(current)
                        result.append(param)
                        param = []
                        current = ""
                        mini_param_mode = False
                    else:
                        current += tag[pointer]
                else:
                    if(tag[pointer] == "\""):
                        ignore_space_mode = False
                    else:
                        current += tag[pointer]
                if(pointer == (tag_len-1)):
                    param.append(current)
                    result.append(param)
            pointer += 1
        return result

def get_html(url):
    r = requests.get(url)
    return r.text

def parse_html(url):
    page = get_html(url).strip().replace("\n","").replace("\r","")
    pointer = 0
    page_len = len(page)
    page_stack = Stack()
    root = DOM("root")
    page_stack.push(root)
    tag_reading = False
    current_tag = ""
    tag_start_already_exists = False
    old_start_pointer = None
    page_text = ""
    while(pointer<page_len):
        if(page[pointer] == "<"):
            if((page[pointer+1]=="!")&(page[pointer+2]=="-")&(page[pointer+3]=="-")):
                pointer += 4
                while(pointer<page_len):
                    if((page[pointer]=="-")&(page[pointer+1]=="-")&(page[pointer+2]==">")):
                        pointer += 3
                        break
                    else:
                        print(page[pointer],end="")
                        pointer += 1
                continue
            if(tag_start_already_exists):
                page_text += page[old_start_pointer:pointer]
                tag_start_already_exists = False
                continue
            else:
                tag_start_already_exists = True
                current_tag = ""
                tag_reading = True
                pointer += 1
                old_start_pointer = pointer
                continue
        if(tag_reading):
            if(page[pointer]==">"):
                tag_reading = False
                tag_start_already_exists = False
                if(page_text.strip() != ""):
                    page_stack.peek().children.append(["text",page_text.strip()])
                page_text = ""
                if(current_tag[0] == "/"):
                    if(current_tag[1:]==page_stack.peek().tag):
                        page_stack.pop()
                else:
                    newDOM = DOM(current_tag)
                    page_stack.peek().children.append(["DOM",newDOM])
                    if(newDOM.tag in ["area","base","br","col","command","embed","hr","img","input","keygen","link","meta","param","source","track","wbr","!DOCTYPE"]):
                        pass
                    else:
                        page_stack.push(newDOM)
            else:
                current_tag += page[pointer]
            pointer += 1
        else:
            page_text += page[pointer]
            pointer += 1
    return root