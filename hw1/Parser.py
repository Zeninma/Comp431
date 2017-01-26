import pdb
import sys
SPECIAL_SPACE = '<>()\t[]\.,;:@" '


def is_whitespace(character):
    is_space = (character == ' ')
    is_tab = (character == '    ')
    return (is_space or is_tab)


def is_alph(character):
    num_val = ord(character)
    capital = ((65<=num_val) and (num_val<=90))
    small = ((97<=num_val) and (num_val<=122))
    result = capital or small
    return result


def is_dig(character):
    result = ((48<=ord(character)) and (ord(character)<=57))
    return result


def is_char(character):
    result = not (character in SPECIAL_SPACE)
    return result


def is_let_dig(character):
    result = is_alph(character) or is_dig(character)
    return result


def parse_whitespace(cmd, pos):
    if (pos+1 >len(cmd)-1):
        print('ERROR -- mail-from-cmd')
        return 0
    if(not is_whitespace(cmd[pos+1])):
        print('ERROR -- mail-from-cmd')
        return 0
    pos +=1
    while( (pos+1)<len(cmd) and is_whitespace(cmd[pos+1]) ):
        pos +=1
    return pos


def parse_null_space(cmd, pos):
    if (pos+1 >len(cmd)-1):
        return pos
    elif (not is_whitespace(cmd[pos+1])):
        return pos
    else:
        pos = parse_whitespace(cmd,pos)
        return pos


def parse_ele(cmd, pos):
    #Debug
    # print('in parse_ele')
    # pdb.set_trace()
    if (pos+1) > (len(cmd)-1):
        print('ERROR -- name')
        return 0
    if(is_alph(cmd[pos+1])):
        pos+=1
        if (pos+1) > (len(cmd)-1):
            print('ERROR -- name')
            return 0
        if(is_let_dig(cmd[pos+1])):
            pos+=1
            while( ((pos+1)<=(len(cmd)-1)) ):
                if(is_let_dig(cmd[pos+1])):
                    pos += 1
                else:
                    return pos
        else:
            print('ERROR -- name')
            return 0
    else:
        print('ERROR -- name')
        return 0
    #Debug
    # print('parse_ele: {position}'.format(position = str(pos)))
    return pos


def is_char_in_bound(cmd,pos):
    if (pos+1) > (len(cmd)-1):
        return False
    return is_char(cmd[pos])


def parse_local_part(cmd, pos):
    '''
    Check whether there is at least one char
    '''
    char_num = 0
    if (pos+1) > (len(cmd)-1):
        print('ERROR -- local-part')
        return 0

    while(is_char_in_bound(cmd,pos+1)):
        pos += 1
        char_num +=1
    if(char_num == 0):
        print('ERROR -- local-part')
        return 0
    else:
        return pos


def parse_domain(cmd, pos):
    '''
    Check whether if the domain has at list one a followed by let-dig-str
    '''
    # pdb.set_trace()
    if (pos+1) > (len(cmd)-1):
        print('ERROR -- domain')
        return 0


    pos = parse_ele(cmd, pos)
    if(pos == 0):
        return 0
    #path error since there should be a '>' after <domain>
    if ((pos+1) > (len(cmd)-1)):
        return pos

    if(cmd[pos+1] == '.'):
        pos+=1
        pos = parse_domain(cmd, pos)

    if(pos == 0):
        return 0
    else:
        #Debug
        return pos


def parse_mailbox(cmd, pos):
    # pdb.set_trace()
    if (pos+1) > (len(cmd)-1):
        print('ERROR -- mailbox')
        return 0
    else:
        pos += 1

    pos = parse_local_part(cmd, pos)
    if(pos == 0):
        return 0
    if (pos+1) > (len(cmd)-1):
        print('ERROR -- mailbox')
        return 0

    if(cmd[pos+1] != "@"):
        print('ERROR -- mailbox')
        return 0
    pos+=1
    pos = parse_domain(cmd, pos)
    if(pos == 0):
        return 0

    return pos


def parse_path(cmd, pos):
    # pdb.set_trace()
    if (pos+1) > (len(cmd)-1):
        print('ERROR -- path')
        return 0
    else:
        pos += 1
    if(cmd[pos]!="<"):
        print('ERROR -- path')
        return 0

    pos = parse_mailbox(cmd, pos)
    if(pos == 0):
        return 0
    
    if (pos+1) > (len(cmd)-1):
        print('ERROR -- path')
        return 0
    else:
        pos += 1

    if(cmd[pos]!=">"):
        print('ERROR -- path')
        return 0
    return pos


def parse_mail_from_cmd(cmd, pos):
    # pdb.set_trace()
    if(len(cmd)<10):
        print('ERROR -- mail-from-cmd')
        return 0
    else:
        pos += 1
    if(cmd[0:4]!='MAIL'):
        print('ERROR -- mail-from-cmd')
        return 0
    else:
        pos += 3
    # now cmd[pos] must be ' '
    pos = parse_whitespace(cmd, pos)
    if(pos == 0):
        return 0
    #Debug
    if (pos+1) > (len(cmd)-1):
        print('ERROR -- path')
        return 0
    else:
        pos += 1

    if(cmd[pos:pos+5]!='FROM:'):
        print('ERROR -- mail-from-cmd')
        return 0
    else:
        pos += 4

    pos = parse_null_space(cmd, pos)
    if(pos == 0):
        print('ERROR -- mail-from-cmd')
        return 0
    pos = parse_path(cmd, pos)
    if(pos == 0):
        return 0
    
    pos = parse_null_space(cmd, pos)

    if(cmd[-1] == '\n'):
        print('Sender OK')
    #to be ctn'd for <CRLF>



if __name__ == '__main__':
    for line in sys.stdin:
            print(line[:len(line)-1])
            parse_mail_from_cmd(line, -1)