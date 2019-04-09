def makestr(message):
    str_ = ''
    x = 0
    lenth = len(message)
    while lenth > 0:
        str_ = str_ + message[x:x + 2] + ' '
        x += 2
        lenth -= 2
    return str_


def makelist(message):
    list = []
    x = 0
    lenth = len(message)
    while lenth > 0:
        list.append(message[x:x + 2])
        x += 2
        lenth -= 2
    return list


def strto0x(context):
    context = [int(x, 16) for x in context]
    new_context = []
    while context:
        current_context = chr(context.pop())
        new_context.append(current_context)
    new_context.reverse()
    return new_context


def list2str(message):
    text = ''
    i = 0
    lenth = len(message)
    while lenth > 0:
        text = text + message[i]
        i += 1
        lenth -= 1
    return text


def lenth(code):
    L1 = bin(int(code[0], 16))[2:-2].zfill(6)
    L2 = bin(int(code[1], 16))[2:].zfill(8)
    len_ = int(L2 + L1, 2)
    print('len', len_)
    return len_


def CS(list):
    sum = 0
    while list:
        sum = sum + ord(list.pop())
    sum = hex(sum & 0xff)[2:]
    if len(sum) == 1:
        sum = "0" + sum
    return sum


def analysis(code):
    code = makelist(code)
    while 1:
        if code[0] == '68':
            break
        else:
            code = code[1:]
    L1 = code[1:3]
    APDU_len = lenth(L1)
    APDU = code[6:6 + APDU_len]
    A1 = list2str(APDU[1:3])
    A2 = list2str(APDU[3:5])
    DAT_rec = list2str(APDU[6:]).replace(' ', '')
    DAT_sign = '027300000100'
    if DAT_sign == DAT_rec:
        A3 = '66'
        L_C = '68 32 00 32 00 68 40'
        DAT_ret = '006300000100'
        re_message = L_C + A1 + A2 + A3 + DAT_ret.replace(' ', '')
        cs = CS(strto0x(makelist(re_message)))
        re_message = (re_message + cs + '16').replace(' ', '')
        return re_message

