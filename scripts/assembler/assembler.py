#32 bit assembler

from typing import List,Tuple
import sys

import lark
 
droidspeak_parser = lark.Lark(r'''

                         
identifier : CNAME
                         
address : SIGNED_INT 
         | "&" identifier  ["+" SIGNED_INT]

                         
newidentifier : identifier ["=" address]

                         
                         
command : CNAME [newidentifier [newidentifier]] ["->" address] 

commandwithjmp : command ";" [ "goto" address ]

line :   [identifier ":"] commandwithjmp ";"
       | [identifier ":"] command ";"

macro : CNAME "!" "(" newidentifier address address ")" ";"
                                         
program : (macro|line)+

%import common.SIGNED_INT
%import common.CNAME
%import common.WS
%import common.C_COMMENT
%ignore WS
%ignore C_COMMENT
                         
''', start="program")
ncnt=1


class memaddress:
    def __init__(self,iden,offset=None):
        if offset is None:
            offset=0
        #print("address",iden)
        self.iden=iden
        self.offset=int(offset)

    def getbin(self,idenlist):
        return idenlist[self.iden]+self.offset

cmdbin = {
    "write":2,
    "add":3,
    "xor":4,
    "display":9,#8,
    "split":8,
    "nop":0,
    "cmov":5,
    "inc":1,
    "and":6,
    "shr":7
}

def newvar():
    global ncnt
    ncnt+=1
    return "_"+str(ncnt)

'''
write _=&modder -> &writer;
write _=&outp1 -> &writer+2;
goto &writer;

modder: write _=&writer+4 -> &writer;
write _=&outp2 -> &writer+2;
writer: write inp -> outp1;
'''
def splitmaker(inp,outp1,outp2, initvals):
    writer= newvar()
    modder= newvar()

    inptoi1=newvar()
    initvals[inptoi1] = memaddress(modder)

    inptoi2=newvar()
    initvals[inptoi2] = outp1

    inptoi3=newvar()
    initvals[inptoi3] = memaddress(writer,4)

    inptoi4=newvar()
    initvals[inptoi4] = outp2

    return [
        (newvar(),asminstr("write", inptoi1, None, memaddress(writer))),
        (newvar(),asminstr("write", inptoi2, None, memaddress(writer,2), memaddress(writer))),

        (modder,  asminstr("write", inptoi3, None, memaddress(writer))),
        (newvar(),asminstr("write", inptoi4, None, memaddress(writer,2))),
        (writer,  asminstr("write", inp, None, memaddress("NULL")))
    ]

macros = {
    'copy': splitmaker
}

class asminstr:
    def __init__(self, instr, inp1iden, inp2iden, outpaddr : memaddress, jmpaddr=None):
        self.instr = instr
        self.inp1iden = inp1iden
        self.inp2iden = inp2iden
        self.outpaddr = outpaddr 
        self.jmpaddr = jmpaddr

    def calcsize(self):
        if self.outpaddr is None and self.inp1iden is None:
            return 2
        elif self.inp2iden is None:
            return 4
        else:
            return 5

    def addidens(self,iden,idenlist):
        if self.jmpaddr is None:
            self.jmpaddr = memaddress(iden,self.calcsize())

        if self.inp1iden is not None:
            assert self.inp1iden not in idenlist, f"error with {self.inp1iden} in {iden}"
            idenlist[self.inp1iden] = idenlist[iden]+3
            if self.inp2iden!=None:
                assert self.inp2iden not in idenlist
                idenlist[self.inp2iden] = idenlist[iden]+4

    def getbin(self,idenlist,initvals):
        if self.outpaddr is None and self.inp1iden is None:
            return [self.jmpaddr.getbin(idenlist),cmdbin[self.instr],]
        elif self.inp2iden is None:
            if self.outpaddr is None:
                self.outpaddr=memaddress('NULL',0)
            return [self.jmpaddr.getbin(idenlist),cmdbin[self.instr],self.outpaddr.getbin(idenlist),initvals[self.inp1iden].getbin(idenlist) & 0xffffffff]
        else:
            return [self.jmpaddr.getbin(idenlist),cmdbin[self.instr],self.outpaddr.getbin(idenlist),initvals[self.inp1iden].getbin(idenlist) & 0xffffffff,initvals[self.inp2iden].getbin(idenlist) & 0xffffffff]




class AssemblyCodeParser(lark.Transformer):
    
    def __init__(self):
        self.identifiers = {'NULL':0}
        self.cmdlist = []
        self.initvals={}

    def identifier(self, items):

        if len(items)==0 or items[0]=='_':
            return newvar()
        else:
            return str(items[0])
        
    def newidentifier(self,items):
        self.initvals[items[0]] = items[1] if items[1] is not None else memaddress("NULL")
        return items[0]

    
    def address(self, items):
        if len(items)==1:
            return memaddress("NULL",int(items[0]))
        return memaddress(*items)
    
    def macro(self, items):
        return macros[items[0]](*items[1:],self.initvals)
            
    def command(self, items):
        return asminstr(*items)
    
    def commandwithjmp(self,items):
        cmd = items[0]
        cmd.jmpaddr=items[1]
        return cmd

        
    def line(self, items):
        if items[0] is None:
            return newvar(), items[1]
        else:
            return tuple(items)
        
    def program(self,items : List[List[Tuple[str,asminstr]]|Tuple[str,asminstr]]):
        prog=0
        curridx=2

        lines : List[Tuple[str,asminstr]] =[]

        for i in items:
            if isinstance(i,list):
                lines+=i
            else:
                lines.append(i)


        for iden, cmd in lines:
            #print(iden)
            assert iden not in self.identifiers
            self.identifiers[iden] = curridx
            cmd.addidens(iden, self.identifiers)
            curridx+=cmd.calcsize()

            self.cmdlist.append(cmd)

        return self

    def generatebinary(self):
        bina = [0,0]
        for cmd in self.cmdlist:
            bina+=cmd.getbin(self.identifiers,self.initvals)
        bina+=[0,0,0]
        return bina
        

def assemble_code(code):      
    parsed_tree = droidspeak_parser.parse(code)

    generated_instructions = AssemblyCodeParser().transform(parsed_tree)

    return generated_instructions.generatebinary()

if __name__ == "__main__":
    if len(sys.argv) == 2:
        with open(sys.argv[1], 'r') as code_file:
            print(assemble_code(code_file.read()))
    else:
        print('To use this assembler, input a file as a command line argument. A list of numbers to be put in ram will be output.')
        print('To actually get a pattern, use the assemble processor script.')

        
