import ply.lex as lex
import ply.yacc as yacc
import sys

# BAJURNY WOJCIECH 268515
# KOMPILATOR
# JFTT INA 2023/2024

#pierwsza wolna komórka pamięci
mem_index = 0

#numer rozkazu
k = 0


#tablica procedur
in_procedure = 'MAIN'
procedures = []
def insert_procedure_into_table(name, return_adress, variable_adresses, variables_in_declaration):
    procedures.append([name, return_adress, variable_adresses, variables_in_declaration])

def get_procedure_return_address_by_name(name):
    global procedures
    for i in range(len(procedures)):
        if name == procedures[i][0]:
            return procedures[i][1]
        

def get_addresses_for_variables(name):
    global procedures
    for i in range(len(procedures)):
        if name == procedures[i][0]:
            return procedures[i][2]



#Tablica symboli - informacje, nazwa, pamięć, czy tablica - to do błędów w przyszłości np. oraz tablica procedur
symbol_table = []

def insert_symbol_into_table(name, mem, is_arr, is_ref, curr_proc, is_initialized):
    symbol_table.append([name, mem, is_arr, is_ref, curr_proc, is_initialized])

def get_symbol_by_name(name):
    global symbol_table
    for i in range(len(symbol_table)):
        if name == symbol_table[i][0]:
            return i

def get_symbol_by_memory(mem):
    global symbol_table
    for i in range(len(symbol_table)):
        if mem == symbol_table[i][1]:
            return i

def get_mem_id_by_name(name):
    global symbol_table
    for i in range(len(symbol_table)):
        if name == symbol_table[i][0]:
            return symbol_table[i][1]
        

def get_mem_id_by_name_all_occurences(name):
    global symbol_table
    occurrences = []

    for i in range(len(symbol_table)):
        if name == symbol_table[i][0]:
            occurrences.append(symbol_table[i][1])

    return occurrences

def get_mem_id_by_name_in_prog(name):
    global symbol_table
    for i in range(len(symbol_table)):
        if name == symbol_table[i][0] and symbol_table[i][4] == 'MAIN':
            return symbol_table[i][1]    

def get_name_by_mem_id(mem):
    global symbol_table
    for i in range(len(symbol_table)):
        if mem == symbol_table[i][1]:
            return symbol_table[i][0]
        
def check_if_reference(name):
    global symbol_table
    for i in range(len(symbol_table)):
        if name == symbol_table[i][0]:
            if symbol_table[i][3] == True:
                return True
            else:
                return False
            
def check_if_arr(name):
    global symbol_table
    for i in range(len(symbol_table)):
        if name == symbol_table[i][0]:
            if symbol_table[i][2] == True:
                return True
            else:
                return False
            
def get_name_ref_proc(name, is_ref, current_proc):
    global symbol_table, in_procedure
    for i in range(len(symbol_table)):
        if name == symbol_table[i][0]:
            if is_ref == symbol_table[i][3]:
                if current_proc == in_procedure:
                    return symbol_table[i][1]

def check_if_arr_by_mem(mem):
    global symbol_table
    for i in range(len(symbol_table)):
        if mem == symbol_table[i][1]:
            if symbol_table[i][2] == True:
                return True
            else:
                return False

def initialize_var_by_mem(mem):
    global symbol_table
    for i in range(len(symbol_table)):
        if mem == symbol_table[i][1]:
            symbol_table[i][5] = True

def check_if_initialized(mem):
    global symbol_table
    for i in range(len(symbol_table)):
        if mem == symbol_table[i][1]:
            if symbol_table[i][5]:
                return True
            else:
                return False


        

#Obsługa rejestrów
#dana stała wartość do danego rejestru
def load_value_into_register(value, register):
    #global k
    result_code = ''
    while value != 0:

        if value % 2 == 0:
            result_code = 'SHL {}\n'.format(register) + result_code
            
            value = value/2
        else:
            result_code = 'INC {}\n'.format(register) + result_code
            
            value = value - 1
    result_code = 'RST {}\n'.format(register) + result_code
    
    return result_code

#Zmienna do rejestru
def load_variable_into_register(address, register): #zwrócona wartość jest w a!
    global symbol_table,k
    result_code = ''
    result_code += load_value_into_register(address,register)
    result_code += 'LOAD {}\n'.format(register) #to ładuje do a wartość spod tej komórki pamięci 
    
    return result_code
    
#sklej kod w całość - chyba ok?
def modify_instructions(input_string):
    lines = input_string.split('\n')
    labels = {}

    for i, line in enumerate(lines):
        parts = line.split()
        if len(parts) == 3:
            # Store the index of lines with 3 substrings
            labels[parts[0]] = i

    for i, line in enumerate(lines):
        parts = line.split()
        if len(parts) == 2 and parts[0] == 'JUMP':
            # Modify 'JUMP foo' to 'JUMP index'
            label = parts[1]
            if label in labels:
                lines[i] = f'JUMP {labels[label]}'

    for i, line in enumerate(lines):
        parts = line.split()
        if len(parts) == 3:
            # Remove the first substring (label)
            lines[i] = ' '.join(parts[1:])

    modified_string = '\n'.join(lines)

    code_split = modified_string.split('\n')
    #code_split = modified_string.split('\n')

    # Iterate through each line in code_split
    for i in range(len(code_split)):
        line = code_split[i]

        if ' p' in line:
            txt, n = line.split(' p')[0], int(line.split(' p')[1])
            
            new_value = f'{txt} {i + n}'
            
            code_split[i] = new_value

        elif ' m' in line:
            txt, n = line.split(' m')[0], int(line.split(' m')[1])
            
            new_value = f'{txt} {i - n}'
            
            code_split[i] = new_value
    modified_code = '\n'.join(code_split)
    
    return modified_code

def print_symbol_table():
    global symbol_table
    print(len(symbol_table))
    for i in range(len(symbol_table)):
        for j in range(len(symbol_table[0])):
            print(symbol_table[i][j])



#LEXER chyba działa 

tokens = (
    'ASSIGN', 'ADD', 'SUB', 'MUL', 'DIV', 'MOD',                #:=, +, -, *, /, % 
    'LT', 'GT', 'LE', 'GE', 'EQ', 'NEQ',                        #<. >, <=, >=, =, !=
    'LBRACKET', 'RBRACKET', 'LSQUAREBRACKET', 'RSQUAREBRACKET', #(, ), [, ]
    'WRITE', 'READ',                                            #write (output), read (input)
    'WHILE', 'DO', 'ENDWHILE', 'REPEAT', 'UNTIL',               #pętle
    'IF', 'THEN', 'ELSE', 'ENDIF',                              #ify
    'SEMICOLON', 'COLON', 'COMMA',                              # ; : ,  
    'PROCEDURE', 'IS', 'IN','BEGIN','END', 'PROGRAM',                  # obsluga programu 
    'pidentifier', 'num', 'T',                                  # zmienne i liczby
    'COM'                                                       # komentarz??            
)

t_ASSIGN = r':='
t_ADD = r'\+'
t_SUB = r'\-'
t_MUL = r'\*'
t_DIV = r'\/'
t_MOD = r'\%'
t_LT = r'\<'
t_GT = r'\>'
t_LE = r'\<\='
t_GE = r'\>\='
t_EQ = r'\='
t_NEQ = r'\!\='
t_LBRACKET = r'\('
t_RBRACKET = r'\)'
t_LSQUAREBRACKET = r'\['
t_RSQUAREBRACKET = r'\]'
t_WRITE = r'WRITE'
t_READ = r'READ'
t_WHILE = r'WHILE'
t_DO = r'DO'
t_ENDWHILE = r'ENDWHILE'
t_REPEAT = r'REPEAT'
t_UNTIL = r'UNTIL'
t_IF = r'IF'
t_THEN = r'THEN'
t_ELSE = r'ELSE'
t_ENDIF = r'ENDIF'
t_SEMICOLON = r';'
t_COLON = r':'
t_COMMA = r'\,'
t_PROCEDURE = r'PROCEDURE'
t_IS = r'IS'
t_IN = r'IN'
t_BEGIN = r'BEGIN'
t_END = r'END'
t_PROGRAM = r'PROGRAM'
t_ignore = ' \t'
t_T = r'T' #o co chodzi??

#komentarz


def t_COM(t):
    r'\#.*\n'
    pass
def t_num(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

def t_pidentifier(t):
    r'[_a-z]+'
    t.value = str(t.value)
    return t

def t_newline(t):
    r'\n+'
    t.lexer.lineno += t.value.count('\n')


def t_error(t):
    print('\nNielegalny znak: {0:} w linii {1:}'.format(t.value[0], t.lexer.lineno))
    t.lexer.skip(1)

def build_lex():
    return lex.lex()



#PARSER

precedence = (
    ('left', 'ADD', 'SUB'),
    ('left', 'MUL', 'DIV', 'MOD')
)


def p_programall_proceduresmain(p):
    'program_all : procedures main'
    #global k
    #procedures_length = len(p[1].split('\n'))
    #code = 'JUMP {}\n'.format(procedures_length)
    global in_procedure,symbol_table
    in_procedure = 'MAIN'
    code = ''
#    for i in range(len(symbol_table)):
#        for j in range(len(symbol_table[0])):
#            print(symbol_table[i][j])
    if p[1]:
        procedures_length = len(p[1].split('\n'))
        code = 'JUMP {}\n'.format(procedures_length)
        code += p[1]
    code += p[2]

    modified_code = modify_instructions(code)



    #print_symbol_table()
    p[0] = modified_code + 'HALT'
    #k += 1


def p_procedures_declarations(p):
    'procedures : procedures PROCEDURE proc_head IS declarations IN commands END'
    global in_procedure
    in_procedure = 'MAIN'
    return_address = p[3][0]
    label = p[3][1]
    code = p[1] + label + " " + p[7]
    code += load_value_into_register(return_address, 'h')
    code += 'LOAD h\n'
    code += 'JUMPR a\n'
    p[0] = code


def p_procedures_nodeclarations(p):
    'procedures : procedures PROCEDURE proc_head IS IN commands END'
    global in_procedure
    in_procedure = 'MAIN'
    return_address = p[3][0]
    label = p[3][1]
    code = p[1] + label + " " + p[6]
    code += load_value_into_register(return_address, 'h')
    code += 'LOAD h\n'
    code += 'JUMPR a\n'
    p[0] = code
    #cos zrob

def p_procedures_nothing(p):
    'procedures : '
    p[0] = ''

def p_main_declarations(p):
    'main : PROGRAM IS declarations IN commands END'
    p[0] = p[5]

def p_main_nodeclarations(p):
    'main : PROGRAM IS IN commands END'
    p[0] = p[4]

def p_commands_rec(p):
    'commands : commands command'
    p[0] = p[1] + p[2]

def p_commands_one(p):
    'commands : command'
    p[0] = p[1]
 

    #Assignment
def p_command_assign(p):
    'command : identifier ASSIGN expression SEMICOLON' # w id jest adres zmiennej w expression jest wartosc ktora jest aktualnie w rejestrze A
    global symbol_table,k,in_procedure                
    code = ''
    #print(p[1], in_procedure)
    if in_procedure!='MAIN':
        code += p[3]
        code += 'PUT c\n'
        if len(p[1]) == 5:
            code += load_value_into_register(p[1][0], 'g')
            if p[1][3]:
                code +='LOAD g\n'
                code +='PUT g\n'
            code += load_variable_into_register(p[1][2],'h')
            code += 'ADD g\n'
            code += 'PUT b\n'
            code += 'GET c\n'
            code += 'STORE b\n'

        elif len(p[1]) == 4:
            code += load_value_into_register(p[1][0], 'g')
            if p[1][2]:
                code +='LOAD g\n'
                code +='PUT g\n'
            code += load_value_into_register(p[1][3],'a')
            code += 'ADD g\n'
            code += 'PUT b\n'
            code += 'GET c\n'
            code += 'STORE b\n'

        else:
            code += load_value_into_register(p[1][0],'b')
            if p[1][2]:
                code+='LOAD b\n'
                code+='PUT b\n'
                code+='GET c\n'
            code += 'STORE b\n'

    else:                                        
        if len(p[1]) == 5:                      #identifier to tablica indeksowana zmienną
            code += load_value_into_register(p[1][0], 'g')
            code += load_variable_into_register(p[1][2], 'h')
            code += 'PUT h\n'
            code += 'GET g\n'
            code += 'ADD h\n'
            code += 'PUT b\n'
            code += p[3]
        else:                                   #identifier to zmienna lub tablica indeksowa nstałą
            code += p[3]
            code += load_value_into_register(p[1][0],'b') 
        code += 'STORE b\n'

    initialize_var_by_mem(p[1][0])
    p[0] = code

    #IFy
def p_command_ifelse(p):
    'command : IF condition THEN commands ELSE commands ENDIF'
    #global k
    code = p[2]
    commands_true_length = len(p[4].split('\n'))+1
    commands_false_length = len(p[6].split('\n'))
    code += 'JPOS {}\n'.format('p'+str(commands_true_length))
    
    code += p[4]
    code += 'JUMP {}\n'.format('p'+str(commands_false_length))
    
    code += p[6]
    p[0] = code

def p_command_if(p):
    'command : IF condition THEN commands ENDIF'
    #global k
    code = p[2]
    commands_length = len(p[4].split('\n'))
    code += 'JPOS {}\n'.format('p' + str(commands_length))
    
    code += p[4]
    p[0] = code

    #LOOP
def p_command_while(p):
    'command : WHILE condition DO commands ENDWHILE'
    #global k
    code = p[2]
    condition_length = len(p[2].split('\n'))
    commands_length = len(p[4].split('\n'))
    length = condition_length + commands_length
    code = code + 'JPOS {}\n'.format('p'+str(commands_length+1))
    #k=k+1
    code += p[4]
    code += 'JUMP {}\n'.format('m'+str(length-1))
    #k=k+1
    p[0] = code

def p_command_repeat(p):
    'command : REPEAT commands UNTIL condition SEMICOLON'
    #global k
    code = p[2]
    code += p[4]
    condition_length = len(p[4].split('\n'))
    commands_length = len(p[2].split('\n'))
    length = condition_length + commands_length
    code += 'JPOS {}\n'.format('m'+str(length))
    #k=k+1
    p[0] = code


#INPUT/OUTPUT
#Najpierw read - w a mam wartość reada, potem ładuję do rejestru b adres identifiera i na końcu Store b czyli wartość a do komórki o nr = wartość b 
def p_command_in(p):
    'command : READ identifier SEMICOLON' #w identifier jest adres teraz
    #global k                             #read tylko do maina i normalny xdd nie ma co sie bawić przesadzać
    code = ''
    code = 'READ\n'
    
                                            #TO DO POPRAWY!!!
    #if in_procedure:
    #    code += load_value_into_register(p[2][0],'b')
    code += load_value_into_register(p[2][0],'b') 
    code += 'STORE b\n'
    initialize_var_by_mem(p[2][0])
    
    p[0] = code

def p_command_out(p):
    'command : WRITE value SEMICOLON'
    global in_procedure
    code = ''
    if in_procedure!='MAIN':
        if len(p[2]) == 5:
            code += load_variable_into_register(p[2][0],'g')
            code += 'PUT g\n'
            """ if p[2][3]:
                code += 'LOAD g\n'
                code += 'PUT g\n' """
            code += load_variable_into_register(p[2][2],'h')
            code += 'ADD g\n'
            code += 'LOAD a\n'
        elif len(p[2]) == 4:
            code += load_variable_into_register(p[2][0],'g')
            code += 'PUT g\n'
            """ if p[2][2]:
                code += 'LOAD g\n'
                code += 'PUT g\n' """
            code += load_value_into_register(p[2][3],'a')
            code += 'ADD g\n'
        else:
            if p[2][1]:
                code += load_variable_into_register(p[2][0], 'c')
                if p[2][2]:
                    code+='LOAD a\n'
            else:
                code += load_value_into_register(p[2][0],'a') #p[2][0] to wartość stałeje
    else:
        if len(p[2]) == 5:
            code += load_value_into_register(p[2][0], 'g')
            code += load_variable_into_register(p[2][2], 'h')
            code += 'ADD g\n'
            code += 'LOAD a\n'
        else:
            if p[2][1]: #value is a variable
                code += load_variable_into_register(p[2][0],'c') #p[2][0] to adres zmiennej
            else: #value is a number
                code += load_value_into_register(p[2][0],'a') #p[2][0] to wartość stałeje
    
    code += 'WRITE\n'
    
    p[0] = code
    



def p_command_proccall(p):
    'command : proc_call SEMICOLON' #tu global mem_index przesun tez o 1 bo bedziemy assignowac dla powrotu ?
    code = p[1][0]
    return_adress = p[1][1]
    code += load_value_into_register(return_adress,'b')
    code += load_value_into_register(4,'a')
    code += 'STRK h\n'
    code += 'ADD h\n'
    code += 'STORE b\n'
    code += 'JUMP {}\n'.format(p[1][2]) #tu nr rozkazu w ktorym zaczyna sie procedura
    p[0] = code

def p_prochead_pidentifier(p):
    'proc_head : pidentifier LBRACKET args_decl RBRACKET' 
    global in_procedure, mem_index, symbol_table
    in_procedure = p[1]

    no_of_adresses = p[3][0]                                 #ale wydaje sie ok
    variable_addresses = []
    variables_in_declaration = p[3][1]
    arrays = p[3][2]
    #   #cos takiego jakie są w proc headzie i w commandach look for them, jak sa to wtedy load from pointer?
    for i in range(no_of_adresses):
        variable_addresses.append(mem_index)
        mem_index = mem_index + 1
    insert_procedure_into_table(p[1],mem_index, variable_addresses, variables_in_declaration)
    mem_index = mem_index+1 #adres powrotu
    return_address = get_procedure_return_address_by_name(p[1])

    #wstaw te z args_decl do tablicy symboli
    for i in range(len(variables_in_declaration)):
            if variables_in_declaration[i] in arrays:
                insert_symbol_into_table(variables_in_declaration[i],variable_addresses[i],True,True, p[1], True)
                initialize_var_by_mem(variable_addresses[i]) # tu dodalem args_decl jako takie które mają is_ref = True
            else:
                insert_symbol_into_table(variables_in_declaration[i],variable_addresses[i],False,True, p[1], True)
                initialize_var_by_mem(variable_addresses[i]) # tu dodalem args_decl jako takie które mają is_ref = True
                                                                                               # Przekaż pidentifier w górę i potem zmienna - curr procedure
    p[0] = (return_address, p[1])

def p_proccall_pidentifier(p):
    'proc_call : pidentifier LBRACKET args RBRACKET'
    global symbol_table, in_procedure
    return_address = get_procedure_return_address_by_name(p[1]) #i biore liste adresow z procedures[] dla danej procedury okej i przypisuje tym adresom
    if not return_address:
        print('błąd: niezdefiniowana procedura', p[1], 'w linii', p.lineno(1))
        exit(1)
    if p[1] == in_procedure:
        print('błąd: niewłaściwe użycie procedury', p[1], 'w linii', p.lineno(1))
        exit(1)
    variable_memory_adresseses = p[3]                           #w pamieci wartosci komorek pamieci legitne
    pointers = get_addresses_for_variables(p[1])

    if len(variable_memory_adresseses) != len(pointers):
        print('błąd: zła liczba argumentów procedury', p[1], 'w linii', p.lineno(1))

    
    #do error handlingu
    for m in range(len(variable_memory_adresseses)):
        a = check_if_arr_by_mem(pointers[m])
        b = check_if_arr_by_mem(variable_memory_adresseses[m])
        if a!=b:
            print('błąd: niewłaściwe parametry procedury', p[1], 'w linii', p.lineno(1))
            exit(1)

    code = ''
    for i in range(len(variable_memory_adresseses)):
        code+=load_value_into_register(pointers[i],'b')
        code+=load_value_into_register(variable_memory_adresseses[i],'a')
        if in_procedure!='MAIN':
            for k in range(len(symbol_table)):
                if symbol_table[k][1] == variable_memory_adresseses[i]: 
                    if symbol_table[k][3]:
                        code+='LOAD a\n'
        code+='STORE b\n'

    p[0] = code, return_address, p[1]

def p_argsdecl_argsdeclpid(p): # Tutaj jakby chodzi o to, które zmienne będziemy traktować jako globalne w procedurze? to jakas flaga do nich set
    'args_decl : args_decl COMMA pidentifier'
    p[0] = (p[1][0] + 1, p[1][1] + [p[3]], p[1][2] + [])

    

def p_argsdecl_argsdeclpidarr(p):
    'args_decl : args_decl COMMA T pidentifier'
    p[0] = (p[1][0] + 1, p[1][1] + [p[4]], p[1][2] + [p[4]])



def p_argsdecl_pid(p): #co tu zrobić?
    'args_decl : pidentifier'
    p[0] = (1, [p[1]], [])

def p_argsdecl_pidArr(p):
    'args_decl : T pidentifier'
    p[0] = (1, [p[2]], [p[2]])


def p_args_argspid(p):
    'args : args COMMA pidentifier'
    global in_procedure, symbol_table
    if in_procedure == 'MAIN':
        for i in range(len(symbol_table)):
            if symbol_table[i][0] == p[3]:              #jezeli jest z maina to no normalnie adres maina przekaz tak jak bylo
                if symbol_table[i][4] == in_procedure:
                    p[1].append(symbol_table[i][1])
    elif in_procedure != 'MAIN':
        for i in range(len(symbol_table)):
            if symbol_table[i][0] == p[3]: 
                if symbol_table[i][4] == in_procedure and symbol_table[i][3]: #jesli przekazujemy parametry z danej funkcji w jakiej jestesmy do drugiej
                    p[1].append(symbol_table[i][1])
                elif symbol_table[i][4] == in_procedure and symbol_table[i][3]==False: #przekazywanie lokalnej zmiennej z funkcji (nie parametru)
                    p[1].append(symbol_table[i][1])
    p[0] = p[1]


def p_args_pid(p): #sprawdz czy tablica i w zaleznosci dodaj taki a taki idk nie wiem kurrde
    'args : pidentifier'
    global in_procedure, symbol_table
    if in_procedure == 'MAIN':
        for i in range(len(symbol_table)):
            if symbol_table[i][0] == p[1]:              #jezeli jest z maina to no normalnie adres maina przekaz tak jak bylo
                if symbol_table[i][4] == in_procedure:
                    p[1] = symbol_table[i][1]
    elif in_procedure != 'MAIN':
        for i in range(len(symbol_table)):
            if symbol_table[i][0] == p[1]: 
                if symbol_table[i][4] == in_procedure and symbol_table[i][3]: #jesli przekazujemy parametry z danej funkcji w jakiej jestesmy do drugie
                    p[1] = symbol_table[i][1]
                elif symbol_table[i][4] == in_procedure and symbol_table[i][3]==False: #przekazywanie lokalnej zmiennej z funkcji (nie parametru)
                    p[1] = symbol_table[i][1]
    p[0] = [p[1]]
    



def p_declarations_decpid(p):
    'declarations : declarations COMMA pidentifier'
    global symbol_table, mem_index, in_procedure
    for i in range(len(symbol_table)):
        if symbol_table[i][0] == p[3] and symbol_table[i][4] == in_procedure and symbol_table[i][3] == True:
            print('błąd: powtórne użycie identyfikatora', p[3], 'w linii', p.lineno(2))
            exit(1)

    insert_symbol_into_table(p[3],mem_index,False, False, in_procedure, False)
    mem_index = mem_index + 1

def p_declarations_decpidarr(p):
    'declarations : declarations COMMA pidentifier LSQUAREBRACKET num RSQUAREBRACKET'
    global symbol_table, mem_index, in_procedure
    for i in range(len(symbol_table)):
        if symbol_table[i][0] == p[3] and symbol_table[i][4] == in_procedure and symbol_table[i][3] == True:
            print('błąd: powtórne użycie identyfikatora', p[3], 'w linii', p.lineno(2))
            exit(1)
    insert_symbol_into_table(p[3],mem_index,True, False, in_procedure, False)
    mem_index = mem_index + p[5]

def p_declarations_pid(p):
    'declarations : pidentifier'
    global symbol_table, mem_index, in_procedure
    for i in range(len(symbol_table)):
        if symbol_table[i][0] == p[1] and symbol_table[i][4] == in_procedure and symbol_table[i][3] == True:
            print('błąd: powtórne użycie identyfikatora', p[3], 'w linii', p.lineno(2))
            exit(1)
    insert_symbol_into_table(p[1],mem_index,False, False, in_procedure, False)
    mem_index = mem_index + 1

def p_declarations_pidarr(p):
    'declarations : pidentifier LSQUAREBRACKET num RSQUAREBRACKET'
    global symbol_table, mem_index, in_procedure
    for i in range(len(symbol_table)):
        if symbol_table[i][0] == p[1] and symbol_table[i][4] == in_procedure and symbol_table[i][3] == True:
            print('błąd: powtórne użycie identyfikatora', p[3], 'w linii', p.lineno(2))
            exit(1)
    insert_symbol_into_table(p[1],mem_index,True, False, in_procedure, False)
    mem_index = mem_index + p[3]

def p_expression_value(p):
    'expression : value'
    global symbol_table, in_procedure
    code = ''
    if in_procedure != 'MAIN':
        if len(p[1]) == 5:
            code += load_value_into_register(p[1][0], 'g')
            if p[1][3]:
                code +='LOAD g\n'
                code +='PUT g\n'
            code += load_variable_into_register(p[1][2],'h')
            code += 'ADD g\n'
            code += 'LOAD a\n'
        elif len(p[1]) == 4:
            code += load_value_into_register(p[1][0], 'g')
            if p[1][2]:
                code +='LOAD g\n'
                code +='PUT g\n'
            code += load_value_into_register(p[1][3], 'a')
            code += 'ADD g\n'
            code += 'LOAD a\n'
        else:
            if p[1][1]:
                code += load_variable_into_register(p[1][0],'c')
                if p[1][2]:
                    code += 'LOAD a\n'
            else:
                code += load_value_into_register(p[1][0], 'a')
    else:
        if len(p[1]) == 5: #czy jest tablica indeksowana zmienną
            code += load_value_into_register(p[1][0],'g') #pierwszy indeks tablicy w g
            code += load_variable_into_register(p[1][2],'h') #w h jest adres zmiennej ktora jest w [], a w a jest jej wartośc
            code += 'ADD g\n'  #dodaj g do wartosci
            code += 'PUT c\n'  #odloz adres szukanego elementu do c
            code += 'LOAD c\n' # zaladuj z adresu do a 
        else:               #w.p.p
            if p[1][1]:     #value to zmienna lub tablica indeksowana stałą
                code += load_variable_into_register(p[1][0],'c') 
            else:           #value to stała
                code += load_value_into_register(p[1][0],'a')
    p[0] = code


#MATHS
def p_expression_add(p): #chyba działa, spaghetti code 
    'expression : value ADD value'
    global in_procedure
    code = ''
    if in_procedure != 'MAIN':
        if len(p[1]) == 5 and len(p[3])==5:
            code += load_value_into_register(p[1][0], 'g')
            if p[1][3]:
                    code +='LOAD g\n'
                    code +='PUT g\n'
            code += load_variable_into_register(p[1][2], 'h')
            if p[1][4]:
                code +='LOAD a\n'
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT c\n'
            code += load_value_into_register(p[3][0], 'g')
            if p[3][3]:
                    code +='LOAD g\n'
                    code +='PUT g\n'
            code += load_variable_into_register(p[3][2], 'h')
            if p[3][4]:
                code +='LOAD a\n'
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'ADD c\n'
        else:    
            if p[1][1] and p[3][1]:
                if len(p[1]) == 5 and len(p[3]) != 5:
                    code += load_value_into_register(p[1][0], 'g')
                    if p[1][3]:
                        code +='LOAD g\n'
                        code +='PUT g\n'
                    code += load_variable_into_register(p[1][2], 'h')
                    if p[1][4]:
                        code +='LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                    ### teraz obsluz jak drugi war

                    """  if len(p[3]) == 4:
                        code += load_value_into_register(p[1][0], 'g')
                        if p[1][2]:
                            code +='LOAD g\n'
                            code +='PUT g\n'
                        code += load_value_into_register(p[1][3],'a')
                        code += 'ADD g\n'
                        code += 'LOAD a\n' 
                    else:                   """
                    code += load_variable_into_register(p[3][0], 'd')
                    if p[3][2]:
                        code +='LOAD a\n'
                    code += 'ADD c\n'
                elif len(p[1]) != 5 and len(p[3]) == 5:
                    code += load_value_into_register(p[3][0], 'g')
                    if p[3][3]:
                        code +='LOAD g\n'
                        code +='PUT g\n'
                    code += load_variable_into_register(p[3][2], 'h')
                    if p[3][4]:
                        code +='LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                    code += load_variable_into_register(p[1][0], 'd')
                    if p[1][2]:
                        code +='LOAD a\n'
                    code += 'ADD c\n'                
                
                elif len(p[1]) == 4 and len(p[3]) == 4:
                    code += load_value_into_register(p[1][0], 'g')
                    if p[1][2]:
                        code +='LOAD g\n'
                        code +='PUT g\n'
                    code += load_value_into_register(p[1][3],'a')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                    code += load_value_into_register(p[3][0], 'g')
                    if p[3][2]:
                        code +='LOAD g\n'
                        code +='PUT g\n'
                    code += load_value_into_register(p[3][3],'a')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'ADD c\n'
                elif len(p[1]) == 3 and len(p[3]) == 4:
                    code += load_variable_into_register(p[1][0],'c')
                    if p[1][2]:
                        code+='LOAD a\n'
                    code += 'PUT c\n'
                    code += load_value_into_register(p[3][0],'g')
                    if p[3][2]:
                        code +='LOAD g\n'
                        code +='PUT g\n'
                    code += load_value_into_register(p[3][3],'a')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[1][0],'c')
                    if p[1][2]:
                        code+='LOAD a\n'
                    code += 'PUT d\n'
                    
                    code += load_variable_into_register(p[3][0],'c')
                    if p[3][2]:
                        code+='LOAD a\n'
                    code += 'ADD d\n'   
                
            elif not p[1][1] and p[3][1]:
                code += load_value_into_register(p[1][0],'c')
                if len(p[3])==5:
                    code += load_value_into_register(p[3][0], 'g')
                    if p[3][3]:
                        code +='LOAD g\n'
                        code +='PUT g\n'
                    code += load_variable_into_register(p[3][2], 'h')
                    if p[3][4]:
                        code +='LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'ADD c\n'
                elif len(p[3])==4:
                    code += load_value_into_register(p[3][0], 'g')
                    if p[3][2]:
                        code +='LOAD g\n'
                        code +='PUT g\n'
                    code += load_value_into_register(p[3][3],'a')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                else:
                    code += load_variable_into_register(p[3][0],'d')
                    if p[3][2]:
                        code+='LOAD a\n'
                    code += 'ADD c\n'
                
            elif p[1][1] and not p[3][1]:
                code += load_value_into_register(p[3][0],'c')
                if len(p[1]) == 5:
                    code += load_value_into_register(p[1][0], 'g')
                    if p[1][3]:
                        code +='LOAD g\n'
                        code +='PUT g\n'
                    code += load_variable_into_register(p[1][2], 'h')
                    if p[1][4]:
                        code +='LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'ADD c\n'                
                else: 
                    code += load_variable_into_register(p[1][0],'d')
                    if p[1][2]:
                        code+='LOAD a\n'
                    code += 'ADD c\n'
                
            else:
                code += load_value_into_register(p[1][0],'a')
                code += load_value_into_register(p[3][0], 'c')
                code +='ADD c\n'
                
    else:
        if len(p[1]) == 5 and len(p[3])==5:
            code += load_value_into_register(p[1][0], 'g')
            code += load_variable_into_register(p[1][2], 'h')
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT c\n'
            code += load_value_into_register(p[3][0], 'g')
            code += load_variable_into_register(p[3][2], 'h')
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'ADD c\n'
        else:    
            if p[1][1] and p[3][1]:
                if len(p[1]) == 5 and len(p[3]) != 5:
                    code += load_value_into_register(p[1][0], 'g')
                    code += load_variable_into_register(p[1][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                    code += load_variable_into_register(p[3][0], 'd')
                    code += 'ADD c\n'
                elif len(p[1]) != 5 and len(p[3]) == 5:
                    code += load_value_into_register(p[3][0], 'g')
                    code += load_variable_into_register(p[3][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                    code += load_variable_into_register(p[1][0], 'd')
                    code += 'ADD c\n'                
                else:
                    code += load_variable_into_register(p[1][0],'c')
                    code += 'PUT d\n'
                    
                    code += load_variable_into_register(p[3][0],'c')
                    code += 'ADD d\n'   
                
            elif not p[1][1] and p[3][1]:
                code += load_value_into_register(p[1][0],'c')
                if len(p[3])==5:
                    code += load_value_into_register(p[3][0], 'g')
                    code += load_variable_into_register(p[3][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'ADD c\n'
                else:
                    code += load_variable_into_register(p[3][0],'d')
                    code += 'ADD c\n'
                
            elif p[1][1] and not p[3][1]:
                code += load_value_into_register(p[3][0],'c')
                if len(p[1]) == 5:
                    code += load_value_into_register(p[1][0], 'g')
                    code += load_variable_into_register(p[1][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'ADD c\n'                
                else: 
                    code += load_variable_into_register(p[1][0],'d')
                    code += 'ADD c\n'
                
            else:
                code += load_value_into_register(p[1][0],'a')
                code += load_value_into_register(p[3][0], 'c')
                code +='ADD c\n'
                
    p[0] = code

def p_expression_sub(p):
    'expression : value SUB value'
    global in_procedure
    code = ''
    if in_procedure != 'MAIN':
        if len(p[1]) == 5 and len(p[3]) == 5:
            code += load_value_into_register(p[3][0], 'g')
            if p[3][3]:
                code +='LOAD g\n'
                code +='PUT g\n'
            code += load_variable_into_register(p[3][2], 'h')
            if p[3][4]:
                code +='LOAD a\n'
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT c\n'
            code += load_value_into_register(p[1][0], 'g')
            if p[1][3]:
                code +='LOAD g\n'
                code +='PUT g\n'
            code += load_variable_into_register(p[1][2], 'h')
            if p[1][4]:
                code +='LOAD a\n'
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'SUB c\n'
        else:
            if p[1][1] and p[3][1]:
                if len(p[1]) == 5 and len(p[3]) != 5:
                    code += load_variable_into_register(p[3][0],'c')
                    if p[3][2]:
                        code +='LOAD a\n'
                    code += 'PUT c\n'
                    code += load_value_into_register(p[1][0], 'g')
                    if p[1][3]:
                        code +='LOAD g\n'
                        code +='PUT g\n'
                    code += load_variable_into_register(p[1][2], 'h')
                    if p[1][4]:
                        code +='LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'SUB c\n'

                elif len(p[1]) != 5 and len(p[3]) == 5:
                    code += load_value_into_register(p[3][0], 'g')
                    if p[3][3]:
                        code +='LOAD g\n'
                        code +='PUT g\n'
                    code += load_variable_into_register(p[3][2], 'h')
                    if p[3][4]:
                        code +='LOAD a\n'                    
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                    code += load_variable_into_register(p[1][0], 'd')
                    if p[1][2]:
                        code +='LOAD a\n'
                    code += 'SUB c\n'
                else:
                    code += load_variable_into_register(p[3][0],'c')
                    if p[3][2]:
                        code+='LOAD a\n'
                    code += 'PUT d\n'
                    
                    code += load_variable_into_register(p[1][0],'c')
                    if p[1][2]:
                        code+='LOAD a\n'
                    code += 'SUB d\n'
                    
            elif not p[1][1] and p[3][1]:
                code += load_value_into_register(p[1][0], 'c')
                if len(p[3]) == 5:
                    code += load_value_into_register(p[3][0], 'g')
                    if p[3][3]:
                        code += 'LOAD g\n'
                        code += 'PUT g\n'
                    code += load_variable_into_register(p[3][2], 'h')
                    if p[3][4]:
                        code +='LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                    code += 'GET c\n'
                    code += 'SUB d\n'
                elif len(p[3]) == 4:
                    code += load_value_into_register(p[3][0], 'g')
                    if p[3][2]:
                        code +='LOAD g\n'
                        code +='PUT g\n'
                    code += load_value_into_register(p[3][3],'a')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                    code += 'GET c\n'
                    code += 'SUB d\n'
                else:
                    code += load_variable_into_register(p[3][0],'d')
                    if p[3][2]:
                        code+='LOAD a\n'
                    code += 'PUT d\n'
                    code += 'GET c\n'
                    code += 'SUB d\n'
            elif p[1][1] and not p[3][1]:
                code += load_value_into_register(p[3][0],'c')
                if len(p[1]) == 5:
                    code += load_value_into_register(p[1][0], 'g')
                    if p[1][3]:
                        code += 'LOAD g\n'
                        code += 'PUT g\n'
                    code += load_variable_into_register(p[1][2], 'h')
                    if p[1][4]:
                        code +='LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'SUB c\n'
                else:
                    code += load_variable_into_register(p[1][0],'d')
                    if p[1][2]:
                        code+='LOAD a\n'
                    code += 'SUB c\n'
            else:
                code += load_value_into_register(p[1][0],'a')
                code += load_value_into_register(p[3][0], 'c')
                code +='SUB c\n'
    else:
        if len(p[1]) == 5 and len(p[3]) == 5:
            code += load_value_into_register(p[3][0], 'g')
            code += load_variable_into_register(p[3][2], 'h')
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT c\n'
            code += load_value_into_register(p[1][0], 'g')
            code += load_variable_into_register(p[1][2], 'h')
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'SUB c\n'
        else:
            if p[1][1] and p[3][1]:
                if len(p[1]) == 5 and len(p[3]) != 5:
                    code += load_variable_into_register(p[3][0],'c')
                    code += 'PUT c\n'
                    code += load_value_into_register(p[1][0], 'g')
                    code += load_variable_into_register(p[1][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'SUB c\n'

                elif len(p[1]) != 5 and len(p[3]) == 5:
                    code += load_value_into_register(p[3][0], 'g')
                    code += load_variable_into_register(p[3][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                    code += load_variable_into_register(p[1][0], 'd')
                    code += 'SUB c\n'
                else:
                    code += load_variable_into_register(p[3][0],'c')
                    code += 'PUT d\n'
                    
                    code += load_variable_into_register(p[1][0],'c')
                    code += 'SUB d\n'
                    
            elif not p[1][1] and p[3][1]:
                code += load_value_into_register(p[1][0], 'c')
                if len(p[3]) == 5:
                    code += load_value_into_register(p[3][0], 'g')
                    code += load_variable_into_register(p[3][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                    code += 'GET c\n'
                    code += 'SUB d\n'
                else:
                    code += load_variable_into_register(p[3][0],'d')
                    code += 'PUT d\n'
                    
                    code += 'GET c\n'
                    
                    code += 'SUB d\n'
                    
            elif p[1][1] and not p[3][1]:
                code += load_value_into_register(p[3][0],'c')
                if len(p[1]) == 5:
                    code += load_value_into_register(p[1][0], 'g')
                    code += load_variable_into_register(p[1][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'SUB c\n'
                else:
                    code += load_variable_into_register(p[1][0],'d')
                    code += 'SUB c\n'
            else:
                code += load_value_into_register(p[1][0],'a')
                code += load_value_into_register(p[3][0], 'c')
                code +='SUB c\n'
    p[0] = code

def p_expression_mul(p):##problem - tu są adresy zmiennych (wg kodu maszynowego jest ok ale teraz jak przekazać do funkcji multiplication te zmienne xd
    'expression : value MUL value'
    global k, in_procedure
    code = ''
    
    if in_procedure != 'MAIN':
        if len(p[1]) == 5 and len(p[3]) == 5:
            code += load_value_into_register(p[1][0], 'g')
            if p[1][3]:
                code += 'LOAD g\n'
                code += 'PUT g\n'
            code += load_variable_into_register(p[1][2], 'h')
            if p[1][4]:
                code +='LOAD a\n'            
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT c\n'
            code += load_value_into_register(p[3][0], 'g')
            if p[3][3]:
                code += 'LOAD g\n'
                code += 'PUT g\n'
            code += load_variable_into_register(p[3][2], 'h')
            if p[3][4]:
                        code +='LOAD a\n'            
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT d\n'
        else:
            if p[1][1] and p[3][1]:
                if len(p[1]) == 5 and len(p[3]) != 5:
                    code += load_value_into_register(p[1][0], 'g')
                    if p[1][3]:
                        code +='LOAD g\n'
                        code +='PUT g\n'
                    code += load_variable_into_register(p[1][2], 'h')
                    if p[1][4]:
                        code +='LOAD a\n'            
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                    code += load_variable_into_register(p[3][0], 'd')
                    if p[3][2]:
                        code+='LOAD a\n'
                    code += 'PUT d\n'
                elif len(p[1]) != 5 and len(p[3]) == 5:
                    code += load_variable_into_register(p[1][0], 'c')
                    if p[1][2]:
                        code+='LOAD a\n'
                    code += 'PUT c\n'
                    code += load_value_into_register(p[3][0], 'g')
                    if p[3][3]:
                        code+='LOAD g\n'
                        code+='PUT g\n'
                    code += load_variable_into_register(p[3][2], 'h')
                    if p[3][4]:
                        code+='LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                elif len(p[1]) == 4 and len(p[3]) == 4:
                    code += load_value_into_register(p[1][0], 'g')
                    if p[1][2]:
                        code +='LOAD g\n'
                        code +='PUT g\n'
                    code += load_value_into_register(p[1][3],'a')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                    code += load_value_into_register(p[3][0], 'g')
                    if p[3][2]:
                        code +='LOAD g\n'
                        code +='PUT g\n'
                    code += load_value_into_register(p[3][3],'a')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[1][0], 'c')
                    if p[1][2]:
                        code+='LOAD a\n'
                    code += 'PUT c\n'
                    
                    code += load_variable_into_register(p[3][0], 'd')
                    if p[3][2]:
                        code+='LOAD a\n'
                    code += 'PUT d\n'
                    
            elif not p[1][1] and p[3][1]:
                code += load_value_into_register(p[1][0], 'c')
                if len(p[3]) == 5:
                    code += load_value_into_register(p[3][0], 'g')
                    if p[3][3]:
                        code+='LOAD g\n'
                        code+='PUT g\n'
                    code += load_variable_into_register(p[3][2], 'h')
                    if p[3][4]:
                        code+='LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[3][0], 'd')
                    if p[3][2]:
                        code+='LOAD a\n'
                    code += 'PUT d\n'
                    
            elif p[1][1] and not p[3][1]:
                code += load_value_into_register(p[3][0],'d')
                if len(p[1]) == 5:
                    code += load_value_into_register(p[1][0], 'g')
                    if p[1][3]:
                        code+='LOAD g\n'
                        code+='PUT g\n'
                    code += load_variable_into_register(p[1][2], 'h')
                    if p[1][4]:
                        code+='LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                else:
                    code += load_variable_into_register(p[1][0],'c')
                    if p[1][2]:
                        code+='LOAD a\n'
                    code += 'PUT c\n'
                    
            else:
                code += load_value_into_register(p[1][0], 'c')
                code += load_value_into_register(p[3][0], 'd')
    else:
        if len(p[1]) == 5 and len(p[3]) == 5:
            code += load_value_into_register(p[1][0], 'g')
            code += load_variable_into_register(p[1][2], 'h')
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT c\n'
            code += load_value_into_register(p[3][0], 'g')
            code += load_variable_into_register(p[3][2], 'h')
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT d\n'
        else:
            if p[1][1] and p[3][1]:
                if len(p[1]) == 5 and len(p[3]) != 5:
                    code += load_value_into_register(p[1][0], 'g')
                    code += load_variable_into_register(p[1][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                    code += load_variable_into_register(p[3][0], 'd')
                    code += 'PUT d\n'
                elif len(p[1]) != 5 and len(p[3]) == 5:
                    code += load_variable_into_register(p[1][0], 'c')
                    code += 'PUT c\n'
                    code += load_value_into_register(p[3][0], 'g')
                    code += load_variable_into_register(p[3][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[1][0], 'c')
                    code += 'PUT c\n'
                    
                    code += load_variable_into_register(p[3][0], 'd')
                    code += 'PUT d\n'
                    
            elif not p[1][1] and p[3][1]:
                code += load_value_into_register(p[1][0], 'c')
                if len(p[3]) == 5:
                    code += load_value_into_register(p[3][0], 'g')
                    code += load_variable_into_register(p[3][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[3][0], 'd')
                    code += 'PUT d\n'
                    
            elif p[1][1] and not p[3][1]:
                code += load_value_into_register(p[3][0],'d')
                if len(p[1]) == 5:
                    code += load_value_into_register(p[1][0], 'g')
                    code += load_variable_into_register(p[1][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                else:
                    code += load_variable_into_register(p[1][0],'c')
                    code += 'PUT c\n'
                    
            else:
                code += load_value_into_register(p[1][0], 'c')
                code += load_value_into_register(p[3][0], 'd')

    code +='RST f\n'
    
    code +='GET d\n'
    
    code +='PUT e\n'
    
    code +='SHR e\n'
    
    code +='SHL e\n'
    
    code +='SUB e\n'
    
    code +='JZERO {}\n'.format('p'+str(4))
    
    code +='GET f\n'
    
    code +='ADD c\n'
    
    code +='PUT f\n'
    
    code +='SHL c\n'
    
    code +='SHR d\n'
    
    code +='GET d\n'
    
    code +='JPOS {}\n'.format('m'+str(11))
    
    code +='GET f\n'
    
    p[0] = code

def p_expression_div(p):
    'expression : value DIV value'
    global k, in_procedure
    code = ''
    if in_procedure != 'MAIN':
        if len(p[1]) == 5 and len(p[3]) == 5:
            code += load_value_into_register(p[1][0], 'g')
            if p[1][3]:
                        code +='LOAD g\n'
                        code +='PUT g\n'
            code += load_variable_into_register(p[1][2], 'h')
            if p[1][4]:
                        code +='LOAD a\n'
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT c\n'
            code += load_value_into_register(p[3][0], 'g')
            if p[3][3]:
                        code +='LOAD g\n'
                        code +='PUT g\n'
            code += load_variable_into_register(p[3][2], 'h')
            if p[3][4]:
                        code +='LOAD a\n'
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT d\n'
        else:
            if p[1][1] and p[3][1]:
                if len(p[1]) == 5 and len(p[3]) != 5:
                    code += load_value_into_register(p[1][0], 'g')
                    if p[1][3]:
                        code +='LOAD g\n'
                        code +='PUT g\n'
                    code += load_variable_into_register(p[1][2], 'h')
                    if p[1][4]:
                        code +='LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                    code += load_variable_into_register(p[3][0], 'd')
                    if p[3][2]:
                        code+='LOAD a\n'
                    code += 'PUT d\n'
                elif len(p[1]) != 5 and len(p[3]) == 5:
                    code += load_variable_into_register(p[1][0], 'c')
                    if p[1][2]:
                        code +='LOAD a\n'
                    code += 'PUT c\n'
                    code += load_value_into_register(p[3][0], 'g')
                    if p[3][3]:
                        code +='LOAD g\n'
                        code +='PUT g\n'
                    code += load_variable_into_register(p[3][2], 'h')
                    if p[3][4]:
                        code +='LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[1][0], 'c')
                    if p[1][2]:
                        code+='LOAD a\n'
                    code += 'PUT c\n'
                    
                    code += load_variable_into_register(p[3][0], 'd')
                    if p[3][2]:
                        code+='LOAD a\n'
                    code += 'PUT d\n'
                    
            elif not p[1][1] and p[3][1]:
                code += load_value_into_register(p[1][0], 'c')
                if len(p[3]) == 5:
                    code += load_value_into_register(p[3][0], 'g')
                    if p[3][3]:
                        code+='LOAD g\n'
                        code+='PUT g\n'
                    code += load_variable_into_register(p[3][2], 'h')
                    if p[3][4]:
                        code+='LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[3][0], 'd')
                    if p[3][2]:
                        code+='LOAD a\n'
                    code += 'PUT d\n'
                    
            elif p[1][1] and not p[3][1]:
                code += load_value_into_register(p[3][0],'d')
                if len(p[1]) == 5:
                    code += load_value_into_register(p[1][0], 'g')
                    if p[1][3]:
                        code+='LOAD g\n'
                        code+='PUT g\n'
                    code += load_variable_into_register(p[1][2], 'h')
                    if p[1][4]:
                        code+='LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                else:
                    code += load_variable_into_register(p[1][0],'c')
                    if p[1][2]:
                        code+='LOAD a\n'
                    code += 'PUT c\n'
                    
            else:
                code += load_value_into_register(p[1][0], 'c')
                code += load_value_into_register(p[3][0], 'd')

    else:
        if len(p[1]) == 5 and len(p[3]) == 5:
            code += load_value_into_register(p[1][0], 'g')
            code += load_variable_into_register(p[1][2], 'h')
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT c\n'
            code += load_value_into_register(p[3][0], 'g')
            code += load_variable_into_register(p[3][2], 'h')
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT d\n'
        else:
            if p[1][1] and p[3][1]:
                if len(p[1]) == 5 and len(p[3]) != 5:
                    code += load_value_into_register(p[1][0], 'g')
                    code += load_variable_into_register(p[1][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                    code += load_variable_into_register(p[3][0], 'd')
                    code += 'PUT d\n'
                elif len(p[1]) != 5 and len(p[3]) == 5:
                    code += load_variable_into_register(p[1][0], 'c')
                    code += 'PUT c\n'
                    code += load_value_into_register(p[3][0], 'g')
                    code += load_variable_into_register(p[3][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[1][0], 'c')
                    code += 'PUT c\n'
                    
                    code += load_variable_into_register(p[3][0], 'd')
                    code += 'PUT d\n'
                    
            elif not p[1][1] and p[3][1]:
                code += load_value_into_register(p[1][0], 'c')
                if len(p[3]) == 5:
                    code += load_value_into_register(p[3][0], 'g')
                    code += load_variable_into_register(p[3][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[3][0], 'd')
                    code += 'PUT d\n'
                    
            elif p[1][1] and not p[3][1]:
                code += load_value_into_register(p[3][0],'d')
                if len(p[1]) == 5:
                    code += load_value_into_register(p[1][0], 'g')
                    code += load_variable_into_register(p[1][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                else:
                    code += load_variable_into_register(p[1][0],'c')
                    code += 'PUT c\n'
                    
            else:
                code += load_value_into_register(p[1][0], 'c')
                code += load_value_into_register(p[3][0], 'd')

    code+='RST h\n'
    
    code+='RST e\n'
    
    code+='RST f\n'
    
    code+='RST g\n'
    
    code+='GET d\n'
    
    code+='JZERO {}\n'.format('p'+str(39))
    
    code+='INC e\n'
    
    code+='GET f\n'
    
    code+='ADD c\n'
    
    code+='SUB d\n'
    
    code+='JZERO {}\n'.format('p'+str(5))
    
    code+='ADD d\n'
    
    code+='SHL d\n'
    
    code+='SHL e\n'
    
    code+='JUMP {}\n'.format('m'+str(5))
    
    code+='ADD d\n'
    
    code+='SUB c\n'
    
    code+='PUT f\n'
    
    code+='JZERO {}\n'.format('p'+str(3))
    
    code+='SHR d\n'
    
    code+='SHR e\n'
    
    code+='GET c\n'
    
    code+='SUB d\n'
    
    code+='PUT c\n'
    
    code+='GET g\n'
    
    code+='ADD e\n'
    
    code+='PUT g\n'
    
    code+='SHR d\n'
    
    code+='SHR e\n'
    
    code+='GET e\n'
    
    code+='JZERO {}\n'.format('p'+str(14))
    
    code+='RST f\n'
    
    code+='GET f\n'
    
    code+='ADD c\n'
    
    code+='SUB d\n'
    
    code+='PUT f\n'
    
    code+='JZERO {}\n'.format('p'+str(2))
    
    code+='JUMP {}\n'.format('m'+str(16))
    
    code+='GET f\n'
    
    code+='ADD d\n'
    
    code+='SUB c\n'
    
    code+='PUT f\n'
    
    code+='JZERO {}\n'.format('p'+str(2))
    
    code+='JUMP {}\n'.format('m'+str(16))
    
    code+='GET g\n'
    
    code+='ADD e\n'
    

    

    p[0] = code

def p_expression_mod(p):
    'expression : value MOD value'
    global k, in_procedure
    code = ''
    if in_procedure != 'MAIN':
        if len(p[1]) == 5 and len(p[3]) == 5:
            code += load_value_into_register(p[1][0], 'g')
            if p[1][3]:
                        code +='LOAD g\n'
                        code +='PUT g\n'
            code += load_variable_into_register(p[1][2], 'h')
            if p[1][4]:
                        code +='LOAD a\n'
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT c\n'
            code += load_value_into_register(p[3][0], 'g')
            if p[3][3]:
                        code +='LOAD g\n'
                        code +='PUT g\n'
            code += load_variable_into_register(p[3][2], 'h')
            if p[3][4]:
                        code +='LOAD a\n'
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT d\n'
        else:
            if p[1][1] and p[3][1]:
                if len(p[1]) == 5 and len(p[3]) != 5:
                    code += load_value_into_register(p[1][0], 'g')
                    if p[1][3]:
                        code +='LOAD g\n'
                        code +='PUT g\n'
                    code += load_variable_into_register(p[1][2], 'h')
                    if p[1][4]:
                        code +='LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                    code += load_variable_into_register(p[3][0], 'd')
                    if p[3][2]:
                        code+='LOAD a\n'
                    code += 'PUT d\n'
                elif len(p[1]) != 5 and len(p[3]) == 5:
                    code += load_variable_into_register(p[1][0], 'c')
                    if p[1][2]:
                        code +='LOAD a\n'
                    code += 'PUT c\n'
                    code += load_value_into_register(p[3][0], 'g')
                    if p[3][3]:
                        code +='LOAD g\n'
                        code +='PUT g\n'
                    code += load_variable_into_register(p[3][2], 'h')
                    if p[3][4]:
                        code +='LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                elif len(p[1]) == 4 and len(p[3]) == 4:
                    code += load_value_into_register(p[1][0], 'g')
                    if p[1][2]:
                        code +='LOAD g\n'
                        code +='PUT g\n'
                    code += load_value_into_register(p[1][3],'a')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                    code += load_value_into_register(p[3][0], 'g')
                    if p[3][2]:
                        code +='LOAD g\n'
                        code +='PUT g\n'
                    code += load_value_into_register(p[3][3],'a')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[1][0], 'c')
                    if p[1][2]:
                        code+='LOAD a\n'
                    code += 'PUT c\n'
                    
                    code += load_variable_into_register(p[3][0], 'd')
                    if p[3][2]:
                        code+='LOAD a\n'
                    code += 'PUT d\n'
                    
            elif not p[1][1] and p[3][1]:
                code += load_value_into_register(p[1][0], 'c')
                if len(p[3]) == 5:
                    code += load_value_into_register(p[3][0], 'g')
                    if p[3][3]:
                        code+='LOAD g\n'
                        code+='PUT g\n'
                    code += load_variable_into_register(p[3][2], 'h')
                    if p[3][4]:
                        code+='LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[3][0], 'd')
                    if p[3][2]:
                        code+='LOAD a\n'
                    code += 'PUT d\n'
                    
            elif p[1][1] and not p[3][1]:
                code += load_value_into_register(p[3][0],'d')
                if len(p[1]) == 5:
                    code += load_value_into_register(p[1][0], 'g')
                    if p[1][3]:
                        code+='LOAD g\n'
                        code+='PUT g\n'
                    code += load_variable_into_register(p[1][2], 'h')
                    if p[1][4]:
                        code+='LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'

                elif len(p[1]) == 4:
                    code += load_value_into_register(p[1][0], 'g')
                    if p[1][2]:
                        code +='LOAD g\n'
                        code +='PUT g\n'
                    code += load_value_into_register(p[1][3],'a')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                else:
                    code += load_variable_into_register(p[1][0],'c')
                    if p[1][2]:
                        code+='LOAD a\n'
                    code += 'PUT c\n'
                    
            else:
                code += load_value_into_register(p[1][0], 'c')
                code += load_value_into_register(p[3][0], 'd')

    else:
        if len(p[1]) == 5 and len(p[3]) == 5:
            code += load_value_into_register(p[1][0], 'g')
            code += load_variable_into_register(p[1][2], 'h')
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT c\n'
            code += load_value_into_register(p[3][0], 'g')
            code += load_variable_into_register(p[3][2], 'h')
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT d\n'
        else:
            if p[1][1] and p[3][1]:
                if len(p[1]) == 5 and len(p[3]) != 5:
                    code += load_value_into_register(p[1][0], 'g')
                    code += load_variable_into_register(p[1][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                    code += load_variable_into_register(p[3][0], 'd')
                    code += 'PUT d\n'
                elif len(p[1]) != 5 and len(p[3]) == 5:
                    code += load_variable_into_register(p[1][0], 'c')
                    code += 'PUT c\n'
                    code += load_value_into_register(p[3][0], 'g')
                    code += load_variable_into_register(p[3][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[1][0], 'c')
                    code += 'PUT c\n'
                    
                    code += load_variable_into_register(p[3][0], 'd')
                    code += 'PUT d\n'
                    
            elif not p[1][1] and p[3][1]:
                code += load_value_into_register(p[1][0], 'c')
                if len(p[3]) == 5:
                    code += load_value_into_register(p[3][0], 'g')
                    code += load_variable_into_register(p[3][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[3][0], 'd')
                    code += 'PUT d\n'
                    
            elif p[1][1] and not p[3][1]:
                code += load_value_into_register(p[3][0],'d')
                if len(p[1]) == 5:
                    code += load_value_into_register(p[1][0], 'g')
                    code += load_variable_into_register(p[1][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                else:
                    code += load_variable_into_register(p[1][0],'c')
                    code += 'PUT c\n'
                    
            else:
                code += load_value_into_register(p[1][0], 'c')
                code += load_value_into_register(p[3][0], 'd')

    code+='RST h\n'
    
    code+='RST e\n'
    
    code+='RST f\n'
    
    code+='RST g\n'
    
    code+='GET d\n'
    
    code+='JZERO {}\n'.format('p'+str(48))
    
    code+='INC e\n'
    
    code+='GET f\n'
    
    code+='ADD c\n'
    
    code+='SUB d\n'
    
    code+='JZERO {}\n'.format('p'+str(5))
    
    code+='ADD d\n'
    
    code+='SHL d\n'
    
    code+='SHL e\n'
    
    code+='JUMP {}\n'.format('m'+str(5))
    
    code+='ADD d\n'
    
    code+='SUB c\n'
    
    code+='PUT f\n'
    
    code+='JZERO {}\n'.format('p'+str(5))
    
    code+='SHR d\n'
    
    code+='SHR e\n'
    
    code+='GET e\n'
    
    code+='JZERO {}\n'.format('p'+str(32))
    
    code+='GET c\n'
    
    code+='SUB d\n'
    
    code+='PUT c\n'
    
    code+='GET g\n'
    
    code+='ADD e\n'
    
    code+='PUT g\n'
    
    code+='SHR d\n'
    
    code+='SHR e\n'
    
    code+='GET e\n'
    
    code+='JZERO {}\n'.format('p'+str(20))
    
    code+='RST f\n'
    
    code+='GET f\n'
    
    code+='ADD c\n'
    
    code+='SUB d\n'
    
    code+='PUT f\n'
    
    code+='JZERO {}\n'.format('p'+str(2))
    
    code+='JUMP {}\n'.format('m'+str(16))
    
    code+='GET f\n'
    
    code+='ADD d\n'
    
    code+='SUB c\n'
    
    code+='PUT f\n'
    
    code+='JZERO {}\n'.format('p'+str(2))
    
    code+='JUMP {}\n'.format('m'+str(16))
    
    code+='GET g\n'
    
    code+='ADD e\n'
    
    code+='PUT g\n'
    
    code+='GET c\n'
    
    code+='SUB d\n'
    
    code +='PUT c\n'
    
    code+='JUMP {}\n'.format('p'+str(2))
    
    code+='RST c\n'
    
    code+='GET c\n'
    
    

    p[0] = code

#CONDITIONS = jak wychodzi 0 w Ra to jest to odpowiednik prawdy, a 1 to fałsz, tak przekornie:) (chyba zrobiłem)
def p_condition_eq(p):
    'condition : value EQ value'
    global k, in_procedure
    code = ''
    if in_procedure != 'MAIN':
        if len(p[1]) == 5 and len(p[3]) == 5:
            code += load_value_into_register(p[1][0], 'g')
            if p[1][3]:
                code += 'LOAD g\n'
                code += 'PUT g\n'
            code += load_variable_into_register(p[1][2], 'h')
            if p[1][4]:
                code += 'LOAD a\n'
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT c\n'
            code += load_value_into_register(p[3][0], 'g')
            if p[3][3]:
                code += 'LOAD g\n'
                code += 'PUT g\n'
            code += load_variable_into_register(p[3][2], 'h')
            if p[3][4]:
                code += 'LOAD a\n'
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT d\n'
        else:
            if p[1][1] and p[3][1]:
                if len(p[1]) == 5 and len(p[3]) != 5:
                    code += load_value_into_register(p[1][0], 'g')
                    if p[1][3]:
                        code += 'LOAD g\n'
                        code += 'PUT g\n'
                    code += load_variable_into_register(p[1][2], 'h')
                    if p[1][4]:
                        code += 'LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                    code += load_variable_into_register(p[3][0], 'd')
                    if p[3][2]:
                        code += 'LOAD a\n'
                    code += 'PUT d\n'
                elif len(p[1]) != 5 and len(p[3]) == 5:
                    code += load_variable_into_register(p[1][0], 'c')
                    if p[1][2]:
                        code += 'LOAD a\n'
                    code += 'PUT c\n'
                    code += load_value_into_register(p[3][0], 'g')
                    if p[3][3]:
                        code += 'LOAD g\n'
                        code += 'PUT g\n'
                    code += load_variable_into_register(p[3][2], 'h')
                    if p[3][4]:
                        code += 'LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[1][0], 'c')
                    if p[1][2]:
                        code+='LOAD a\n'
                    code += 'PUT c\n'
                    
                    code += load_variable_into_register(p[3][0], 'd')
                    if p[3][2]:
                        code+='LOAD a\n'
                    code += 'PUT d\n'
                    
            elif not p[1][1] and p[3][1]:
                code += load_value_into_register(p[1][0], 'c')
                if len(p[3]) == 5:
                    code += load_value_into_register(p[3][0], 'g')
                    if p[3][3]:
                        code += 'LOAD g\n'
                        code += 'PUT g\n'
                    code += load_variable_into_register(p[3][2], 'h')
                    if p[3][4]:
                        code += 'LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[3][0], 'd')
                    if p[3][2]:
                        code+='LOAD a\n'
                    code += 'PUT d\n'
                    
            elif p[1][1] and not p[3][1]:
                code += load_value_into_register(p[3][0],'d')
                if len(p[1]) == 5:
                    code += load_value_into_register(p[1][0], 'g')
                    if p[1][3]:
                        code += 'LOAD g\n'
                        code += 'LOAD g\n'
                    code += load_variable_into_register(p[1][2], 'h')
                    if p[1][4]:
                        code += 'LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                else:
                    code += load_variable_into_register(p[1][0],'c')
                    if p[1][2]:
                        code+='LOAD a\n'
                    code += 'PUT c\n'
                    
            else:
                code += load_value_into_register(p[1][0], 'c')
                code += load_value_into_register(p[3][0], 'd')
    else:
        if len(p[1]) == 5 and len(p[3]) == 5:
            code += load_value_into_register(p[1][0], 'g')
            code += load_variable_into_register(p[1][2], 'h')
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT c\n'
            code += load_value_into_register(p[3][0], 'g')
            code += load_variable_into_register(p[3][2], 'h')
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT d\n'
        else:
            if p[1][1] and p[3][1]:
                if len(p[1]) == 5 and len(p[3]) != 5:
                    code += load_value_into_register(p[1][0], 'g')
                    code += load_variable_into_register(p[1][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                    code += load_variable_into_register(p[3][0], 'd')
                    code += 'PUT d\n'
                elif len(p[1]) != 5 and len(p[3]) == 5:
                    code += load_variable_into_register(p[1][0], 'c')
                    code += 'PUT c\n'
                    code += load_value_into_register(p[3][0], 'g')
                    code += load_variable_into_register(p[3][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[1][0], 'c')
                    code += 'PUT c\n'
                    
                    code += load_variable_into_register(p[3][0], 'd')
                    code += 'PUT d\n'
                    
            elif not p[1][1] and p[3][1]:
                code += load_value_into_register(p[1][0], 'c')
                if len(p[3]) == 5:
                    code += load_value_into_register(p[3][0], 'g')
                    code += load_variable_into_register(p[3][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[3][0], 'd')
                    code += 'PUT d\n'
                    
            elif p[1][1] and not p[3][1]:
                code += load_value_into_register(p[3][0],'d')
                if len(p[1]) == 5:
                    code += load_value_into_register(p[1][0], 'g')
                    code += load_variable_into_register(p[1][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                else:
                    code += load_variable_into_register(p[1][0],'c')
                    code += 'PUT c\n'
                    
            else:
                code += load_value_into_register(p[1][0], 'c')
                code += load_value_into_register(p[3][0], 'd')

    code +='RST f\n'
    
    code+='GET c\n'
    
    code+='PUT f\n'
    
    code+='GET c\n'
    
    code+='SUB d\n'
    
    code+='PUT c\n'
    
    code+='GET d\n'
    
    code+='SUB f\n'
    
    code+='ADD c\n'
    

    p[0] = code

def p_condition_neq(p):
    'condition : value NEQ value'
    global k, in_procedure
    code = ''
    if in_procedure != 'MAIN':
        if len(p[1]) == 5 and len(p[3]) == 5:
            code += load_value_into_register(p[1][0], 'g')
            if p[1][3]:
                code += 'LOAD g\n'
                code += 'PUT g\n'
            code += load_variable_into_register(p[1][2], 'h')
            if p[1][4]:
                code += 'LOAD a\n'
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT c\n'
            code += load_value_into_register(p[3][0], 'g')
            if p[3][3]:
                code += 'LOAD g\n'
                code += 'PUT g\n'
            code += load_variable_into_register(p[3][2], 'h')
            if p[3][4]:
                code += 'LOAD a\n'
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT d\n'
        else:
            if p[1][1] and p[3][1]:
                if len(p[1]) == 5 and len(p[3]) != 5:
                    code += load_value_into_register(p[1][0], 'g')
                    if p[1][3]:
                        code += 'LOAD g\n'
                        code += 'PUT g\n'
                    code += load_variable_into_register(p[1][2], 'h')
                    if p[1][4]:
                        code += 'LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                    code += load_variable_into_register(p[3][0], 'd')
                    if p[3][2]:
                        code += 'LOAD a\n'
                    code += 'PUT d\n'
                elif len(p[1]) != 5 and len(p[3]) == 5:
                    code += load_variable_into_register(p[1][0], 'c')
                    if p[1][2]:
                        code += 'LOAD a\n'
                    code += 'PUT c\n'
                    code += load_value_into_register(p[3][0], 'g')
                    if p[3][3]:
                        code += 'LOAD g\n'
                        code += 'PUT g\n'
                    code += load_variable_into_register(p[3][2], 'h')
                    if p[3][4]:
                        code += 'LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[1][0], 'c')
                    if p[1][2]:
                        code+='LOAD a\n'
                    code += 'PUT c\n'
                    
                    code += load_variable_into_register(p[3][0], 'd')
                    if p[3][2]:
                        code+='LOAD a\n'
                    code += 'PUT d\n'
                    
            elif not p[1][1] and p[3][1]:
                code += load_value_into_register(p[1][0], 'c')
                if len(p[3]) == 5:
                    code += load_value_into_register(p[3][0], 'g')
                    if p[3][3]:
                        code += 'LOAD g\n'
                        code += 'PUT g\n'
                    code += load_variable_into_register(p[3][2], 'h')
                    if p[3][4]:
                        code += 'LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[3][0], 'd')
                    if p[3][2]:
                        code+='LOAD a\n'
                    code += 'PUT d\n'
                    
            elif p[1][1] and not p[3][1]:
                code += load_value_into_register(p[3][0],'d')
                if len(p[1]) == 5:
                    code += load_value_into_register(p[1][0], 'g')
                    if p[1][3]:
                        code += 'LOAD g\n'
                        code += 'LOAD g\n'
                    code += load_variable_into_register(p[1][2], 'h')
                    if p[1][4]:
                        code += 'LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                else:
                    code += load_variable_into_register(p[1][0],'c')
                    if p[1][2]:
                        code+='LOAD a\n'
                    code += 'PUT c\n'
                    
            else:
                code += load_value_into_register(p[1][0], 'c')
                code += load_value_into_register(p[3][0], 'd')
    else:
        if len(p[1]) == 5 and len(p[3]) == 5:
            code += load_value_into_register(p[1][0], 'g')
            code += load_variable_into_register(p[1][2], 'h')
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT c\n'
            code += load_value_into_register(p[3][0], 'g')
            code += load_variable_into_register(p[3][2], 'h')
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT d\n'
        else:
            if p[1][1] and p[3][1]:
                if len(p[1]) == 5 and len(p[3]) != 5:
                    code += load_value_into_register(p[1][0], 'g')
                    code += load_variable_into_register(p[1][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                    code += load_variable_into_register(p[3][0], 'd')
                    code += 'PUT d\n'
                elif len(p[1]) != 5 and len(p[3]) == 5:
                    code += load_variable_into_register(p[1][0], 'c')
                    code += 'PUT c\n'
                    code += load_value_into_register(p[3][0], 'g')
                    code += load_variable_into_register(p[3][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[1][0], 'c')
                    code += 'PUT c\n'
                    
                    code += load_variable_into_register(p[3][0], 'd')
                    code += 'PUT d\n'
                    
            elif not p[1][1] and p[3][1]:
                code += load_value_into_register(p[1][0], 'c')
                if len(p[3]) == 5:
                    code += load_value_into_register(p[3][0], 'g')
                    code += load_variable_into_register(p[3][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[3][0], 'd')
                    code += 'PUT d\n'
                    
            elif p[1][1] and not p[3][1]:
                code += load_value_into_register(p[3][0],'d')
                if len(p[1]) == 5:
                    code += load_value_into_register(p[1][0], 'g')
                    code += load_variable_into_register(p[1][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                else:
                    code += load_variable_into_register(p[1][0],'c')
                    code += 'PUT c\n'
                    
            else:
                code += load_value_into_register(p[1][0], 'c')
                code += load_value_into_register(p[3][0], 'd')

    code +='RST f\n'
    
    code+='GET c\n'
    
    code+='PUT f\n'
    
    code+='GET c\n'
    
    code+='SUB d\n'
    
    code+='PUT c\n'
    
    code+='GET d\n'
    
    code+='SUB f\n'
    
    code+='ADD c\n'
    
    code+='JZERO {}\n'.format('p'+str(3))
    
    code+='RST a\n'
    
    code+='JUMP {}\n'.format('p'+str(2))

    code+='INC a\n'
    

    p[0] = code


def p_condition_gt(p):
    'condition : value GT value'
    global k, in_procedure
    code = ''
    if in_procedure != 'MAIN':
        if len(p[1]) == 5 and len(p[3]) == 5:
            code += load_value_into_register(p[1][0], 'g')
            if p[1][3]:
                code += 'LOAD g\n'
                code += 'PUT g\n'
            code += load_variable_into_register(p[1][2], 'h')
            if p[1][4]:
                code += 'LOAD a\n'
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT c\n'
            code += load_value_into_register(p[3][0], 'g')
            if p[3][3]:
                code += 'LOAD g\n'
                code += 'PUT g\n'
            code += load_variable_into_register(p[3][2], 'h')
            if p[3][4]:
                code += 'LOAD a\n'
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT d\n'
        else:
            if p[1][1] and p[3][1]:
                if len(p[1]) == 5 and len(p[3]) != 5:
                    code += load_value_into_register(p[1][0], 'g')
                    if p[1][3]:
                        code += 'LOAD g\n'
                        code += 'PUT g\n'
                    code += load_variable_into_register(p[1][2], 'h')
                    if p[1][4]:
                        code += 'LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                    code += load_variable_into_register(p[3][0], 'd')
                    if p[3][2]:
                        code += 'LOAD a\n'
                    code += 'PUT d\n'
                elif len(p[1]) != 5 and len(p[3]) == 5:
                    code += load_variable_into_register(p[1][0], 'c')
                    if p[1][2]:
                        code += 'LOAD a\n'
                    code += 'PUT c\n'
                    code += load_value_into_register(p[3][0], 'g')
                    if p[3][3]:
                        code += 'LOAD g\n'
                        code += 'PUT g\n'
                    code += load_variable_into_register(p[3][2], 'h')
                    if p[3][4]:
                        code += 'LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[1][0], 'c')
                    if p[1][2]:
                        code+='LOAD a\n'
                    code += 'PUT c\n'
                    
                    code += load_variable_into_register(p[3][0], 'd')
                    if p[3][2]:
                        code+='LOAD a\n'
                    code += 'PUT d\n'
                    
            elif not p[1][1] and p[3][1]:
                code += load_value_into_register(p[1][0], 'c')
                if len(p[3]) == 5:
                    code += load_value_into_register(p[3][0], 'g')
                    if p[3][3]:
                        code += 'LOAD g\n'
                        code += 'PUT g\n'
                    code += load_variable_into_register(p[3][2], 'h')
                    if p[3][4]:
                        code += 'LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[3][0], 'd')
                    if p[3][2]:
                        code+='LOAD a\n'
                    code += 'PUT d\n'
                    
            elif p[1][1] and not p[3][1]:
                code += load_value_into_register(p[3][0],'d')
                if len(p[1]) == 5:
                    code += load_value_into_register(p[1][0], 'g')
                    if p[1][3]:
                        code += 'LOAD g\n'
                        code += 'PUT g\n'
                    code += load_variable_into_register(p[1][2], 'h')
                    if p[1][4]:
                        code += 'LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                else:
                    code += load_variable_into_register(p[1][0],'c')
                    if p[1][2]:
                        code+='LOAD a\n'
                    code += 'PUT c\n'
                    
            else:
                code += load_value_into_register(p[1][0], 'c')
                code += load_value_into_register(p[3][0], 'd')
    else:
        if len(p[1]) == 5 and len(p[3]) == 5:
            code += load_value_into_register(p[1][0], 'g')
            code += load_variable_into_register(p[1][2], 'h')
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT c\n'
            code += load_value_into_register(p[3][0], 'g')
            code += load_variable_into_register(p[3][2], 'h')
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT d\n'
        else:
            if p[1][1] and p[3][1]:
                if len(p[1]) == 5 and len(p[3]) != 5:
                    code += load_value_into_register(p[1][0], 'g')
                    code += load_variable_into_register(p[1][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                    code += load_variable_into_register(p[3][0], 'd')
                    code += 'PUT d\n'
                elif len(p[1]) != 5 and len(p[3]) == 5:
                    code += load_variable_into_register(p[1][0], 'c')
                    code += 'PUT c\n'
                    code += load_value_into_register(p[3][0], 'g')
                    code += load_variable_into_register(p[3][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[1][0], 'c')
                    code += 'PUT c\n'
                    
                    code += load_variable_into_register(p[3][0], 'd')
                    code += 'PUT d\n'
                    
            elif not p[1][1] and p[3][1]:
                code += load_value_into_register(p[1][0], 'c')
                if len(p[3]) == 5:
                    code += load_value_into_register(p[3][0], 'g')
                    code += load_variable_into_register(p[3][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[3][0], 'd')
                    code += 'PUT d\n'
                    
            elif p[1][1] and not p[3][1]:
                code += load_value_into_register(p[3][0],'d')
                if len(p[1]) == 5:
                    code += load_value_into_register(p[1][0], 'g')
                    code += load_variable_into_register(p[1][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                else:
                    code += load_variable_into_register(p[1][0],'c')
                    code += 'PUT c\n'
                    
            else:
                code += load_value_into_register(p[1][0], 'c')
                code += load_value_into_register(p[3][0], 'd')

    code+='GET c\n'
    
    code+='SUB d\n'
    
    code+='JZERO {}\n'.format('p'+str(3))
    
    code+='RST a\n'
    
    code+='JUMP {}\n'.format('p'+str(2))
    
    code+='INC a\n'
    

    p[0] = code
        

def p_condition_lt(p):
    'condition : value LT value'
    global k, in_procedure
    code = ''
    if in_procedure != 'MAIN':   
        if len(p[1]) == 5 and len(p[3]) == 5:
            code += load_value_into_register(p[1][0], 'g')
            if p[1][3]:
                code +='LOAD g\n'
                code +='PUT g\n'
            code += load_variable_into_register(p[1][2], 'h')
            if p[1][4]:
                code += 'LOAD a\n'
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT d\n'
            code += load_value_into_register(p[3][0], 'g')
            if p[3][3]:
                code +='LOAD g\n'
                code +='PUT g\n'
            code += load_variable_into_register(p[3][2], 'h')
            if p[3][4]:
                code +='LOAD a\n'
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT c\n'
        else:
            if p[1][1] and p[3][1]:
                if len(p[1]) == 5 and len(p[3]) != 5:
                    code += load_value_into_register(p[1][0], 'g')
                    if p[1][3]:
                        code+='LOAD g\n'
                        code+='PUT g\n'
                    code += load_variable_into_register(p[1][2], 'h')
                    if p[1][4]:
                        code+='LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                    code += load_variable_into_register(p[3][0], 'd')
                    if p[3][2]:
                        code+='LOAD a\n'
                    code += 'PUT c\n'
                elif len(p[1]) != 5 and len(p[3]) == 5:
                    code += load_variable_into_register(p[1][0], 'd')
                    if p[1][2]:
                        code+='LOAD a\n'
                    code += 'PUT d\n'
                    code += load_value_into_register(p[3][0], 'g')
                    if p[3][3]:
                        code+='LOAD g\n'
                        code+='PUT g\n'
                    code += load_variable_into_register(p[3][2], 'h')
                    if p[3][4]:
                        code+='LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                else:
                    code += load_variable_into_register(p[1][0], 'd')
                    if p[1][2]:
                        code+='LOAD a\n'
                    code += 'PUT d\n'
                    
                    code += load_variable_into_register(p[3][0], 'c')
                    if p[3][2]:
                        code+='LOAD a\n'
                    code += 'PUT c\n'
                    
            elif not p[1][1] and p[3][1]:
                code += load_value_into_register(p[1][0], 'd')
                if len(p[3]) == 5:
                    code += load_value_into_register(p[3][0], 'g')
                    if p[3][3]:
                        code+='LOAD g\n'
                        code+='PUT g\n'
                    code += load_variable_into_register(p[3][2], 'h')
                    if p[3][4]:
                        code+='LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                else:
                    code += load_variable_into_register(p[3][0], 'c')
                    if p[3][2]:
                        code+='LOAD a\n'
                    code += 'PUT c\n'
                    
            elif p[1][1] and not p[3][1]:
                code += load_value_into_register(p[3][0],'c')
                if len(p[1]) == 5:
                    code += load_value_into_register(p[1][0], 'g')
                    if p[1][3]:
                        code+='LOAD g\n'
                        code+='PUT g\n'
                    code += load_variable_into_register(p[1][2], 'h')
                    if p[1][4]:
                        code+='LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[1][0],'d')
                    if p[1][2]:
                        code+='LOAD a\n'
                    code += 'PUT d\n'
                    
            else:
                code += load_value_into_register(p[1][0], 'd')
                code += load_value_into_register(p[3][0], 'c')

    else:    

        if len(p[1]) == 5 and len(p[3]) == 5:
            code += load_value_into_register(p[1][0], 'g')
            code += load_variable_into_register(p[1][2], 'h')
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT d\n'
            code += load_value_into_register(p[3][0], 'g')
            code += load_variable_into_register(p[3][2], 'h')
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT c\n'
        else:
            if p[1][1] and p[3][1]:
                if len(p[1]) == 5 and len(p[3]) != 5:
                    code += load_value_into_register(p[1][0], 'g')
                    code += load_variable_into_register(p[1][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                    code += load_variable_into_register(p[3][0], 'd')
                    code += 'PUT c\n'
                elif len(p[1]) != 5 and len(p[3]) == 5:
                    code += load_variable_into_register(p[1][0], 'd')
                    code += 'PUT d\n'
                    code += load_value_into_register(p[3][0], 'g')
                    code += load_variable_into_register(p[3][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                else:
                    code += load_variable_into_register(p[1][0], 'd')
                    code += 'PUT d\n'
                    
                    code += load_variable_into_register(p[3][0], 'c')
                    code += 'PUT c\n'
                    
            elif not p[1][1] and p[3][1]:
                code += load_value_into_register(p[1][0], 'd')
                if len(p[3]) == 5:
                    code += load_value_into_register(p[3][0], 'g')
                    code += load_variable_into_register(p[3][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                else:
                    code += load_variable_into_register(p[3][0], 'c')
                    code += 'PUT c\n'
                    
            elif p[1][1] and not p[3][1]:
                code += load_value_into_register(p[3][0],'c')
                if len(p[1]) == 5:
                    code += load_value_into_register(p[1][0], 'g')
                    code += load_variable_into_register(p[1][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[1][0],'d')
                    code += 'PUT d\n'
                    
            else:
                code += load_value_into_register(p[1][0], 'd')
                code += load_value_into_register(p[3][0], 'c')

    code+='GET c\n'
    
    code+='SUB d\n'
    
    code+='JZERO {}\n'.format('p'+str(3))
    
    code+='RST a\n'
    
    code+='JUMP {}\n'.format('p'+str(2))
    
    code+='INC a\n'
    

    p[0] = code

def p_condition_ge(p):
    'condition : value GE value'
    global k, in_procedure
    code = ''
    if in_procedure != 'MAIN':   
        if len(p[1]) == 5 and len(p[3]) == 5:
            code += load_value_into_register(p[1][0], 'g')
            if p[1][3]:
                code +='LOAD g\n'
                code +='PUT g\n'
            code += load_variable_into_register(p[1][2], 'h')
            if p[1][4]:
                code += 'LOAD a\n'
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT d\n'
            code += load_value_into_register(p[3][0], 'g')
            if p[3][3]:
                code +='LOAD g\n'
                code +='PUT g\n'
            code += load_variable_into_register(p[3][2], 'h')
            if p[3][4]:
                code +='LOAD a\n'
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT c\n'
        else:
            if p[1][1] and p[3][1]:
                if len(p[1]) == 5 and len(p[3]) != 5:
                    code += load_value_into_register(p[1][0], 'g')
                    if p[1][3]:
                        code+='LOAD g\n'
                        code+='PUT g\n'
                    code += load_variable_into_register(p[1][2], 'h')
                    if p[1][4]:
                        code+='LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                    code += load_variable_into_register(p[3][0], 'd')
                    if p[3][2]:
                        code+='LOAD a\n'
                    code += 'PUT c\n'
                elif len(p[1]) != 5 and len(p[3]) == 5:
                    code += load_variable_into_register(p[1][0], 'd')
                    if p[1][2]:
                        code+='LOAD a\n'
                    code += 'PUT d\n'
                    code += load_value_into_register(p[3][0], 'g')
                    if p[3][3]:
                        code+='LOAD g\n'
                        code+='PUT g\n'
                    code += load_variable_into_register(p[3][2], 'h')
                    if p[3][4]:
                        code+='LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                else:
                    code += load_variable_into_register(p[1][0], 'd')
                    if p[1][2]:
                        code+='LOAD a\n'
                    code += 'PUT d\n'
                    
                    code += load_variable_into_register(p[3][0], 'c')
                    if p[3][2]:
                        code+='LOAD a\n'
                    code += 'PUT c\n'
                    
            elif not p[1][1] and p[3][1]:
                code += load_value_into_register(p[1][0], 'd')
                if len(p[3]) == 5:
                    code += load_value_into_register(p[3][0], 'g')
                    if p[3][3]:
                        code+='LOAD g\n'
                        code+='PUT g\n'
                    code += load_variable_into_register(p[3][2], 'h')
                    if p[3][4]:
                        code+='LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                else:
                    code += load_variable_into_register(p[3][0], 'c')
                    if p[3][2]:
                        code+='LOAD a\n'
                    code += 'PUT c\n'
                    
            elif p[1][1] and not p[3][1]:
                code += load_value_into_register(p[3][0],'c')
                if len(p[1]) == 5:
                    code += load_value_into_register(p[1][0], 'g')
                    if p[1][3]:
                        code+='LOAD g\n'
                        code+='PUT g\n'
                    code += load_variable_into_register(p[1][2], 'h')
                    if p[1][4]:
                        code+='LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[1][0],'d')
                    if p[1][2]:
                        code+='LOAD a\n'
                    code += 'PUT d\n'
                    
            else:
                code += load_value_into_register(p[1][0], 'd')
                code += load_value_into_register(p[3][0], 'c')

    else:    

        if len(p[1]) == 5 and len(p[3]) == 5:
            code += load_value_into_register(p[1][0], 'g')
            code += load_variable_into_register(p[1][2], 'h')
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT d\n'
            code += load_value_into_register(p[3][0], 'g')
            code += load_variable_into_register(p[3][2], 'h')
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT c\n'
        else:
            if p[1][1] and p[3][1]:
                if len(p[1]) == 5 and len(p[3]) != 5:
                    code += load_value_into_register(p[1][0], 'g')
                    code += load_variable_into_register(p[1][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                    code += load_variable_into_register(p[3][0], 'd')
                    code += 'PUT c\n'
                elif len(p[1]) != 5 and len(p[3]) == 5:
                    code += load_variable_into_register(p[1][0], 'd')
                    code += 'PUT d\n'
                    code += load_value_into_register(p[3][0], 'g')
                    code += load_variable_into_register(p[3][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                else:
                    code += load_variable_into_register(p[1][0], 'd')
                    code += 'PUT d\n'
                    
                    code += load_variable_into_register(p[3][0], 'c')
                    code += 'PUT c\n'
                    
            elif not p[1][1] and p[3][1]:
                code += load_value_into_register(p[1][0], 'd')
                if len(p[3]) == 5:
                    code += load_value_into_register(p[3][0], 'g')
                    code += load_variable_into_register(p[3][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                else:
                    code += load_variable_into_register(p[3][0], 'c')
                    code += 'PUT c\n'
                    
            elif p[1][1] and not p[3][1]:
                code += load_value_into_register(p[3][0],'c')
                if len(p[1]) == 5:
                    code += load_value_into_register(p[1][0], 'g')
                    code += load_variable_into_register(p[1][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[1][0],'d')
                    code += 'PUT d\n'
                    
            else:
                code += load_value_into_register(p[1][0], 'd')
                code += load_value_into_register(p[3][0], 'c')


    code+='GET c\n'
    
    code+='SUB d\n'
    
    code+='JPOS {}\n'.format('p'+str(2))
    
    code+='JUMP {}\n'.format('p'+str(3))
    
    code+='RST a\n'
    
    code+='INC a\n'
    

    p[0] = code
    

def p_condition_le(p):
    'condition : value LE value'
    global k, in_procedure
    code = ''
    if in_procedure != 'MAIN':
        if len(p[1]) == 5 and len(p[3]) == 5:
            code += load_value_into_register(p[1][0], 'g')
            if p[1][3]:
                code += 'LOAD g\n'
                code += 'PUT g\n'
            code += load_variable_into_register(p[1][2], 'h')
            if p[1][4]:
                code += 'LOAD a\n'
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT c\n'
            code += load_value_into_register(p[3][0], 'g')
            if p[3][3]:
                code += 'LOAD g\n'
                code += 'PUT g\n'
            code += load_variable_into_register(p[3][2], 'h')
            if p[3][4]:
                code += 'LOAD a\n'
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT d\n'
        else:
            if p[1][1] and p[3][1]:
                if len(p[1]) == 5 and len(p[3]) != 5:
                    code += load_value_into_register(p[1][0], 'g')
                    if p[1][3]:
                        code += 'LOAD g\n'
                        code += 'PUT g\n'
                    code += load_variable_into_register(p[1][2], 'h')
                    if p[1][4]:
                        code += 'LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                    code += load_variable_into_register(p[3][0], 'd')
                    if p[3][2]:
                        code += 'LOAD a\n'
                    code += 'PUT d\n'
                elif len(p[1]) != 5 and len(p[3]) == 5:
                    code += load_variable_into_register(p[1][0], 'c')
                    if p[1][2]:
                        code += 'LOAD a\n'
                    code += 'PUT c\n'
                    code += load_value_into_register(p[3][0], 'g')
                    if p[3][3]:
                        code += 'LOAD g\n'
                        code += 'PUT g\n'
                    code += load_variable_into_register(p[3][2], 'h')
                    if p[3][4]:
                        code += 'LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[1][0], 'c')
                    if p[1][2]:
                        code+='LOAD a\n'
                    code += 'PUT c\n'
                    
                    code += load_variable_into_register(p[3][0], 'd')
                    if p[3][2]:
                        code+='LOAD a\n'
                    code += 'PUT d\n'
                    
            elif not p[1][1] and p[3][1]:
                code += load_value_into_register(p[1][0], 'c')
                if len(p[3]) == 5:
                    code += load_value_into_register(p[3][0], 'g')
                    if p[3][3]:
                        code += 'LOAD g\n'
                        code += 'PUT g\n'
                    code += load_variable_into_register(p[3][2], 'h')
                    if p[3][4]:
                        code += 'LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[3][0], 'd')
                    if p[3][2]:
                        code+='LOAD a\n'
                    code += 'PUT d\n'
                    
            elif p[1][1] and not p[3][1]:
                code += load_value_into_register(p[3][0],'d')
                if len(p[1]) == 5:
                    code += load_value_into_register(p[1][0], 'g')
                    if p[1][3]:
                        code += 'LOAD g\n'
                        code += 'LOAD g\n'
                    code += load_variable_into_register(p[1][2], 'h')
                    if p[1][4]:
                        code += 'LOAD a\n'
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                else:
                    code += load_variable_into_register(p[1][0],'c')
                    if p[1][2]:
                        code+='LOAD a\n'
                    code += 'PUT c\n'
                    
            else:
                code += load_value_into_register(p[1][0], 'c')
                code += load_value_into_register(p[3][0], 'd')
    else:
        if len(p[1]) == 5 and len(p[3]) == 5:
            code += load_value_into_register(p[1][0], 'g')
            code += load_variable_into_register(p[1][2], 'h')
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT c\n'
            code += load_value_into_register(p[3][0], 'g')
            code += load_variable_into_register(p[3][2], 'h')
            code += 'ADD g\n'
            code += 'LOAD a\n'
            code += 'PUT d\n'
        else:
            if p[1][1] and p[3][1]:
                if len(p[1]) == 5 and len(p[3]) != 5:
                    code += load_value_into_register(p[1][0], 'g')
                    code += load_variable_into_register(p[1][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                    code += load_variable_into_register(p[3][0], 'd')
                    code += 'PUT d\n'
                elif len(p[1]) != 5 and len(p[3]) == 5:
                    code += load_variable_into_register(p[1][0], 'c')
                    code += 'PUT c\n'
                    code += load_value_into_register(p[3][0], 'g')
                    code += load_variable_into_register(p[3][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[1][0], 'c')
                    code += 'PUT c\n'
                    
                    code += load_variable_into_register(p[3][0], 'd')
                    code += 'PUT d\n'
                    
            elif not p[1][1] and p[3][1]:
                code += load_value_into_register(p[1][0], 'c')
                if len(p[3]) == 5:
                    code += load_value_into_register(p[3][0], 'g')
                    code += load_variable_into_register(p[3][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT d\n'
                else:
                    code += load_variable_into_register(p[3][0], 'd')
                    code += 'PUT d\n'
                    
            elif p[1][1] and not p[3][1]:
                code += load_value_into_register(p[3][0],'d')
                if len(p[1]) == 5:
                    code += load_value_into_register(p[1][0], 'g')
                    code += load_variable_into_register(p[1][2], 'h')
                    code += 'ADD g\n'
                    code += 'LOAD a\n'
                    code += 'PUT c\n'
                else:
                    code += load_variable_into_register(p[1][0],'c')
                    code += 'PUT c\n'
                    
            else:
                code += load_value_into_register(p[1][0], 'c')
                code += load_value_into_register(p[3][0], 'd')

    code+='GET c\n'
    
    code+='SUB d\n'
    
    code+='JPOS {}\n'.format('p'+str(2))
    
    code+='JUMP {}\n'.format('p'+str(3))
    
    code+='RST a\n'
    
    code+='INC a\n'
    

    p[0] = code

def p_value_num(p):
    'value : num'
    p[0] = (p[1], False)

def p_value_identifier(p): #zwraca adres, True - zmienna, i True/False (czy indeksem tablicy jest zmienna, true jesli tak)
    'value : identifier'
    if len(p[1]) == 5: #tablica indeksowana zmienną - sprawdzamy czy dlugosc tupla jest rowna 3
        p[0] = (p[1][0], True, p[1][2], p[1][3], p[1][4])
    elif len(p[1]) == 4:                           # w procedurze tablica indeksowana stałą lol
        p[0] = (p[1][0], True, p[1][2], p[1][3])
    else:              #zmienna lub tablica indeksowana numerem   
        p[0] = (p[1][0], True, p[1][2]) 

def p_identifier_pid(p):
    'identifier : pidentifier'       
    global in_procedure, symbol_table
    check = get_mem_id_by_name(p[1])
    #print(check)
    is_arr = check_if_arr(p[1])
    if is_arr:
        print("błąd: niewłaściwe użycie tablicy", p[1], 'w linii', p.lineno(1))
        exit(1)
    if check is None:
        print("błąd: użycie niezadeklarowanej zmiennej", p[1], 'w linii', p.lineno(1))
        exit(1)
    
                                
    if in_procedure == 'MAIN':                                      
        memory_address = get_mem_id_by_name_in_prog(p[1])
        p[0] = (memory_address, False, False)
    
    else:           
        returnThing = None
        for i in range(len(symbol_table)):
            if symbol_table[i][0] == p[1]:
                if symbol_table[i][4] == in_procedure:
                    if symbol_table[i][3]:
                        returnThing = (symbol_table[i][1],False,True)
                    else:
                        returnThing = (symbol_table[i][1],False,False)

        p[0] = returnThing

def p_identifier_pidarrnum(p):
    'identifier : pidentifier LSQUAREBRACKET num RSQUAREBRACKET'
    global in_procedure
    if in_procedure == 'MAIN':
        memory_address = get_mem_id_by_name_in_prog(p[1]) + p[3]
        p[0] = (memory_address,False,False)
    else:
        offset = p[3]
        returnThing = None
        for i in range(len(symbol_table)):
            if symbol_table[i][0] == p[1]:
                if symbol_table[i][4] == in_procedure:
                    if symbol_table[i][3]:
                        returnThing = (symbol_table[i][1],False,True, offset)
                    else:
                        returnThing = (symbol_table[i][1],False,False, offset)
        p[0] = returnThing

def p_identifier_pidarrpid(p):                                          #to nwm
    'identifier : pidentifier LSQUAREBRACKET pidentifier RSQUAREBRACKET'

    global in_procedure
    if in_procedure == 'MAIN':
        memory_address = get_mem_id_by_name_in_prog(p[1])
        memory_address_cell = get_mem_id_by_name_in_prog(p[3])
        p[0] = (memory_address, True, memory_address_cell, False, False)
    else:
        tupleOne = None
        tupleTwo = None
        for i in range(len(symbol_table)):
            if symbol_table[i][0] == p[1]:
                if symbol_table[i][4] == in_procedure:
                    if symbol_table[i][3]:
                        tupleOne = (symbol_table[i][1],False,True)
                    else:
                        tupleOne = (symbol_table[i][1],False,False)
        for i in range(len(symbol_table)):
            if symbol_table[i][0] == p[3]:
                if symbol_table[i][4] == in_procedure:
                    if symbol_table[i][3]:
                        tupleTwo = (symbol_table[i][1],False,True)
                    else:
                        tupleTwo = (symbol_table[i][1],False,False)
        tuple = (tupleOne[0], True, tupleTwo[0],tupleOne[2],tupleTwo[2])
        p[0] = tuple

def p_error(p):
    if p != None:
        print(f'\nsyntax error: ‘{p.value}’')
    else:
        print(f'syntax error')



lexer = build_lex()

# Instantiate the parser
parser = yacc.yacc()

# Function to parse the file
def parse_and_write(filename, output_filename):
    try:
        with open(filename, 'r') as file:
            data = file.read()
            result = parser.parse(data)
            if result is not None:
                with open(output_filename, 'w') as output_file:
                    output_file.write(str(result))
            else:
                print('empty file')
    except FileNotFoundError:
        print("File not found.")

# Function to tokenize a file
def tokenize_file(filename):
    try:
        with open(filename, 'r') as file:
            data = file.read()
            lexer.input(data)
            while True:
                tok = lexer.token()
                if not tok:
                    break  # No more input
                print(tok)
    except FileNotFoundError:
        print("File not found.")

# Example usage
if __name__ == "__main__":
    file_name = sys.argv[1]
    output_file = sys.argv[2]
    parse_and_write(file_name, output_file)
