from bs4 import BeautifulSoup


def parse(data,type):
    data = BeautifulSoup(data, "lxml")
    result_list = data.find_all(name="li", class_="gl-item")
    print(data)
    for k in range(0,len(result_list)):
        i = result_list[k]
        yield (str(i),True)



def parse_list_page(data):
    data = BeautifulSoup(data, "lxml")
    result_list = data.find_all(name="li", class_="gl-item")
    print(data)
    for k in range(0,len(result_list)):
        i = result_list[k]
        yield (str(i),True)

def parse_single_goods():
    pass

TYPE_LIST_PAGE = 1
TYPE_SINGLE_GOODS = 2