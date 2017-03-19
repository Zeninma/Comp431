import sys
import pdb

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
    def __init__(self, file_name):
        '''
        constructor for Forwar_file_reader
        '''
        self.state = ReaderState.LISTEN_FROM
        self.file = open(file_name, "r")
    
    def quit(self):
        '''
        A helper function for print 'QUIT' command
        and then exit
        '''
        print('QUIT')
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
            elif line_len > 4:
                if line[0:5] == 'From:':
                    self.state = ReaderState.LISTEN_TO
                    print('DATA')
                    if self.wait(SUCCESS_354) == Response.ERROR:
                        self.quit()
                    print('.')
                    return CommandType.NEWSTART
                else:
                    print('DATA')
                    if self.wait(SUCCESS_354) == Response.ERROR:
                        self.quit()
                    return CommandType.DATA
        else:
            if line_len > 4:
                if line[0:5] == 'From:':
                    self.state = ReaderState.LISTEN_TO
                    print('.')
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
        raw_response = raw_input()
        raw_response_length = len(raw_response)
        response = raw_response + '\n'
        sys.stderr.write(response)
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
        for line in self.file.readlines():
            # pdb.set_trace()
            cmd_type = self.type_check(line)
            if cmd_type == CommandType.MAIL_FROM:
                if len(line) > 7:
                    print('MAIL FROM: ' + line[6:].strip('\n'))
                else:
                    print(FORWARD_FILE_ERROR)
                if self.wait(SUCCESS_250) == Response.ERROR:
                    self.quit()
            elif cmd_type == CommandType.RCPT:
                if len(line) > 4:
                    print('RCPT TO: ' + line[4:].strip('\n'))
                else:
                    print(FORWARD_FILE_ERROR)
                if self.wait(SUCCESS_250) == Response.ERROR:
                    self.quit()
            elif cmd_type == CommandType.NEWSTART:
                if len(line) > 7:
                    print('MAIL FROM: ' + line[6:].strip('\n'))
                else:
                    print(FORWARD_FILE_ERROR)
                if self.wait(SUCCESS_250) == Response.ERROR:
                    self.quit()
            #Then the line must be a part of the DATA
            else:
                print(line.strip('\n'))
        # out of the for loop, need to type the end Command
        # Need to check the case, where the file ends with empty data part
        # for the DATA part
        # the whole file ends with empty message
        if self.state == ReaderState.DATA_MODE:
            print('.')
            if self.wait(SUCCESS_250) == Response.ERROR:
                self.quit()
            self.quit()
        elif self.state == ReaderState.LISTEN_TO_MUL:
            print('DATA')
            if self.wait(SUCCESS_354) == Response.ERROR:
                self.quit()
            print('.')
            if self.wait(SUCCESS_250) == Response.ERROR:
                self.quit()
            self.quit()
        else:
            self.quit()

if __name__ == '__main__':
    file_name = sys.argv[1]
    file_reader = ForwardFileReader(file_name)
    file_reader.start()
