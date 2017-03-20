import sys
import pdb
from socket import *

####################################################################
###########################SMTP2 Begin##############################
####################################################################
SUCCESS_250 = '250 '
SUCCESS_354 = '354 '
FORWARD_FILE_ERROR = 'ERROR IN ORIGINAL FORWARD FILE'

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

class CommandType(SuperEnum):
    '''
    Enum for command type
    '''
    MAIL_FROM = 1
    RCPT = 2
    DATA = 3
    NEWSTART = 4

class ReaderState(SuperEnum):
    '''
    an ENUM for ForwardFileReader state
    '''
    #waiting for FROM command
    LISTEN_FROM = 1
    #waiting for RCPT TO command
    LISTEN_TO = 2
    #receive following line as part of DATA
    DATA_MODE = 3
    #have already recieved one RCPT TO command,
    #waiting for other RCPT TO command or DATA
    LISTEN_TO_MUL = 4

class Response(SuperEnum):
    '''
    an ENUM for response from SMTP server
    '''
    OKM = 1
    ERROR = 2

#########################################################################
#######################Above are helper class, mainly ENUM ##############
#########################################################################

class ForwardFileReader():
    '''
    Read a forward file, and then generate SMTP command correspondingly.
    After ouputing each command, pause and wait for SMTP server respond.
    Quit if there is any error or reaching the end of the forward file.
    '''
    def __init__(self, new_mail_content, new_socket):
        '''
        constructor for Forwar_file_reader
        KeyArgument:
        new_mail_content: A list of lines of mail content.
        new_socket: The client socket
        '''
        self.state = ReaderState.LISTEN_FROM
        self.mail_content = new_mail_content
        self.client_socket = new_socket

    def quit(self):
        '''
        A helper function for print 'QUIT' command
        and then exit
        '''
        socket.send('QUIT'.encode())
        socket.close()
        sys.exit(0)

    def type_check(self, line):
        '''
        check the command type of the input line,
        then echo the input line, and return the
        command's type
        '''
        line_len = len(line)
        if self.state == ReaderState.LISTEN_FROM:
            if line_len > 4:
                if line[0:5] == 'From:':
                    self.state = ReaderState.LISTEN_TO
                    return CommandType.MAIL_FROM
        elif self.state == ReaderState.LISTEN_TO:
            if line_len > 2:
                if line[0:3] == 'To:':
                    self.state = ReaderState.LISTEN_TO_MUL
                    return CommandType.RCPT
            #the original document has error
        elif self.state == ReaderState.LISTEN_TO_MUL:
            if line_len > 2:
                if line[0:3] == 'To:':
                    return CommandType.RCPT
            # empty message followed by another forward email
            if line_len > 4:
                if line[0:5] == 'From:':
                    self.state = ReaderState.LISTEN_TO
                    socket.send('DATA'.encode())
                    if self.wait(SUCCESS_354) == Response.ERROR:
                        self.quit()
                    socket.send('.'.encode())
                    return CommandType.NEWSTART
                else:
                    socket.send('DATA'.encode())
                    self.state = ReaderState.DATA_MODE
                    if self.wait(SUCCESS_354) == Response.ERROR:
                        self.quit()
                    return CommandType.DATA
            socket.send('DATA'.encode)
            self.state = ReaderState.DATA_MODE
            if self.wait(SUCCESS_354) == Response.ERROR:
                self.quit()
            return CommandType.DATA
        else:
            if line_len > 4:
                if line[0:5] == 'From:':
                    self.state = ReaderState.LISTEN_TO
                    socket.send('.'.encode())
                    if self.wait(SUCCESS_250) == Response.ERROR:
                        self.quit()
                    return CommandType.NEWSTART
            else:
                return CommandType.DATA

    def wait(self, response_num):
        '''
        wait for SMTP server's response
        and return status accordingly
        '''
        raw_response = socket.recv(1024).decode()
        raw_response_length = len(raw_response)
        #The original response sent by the sever contains new line at the end now
        # response = raw_response + '\n'
        # No stderr for the response
        # sys.stderr.write(response)
        if raw_response_length < 4:
            return Response.ERROR
        else:
            if raw_response[0:4] == response_num:
                return Response.OKM
            else:
                return Response.ERROR

    def start(self):
        '''
        start processing forward file
        '''
        for line in self.mail_content:
            # pdb.set_trace()
            cmd_type = self.type_check(line)
            if cmd_type == CommandType.MAIL_FROM:
                if len(line) > 7:
                    socket.send(('MAIL FROM: ' + line[6:].strip('\n')).encode())
                else:
                    print(FORWARD_FILE_ERROR)
                if self.wait(SUCCESS_250) == Response.ERROR:
                    self.quit()
            elif cmd_type == CommandType.RCPT:
                if len(line) > 4:
                    socket.send(('RCPT TO: ' + line[4:].strip('\n')).encode())
                else:
                    print(FORWARD_FILE_ERROR)
                if self.wait(SUCCESS_250) == Response.ERROR:
                    self.quit()
            elif cmd_type == CommandType.NEWSTART:
                if len(line) > 7:
                    socket.send(('MAIL FROM: ' + line[6:].strip('\n')).encodoe())
                else:
                    print(FORWARD_FILE_ERROR)
                if self.wait(SUCCESS_250) == Response.ERROR:
                    self.quit()
            #Then the line must be a part of the DATA
            else:
                socket.send(line.strip('\n').encode())
        # out of the for loop, need to type the end Command
        # Need to check the case, where the file ends with empty data part
        # for the DATA part
        # the whole file ends with empty message
        if self.state == ReaderState.DATA_MODE:
            socket.send('.'.encode())
            if self.wait(SUCCESS_250) == Response.ERROR:
                self.quit()
            self.quit()
        elif self.state == ReaderState.LISTEN_TO_MUL:
            socket.send('DATA'.encode())
            if self.wait(SUCCESS_354) == Response.ERROR:
                self.quit()
            socket.send('.'.encode())
            if self.wait(SUCCESS_250) == Response.ERROR:
                self.quit()
            self.quit()
        else:
            self.quit()
####################################################################
###########################SMTP2 Ends###############################
####################################################################

FROM_MESSAGE = 'From:\n'
REENTER_FROM_MESSAGE = 'Please re enter the domain for the FROM: field:\n'
TO_LIST_MESSAGE = 'Please enter a list of recepients split by commas\n'
REENTER_TO_LIST_MESSAGE = 'Please re enter the domain for the TO: field\n'
SUBJECT_MESSAGE = 'SUBJECT:\n'
MESSAGE_MESSAGE = 'MESSAGE:\n'

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
        self.message_line_list = []
        self.subject = ''
        self.client_socket = None
        self.sender = None

    def parse_from_cmd(self):
        '''
        Keep asking user until receives valid domain
        '''
        from_domain = raw_input(FROM_MESSAGE)
        while parse_mailbox(from_domain, 0) == 0:
            from_domain = raw_input(REENTER_FROM_MESSAGE)
        self.from_domain = from_domain

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
        pdb.set_trace()
        print(MESSAGE_MESSAGE)
        for line in sys.stdin:
            if line == '.\n':
                break
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

    def form_message(self):
        '''
        Form the intergrated message that is going to be sent
        to the sever.
        '''
        #MAIL FROM: mail_box
        self.message_to_server += 'MAIL FROM: ' + self.from_domain + '\n'
        #RCPT TO: mail_box
        for receipt in self.receipt_list:
            self.message_to_server += 'RCPT TO: ' + receipt + '\n'
        #FROM: mail_box
        self.message_to_server += 'FROM: ' + self.from_domain + '\n'
        #TO: mail_box
        for receipt in self.receipt_list:
            self.message_to_server += 'TO: ' + receipt + '\n'
        #SUBJECT: subject
        self.message_to_server += 'SUBJECT: ' + self.subject + '\n'
        #empty line followed by message
        self.message_to_server += '\n'
        #body of the message
        self.message_to_server += self.message
        self.message_line_list = self.message.split('\n')

    def send_mail(self):
        '''
        Interacte with the server and send the mail
        '''
        self.sender = ForwardFileReader(self.message_line_list, self.client_socket)
        # the sender will close the socket when it quits
        self.sender.start()

    def wait_greeting(self):
        '''
        To Receive the greeting message from the server
        '''
        #receive greeting
        self.client_socket.recv(1024)
        helo_message = 'HELO ' + self.domain + '\n'
        #send HELO and receive 250 ack
        self.client_socket.send(helo_message.encode())
        ack_num = self.client_socket.recv(1024).decode()
        ack_num = int(ack_num[0:3])
        if ack_num == 250:
            self.form_message()
            self.send_mail()


    def make_connection(self):
        '''
        Make connection to the SERVER
        '''
        self.client_socket = socket(AF_INET, SOCK_STREAM)
        self.client_socket.connect((self.serverName, self.serverPort))
        self.wait_greeting()

    def start(self):
        '''
        Start the client process
        '''
        self.take_input_message()
        pdb.set_trace()
        self.make_connection()

if __name__ == '__main__':
    client = Ao_Client(sys.argv[1], sys.argv[2])
    client.start()
