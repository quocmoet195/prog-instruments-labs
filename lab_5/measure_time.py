import os
import json
import time
import matplotlib.pyplot as plt
from matplotlib import pyplot as plt

from card import create_card_number


def read_statistics(file_name: str) -> dict:
    """
    Функция считывает статистику из файла
    file_name: Имя файла для чтения данных
    Return: Словарь
    """
    result = dict()
    try:
        with open(file_name, 'r') as f:
            tmp=json.load(f)
        print("Статистика успешно считана")
    except Exception as ex:
        raise Exception(f"Не удалось считать статистику {ex}")
    for i in tmp.items():
        processes, time = i
        result[int(processes)] = float(time)
    return result


def write_statistics(data, file_name: str) -> None:
    """
    Записывает статистику в файл JSON.
    processes: Количество используемых процессов
    time: Затраченное время
    file_name: Имя файла для записи данных
    """
    try:
        with open(file_name, 'w') as f:
            json.dump(data, f)
    except Exception as ex:
        raise Exception(f"Не удалось записать статистику: {ex}")


def measure_time(hash_number: str, bins: list, last_four_numbers: str, file_statistic: str) ->None:
    """
    Замерить время для поиска коллизии хеша при различном числе процессов

    """
    time_dict={}
    for i in range(1, 11):
        time_begin = time.time()
        create_card_number(hash_number, bins, last_four_numbers, i)
        time_end = time.time()
        time_dict[i]=time_end-time_begin
    write_statistics(time_dict, file_statistic)
    print("Статистика успешно посчитана")


def mark_global_point(statistics: dict, file_name: str) -> None:
    """
    Функция на графике отметить точку глобального минимума полученной зависимости
    statistics: Статистика
    file_name: Путь к файлу
    """
    x = statistics.keys()
    y = statistics.values()
    plt.ylabel('time')
    plt.xlabel('processes')
    plt.title('y=sinc(x)')
    plt.plot(x,y, color='navy', linestyle = '--', marker='x', linewidth=1, markersize=4 )
    plt.savefig(file_name)
