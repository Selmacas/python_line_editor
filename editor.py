import os
SCREEN_LINES = 25

INT, CHAR, END, ERR = "INT", "CHAR", "END", "ERR"

class tokenizer:
    def __init__(self, cmd):
        self.cmd = cmd
        self.position = 0
        self.len = len(cmd)

    def eatWhite(self):
        while (self.cmd[self.position].isspace() or self.cmd[self.position] == ",") and self.position < self.len:
            self.position += 1

    def nextTok(self):
        if self.position >= self.len:
            return (END, None)

        self.eatWhite()

        if self.position >= self.len:
            return (END, None)

        if self.cmd[self.position].isdigit():
            res=""
            while self.cmd[self.position].isdigit() and self.position < self.len:
                res += self.cmd[self.position]
                self.position += 1
            return (INT, int(res))
        elif self.cmd[self.position].isalpha():
            self.position += 1
            return (CHAR, self.cmd[self.position - 1])
        else:
            return (ERR, None)

class editor:
    def __init__(self, file):
        self.filename = file
        self.fcns =  {"l": self.list, "w": self.write, "q": self.quit, "d": self.delete, "i": self.insert, "s": self.search, "a": self.append, "r": self.replace, "h": self.help}
        self.running = True
        self.buf = []
        try:
            f=open(file, "r")
            self.buf = f.readlines()
            f.close()
        except:
            print("File " + file + " does not exist")

    def help(self, p):
        print("All commands are case insenssitive, argument nubmers can be separated using spaces or comas,") 
        print("command could be separated too by spaces or commas but it is not necessary.\n")
        print("Commands: ")
        print("H        - Show this help")
        print("n[,m]L   - Show lines in range n..m (if no m, then show 25 lines)")
        print("n[,m]D   - Delete line n (if inserted m then deletes lines in range n..m)")
        print("nI       - Insert line to position n, insering lines until is writen only single dot on line")
        print("nA       - Append to line n")
        print("R        - Replace - not implemented yet")
        print("S        - Search - not implemented yet")
        print("W        - Save the file")
        print("Q        - Quit editor without save")

    def replace(self, p):
        print("Replace: " + str(p))

    def append(self, p):
        if len(p) == 0:
            print("Error: Missing line number")
            return
        if p[0] < 1 or p[0] > len(self.buf):
            print("Error: Wrong line number")
            return
        t = input("a> ")
        if len(t) > 0:
            t += "\n"
            self.buf[p[0] - 1] = self.buf[p[0] - 1].rstrip("\n")
            self.buf[p[0] - 1] += t

    def search(self, p):
        print("Search: " + str(p))

    def insert(self, p):
        if len(p) == 0:
            print("Error: Missing line number")
            return
        if p[0] < 1 or p[0] > len(self.buf)+1:
            print("Error: Wrong line number")
            return
        cnt = p[0] - 1
        while True:
            t = input("i> ")
            if (len(t) == 1) and (t[0] == "."):
                break
            elif len(t) == 0:
                continue
            else:
                t += "\n"
                self.buf.insert(cnt, t)
                cnt += 1

    def delete(self, p):
        if len(self.buf) == 0:
            print("Error: empty file, can not deleteline")
            return

        if len(p) == 0:
            print("Error: Missing line number")
            return
        elif len(p) == 1:
            if max(p[0] - 1, 0) < len(self.buf):
                self.buf.pop(p[0] - 1)
            else:
                print("Error: wrong line number")
        elif len(p) == 2:
            start = 0
            end = 0
            if max(p[0] - 1, 0) < len(self.buf):
                start = p[0] - 1
            else:
                print("Error: wrong line number")
                return
            if (p[1] - 1  >= start) and (p[1] - 1 < len(self.buf)) :
                end = p[1] - 1
            else:
                print("Error: wrong line number")
                return
            for i in range(end, start-1, -1):
                self.buf.pop(i)

    def list(self, p):
        start = 0
        end = 0
        if len(self.buf) == 0:
            print("Error: Empty file")
            return

        if len(p) == 0: 
            print("Error: Missing line number")
            return
        elif len(p) == 1: # print od cisla
            start = min(max(p[0]-1, 0), len(self.buf)-1)
            end = min(len(self.buf) - 1, p[0] - 1  + SCREEN_LINES)
        elif len(p) == 2: # print od cisla do cisla
            start = min(max(p[0]-1, 0), len(self.buf)-1)
            end = min(len(self.buf) - 1, max(p[1]-1, start))

        for i in range(start, end + 1):
            print(f"{i+1:5d}:", end="")
            if (i + 1)  == len(self.buf):
                print("* " + self.buf[i], end="") 
            else:
                print("  " + self.buf[i], end="") 

    def write(self, p):
        try:
            os.rename(self.filename, self.filename + ".old")
        except:
            b = input("Can not move old file, replace it anyway? (y/N): ")
            if len(b) > 0:
                if b[0] == "y" or b[0] == "Y":
                    try:
                        fw = open(self.filename, "w")
                        for ln in self.buf:
                            fw.write(ln)
                        fw.close()
                    except:
                        print("Can not write file")
                        return
        else:
            try:
                fw = open(self.filename, "w")
                for ln in self.buf:
                    fw.write(ln)
                fw.close()
            except:
                os.rename(self.filename + ".old", self.filename)
            else:
                os.remove(self.filename + ".old")

    def quit(self, p):
        self.running = False

    def interpret(self, cmd):
        tok = tokenizer(cmd)
        params = []
        for i in range(3):
            tmp = tok.nextTok()
            if tmp[0] == CHAR:
                cmd = tmp[1].lower()
                if cmd in self.fcns:
                    self.fcns[cmd](params)
                else:
                    print("Error: uknown command")
                    return
                return
            elif tmp[0] ==  ERR or tmp[0] == END:
                print("Error: unknown sequence")
                return
            elif i == 2 and tmp[0] != CHAR:
                print("Error: unknown sequence")
                return
            elif tmp[0] == INT:
                params.append(int(tmp[1]))
            else:
                pass    
           
    def run(self):
        while self.running:
            c = input("> ")
            self.interpret(c)


def edit(file=None):
    while file == None or len(file) == 0:
        file = input("Filename: ")
    e=editor(file)
    e.run()

edit()

