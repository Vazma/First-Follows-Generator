##
#Alexis Vázquez
#Compiladores
#Generador First Follows
##

#Initialize arrays, variables and sets to be used
productions = []
productionsParsed = {}
headers = []
terminals = []
FIRST = {}
FOLLOW = {}
last = ''
isLL = True

#Function to get non terminals or headers
def getHeaders():
    for i in range(0, len(productions)):
        #split the array into it's elements to obtain separate productions
        prod = productions[i].split()
        #check if the first element in the production is already a header, if not, add it to the list
        if prod[0] not in headers:
            headers.append(prod[0])

#Function to get terminals
def getTerminals():
    for i in range(0, len(productions)):
        #split the array into it's elements to obtain separate productions
        prod = productions[i].split()
        #another for loop iterates over the separated productions to add unique values to the array, also ignoring the arrow
        for j in range(0, len(prod)):
            if prod[j] not in headers and prod[j] not in terminals and prod[j] != "->" and prod[j] != "'":
                terminals.append(prod[j])   

#Funtion to parse productions
def parseProductions():
    #create sets for every header
    for header in headers:
        productionsParsed[header] = []

    #fill the sets for every header with the possible outcomes based in the grammar
    for production in productions:
        splitProd = production.split(" -> ")
        #remove '\n' that appears when reading file
        withoutBr = splitProd[1].split("\n")
        productionsParsed[splitProd[0]].append(withoutBr[0])

#Function to get the "first" generations
def getFirst(prod, auxprod):
    #start the "first" variable
    f = set()

    if prod == auxprod:
        global isLL
        isLL = False
        
    #Check if the production is part of the headers or non-terminals
    elif prod in headers:
        #Chech productions parsed to obtain array of individual productions based on header
        prodOptions = productionsParsed[prod]

        #Iterate over the different individual productions
        for prodOption in prodOptions:
            #Recursive method to check the next option in the terminals
            if prodOption != "' '":
                sp = prodOption.split(' ')
                fAux = getFirst(sp[0], prod)
                f = f | fAux
            else:
                fAux = getFirst("' '", prod)
                f = f | fAux

    #Check if the production is part of the terminals, the case where it returns the terminal       
    elif prod in terminals:
        f = {prod}
    
    #Check if the production is epsilon, if it's the case, return it but don't include it in the terminals
    elif prod == "' '" or prod == '@':
        f = {"' '"}

    #Else case to iterate in composed productions
    else:
        splitted = prod.split(' ')
        fAux = getFirst(splitted[0], "auxprod")
            #check if epsilon is in the composed production, else return the current production
        if "' '" in fAux:
            i = 1
            #Start cycle to iterate over the productions
            while "' '" in fAux:
                #From te auxiliary first, check for epsilon
                f = f | (fAux - {"' '"})
                #Check if terminal or end of composed production
                if splitted[i:] in terminals:
                    f = f | {splitted[i:]}
                    break
                elif splitted[i:] == '':
                    f = f | {"' '"}
                    break
                #Recursive method to ceck again the remaining productions by the same header
                fAux = getFirst(splitted[i:], "auxprod")
                f = f | fAux - {"' '"}
                i += 1
        else:
            f = f | fAux  

    return f

#Function to get the "follow" generations
def getFollow(header):
    #start the "follow" variable
    f = set()
    #get the key-value dictionary items
    prods = productionsParsed.items()
    #RULE 1, apply the special character to the first element
    if header == firstHeader:
        f = f | {'$'}
    for head,production in prods:
        #divide the productins in individual elements
        for singProd in production:
            #transform epsilon in a different character
            #if singProd == "' '":
            #    singProd = '@'
            splitted = singProd.split(" ")
            #search in individual symbols or characters
            for symb in splitted:
                #search for the following item if it matches the desired header
                if symb==header:
                    following = splitted[splitted.index(symb) + 1:]
                    #search if there are no more productions
                    if not following:
                        #RULE 3, if the head and the header match, continues, otherwise it would iterate over and over again
                        if head==header:
                            continue
                        #RULE 3, if they don't match, it gets the follow of the head
                        else:
                            f = f | getFollow(head)
                    else:
                        #RULE 2
                        f2 = getFirst(following[0], "auxprod")
                        #RULE 2 if the first of the following element is epsilon, remove it
                        if "' '" in f2:
                            f = f | f2-{"' '"}
                            f = f | getFollow(head)
                        #RULE 2, iterate over the getFirst() function to obtain the first of a header or return the terminal if it's the case
                        else:
                            f = f | f2                        
    
    return f

#Function to define LL rules
def LLRules():
    global isLL
    for header in headers:
        aux = []
        if (len(productionsParsed[header]) >= 2):
            for prod in productionsParsed[header]:
                splitted = prod.split()
                if splitted[0] in aux:
                    isLL = False
                aux.append(splitted[0])

#Function to check if it is ll
def getLL():
    LLRules()
    return "yes" if isLL else "no"
    
#Function to receive an input file if the option number 1 is selected
def lexicalAnalyzerConsoleFile():
    #input file name
    fileName = input("\nFilename: ")
    #open file and handle error if file doesn't exists
    try:
        OFile = open(fileName, "r")
    except:
        print("File not found")
    
    lines = str(OFile.readline()).split()

    #Append the productions to the array "productions"
    for i in range(0, int(lines[0])):
        productions.append(OFile.readline())
    
#Function to receive the productions from an input if option 2 is selected
def lexicalAnalyzerConsoleCMD():
    amount = int(input("\nHow many productions are?(write them after) "))
    
    #Appending the input to the productions while reading them
    for i in range(0, amount):
        productions.append(input())

# lexical analyzer Function
def lexicalAnalyzer():
    #Usage options
    print("First Follows Generator\n")
    print("There are two ways of using the generator, from file and from command line")
    option = input("Select the option: (1. From file, 2. From command line.) ")
    if option == "1": 
        lexicalAnalyzerConsoleFile()
    else:
        lexicalAnalyzerConsoleCMD()

    #Execute the functions to find elements and productions
    getHeaders()
    getTerminals()
    parseProductions()

# first follows generator function
def firstFollows():

    #Start the First and Follow arrays with empty sets
    for header in headers:
        FIRST[header] = set()
    for header in headers:
        FOLLOW[header] = set()

    #fill the 'FIRST' set following the rules
    for header in headers:
        FIRST[header] = FIRST[header] | getFirst(header, "auxprod")
    
    #Prepare the default case for the first FOLLOW production
    FOLLOW[firstHeader] = FOLLOW[firstHeader] | {'$'}
    #fill the 'FOLLOW' set following the rules
    for header in headers:
        FOLLOW[header] = FOLLOW[header] | getFollow(header)


##      Start running

#Execute lexical analyzer function
lexicalAnalyzer()

#Find the first header to later be used in the "follows" part
firstHeader = headers[0]

#Execute the firstFollows function
firstFollows()


#Test prints
#print("productions")
#print(productions)

#Print formatted elements
for header in headers:
    print(header + " \t=> FIRST = " + str(FIRST[header]) + "," + "\t FOLLOW = " + str(FOLLOW[header]))

print("LL(1)? " + getLL())

