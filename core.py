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
    global A1, A2
    C = '41'
    Data = '66 01 77 00 00 02 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'
    re_message = C + A1 + A2 + Data.replace(' ', '')
    cs = CS(strto0x(makelist(re_message)))
    return '687200720068' + re_message + cs + '16'


def set_test_point():
    global A1, A2
    C = '4a'
    Data = '66 04 72 00 00 01 04 01 03 20 00 FF FF FF 7F 00 00 05 00 00 00 01 05 00 55 23 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00 00'
    re_message = C + A1 + A2 + Data.replace(' ', '')
    cs = CS(strto0x(makelist(re_message)))
    return '68be00be0068' + re_message + cs + '16', A1, A2


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
        if list2str(data[2:6]) == '01010103':
            list_ = [list2str(data[13:10:-1]), list2str(data[16:13:-1]), list2str(data[19:16:-1]),
                     list2str(data[22:19:-1]), list2str(data[25:22:-1]), list2str(data[28:25:-1]),
                     list2str(data[31:28:-1]), list2str(data[34:31:-1]), list2str(data[36:34:-1]),
                     list2str(data[38:36:-1]), list2str(data[40:38:-1]), list2str(data[42:40:-1]),
                     list2str(data[44:42:-1]), list2str(data[46:44:-1]), list2str(data[48:46:-1]),
                     list2str(data[51:48:-1]), list2str(data[54:51:-1]), list2str(data[57:54:-1]),
                     list2str(data[60:57:-1]), list2str(data[63:60:-1]), list2str(data[66:63:-1]),
                     list2str(data[69:66:-1]), list2str(data[72:69:-1])
                     ]
            print('list', list_)
            x = ['一类数据F25:', '抄表日期:' + data[10] + '年' + data[9] + '月' + data[8] + '日' + data[7] + '时' + data[6] + '分',
                 '当前总有功功率:' + add_point(list_[0], 0.0001), '当前A相有功功率:' + add_point(list_[1], 0.0001),
                 '当前B相有功功率:' + add_point(list_[2], 0.0001), '当前C相有功功率:' + add_point(list_[3], 0.0001),
                 '当前总无功功率:' + add_point(list_[4], 0.0001), '当前A相无功功率:' + add_point(list_[5], 0.0001),
                 '当前B相无功功率:' + add_point(list_[6], 0.0001), '当前C相无功功率:' + add_point(list_[7], 0.0001),
                 '当前总功率因数' + add_point(list_[8], 0.1), '当前A相功率因数' + add_point(list_[9], 0.1),
                 '当前B相功率因数' + add_point(list_[10], 0.1), '当前C相功率因数' + add_point(list_[11], 0.1),
                 '当前A相电压' + add_point(list_[12], 0.1), '当前B相电压' + add_point(list_[13], 0.1),
                 '当前C相电压' + add_point(list_[14], 0.1),
                 '当前A相电流' + add_point(list_[15], 0.001), '当前B相电流' + add_point(list_[16], 0.001),
                 '当前C相电流' + add_point(list_[17], 0.001), '当前零序电流' + add_point(list_[18], 0.001),
                 '当前总视在功率' + add_point(list_[19], 0.0001), '当前A相视在功率' + add_point(list_[20], 0.0001),
                 '当前B相视在功率' + add_point(list_[21], 0.0001), '当前C相视在功率' + add_point(list_[22], 0.0001)
                 ]
            data_ = ['666666', '111111', '222222', '333333', '33333', '22222', '11111', '66666', '0321', '0654', '0987',
                     '0789', '2233', '2212', '2211', '005300', '005200', '005100', '444444', '055005', '055050',
                     '055500', '055555']
            q = 0
            error_list = []
            for a in list_:
                if data_[q] == a:
                    pass
                else:
                    error_list.append(x[q + 1])
                q += 1
            print('error_list', error_list)
            return 3, x


def add_point(num, bit):
    return str(int(num) * bit)


def SEQ(num):
    bin_ = bin(int(num, 16))[2:].zfill(8)
    PSEQ = bin_[-4:]
    return PSEQ


A1 = ''
A2 = ''
