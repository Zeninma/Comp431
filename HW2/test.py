import sys
import pdb

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
    # pdb.set_trace()
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
    # pdb.set_trace()
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


def parse_path(cmd, pos):
    '''
    parse <reverse-path>
    '''
    # pdb.set_trace()
    if (pos+1) > (len(cmd)-1):
        print('ERROR -- path')
        return 0
    else:
        pos += 1

    if cmd[pos] != "<":
        print('ERROR -- path')
        return 0

    pos = parse_mailbox(cmd, pos)
    if pos == 0:
        return 0

    if (pos+1) > (len(cmd)-1):
        print('ERROR -- path')
        return 0
    else:
        pos += 1

    if cmd[pos] != ">":
        print('ERROR -- path')
        return 0
    return pos


def parse_mail_from_cmd(cmd, pos):
    '''
    parse <mail-from-cmd> at root
    '''
    if len(cmd) < 10:
        print('ERROR -- mail-from-cmd')
        return 0
    if cmd[0:4] != 'MAIL':
        print('ERROR -- mail-from-cmd')
        return 0
    else:
        pos += 3
    # now cmd[pos] must be ' '
    pos = parse_whitespace(cmd, pos)
    if pos == 0:
        return 0
    #Debug
    if (pos+1) > (len(cmd)-1):
        print('ERROR -- path')
        return 0
    else:
        pos += 1

    if cmd[pos:pos+5] != 'FROM:':
        print('ERROR -- mail-from-cmd')
        return 0
    else:
        pos += 4

    pos = parse_null_space(cmd, pos)
    if pos == 0:
        print('ERROR -- mail-from-cmd')
        return 0
    pos = parse_path(cmd, pos)
    if pos == 0:
        return 0

    pos = parse_null_space(cmd, pos)
    if (pos+1) > (len(cmd)-1):
        print('ERROR -- path')
        return 0
    else:
        pos += 1

    if cmd[pos] == '\n':
        print('Sender ok')
        return pos
    else:
        print('ERROR -- mail-from-cmd')
        return 0


def parse_rcpt_to(cmd, pos):
    '''
    parse <rcpt_to_cmd> at root
    '''
    if len(cmd) < 8:
        print('ERROR -- mail-from-cmd')
        return 0
    if cmd[0:4] != 'RCPT':
        print('ERROR -- mail-from-cmd')
        return 0
    else:
        pos += 3
    pdb.set_trace()
    pos = parse_whitespace(cmd, pos)
    if pos == 0:
        return 0
    else:
        pos += 1
    #Debug
    if cmd[pos:pos+3] != 'TO:':
        print('ERROR -- mail-from-cmd')
        return 0
    else:
        pos += 2

    pos = parse_null_space(cmd, pos)
    if pos == 0:
        print('ERROR -- mail-from-cmd')
        return 0
    pos = parse_path(cmd, pos)
    if pos == 0:
        return 0

    pos = parse_null_space(cmd, pos)
    if (pos+1) > (len(cmd)-1):
        print('ERROR -- path')
        return 0
    else:
        pos += 1

    if cmd[pos] == '\n':
        print('Sender ok')
        return pos
    else:
        print('ERROR -- mail-from-cmd')
        return 0


def parse_data_cmd(cmd, pos):
    '''
    Keyword Argument:
        cmd
        pos
    parse data cmd from the root
    '''
    if len(cmd) < 5:
        print('500 Syntax error: command unrecognized')
        return 0
    if cmd[0:4] != 'DATA':
        print('500 Syntax error: command unrecognized')
        return 0
    pos = 4
    pos = parse_null_space(cmd, pos)
    if len(cmd) < pos + 1:
        print('500 Syntax error: command unrecognized')
        return 0
    if cmd[pos + 1] != '\n':
        print('500 Syntax error: command unrecognized')
        return 0
    else:
        print('354 Start mail input; end with <CRLF>.<CRLF>')
        return 1


def build_str(str_builder, new_str):
    '''
    add new input to the string culmulatively
    '''
    str_builder = str_builder + new_str
    return str_builder


def is_end(data, new_data):
    '''
    check whether the data input is ended
    '''
    if (new_data == '.\n') and (data[-1] == '\n'):
        return True
    else:
        return False


def construct_smtp(cmd):
    '''
    acts like a state machine, consume input to change phase
    '''
    str_builder = ''
    line_reader = sys.stdin
    #Consume the line and check its validity for mail from cmd
    cmd = line_reader.readline()
    if parse_mail_from_cmd(cmd, 0) == 1:
        str_builder = build_str(str_builder, cmd)
        print(cmd)
        print('250 OK')
    #Consume the line and check its validity for RCPT command
    cmd = line_reader.readline()
    if parse_rcpt_to(cmd, 0) == 1:
        str_builder = build_str(str_builder, cmd)
        print(cmd)
        print('250 OK')
    #Consume the line, see whether it is another rcpt_to_cmd or
    #a data, and keep adding rcpt if the line is a valid rcpt command


if __name__ == '__main__':
    for line in sys.stdin:
        parse_rcpt_to(line, 0)
