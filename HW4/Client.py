import sys
import pdb
from socket import *

FROM_MESSAGE = 'From:'
REENTER_FROM_MESSAGE = 'Please re enter the domain for the FROM: field'
TO_LIST_MESSAGE = 'Please enter a list of recepients split by commas'
REENTER_TO_LIST_MESSAGE = 'Please re enter the domain for the TO: field'
SUBJECT_MESSAGE = 'SUBJECT'

SPECIAL_SPACE = '<>()\t[]\.,;:@" '


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
        print('ERROR -- mail-from-cmd')
        return 0
    if not is_whitespace(cmd[pos + 1]):
        print('ERROR -- mail-from-cmd')
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
        print('ERROR -- element')
        return 0
    if is_alph(cmd[pos+1]):
        pos += 1
        if (pos+1) > (len(cmd)-1):
            print('ERROR -- element')
            return 0
        if is_let_dig(cmd[pos+1]):
            pos += 1
            while (pos+1) <= (len(cmd)-1):
                if is_let_dig(cmd[pos+1]):
                    pos += 1
                else:
                    return pos
        else:
            print('ERROR -- element')
            return 0
    else:
        print('ERROR -- element')
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
        print('ERROR -- local-part')
        return 0

    while is_char_in_bound(cmd, pos + 1):
        pos += 1
        char_num += 1
    if char_num == 0:
        print('ERROR -- local-part')
        return 0
    else:
        return pos


def parse_domain(cmd, pos):
    '''
    parse <domain> by checking whether if
    the domain has at list one a followed by let-dig-str
    '''
    if (pos+1) > (len(cmd)-1):
        print('ERROR -- domain')
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
    pdb.set_trace()
    pos = parse_local_part(cmd, pos)
    if pos == 0:
        return 0
    if (pos+1) > (len(cmd)-1):
        print('ERROR -- mailbox')
        return 0

    if cmd[pos+1] != "@":
        print('ERROR -- mailbox')
        return 0
    pos += 1
    pos = parse_domain(cmd, pos)
    if pos == 0:
        return 0

    return pos
####################################################################
###########################Begain Client Part#######################
####################################################################

class Ao_Client():
    '''
    Class of the client for Homework 4
    '''
    def __init__(self, new_host_name, new_port_num):
        self.domain = 'snapper.cs.unc.edu'
        self.serverName = new_host_name
        self.serverPort = int(new_port_num)
        self.message = ''
        self.message_to_server = ''
        self.receipt_list = []

    def parse_from_cmd(self):
        '''
        Keep asking user until receives valid domain
        '''
        from_domain = raw_input(FROM_MESSAGE)
        while parse_mailbox(from_domain, 0) == 0:
            from_domain = raw_input(REENTER_FROM_MESSAGE)
        self.domain = from_domain

    def not_qualified_receipt_list(self):
        '''
        Return True if the receipt_list is not valid
        Check the length
        and whether each item in the list is a valid mail_box
        '''
        is_empty =  len(self.receipt_list) < 1
        not_valid = False
        for receipt in self.receipt_list:
            if parse_mailbox(receipt, 0) == 0:
                return True
        return is_empty or not_valid

    def parse_to_cmd(self):
        '''
        Keep asking user until recieves a valid list of
        recepients
        '''
        to_list = raw_input(TO_LIST_MESSAGE)
        raw_receipt_list = to_list.split(',')
        for raw_receipt in raw_receipt_list:
            self.receipt_list.append(raw_receipt.strip(' '))
        while self.not_qualified_receipt_list():
            to_list = raw_input(REENTER_TO_LIST_MESSAGE)
            raw_receipt_list = to_list.split(',')
            for raw_receipt in raw_receipt_list:
                self.receipt_list.append(raw_receipt.strip(' '))

    def parse_subject_cmd(self):
        '''
        parse the subject command
        '''
        self.subject = raw_input(SUBJECT_MESSAGE)

    def parse_message_cmd(self):
        '''
        parse the message
        '''
        for line in sys.stdin:
            if line == '.':
                return
            else:
                self.message += line

    def take_input_message(self):
        '''
        Start the interactive mode, to gain the info from the user
        '''
        self.parse_from_cmd()
        self.parse_to_cmd()
        self.parse_subject_cmd()
        self.parse_message_cmd()

    def wait_greeting(self):
        '''
        To Receive the greeting message from the server
        '''
        self.client_socket.recv(1024)
        helo_message = 'HELO ' + self.domain + '\n'
        self.client_socket.send(helo_message.encode())

    def make_connection(self):
        '''
        Make connection to the SERVER
        '''
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect((self.serverName, self.serverPort))
        self.wait_greeting()
