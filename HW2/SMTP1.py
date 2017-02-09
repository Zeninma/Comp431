import sys
import pdb

class SuperEnum(object):
    '''
    an Enum built for Python 2.7
    original source:
    http://codereview.stackexchange.com/questions/109724/yet-another-lightweight-enum-for-python-2-7
    '''
    class __metaclass__(type):
        def __iter__(self):
            for item in self.__dict__:
                if item == self.__dict__[item]:
                    yield item

'''
SPECIAL_SPACE are special char and white space specified in
the grammar of mail-cmd-from
'''
SPECIAL_SPACE = '<>()\t[]\.,;:@" '

'''
Following are output messages
'''
ERROR500 = "500 Syntax error: command unrecognized"
ERROR501 = "501 Syntax error in parameters or arguments"
ERROR503 = "503 Bad sequence of commands"
SUCCESS = "250 OK"
DATABEGIN = "354 Start mail input; end with <CRLF>.<CRLF>"

class State(SuperEnum):
    '''
    Enum for state of automaton
    '''
    INITIAL = 1
    RCPT = 2
    RCPTORDATA = 3
    DATA = 4

class CommandType(SuperEnum):
    '''
    Enum for command type
    '''
    MAIL_FROM = 1
    RCPT = 2
    DATA = 3
    ERROR = 4

def is_whitespace(character):
    '''
    parse white space
    return True if there is one
    '''
    is_space = (character == ' ')
    is_tab = (character == '\t')
    return is_space or is_tab


def is_alph(character):
    '''
    return True if arg is in <a>
    return False otherwise
    '''
    num_val = ord(character)
    capital = (num_val >= 65) and (num_val <= 90)
    small = (num_val >= 97) and (num_val <= 122)
    result = capital or small
    return result


def is_dig(character):
    '''
    return True if arg is in <d>
    return False otherwise
    '''
    result = (ord(character) >= 48) and (ord(character) <= 57)
    return result


def is_char(character):
    '''
    return True if arg is in <char>
    return False otherwise
    '''
    result = not character in SPECIAL_SPACE
    result = result and 0 <= ord(character) <= 127
    return result


def is_let_dig(character):
    '''
    return True if arg is in <let-dig>
    return False otherwise
    '''
    result = is_alph(character) or is_dig(character)
    return result


def parse_whitespace(cmd, pos):
    '''
    parse <whitespace>
    '''
    if pos+1 > len(cmd)-1:
        return 0
    if not is_whitespace(cmd[pos + 1]):
        return 0
    pos += 1
    while ((pos+1) < len(cmd)) and is_whitespace(cmd[pos+1]):
        pos += 1
    return pos


def parse_null_space(cmd, pos):
    '''
    parse <nullspace>
    '''
    if pos+1 > len(cmd)-1:
        return pos
    elif not is_whitespace(cmd[pos+1]):
        return pos
    else:
        pos = parse_whitespace(cmd, pos)
        return pos


def parse_ele(cmd, pos):
    '''
    parse <element>
    '''
    #Debug
    # print('in parse_ele')
    # pdb.set_trace()
    if (pos+1) > (len(cmd)-1):
        return 0
    if is_alph(cmd[pos+1]):
        pos += 1
        if (pos+1) > (len(cmd)-1):
            return 0
        if is_let_dig(cmd[pos+1]):
            pos += 1
            while (pos+1) <= (len(cmd)-1):
                if is_let_dig(cmd[pos+1]):
                    pos += 1
                else:
                    return pos
        else:
            return 0
    else:
        return 0
    #Debug
    # print('parse_ele: {position}'.format(position = str(pos)))
    return pos


def is_char_in_bound(cmd, pos):
    '''
    return True if cmd[pos+1] is not out of bound and is in <char>
    return False otherwise and print error otherwise
    '''
    if (pos+1) > (len(cmd)-1):
        return False
    return is_char(cmd[pos])


def parse_local_part(cmd, pos):
    '''
    parse <local-part> by checking whether there is at least one char
    '''
    char_num = 0
    if (pos+1) > (len(cmd)-1):
        return 0

    while is_char_in_bound(cmd, pos + 1):
        pos += 1
        char_num += 1
    if char_num == 0:
        return 0
    else:
        return pos


def parse_domain(cmd, pos):
    '''
    parse <domain> by checking whether if
    the domain has at list one a followed by let-dig-str
    '''
    # pdb.set_trace()
    if (pos+1) > (len(cmd)-1):
        return 0

    pos = parse_ele(cmd, pos)
    if pos == 0:
        return 0
    #path error since there should be a '>' after <domain>
    if (pos+1) > (len(cmd)-1):
        return pos

    if cmd[pos+1] == '.':
        pos += 1
        pos = parse_domain(cmd, pos)

    if pos == 0:
        return 0
    else:
        #Debug
        return pos


def parse_mailbox(cmd, pos):
    '''
    parse <mailbox>
    '''
    # pdb.set_trace()
    pos = parse_local_part(cmd, pos)
    if pos == 0:
        return 0
    if (pos+1) > (len(cmd)-1):
        return 0

    if cmd[pos+1] != "@":
        return 0
    pos += 1
    pos = parse_domain(cmd, pos)
    if pos == 0:
        return 0

    return pos


def parse_path(cmd, pos):
    '''
    parse <reverse-path>
    '''
    if (pos+1) > (len(cmd)-1):
        return 0
    else:
        pos += 1

    if cmd[pos] != "<":
        return 0

    pos = parse_mailbox(cmd, pos)
    if pos == 0:
        return 0

    if (pos+1) > (len(cmd)-1):
        return 0
    else:
        pos += 1

    if cmd[pos] != ">":
        return 0
    return pos


def parse_mail_from_cmd(cmd, pos):
    '''
    parse <mail-from-cmd> at root
    '''
    if len(cmd) < 10:
        return 0
    if cmd[0:4] != 'MAIL':
        return 0
    else:
        pos += 3
    # now cmd[pos] must be ' '
    pos = parse_whitespace(cmd, pos)
    if pos == 0:
        return 0
    if (pos+1) > (len(cmd)-1):
        return 0
    else:
        pos += 1

    if cmd[pos:pos+5] != 'FROM:':
        return 0
    else:
        pos += 4

    pos = parse_null_space(cmd, pos)
    if pos == 0:
        return 0
    pos = parse_path(cmd, pos)
    if pos == 0:
        return 0
#####################parse_mail_from_cmd done####################################
def check_cmd(line):
    '''
    try to parse command token and return corresponding state
    '''
    line_length = len(line)
    if line_length < 4:
        return CommandType.ERROR
    if line[0:4] == 'DATA':
        return CommandType.DATA
    if line_length >= 8:
        if line[0:8] == 'RCPT TO:':
            return CommandType.RCPT
    if line_length >= 10:
        if line[0:10] == 'MAIL FROM:':
            return CommandType.MAIL_FROM
    return CommandType.ERROR

def parse_data_cmd(cmd, pos):
    '''
    parse data cmd
    '''
    if len(cmd) < 5:
        return 0
    elif cmd[0:4] != 'DATA':
        return 0
    else:
        pos = 3
    pos = parse_null_space(cmd, pos)
    if (pos + 1) > len(cmd):
        return 0
    else:
        pos += 1
    if cmd[pos] == '\n':
        return 1
    else:
        return 0

def parse_rcpt_cmd(cmd, pos):
    '''
    parse <rcpt_to_cmd> at root
    '''
    if len(cmd) < 8:
        return 0
    if cmd[0:4] != 'RCPT':
        return 0
    else:
        pos += 3
    pos = parse_whitespace(cmd, pos)
    if pos == 0:
        return 0
    else:
        pos += 1
    #Debug
    if cmd[pos:pos+3] != 'TO:':
        return 0
    else:
        pos += 2

    pos = parse_null_space(cmd, pos)
    if pos == 0:
        return 0
    pos = parse_path(cmd, pos)
    if pos == 0:
        return 0

    pos = parse_null_space(cmd, pos)
    if (pos+1) > (len(cmd)-1):
        return 0
    else:
        pos += 1

    if cmd[pos] == '\n':
        return pos
    else:
        return 0


def output(mail_to, data):
    '''
    writing output file
    '''
    for forward_path in mail_to:
        mail_file = open('forward/' + forward_path, "a+")
        mail_file.write(data)
        mail_file.close()

def smtp_automaton():
    '''
    statemachine that handle the input lines
    '''
    state = State.INITIAL
    mail_from = ''
    mail_to = []
    data = ''
    for line in sys.stdin:
        print(line[0:len(line)-1])
        if state == State.DATA:
            if line == '.\n':
                #end message and start outputing
                print(SUCCESS)
                output(mail_to, data)
                mail_from = ''
                mail_to = []
                data = ''
                state = State.INITIAL
            else:
                data += line
        else:
            #Consume input and alter state
            cmd_type = check_cmd(line)
            if cmd_type == CommandType.ERROR:
                print(ERROR500)
                state = State.INITIAL
                mail_from = ''
                mail_to = []
                data = ''
            elif cmd_type == CommandType.MAIL_FROM:
                if state == State.INITIAL:
                    parse_result = parse_mail_from_cmd(line, 0)
                    if parse_result == 0:
                        print(ERROR501)
                        state = State.INITIAL
                        mail_from = ''
                        mail_to = []
                        data = ''
                    else:
                        print(SUCCESS)
                        path_start_pos = line.find('<')
                        mail_from = line[path_start_pos:len(line) - 1]
                        data += 'From: ' + mail_from + '\n'
                        state = State.RCPT
                else:
                    print(ERROR503)
                    state = State.INITIAL
                    mail_from = ''
                    mail_to = []
                    data = ''
            elif cmd_type == CommandType.RCPT:
                if state == State.RCPT or state == State.RCPTORDATA:
                    parse_result = parse_rcpt_cmd(line, 0)
                    if parse_result == 0:
                        print(ERROR501)
                        state = State.INITIAL
                        mail_from = ''
                        mail_to = []
                        data = ''
                    else:
                        print(SUCCESS)
                        path_start_pos = line.find('<')
                        mail_to.append(line[path_start_pos+1:len(line) - 2])
                        data += 'To: ' + line[path_start_pos:len(line) - 1] + '\n'
                        if state == State.RCPT:
                            state = State.RCPTORDATA
                else:
                    print(ERROR503)
                    state = State.INITIAL
                    mail_from = ''
                    mail_to = []
                    data = ''
            # CommandType.DATA
            else:
                if state == State.RCPTORDATA:
                    parse_result = parse_data_cmd(line, 0)
                    if parse_result == 0:
                        print(ERROR501)
                        state = State.INITIAL
                        mail_from = ''
                        mail_to = []
                        data = ''
                    else:
                        print(DATABEGIN)
                        state = State.DATA
                else:
                    print(ERROR503)
                    state = State.INITIAL
                    mail_from = ''
                    mail_to = []
                    data = ''

if __name__ == '__main__':
    smtp_automaton()
