source_str = '6b2a2a6b4a4b3a6b'
def ip_convert(source_str):
    mapper = {
        "a":"0",
        "b":"1"
    }
    dst_str = ""
    num_str = ""
    for i in range(0,len(source_str)):
        if source_str[i].isdigit():
            num_str+=source_str[i]
        else:
            for j in range(0,int(num_str)):
                dst_str += mapper[source_str[i]]
            num_str = ""

    divide = [7,15,23,31]
    x = 128
    son_num = 0
    ip = ''
    for i in range(0,len(dst_str)):
        if dst_str[i] == "1":
            son_num+=x
        x /= 2

        if i in divide:
            son_num = int(son_num)

            ip += str(son_num)
            ip += '.'
            x = 128
            son_num = 0

    ip= ip[0:-1]
    return ip
ip = ip_convert(source_str)
print(ip)



