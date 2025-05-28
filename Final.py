# Final Project
# Last update: 2/27/25

# Globals
#----------------------------------------------------#
sym = None              # char
val = None              # int
id = None               # int
tokenName = None        # str
instructionNum = 1      # int
glblBlockNum = 1        # int
currentBlock = None     # basicBlock
firstWhile = True       # bool
glblWhileBlock = None   # basicBlock

file = open("graph.txt", "w").close()     # clear file
file = open("graph.txt", "a")
inputfile = open("input.txt", "r")
buffer = inputfile.read()

def next():
    global sym, buffer

    if len(buffer) > 0:
        sym = buffer[0]
        buffer = buffer[1:]
    
    else:
        sym = None

def checkFor(actualToken: int, expectedToken: int):     # Redundant
    if actualToken == expectedToken:                    # Same as saying '=='
        return True
    else:
        return False

def idWarning(tokenName: str):
    if not 0 in constants:
        makeConst(0)

    if not tokenName in currentBlock.data: 
        print("WARNING: variable '" + tokenName + "' in block " + str(currentBlock.blockNum) + " was not initialized, initializing with value 0")
        currentBlock.data[tokenName] = constants[0]
    elif isinstance(currentBlock.data[tokenName], list):
        print("WARNING: array '" + tokenName + "' in block " + str(currentBlock.blockNum) + " has uninitialized index, initializing with value 0")
    else:
        SyntaxErr("idWarning: somehow this managed to break...")
        
    return constants[0]

def SyntaxErr(location=None):
    if location is None:
        print("Syntax Error")
        exit()
    else:
      print("Syntax Error at " + location)
      exit()

def makeConst(constVal: int):       # Makes Constant
    global instructionNum
    constants[constVal] = instructionNum
    bb0.instructions += "|" + str(instructionNum) + ": const #" + str(constVal)
    instructionNum = instructionNum + 1
    return constants[constVal]

def elimInstruct(instruct: str):    # Eliminate redundant instruction
    instructExists = currentBlock.instructions.find(instruct)
    if instructExists != -1:
        existsNum = ""
        reversed_string = currentBlock.instructions[:instructExists]
        reversed_string = reversed_string[::-1]
        for char in reversed_string:
            if char == '|':
                break
            else:
                existsNum = char + existsNum
        return int(existsNum)
    else:
        return -1

def deepCopy(data):                 # Deep copy dict for basic blocks
    copied_dict = {}
    for key, value in data.items():
        if isinstance(value, list):
            copied_dict[key] = [item if not isinstance(item, (dict, list)) else deepCopy(item) if isinstance(item, dict) else list(item) for item in value] # Copy lists
        else:
            copied_dict[key] = value
    return copied_dict

def arrayGetIndex():                # Get array indicies from text
    global sym, buffer
    idxs = []
    token = getNext()
    while token == tokenTable.index("["):
        token = getNext()
        idxs.append(val)
        token = getNext()
        if token != tokenTable.index("]"):
            SyntaxErr("arrayGetElement(): missing ']'")
        token = getNext()

    if token != None:
        buffer = tokenTable[token] + " " + sym + " " + buffer
        sym = " "

    return idxs

def arrayGetElement(array, idxs):   # Get array element from indicies
    if not idxs:
        return array
    
    if idxs[0] >= len(array):
        SyntaxErr("arrayGetElement(): out of bounds")
    
    return arrayGetElement(array[idxs[0]], idxs[1:])

def arrayStrElement(array, indices, num):   # Store array element from indicies
    if len(indices) == 1:
        array[indices[0]] = num
        return
    
    if indices[0] >= len(array):
        SyntaxErr("arrayStrElement(): out of bounds")
    
    arrayStrElement(array[indices[0]], indices[1:], num)

# Basic Block
#----------------------------------------------------#
class basicBlock():                 # Basic blocks for instructions
    def __init__(self, data, blockNum, prev):
        self.instructions = ""                                      # Format for writing to file
        self.branchInstruct = ""                                    # Block branch instruction
        self.data = deepCopy(data)                                  # Current instruction num for each variable (deep copy)
        self.blockNum = blockNum                                    # Block number
        self.join = False                                           # Join block
        self.nexts = []                                             # Next blocks
        self.prevs = []                                             # Previous blocks
        self.nexts_print = []                                       # Printing purposes
        self.prevs_print = []                                       # Printing purposes
        
        if prev != None:
            self.prevs.append(prev)
            self.prevs_print.append(prev.blockNum)

        blocks.append(self)

    def addNext(self, next):
        self.nexts.append(next)
        self.nexts_print.append(next.blockNum)

    def addPrev(self, prev):
        self.prevs.append(prev)
        self.prevs_print.append(prev.blockNum)

    def print(self):
        if len(self.instructions) > 0:
            print("Block " + str(self.blockNum) + ": " + self.instructions[1:])
        else:
            print("Block " + str(self.blockNum) + ": No instructions")
        print("data: " + str(self.data))
        print("nexts: " + str(self.nexts_print))
        print("prevs: " + str(self.prevs_print))

        properties = "bb" + str(self.blockNum) + " [shape=record, label=\"<b>BB" + str(self.blockNum) + "| {"
        if self.join == True:
            properties = "bb" + str(self.blockNum) + " [shape=record, label=\"<b>join\\nBB" + str(self.blockNum) + "| {"
        file.write(properties + self.instructions[1:] + "}\"];\n")

    def print_actuals(self):
        print("nexts: " + str(self.nexts))
        print("prevs: " + str(self.prevs))

# Functions
#----------------------------------------------------#
def InputNum():
    global instructionNum
    token = getNext()
    if token == tokenTable.index("("):
        currentBlock.instructions += "|" + str(instructionNum) + ": read"
        instructionNum += 1
        token = getNext()
        if token != tokenTable.index(")"):
            SyntaxErr("InputNum(): missing ')'")
    else:
        SyntaxErr("InputNum(): missing '('")

def OutputNum():
    global instructionNum
    token = getNext()
    if token == tokenTable.index("("):
        returnVal = Expression()
        currentBlock.instructions += "|" + str(instructionNum) + ": write (" + str(returnVal) +")"
        instructionNum += 1
        token = getNext()
        if token != tokenTable.index(")"):
            SyntaxErr("OutputNum(): missing ')'")
    else:
        SyntaxErr("OutputNum(): missing '('")

def OutputNewLine():
    global instructionNum
    token = getNext()
    if token == tokenTable.index("("):
        currentBlock.instructions += "|" + str(instructionNum) + ": writeNewLine"
        instructionNum += 1
        token = getNext()
        if token != tokenTable.index(")"):
            SyntaxErr("OutputNewLine(): missing ')'")
    else:
        SyntaxErr("OutputNewLine(): missing '('")

# Token Table
#----------------------------------------------------#
    
tokenTable = [
    "main", "let", "var", "array", "call", "return",    # Key words
    "if", "then", "else", "fi",      
    "while", "do", "od",
    "+", "-", "*", "/",                                 # Operations
    "==", "!=", "<", "<=", ">", ">=",
    "(", ")", "{", "}", "[", "]", ",", ";", ".", "<-",  # Syntax
    "numberToken", "idToken",                           # Types
    "InputNum", "OutputNum", "OutputNewLine"            # Functions
]

blocks = []
constants = {}
varStartIdx = len(tokenTable)

# Tokenizer
#----------------------------------------------------#
def getNext():
    global buffer
    while(sym == " " or sym == "\n" or sym == "\t"):
        next()
    
    match sym:
        case None:
            return
        
        case '=':
            next()
            if sym == "=":
                next()
                return(tokenTable.index("=="))
            else:
                SyntaxErr("getNext(): Invalid token: " + sym)
            
        case '!':
            next()
            if sym == "=":
                next()
                return(tokenTable.index("!="))
            else:
                SyntaxErr("getNext(): Invalid token: " + sym)

        case '<':
            next()
            if sym == "=":
                next()
                return(tokenTable.index("<="))
            elif sym == "-":
                next()
                return(tokenTable.index("<-"))
            else:
                buffer = sym + buffer
                next()
                return(tokenTable.index("<"))

        case '>':
            next()
            if sym == "=":
                next()
                return(tokenTable.index(">="))
            else:
                buffer = sym + buffer
                next()
                return(tokenTable.index(">"))
        
        case number if sym.isdigit():
            Number()
            return(tokenTable.index("numberToken"))
        
        case identifier if sym.isalpha():
            return(Identifier())
        
        case _:
            if sym in tokenTable:
                symCopy = sym
                next()
                return(tokenTable.index(symCopy))
            else:
                SyntaxErr("getNext(): Invalid token: " + sym)

def Number():
    global val
    val = int(sym)
    next()
    if sym == None or not sym.isdigit():
        return
    
    while int(sym) <= 9 and int(sym) >= 0:
        val = val * 10 + int(sym)
        next()

        if sym == None or not sym.isdigit():
            break

def Identifier():
    global id, tokenName
    tokenName = sym
    next()

    if sym != None:
        while sym.isdigit() or sym.isalpha():
            tokenName += sym
            next()

            if sym == None:
                break
    
    if tokenName in tokenTable:
        id = tokenTable.index(tokenName)
        if id > varStartIdx - 1:
            return tokenTable.index("idToken")
        else:
            return id
    else:
        return tokenTable.index("idToken")

# Parser
#----------------------------------------------------#
# Declarations
def Computation():
    global buffer, sym
    next()

    if checkFor(getNext(), tokenTable.index("main")):
        token = getNext()
        while token != tokenTable.index("."):
            if token == tokenTable.index("var") or token == tokenTable.index("array"):
                varDecl(token)
            elif checkFor(token, tokenTable.index("{")):
                statSequence()
                token = getNext()
                if token != tokenTable.index("}"):
                    SyntaxErr("Computation(): missing '}'")
            else:
                SyntaxErr("Computation(): missing '.'")
            token = getNext()
    else:
        SyntaxErr("Computation(): must start with 'main'") 

def varDecl(mode: int):
    global sym, buffer

    token = getNext()
    while token != tokenTable.index(";"):
        if mode == tokenTable.index("array"):
                dims = []
                while token == tokenTable.index("["):
                    token = getNext()
                    if token == tokenTable.index("numberToken"):
                        dims.append(val)
                    else:
                        SyntaxErr("varDecl(): array declaration should use numbers")
                    
                    token = getNext()
                    if token != tokenTable.index("]"):
                        SyntaxErr("varDecl(): array declaration missing ']'")

                    token = getNext()

                base_array = []
                if len(dims) == 1:
                    base_array = dims[-1] * [0]
                elif len(dims) == 2:
                    base_array = [[0] * dims[-1] for _ in range(dims[0])]
                elif len(dims) > 2:
                    base_array = [[0] * dims[1] for _ in range(dims[0])]
                    for x in dims[2:]:
                        base_array = [[row[:] for row in base_array] for _ in range(x)]     # Error: references copy for dim >= 4

        if checkFor(token, tokenTable.index("idToken")):
            if mode == tokenTable.index("array"):
                currentBlock.data[tokenName] = base_array
            tokenTable.append(tokenName)  
            token = getNext()
            if checkFor(token, tokenTable.index(",")):
                token = getNext()
            elif checkFor(token, tokenTable.index(";")):
                continue
            else:
                SyntaxErr("varDecl(): ',' or ';'")
        else:
            SyntaxErr("varDecl(): missing valid identifier")

def statSequence():
    global sym, buffer
    statementToken = True
    while statementToken:
        token = getNext()
        if token == tokenTable.index(";"):
            token = getNext()
        statementToken = Statement(token)

    buffer = tokenTable[token] + " " + sym + " " + buffer
    sym = " "

# Statements
def Statement(token: int):
    match token:
        case letToken if token == tokenTable.index("let"):
            Assignment()
            return True
        case function if token == tokenTable.index("call"):
            funcCall()
            return True
        case ifToken if token == tokenTable.index("if"):
            ifStatement()
            return True
        case whileToken if token == tokenTable.index("while"):
            whileStatement()
            return True
        case returnToken if token == tokenTable.index("return"):
            print("return")
            return True
        case _:
            return False

def Assignment():
    arrayAssignment = False
    token = getNext()
    if checkFor(token, tokenTable.index("idToken")):
        assignmentVarName = tokenName
        if assignmentVarName in currentBlock.data and isinstance(currentBlock.data[assignmentVarName], list):
            idxs = arrayGetIndex()
            arrayAssignment = True
        token = getNext()
        if checkFor(token, tokenTable.index("<-")):
            if arrayAssignment == True:
                instructNum = Expression()
                arrayStrElement(currentBlock.data[assignmentVarName], idxs, instructNum)
            else:
                currentBlock.data[assignmentVarName] = Expression()
        else:
            SyntaxErr("Assignment(): missing '<-''")
    else:
        SyntaxErr("Assignment(): missing identifier")

def funcCall():
    token = getNext()
    if token == tokenTable.index("InputNum"):
        InputNum()
    elif token == tokenTable.index("OutputNum"):
        OutputNum()
    elif token == tokenTable.index("OutputNewLine"):
        OutputNewLine()

def ifStatement():
    global currentBlock, instructionNum, glblBlockNum, firstWhile
    op = Relation()
    prevBlock = currentBlock
    cmpInstruct = instructionNum - 1
    token = getNext()
    if token == tokenTable.index("then"):
        # if block
        ifBlock = basicBlock(currentBlock.data, glblBlockNum + 1, currentBlock)
        file.write("bb" + str(currentBlock.blockNum) + ":s -> bb" + str(ifBlock.blockNum) + ":n [label=\"fall-through\"];\n")
        currentBlock.addNext(ifBlock)
        glblBlockNum += 1
        currentBlock = ifBlock
        instructionNum += 1
        statSequence()

        match op:    # checking correct branch operation
            case eql if op == tokenTable.index("=="):
                prevBlock.branchInstruct += "|" + str(cmpInstruct + 1) + ": BEQ (" + str(cmpInstruct) + ") ("
            case neq if op == tokenTable.index("!="):
                prevBlock.branchInstruct += "|" + str(cmpInstruct + 1) + ": BNE (" + str(cmpInstruct) + ") ("
            case les if op == tokenTable.index("<"):
                prevBlock.branchInstruct += "|" + str(cmpInstruct + 1) + ": BLT (" + str(cmpInstruct) + ") ("
            case lte if op == tokenTable.index("<="):
                prevBlock.branchInstruct += "|" + str(cmpInstruct + 1) + ": BLE (" + str(cmpInstruct) + ") ("
            case gre if op == tokenTable.index(">"):
                prevBlock.branchInstruct += "|" + str(cmpInstruct + 1) + ": BGT (" + str(cmpInstruct) + ") ("
            case gte if op == tokenTable.index(">="):
                prevBlock.branchInstruct += "|" + str(cmpInstruct + 1) + ": BGE (" + str(cmpInstruct) + ") ("
            case _:
                SyntaxErr("ifStatement(): unknown operator")

        # else block
        firstWhile = True
        elseBlock = basicBlock(prevBlock.data, glblBlockNum + 1, prevBlock)
        file.write("bb" + str(prevBlock.blockNum) + ":s -> bb" + str(elseBlock.blockNum) + ":n [label=\"branch\"];\n")
        prevBlock.addNext(elseBlock)
        glblBlockNum += 1

        ifBlock = currentBlock
        currentBlock = elseBlock
        token = getNext()
        if token == tokenTable.index("else"):
            statSequence()
            token = getNext()

        if elseBlock.instructions == "":
            elseBlock.instructions += "|" + str(instructionNum) + ": \\<empty\\>"
            instructionNum += 1
            
        if token != tokenTable.index("fi"):
            SyntaxErr("ifStatement(): missing 'fi'")
        
    else:
        SyntaxErr("ifStatement(): missing 'then'")

    # join block
    elseBlock = currentBlock
    joinBlock = basicBlock({}, glblBlockNum + 1, None)
    joinBlock.join = True
    glblBlockNum = glblBlockNum + 1
    joinInstructStart = instructionNum

    currentBlock = joinBlock
    ifBlock.addNext(currentBlock)
    elseBlock.addNext(currentBlock)
    currentBlock.addPrev(ifBlock)
    currentBlock.addPrev(elseBlock)
    
    # phi
    for varData in ifBlock.data:
        if varData in elseBlock.data:
            if ifBlock.data[varData] != elseBlock.data[varData]:
                currentBlock.data[varData] = instructionNum
                currentBlock.instructions += "|" + str(instructionNum) + ": phi (" + str(ifBlock.data[varData]) + ") (" + str(elseBlock.data[varData]) + ")"
                instructionNum += 1
            else:
                currentBlock.data[varData] = ifBlock.data[varData]
        else:
            currentBlock.data[varData] = ifBlock.data[varData]

    if currentBlock.instructions == "":
            currentBlock.instructions += "|" + str(instructionNum) + ": \\<empty\\>"
            instructionNum += 1

    if elseBlock.instructions == "":
            elseBlock.instructions += "|" + str(instructionNum) + ": \\<empty\\>"
            instructionNum += 1

    ifBlock.instructions += "|" + str(instructionNum) + ": branch [" + str(joinInstructStart) + "]"
    instructionNum += 1

    file.write("bb" + str(ifBlock.blockNum) + ":s -> bb" + str(currentBlock.blockNum) + ":n [label=\"branch\"];\n")
    file.write("bb" + str(elseBlock.blockNum) + ":s -> bb" + str(currentBlock.blockNum) + ":n [label=\"fall-through\"];\n")

def whileStatement():
    global currentBlock, instructionNum, glblBlockNum, glblWhileBlock, firstWhile
    
    prevBlock = basicBlock(currentBlock.data, glblBlockNum + 1, currentBlock)
    glblBlockNum += 1
    currentBlock.addNext(prevBlock)
    file.write("bb" + str(currentBlock.blockNum) + ":s -> bb" + str(prevBlock.blockNum) + ":n;\n")
    currentBlock = prevBlock
    prevBlock = currentBlock

    op = Relation()
    cmpInstruct = instructionNum - 1
    
    token = getNext()
    if token == tokenTable.index("do"):
        # while block
        whileBlock = basicBlock(currentBlock.data, glblBlockNum + 1, currentBlock)
        file.write("bb" + str(currentBlock.blockNum) + ":s -> bb" + str(whileBlock.blockNum) + ":n [label=\"fall-through\"];\n")
        currentBlock.addNext(whileBlock)
        if firstWhile == False:
            whileBlock.addNext(currentBlock)
        currentBlock.join = True
        currentBlock = whileBlock
        instructionNum += 1
        glblBlockNum += 1
        statSequence()

        whileBlock = currentBlock

        # phi
        phiBlock = whileBlock
        if firstWhile != True:
            phiBlock = glblWhileBlock

        replace1 = {}
        replace2 = {}
        phiInstructions = ""
        for varData in prevBlock.data:
            if varData in phiBlock.data:
                if prevBlock.data[varData] != phiBlock.data[varData]:
                    phiInstructions += "|" + " (" + varData +") " + str(instructionNum) + ": phi (" + str(prevBlock.data[varData]) + ") (" + str(currentBlock.data[varData]) + ")"
                    replace1["(" + str(prevBlock.data[varData]) + ")"] = "(" + str(instructionNum) + ")"
                    replace2["(" + str(phiBlock.data[varData]) + ")"] = "(" + str(instructionNum) + ")"
                    prevBlock.data[varData] = instructionNum
                    instructionNum += 1
            else:
                whileBlock.data[varData] = prevBlock.data[varData]
        
        for block in blocks[prevBlock.blockNum: phiBlock.blockNum + 1]:
            for key in replace1:
                block.instructions = block.instructions.replace(key, replace1[key])
            for key in replace2:
                block.instructions = block.instructions.replace(key, replace2[key])
        
        prevBlock.instructions = phiInstructions + prevBlock.instructions

        if firstWhile == True:
            instructNum = ""
            for char in prevBlock.instructions[1:]:
                if char == ':':
                    break
                else:
                    if char.isdigit():
                        instructNum += char

            whileBlock.instructions += "|" + str(instructionNum) + ": branch [" + instructNum + "]"
            file.write("bb" + str(whileBlock.blockNum) + ":s -> bb" + str(prevBlock.blockNum) + ":n [label=\"branch\"];\n")
            instructionNum += 1

        match op:    # checking correct branch operation
            case eql if op == tokenTable.index("=="):
                prevBlock.branchInstruct += "|" + str(cmpInstruct + 1) + ": BEQ (" + str(cmpInstruct) + ") (" 
            case neq if op == tokenTable.index("!="):
                prevBlock.branchInstruct += "|" + str(cmpInstruct + 1) + ": BNE (" + str(cmpInstruct) + ") (" 
            case les if op == tokenTable.index("<"):
                prevBlock.branchInstruct += "|" + str(cmpInstruct + 1) + ": BLT (" + str(cmpInstruct) + ") (" 
            case lte if op == tokenTable.index("<="):
                prevBlock.branchInstruct += "|" + str(cmpInstruct + 1) + ": BLE (" + str(cmpInstruct) + ") (" 
            case gre if op == tokenTable.index(">"):
                prevBlock.branchInstruct += "|" + str(cmpInstruct + 1) + ": BGT (" + str(cmpInstruct) + ") (" 
            case gte if op == tokenTable.index(">="):
                prevBlock.branchInstruct += "|" + str(cmpInstruct + 1) + ": BGE (" + str(cmpInstruct) + ") (" 
            case _:
                SyntaxErr("whileStatement(): unknown operator")

        exitBlock = basicBlock(prevBlock.data, glblBlockNum + 1, prevBlock)
        file.write("bb" + str(prevBlock.blockNum) + ":s -> bb" + str(exitBlock.blockNum) + ":n [label=\"branch\"];\n")
        prevBlock.addNext(exitBlock)
        glblBlockNum += 1
        currentBlock = exitBlock

        if firstWhile == True:
            glblWhileBlock = exitBlock
            firstWhile = False
        else:
            instructNum = ""
            for char in prevBlock.instructions[1:]:
                if char == ':':
                    break
                else:
                    if char.isdigit():
                        instructNum += char

            glblWhileBlock.addNext(prevBlock)
            file.write("bb" + str(glblWhileBlock.blockNum) + ":s -> bb" + str(prevBlock.blockNum) + ":n [label=\"branch\"];\n")
            glblWhileBlock.instructions += "|" + str(instructionNum) + ": branch [" + instructNum + "]"
            instructionNum += 1
            glblWhileBlock = exitBlock

        if whileBlock.instructions == "":
            whileBlock.instructions += "|" + str(instructionNum) + ": \\<empty\\>"
            instructionNum += 1
            
        token = getNext()
        if token != tokenTable.index("od"):
            SyntaxErr("whileStatement(): missing 'od'")
    else:
        SyntaxErr("whileStatement(): missing 'do'")

# Operations
def Expression():
    global sym, buffer, instructionNum
    instructNum = Term()
    token = getNext()
    while token == tokenTable.index("+") or token == tokenTable.index("-"):
        instructNum2 = Term()
        if token == tokenTable.index("+"):
            prevInstruct = elimInstruct(": ADD (" + str(instructNum) + ") (" + str(instructNum2) + ")")
            if prevInstruct == -1:
                currentBlock.instructions += "|" + str(instructionNum) + ": ADD (" + str(instructNum) + ") (" + str(instructNum2) + ")"
                instructNum = instructionNum
                instructionNum += 1
            else:
                instructNum = prevInstruct
        else:
            prevInstruct = elimInstruct(": SUB (" + str(instructNum) + ") (" + str(instructNum2) + ")")
            if prevInstruct == -1:
                currentBlock.instructions += "|" + str(instructionNum) + ": SUB (" + str(instructNum) + ") (" + str(instructNum2) + ")"
                instructNum = instructionNum
                instructionNum += 1
            else:
                instructNum = prevInstruct

        token = getNext()

    if token != None:
        buffer = tokenTable[token] + " " + sym + " " + buffer
        sym = " "

    return instructNum

def Term():
    global sym, buffer, instructionNum
    instructNum = Factor()
    token = getNext()
    while token == tokenTable.index("*") or token == tokenTable.index("/"):
        instructNum2 = Factor()
        if token == tokenTable.index("*"):
            prevInstruct = elimInstruct(": MUL (" + str(instructNum) + ") (" + str(instructNum2) + ")")
            if prevInstruct == -1:
                currentBlock.instructions += "|" + str(instructionNum) + ": MUL (" + str(instructNum) + ") (" + str(instructNum2) + ")"
                instructNum = instructionNum
                instructionNum += 1
            else:
                instructNum = prevInstruct
        else:
            prevInstruct = elimInstruct(": DIV (" + str(instructNum) + ") (" + str(instructNum2) + ")")
            if prevInstruct == -1:
                currentBlock.instructions += "|" + str(instructionNum) + ": DIV (" + str(instructNum) + ") (" + str(instructNum2) + ")"
                instructNum = instructionNum
                instructionNum += 1
            else:
                instructNum = prevInstruct

        token = getNext()

    if token != None:
        buffer = tokenTable[token] + " " + sym + " " + buffer
        sym = " "

    return instructNum

def Factor():
    token = getNext()

    # Designator (id / array)
    if token == tokenTable.index("idToken"):
        if not tokenName in currentBlock.data:      #currentBlock.data[tokenName] == 0
            return(idWarning(tokenName))
        else:
            if isinstance(currentBlock.data[tokenName], list):  # array case
                idxs = arrayGetIndex()
                element = arrayGetElement(currentBlock.data[tokenName], idxs)
                if element == 0:
                    instructZero = idWarning(tokenName)
                    arrayStrElement(currentBlock.data[tokenName], idxs, instructZero)
                    return(instructZero)
                return element

            return currentBlock.data[tokenName]
    
    # Number
    elif checkFor(token, tokenTable.index("numberToken")):
        if not val in constants:
            return(makeConst(val))
        else:
            return constants[val]

    # Expression
    elif token == tokenTable.index("("):
        Expression()
        token = getNext()
        if token != tokenTable.index(")"):
            SyntaxErr("Factor(): missing ')'")
        else:
            return instructionNum - 1

    # funcCall
    elif token == tokenTable.index("call"):
        funcCall()
        return instructionNum - 1
    
    else:
        SyntaxErr("Factor(): invalid symbol '" + str(tokenTable[token]) + "'")

    return 

def Relation():
    global instructionNum
    first = Expression()
    token = getNext()
    second = Expression()
    currentBlock.instructions += "|" + str(instructionNum) + ": CMP (" + str(first) + ") (" + str(second) + ")"
    instructionNum += 1
    return token 

bb0 = basicBlock({}, 0, None)     # constants
bb1 = basicBlock({}, 1, bb0)        # first block
bb0.addNext(bb1)
currentBlock = bb1

file.write("digraph G {\n")
file.write("bb0:s -> bb1:n ;\n")

Computation()
if currentBlock.instructions == "":
    currentBlock.instructions += "|" + str(instructionNum) + ": \\<empty\\>"
    instructionNum += 1
if bb0.instructions == "":
    bb0.instructions += "|" + str(instructionNum) + ": \\<empty\\>"

for block in blocks:
    if block.branchInstruct != "":
        instructNum = ""
        if block.nexts[1].instructions == "":
            block.nexts[1].instructions += "|" + str(instructionNum) + ": \\<empty\\>"
            instructionNum += 1
        else:
            branchInstructs = block.nexts[1].instructions[1:]
            for char in branchInstructs:
                if char == ':':
                    break
                else:
                    if char.isdigit():
                        instructNum += char
                    

        block.instructions += block.branchInstruct + instructNum + ")"
    block.print()
file.write("}")
file.close()
inputfile.close()

# Array issues
# dim >= 3 breaks block deepcopy
# dim >= 3 creates references instead of new lists
# phi????
# call inputNum????