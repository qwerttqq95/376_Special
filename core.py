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


def F2040():
    global A1, A2
    C = '4b'
    Data = '66 0c 75 00 00 80 fe'
    re_message = C + A1 + A2 + Data.replace(' ', '')
    cs = CS(strto0x(makelist(re_message)))
    return '683200320068' + re_message + cs + '16'


def data_init():
    global A1,A2
    C = '41'
    Data = '66 01 77 00 00 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'
    re_message = C + A1 + A2 + Data.replace(' ', '')
    cs = CS(strto0x(makelist(re_message)))
    return '687200720068' + re_message + cs + '16'


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
    global A1, A2
    A1 = list2str(APDU[1:3])
    A2 = list2str(APDU[3:5])
    return AFN(A1, A2, APDU[6:])


def AFN(A1, A2, data):
    if data[0] == '00':
        print('确认/否认')
        if list2str(data[2:6]) == '00000100':
            print('终端确认所发请求')
            return 1, '终端确认所发请求'
        else:
            print('Others')

    if data[0] == '02':
        print('链路接口检测')
        if list2str(data[2:6]) == '00000100' or list2str(data[2:6]) == '00000400':
            seq = hex(int('0110' + SEQ(data[1]), 2))[2:].zfill(2)
            print('seq', seq)
            re_data = '00' + seq + '00000100'
            L_ = '68 32 00 32 00 68'
            A3 = '66'
            C = '40'
            re_message = C + A1 + A2 + A3 + re_data.replace(' ', '')
            cs = CS(strto0x(makelist(re_message)))
            re_message = (L_ + re_message + cs + '16').replace(' ', '')
            return 0, re_message

    if data[0] == '0c':
        print('请求一类数据')
        if list2str(data[2:6]) == '000080fe':
            x = 'F2040 \n' + '信号强度:' + data[6] + '\n电话号码:' + list2str(data[7:13]) + '\nICCID:' + list2str(data[13:])
            print(x)
            return 1, x


def SEQ(num):
    bin_ = bin(int(num, 16))[2:].zfill(8)
    PSEQ = bin_[-4:]
    return PSEQ


A1 = ''
A2 = ''
