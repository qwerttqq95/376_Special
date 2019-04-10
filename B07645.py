'''
    模拟表程序
'''
import Comm, binascii, re, serial, time, datetime,traceback


def Electricity_meter_date_and_week_and_time(data):
    if data == '@GetDateWeek@':
        time1_str = datetime.datetime.now().strftime('%C%m%d%w')
        if len(time1_str) == 7:
            time1_str = time1_str[0:6] + '0' + time1_str[-1]
        return time1_str
    elif data == '@GetTime@':
        time2_str = datetime.datetime.now().strftime('%T').replace(':', '')
        return time2_str
    elif data == '@freezeTime@':
        time3_str = datetime.datetime.now().strftime('%M%H%d%m%y').replace(':', '')
        return time3_str
    else:
        print('Electricity_meter_date_and_week_and_time not found!',data)


def conctrlcode(code):
    if code == '11':
        recode = int(code, 16) + 128
        recode = hex(recode)[2:]
        return recode


def data_len(code):
    m = hex(int(code, 16) - 4)[2]
    if m == '0':
        return m
    if m == '1':
        pass
    if m == '6':
        return m


def strto0x(context):  # list
    context = [int(x, 16) for x in context]
    new_context = []
    while context:
        current_context = chr(context.pop())
        new_context.append(current_context)
    new_context.reverse()
    return new_context


def CS(list, b):
    sum = 0
    while list:
        sum = sum + ord(list.pop())
    sum = hex(sum & 0xff)[2:]
    if len(sum) == 1:
        sum = "0" + sum
    try:
        if sum == b.lower():
            pass
    except:
        if b is None:
            pass
        else:
            print('校验错误')
    return sum


def readdata(OI):
    f = open('source\\07data', 'r', encoding='UTF-8')
    while 1:
        text = f.readline()
        if text == '':
            print('ERROR ON read_data',OI.lower())
            break
        text1 = re.findall(OI.lower(), text)
        if not text1:
            continue
        else:
            if text1[0] == OI.lower():
                text = text.split(' ')
                data = text[-1][0:-1]
                if re.findall(',',data) is not None:
                    data = data.split(',')
                    data = Comm.list2str(data)
                name = text[-2]
                if data[0] == '@':
                    data_time = Electricity_meter_date_and_week_and_time(data)
                    print('数据标识及时间', name, datetime.datetime.now().strftime('%T'))
                    return data_time, name
                print('数据标识及时间:', name, datetime.datetime.now().strftime('%T'))
                return data, name
    f.close()


def plus33(message):
    newstr = ''
    if message is None:
        print('plus33 is none')
    else:
        if re.findall(',', message):
            message = message.split(',')
            lenth = len(message)
            i = 0
            while lenth:
                new_list = []
                lenth -= 1
                returnvalue = Comm.makelist(message[i])
                i += 1
                while returnvalue:
                    new_list.append(hex(int(returnvalue.pop(), 16) + 51)[2:])
                value_str = Comm.list2str(new_list)
                newstr = newstr + value_str
                return newstr
        else:
            message = Comm.makelist(message)
            lenth = len(message)
            new_list = []
            while lenth:
                lenth -= 1
                new_list.append(hex(int(message.pop(), 16) + 51)[2:])
            newstr = Comm.list2str(new_list)
            return newstr


def minus33(list):
    new_list = []
    while list:
        middle = hex(int(list.pop(), 16) - 51)[2:]
        if len(middle) == 1:
            middle = '0' + middle
        if middle == 'x1':
            middle = 'FF'
        new_list.append(middle)
    return new_list


def returnframe(add, reconctrlcode, L, D, N):
    text = '68' + add + '68' + reconctrlcode + L + D + N
    cs = CS(strto0x(Comm.makelist(text)), None)
    text = text + cs + '16'
    return text


def deal_receive(message):
    while 1:
        if message[0] == '68':
            address = message[1:7]
            break
        else:
            del message[0]
    reconctrlcode = conctrlcode(message[8])
    datasign = message[10:14]
    D = Comm.list2str(datasign)
    cs = CS(strto0x(message[0:-2]), message[-2])
    OI = Comm.list2str(minus33(datasign))
    a = readdata(OI)
    if not a:
        print('OI 无法解析')
    else:
        returnstr = plus33(a[0])  # Date!!!!
        L = hex(4 + len(Comm.makelist(returnstr)))[2:].zfill(2)
        text = returnframe(Comm.list2str(address), reconctrlcode, L, D, returnstr)
        print('Sending:', Comm.makestr(text))
        t.write(binascii.a2b_hex(text))

def check(temp):
    global temp_list
    Malist = Comm.makelist(temp)
    temp_list = temp_list + Malist
    while 1:
        try:
            if temp_list[0] == '68':
                add = temp_list[1:7]
                if temp_list[7] == '68':
                    ctrlcode = temp_list[8]
                    lenth = temp_list[9]
                    data_sign = temp_list[10:14]
                    left = int(lenth,16) - 4
                    if left > 0:
                        exter = temp_list[14:14+left]
                        total = 14+ left +2
                        message = temp_list[0:16+left]
                    else:
                        message = temp_list[0:16]
                    return message
            else:
                del temp_list[0]
        except:
            traceback.print_exc(file=open('bug.txt', 'a+'))
            return 1


def clear_templist():
    global temp_list
    temp_list = []

temp_list = []

if __name__ == '__main__':
    data = ''
    t = serial.Serial('COM7', 2400, timeout=0.5, parity='E', stopbits=1)
    while 1:
        time.sleep(1.2)
        num = t.inWaiting()
        data = data + str(binascii.b2a_hex(t.read(num)))[2:-1]
        if data == '':
            continue
        else:
            message = check(data)
            if message != 1 and message is not None:
                print('Received: ', message)
                deal_receive(message)
                temp_list = []
                data = ''
            else:
                continue


