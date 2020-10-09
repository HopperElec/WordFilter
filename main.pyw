import pygame,sys
from pygame.locals import *
from ctypes import windll; windll.user32.SetProcessDPIAware()
from random import seed,randint
from json import load as jsonread
from math import ceil

class LineOfText(pygame.sprite.Sprite):
    __slots__ = ('game','text','x','y','size','font','color','static','textid','image','rect','istouched','ishit','align')
    def __init__(self,game,text,x,y,size,font,color,static=0,textid="0",align="center"):
        self.text,self.x,self.y,self.size,self.color,self.static,self.textid,self.istouched,self.ishit,self.align = text,int(x),int(y),size,color,static,textid,0,0,align
        self.font = game.filepath+font+".ttf"
        pygame.sprite.Sprite.__init__(self,game.texts)
        self.image = pygame.font.Font(self.font,self.size).render(self.text,True,color)
        self.refresh()
    def touch(self): self.istouched = 1; self.image = pygame.font.Font(self.font,int(self.size*1.5)).render(self.text,True,(255,255,0)); self.refresh()
    def untouch(self): self.istouched = 0; self.image = pygame.font.Font(self.font,int(self.size)).render(self.text,True,self.color); self.refresh()
    def update(self, newtext): self.text = newtext; self.image = pygame.font.Font(self.font,self.size).render(self.text,True,self.color); self.refresh()
    def refresh(self):
        if self.align == "center": self.rect = self.image.get_rect(**{"center":(int(self.x),int(self.y))})

class Program:
    def refreshwords(self):
        self.words,self.tempfilter,checktype = self.defaultwords,[f"Remove from list",[]],0
        for filterspec in [filterfull[1] for filterfull in self.filters]:
            toRemove = []

            while len(filterspec) != 0:
                if filterspec[0] == 0: 
                    toRemove.append([x for x in self.words if x == filterspec[1]])
                    if checktype == 0: filterspec = filterspec[2:]
                    else: filterspec = [filterspec[0]]+filterspec[3:]
                elif filterspec[0] == 1: 
                    toRemove.append([x for x in self.words if x != filterspec[1]])
                elif filterspec[0] in ["&","/","!"]: checktype = 1
                
                if checktype == 1:
                    if filterspec[0] == "&":
                        tempremove = []
                        for remove in toRemove[len(toRemove)-2]:
                            if remove in toRemove[len(toRemove)-1]: tempremove.append(remove)
                        toRemove[len(toRemove)-2:] = [tempremove]
                    elif filterspec[0] == "/":
                        for remove in toRemove[-1]: toRemove[len(toRemove)-2].append(remove)
                        toRemove = toRemove[:len(toRemove)-1]
                    elif filterspec[0] == "!":
                        for remove in toRemove[len(toRemove)-2]:
                            if remove in toRemove[len(toRemove)-1]:
                                toRemove[len(toRemove)-2].remove(remove)
                        toRemove = toRemove[:len(toRemove)-1]
                    filterspec = filterspec[1:]
            for removeList in toRemove:
                for remove in removeList: self.words.remove(remove)
    # def refreshwords(self):
    #     self.words,self.tempfilter,checktype = self.defaultwords,[],0
    #     for filterspec in [filterfull[1] for filterfull in self.filters]:
    #         toRemove,y = [],0
    #         while len(filterspec) != 0:
    #             print(toRemove)
    #             if filterspec[0+y] == 0: 
    #                 toRemove.append([x for x in self.words if x == filterspec[1+y]])
    #                 if checktype == 0: filterspec = filterspec[2:]
    #                 else: filterspec = [filterspec[0]]+filterspec[3:]
    #             elif filterspec[0+y] == "&": checktype = 1
    #             if checktype == 1:
    #                 if filterspec[0] == "&":
    #                     tempremove = []
    #                     for remove in toRemove[len(toRemove)-2]:
    #                         if remove in toRemove[len(toRemove)-1]: tempremove.append(remove)
    #                     toRemove[len(toRemove)-2:] = [tempremove]
    #                 filterspec = filterspec[1:]
    #         print(toRemove)
    #         for removeList in toRemove:
    #             for remove in removeList: print(remove);self.words.remove(remove)

    def __init__(self):
        self.window = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
        pygame.event.set_allowed([QUIT,KEYDOWN,MOUSEBUTTONDOWN,MOUSEBUTTONUP])
        self.clock = pygame.time.Clock(); pygame.display.set_caption('Word filter')
        self.window_w,self.window_h = pygame.display.get_surface().get_size()
        self.texts = pygame.sprite.Group()
        self.menu,self.display,self.key,self.inputboxtimer,self.down,self.scroll,self.key,self.letter = "home",0,"",0,0,0,"",""

        self.filepath = sys._MEIPASS+'\\' if getattr(sys,'frozen',False) else ''
        self.sounds = [pygame.mixer.Sound(self.filepath+"click.wav")]
        with open(self.filepath+'dictionary.json','r') as jsonfile: self.defaultwords = [word[0] for word in jsonread(jsonfile) if not "-" in word[0]]
        self.filters = []; self.refreshwords()

    def run(self):
        self.clock.tick(15)
        self.window.fill((227,19,19))
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit();sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DELETE: pygame.quit();sys.exit()
                elif event.key == pygame.K_ESCAPE:
                    if self.menu == "home": pygame.quit();sys.exit()
                    elif self.menu == "addfilter0": self.menu = "home"
                elif self.menu in ["addfilter10","addfilter11"]: self.key,self.letter = event.key,event.unicode
                elif self.menu == "home":
                    if event.key == pygame.K_UP and self.scroll != 0: self.scroll -= 1; self.display = "refresh"
                    elif event.key == pygame.K_DOWN and self.scroll < ceil(len(self.words)/8)-4: self.scroll += 1; self.display = "refresh"
                        
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1: self.down = 1
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1: self.down = 0

        if self.display != self.menu:
            self.display = self.menu
            if self.menu == "home":
                self.ask("Word filter","Choose a filter to edit it, add a filter or explore words filtered","selection",
                    [[[["Filters (use W and S to scroll)","Category"]] + (
                        [[f[0],"filter"+str(i)] for i,f in enumerate(self.filters)] if len(self.filters) >= 1 else [["None!","Static"]]) + [["Add filter","addfilter"]]],
                    [[["Words (use arrow keys to scroll)","Category"]] + (
                        [[", ".join(self.words[i*8:(i+1)*8]),"Static"] for i in range(ceil(len(self.words)/8))] if len(self.words) != 0 and len(self.words) <= 32
                        else [[", ".join(self.words[i*8:(i+1)*8]),"Static"] for i in range(self.scroll,4+self.scroll)] if len(self.words) != 1
                        else [["None!","Static"]])]])
            elif self.menu == "addfilter0":
                if self.tempfilter[1] == []: desc = "Remove from list when..."
                else: desc = self.tempfilter[0]
                self.ask("Add filter",desc,"selection",
                    [[[["Filters","Category"],["word is...","addfilter10"],["word is not...","addfilter11"]]]])
            elif self.menu == "addfilter10":
                self.ask("Add filter","Remove from list when word is...","input")
            elif self.menu == "addfilter11":
                self.ask("Add filter","Remove from list when word is not...","input")
            elif self.menu == "addfilter-AOU":
                self.ask("Add filter",self.tempfilter[0]+"","selection",
                    [[[["Would you like to add more to this filter?","Category"],["& (and)","and"],["/ (or)","or"],["! (unless)","unless"],["Done","done"]]]])

        if self.key != "" or self.letter != "":
            if self.key == pygame.K_RETURN:
                if self.userinput != "":
                    if self.menu == "addfilter10": desc = " when word is "
                    elif self.menu == "addfilter11": desc = " when word is not "
                    self.tempfilter[0] += desc+self.userinput
                    self.tempfilter[1] += [int(self.menu[-1]),self.userinput]
                    self.menu = "addfilter-AOU"
            elif self.key == pygame.K_BACKSPACE: self.userinput = self.userinput[0:-1]
            elif self.letter != "": self.userinput += self.letter.lower()
            self.letter,self.key = "",""

        for text in self.texts:
            if text.align == "center":
                if text.rect.collidepoint(pygame.mouse.get_pos()) and text.static == 0: text.touch()
                elif not text.rect.collidepoint(pygame.mouse.get_pos()) and text.static == 0 and text.istouched == 1 and text.ishit == 0: text.untouch()
                if text.istouched == 1 and self.down == 1: text.ishit = 1
                elif self.down == 0 and text.ishit == 1:
                    text.ishit = 0
                    pygame.mixer.Sound.play(self.sounds[0])
                    if text.textid == "addfilter": self.menu = "addfilter0"
                    elif text.textid.startswith("addfilter") and len(text.textid) > 9: self.menu = text.textid
                    elif text.textid == "and":
                        self.tempfilter[0] += " and"
                        self.tempfilter[1].append("&")
                        self.menu = "addfilter0"
                    elif text.textid == "or":
                        self.tempfilter[0] += " or"
                        self.tempfilter[1].append("/")
                        self.menu = "addfilter0"
                    elif text.textid == "unless":
                        self.tempfilter[0] += " unless"
                        self.tempfilter[1].append("!")
                        self.menu = "addfilter0"
                    elif text.textid == "done":
                        self.filters.append(self.tempfilter)
                        self.menu = "home"
                        self.singletext("Please wait a moment, this can take a while!",0)
                        self.refreshwords()
                if text.textid == "userinput":
                    self.inputboxtimer += 1
                    if self.inputboxtimer == 10:
                        if text.text[-1] == "_": text.update(self.userinput+"  ")
                        else: text.update(self.userinput+"_")
                        self.inputboxtimer = 0
                    elif text.text != self.userinput: text.update(self.userinput+text.text[-1])

            if text.textid == "userinput":
                self.inputboxtimer += 1
                if self.inputboxtimer == 30:
                    if text.text[-1] == "_": text.update(self.userinput+"  ")
                    else: text.update(self.userinput+"_")
                    self.inputboxtimer = 0
                elif text.text != self.userinput: text.update(self.userinput+text.text[-1])
            if text.align == "center": self.window.blit(text.image,(text.rect.x,text.rect.y))
            else: self.window.blit(text.image,(text.x,text.y))
        pygame.display.update()

    def ask(self,question,information,asktype,other=""):
        self.texts = pygame.sprite.Group()
        LineOfText(self,question,self.window_w/2,24,48,"Impact",(255,255,255),1)
        LineOfText(self,information,self.window_w/2,64,32,"Arial",(196,196,196),1)

        if asktype == "selection":
            for iterate0,rowofanswers in enumerate(other):
                for iterate1,groupofanswers in enumerate(rowofanswers):
                    for iterate2,answer in enumerate(groupofanswers):
                        x = self.window_w/(len(rowofanswers)+1)*(iterate1+1)
                        y = self.window_h/(len(other)+1)*(iterate0+1)-46*(len(groupofanswers)/2-iterate2)
                        if iterate2 == 0: LineOfText(self,answer[0],x,y,32,"Impact",(255,255,255),1,answer[1])
                        elif answer[1] == "Static": LineOfText(self,answer[0],x,y,32,"Arial",(255,255,255),1,answer[1])
                        else: LineOfText(self,answer[0],x,y,32,"Arial",(255,255,255),textid=answer[1])
        elif asktype == "input":
            self.userinput,self.key = "",""
            LineOfText(self,"_",self.window_w/2,self.window_h/2,32,"Impact",(255,255,255),textid="userinput")
            LineOfText(self,"Press [ENTER] to confirm your choice",self.window_w/2,96,24,"Arial",(196,196,196),1)
        elif asktype == "about":
            for iterate0,group in enumerate(other):
                for iterate1,line in enumerate(group):
                    x = self.window_w/(len(other)+1)*(iterate0+1)
                    y = self.window_h/2-23*(len(group))+46*iterate1
                    if len(other) > 1 and iterate1 == 0: LineOfText(self,line,x,y,32,"Impact",(255,255,255))
                    else: LineOfText(self,line,x,y,32,"Arial",(255,255,255))
            LineOfText(self,"Press [ESC] to go back!",self.window_w/2,self.window_h-32,40,"Arial",(255,255,255))

    def singletext(self,text,time):
        self.texts = pygame.sprite.Group(); self.window.fill((227,19,19))
        LineOfText(self,text,self.window_w/2,self.window_h/2,64,"Impact",(255,255,255))
        for text in self.texts: self.window.blit(text.image,(text.rect.x,text.rect.y))
        pygame.display.update()
        pygame.time.delay(time)

pygame.mixer.init(buffer=2)
pygame.init(); g = Program()
while True: g.run()