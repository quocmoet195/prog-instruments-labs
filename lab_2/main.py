#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
import re
from tqdm import tqdm
import argparse


class Reader:

    def __init__(self):
        pass

    def read_data(self, path: str) -> list:
        '''
        Метод считывает файл по заданому пути и возвращает список с задаными данными.
        Передаеться путь файла который будет считываться.
        '''
        data = json.load(open(path, encoding='windows-1251'))


class Validator:

    readers = {}

    def __init__(self, reader: object, format_data_reader : str)-> None:
        '''
        Конструктор класса.
        Объект класса который будет считывать файлы.
        Формат считываемых даных.
        '''
        self.reader = reader
        self.readers[format_data_reader] = reader
        self.invalid_data = {
            'invalid_telephone': 0,
            'invalid_height': 0,
            'invalid_inn': 0,
            'invalid_passport_number': 0,
            'invalid_university': 0,
            'invalid_age': 0,
            'invalid_political_views': 0,
            'invalid_world_view': 0,
            'invalid_address': 0
        }
        self.valid_data = 0
        self.sum_invalid_data = 0

    def valid_telephone(self, phone_number: str) -> bool:

        patern = '[+-]7\-\(\d\d\d\)\-\d\d\d\-\d\d\-\d\d'
        if re.match(patern, phone_number):
            return True
        self.count_invalid_data("invalid_telephone")
        return False

    def valid_height(self, height) -> bool:

        if isinstance(height, float):
            if 2 > height > 0.7:
                return True
            self.count_invalid_data("invalid_height")
            return False
        if not height.replace(".", "").isdigit():
            self.count_invalid_data("invalid_height")
            return False
        elif "," not in height and (2 > float(height) > 0.7):
            return True
        self.count_invalid_data("invalid_height")
        return False

    def valid_inn(self, inn: str) -> bool:
        if len(inn) > 12:
            self.count_invalid_data("invalid_inn")
            return False
        if not inn.isdigit():
            self.count_invalid_data("invalid_inn")
            return False
        return True

    def valid_passport_number(self, passport_number) -> bool:

        if not str(passport_number).isdigit():
            self.count_invalid_data("invalid_passport_number")
            return False
        elif len(str(passport_number)) > 6:
            self.count_invalid_data("invalid_passport_number")
            return False
        return True

    def valid_university(self, university: str) -> bool:

        universitys = ['Филиал Российской правовой академии',                                                         # Список валидных университетов
                       'Санкт-Петербургский государственный политехнический университет',
                       'Государственная морская академия имени адмирала С.О. Макарова',
                       'Филиал Академии Генеральной прокуратуры РФ', 'Госуниверситет нефти и газа имени Губкина',
                       'САУ им. С.П. Королева', 'Новосибирский технический госуниверситет', 'СПбГУ',
                       'Санкт-Петербургский государственный архитектурно-строительный университет',
                       'Авиационно-технический университетАвиационно-технический университет', 'МФТИ',
                       'Государственный технологический университет им. К.Э. Циолковского',
                       'Филиал Российской академии правосудия', 'МГУ им. Ломоносова',
                       'Ульяновский высший авиационный институт гражданской авиации',
                       'Университет аэрокосмического приборостроения', 'Госуниверситет гражданской авиации',
                       'Московский авиационный институт', 'Бауманское МГТУ',
                       'Санкт-Петербургский политехнический университет',
                       'Томский национальный исследовательский политех']
        if university not in universitys:
            self.count_invalid_data('invalid_university')
            return False
        return True

    def valid_age(self, age) -> bool:

        if isinstance(age, str):
            self.count_invalid_data('invalid_age')
            return False
        elif isinstance(age, int):
            if age > 100 or age < 15:
                self.count_invalid_data('invalid_age')
                return False
        return True

    def valid_political_views(self, political_view: str) -> bool:

        political_views_list = ['Умеренные', 'Анархистские', 'Социалистические', 'Либеральные', 'Консервативные',                                 'Либертарианские', 'Индифферентные', 'Коммунистические']
        if political_view not in political_views_list:
            self.count_invalid_data('invalid_political_views')
            return False
        return True

    def valid_world_view(self, world_view: str) -> bool:

        world_views = ['Пантеизм', 'Секулярный гуманизм', 'Агностицизм', 'Деизм', 'Буддизм', 'Католицизм', 'Атеизм', # Список валидных общих взглядов
                       'Конфуцианство', 'Иудаизм']
        if world_view not in world_views:
            self.count_invalid_data('invalid_world_view')
            return False
        return True

    def valid_address(self, address: str) -> bool:

        if address.split(" ")[0] not in ("ул.", "Аллея"):
            self.count_invalid_data('invalid_address')
            return False
        return True

    def count_invalid_data(self, valid_data: str) -> None:

        self.invalid_data[valid_data] += 1

    def count_valid_data(self) -> None:

        self.valid_data += 1

    valid_func = {
        'telephone': valid_telephone,
        'height': valid_height,
        'inn': valid_inn,
        'passport_number': valid_passport_number,
        'university': valid_university,
        'age': valid_age,
        'political_views': valid_political_views,
        'worldview': valid_world_view,
        'address': valid_address
    }

    def check_data(self, data: dict) -> bool:

        result = True
        for key, value in data.items():
            result = self.valid_func[key](self, value) and result
        return result

    def start_validation(self, format_data: str, path: str, path_write: str) -> None:

        data = self.readers[format_data].read_data(path)
        file = open(path_write, 'w')
        with tqdm(total=100) as progressbar:
            for i in data:
                if self.check_data(i):
                    file.write(str(i))
                    file.write(",")
                    self.count_valid_data()
                    progressbar.update(0.00109378)
                else:
                    self.sum_invalid_data += 1
        file.write("]")
        file.close()
        file = open(path_write, "r")
        text = file.read()
        text = text.replace("\'", "\"")
        text = text[:-2]+text[-1]
        file.close()
        file = open(path_write, "w")
        file.write(text)
        file.close()


reader_json = Reader()
valid = Validator(reader_json, 'json')
valid.start_validation('json', "80.txt", "output.txt")