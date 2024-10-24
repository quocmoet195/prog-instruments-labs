import json


class Person:
    def __init__(self, info_dict):

        self.person_dict = info_dict
        self.telephone = info_dict['telephone']
        self.height = info_dict['height']
        self.inn = info_dict['inn']
        self.passport_number = info_dict['passport_number']
        self.university = info_dict['university']
        self.age = info_dict['age']
        self.political_views = info_dict['political_views']
        self.worldview = info_dict['worldview']
        self.address = info_dict['address']

    def get_person_info(self, parametr: str):
        '''
        Метод класса, который возвращает значение объекта по его названию.
        '''
        return self.person_dict[parametr]


def create_list_person(list_info):
    '''
    Функция принимает список словарей и возвращает список объектов класса Person
    '''
    list_persons = [] # Создали пустой список
    for i in list_info: # Цикл перебирает список
        person = Person(i) # создание объекта
        list_persons.append(person) # В конец списка обавляем объект
    return list_persons


def serialize(path, List):
    '''
    Функция для записи отсортированых данных в json файл
    '''
    write_list = [i.person_dict for i in List]
    with open(path, "w") as write_file:
        json.dump(write_list, write_file)


def deserialize(path):
    '''
    Функция принимает путь и читает json файл, возвращает содержание файла
    '''
    with open(path, 'r') as f:
        data = json.load(f)
        list_data = create_list_person(data)
    return list_data


def merge_sort(alist, sort_on):
    '''
    Функция сортировки слиянием. Сортирует объекты класса Person по указаному параметру.
    '''
    if len(alist) > 1:  # Если длина списка больше одного
        mid = len(alist)//2
        lefthalf = alist[:mid]
        righthalf = alist[mid:]

        merge_sort(lefthalf, sort_on)
        merge_sort(righthalf, sort_on)

        i = 0
        j = 0
        k = 0

        while i < len(lefthalf) and j < len(righthalf):  #Цикл, работает пока i меньше длины левой части спика и j меньше длины правой части спика
            if lefthalf[i].get_person_info(sort_on) < righthalf[j].get_person_info(sort_on):
                alist[k] = lefthalf[i]
                i = i+1
            else:
                alist[k] = righthalf[j]  # В результирующий список перемещаем на k место элемент правой части
                j = j+1
            k = k+1

        while i < len(lefthalf):  # Цикл работает пока длина левой части больше i
            alist[k] = lefthalf[i]  # В результирующий список перемещаем на k место элемент левой части
            i = i+1
            k = k+1

        while j < len(righthalf):  # Цикл работает пока длина правой части больше j
            alist[k] = righthalf[j]  # В результирующий список перемещаем на k место элемент правой части
            j = j+1
            k = k+1
    return alist


data = json.load(open("output.txt", encoding='windows-1251'))
sort_on = "age"
list_data = create_list_person(data)
result = merge_sort(list_data, sort_on)

serialize("110.json", result)
print(deserialize('110.json'))