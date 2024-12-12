import json
import argparse

from card import create_card_number
from measure_time import mark_global_point , read_statistics, measure_time
from luna import Luna


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('-card', '--card_number_enumeration', type=int, nargs='?', const=6, help='Ищет номер карты с помощью хеша')
    group.add_argument('-sta', '--statistics', action='store_true', help='Получается статистику подбирая номер карты на разном количестве процессов')
    group.add_argument('-lun', '--luna_algorithm', action='store_true', help='Проверяет валидность номера карты с помощью алгоритма Луна')
    group.add_argument('-vis', '--visualize_statistics', action='store_true', help='Создает гистограмму по имеющейся статистике')
    args = parser.parse_args()
    try:
        with open("settings.json", "r", encoding='UTF-8') as f:
            settings = json.load(f)
    except Exception as ex:
        raise Exception(f"Не удалось считать данные!{ex}")
    hash_number = settings['hash']
    bins = settings['bins']
    last_four_numbers = settings['last_four_numbers']
    card_file=settings['card_number']
    file_statistic=settings['file_statistics']
    png_file=settings['image_statistics']
    
    match (args.card_number_enumeration, args.statistics, args.luna_algorithm, args.visualize_statistics):
        case (True, False, False, False):
            card_number = create_card_number(hash_number, bins, last_four_numbers, 6)
            if card_number:
                with open(card_file, 'w') as f:
                    f.write(card_number)
            else:
                print("Не удалось найти номер карты")
        case (False, True, False, False):
            measure_time(hash_number, bins, last_four_numbers, file_statistic)
        case (False, False, True, False):
            with open(card_file, 'r') as f:
                card_number = f.read()
            if Luna(card_number):
                print("Номер карты действителен")
            else:
                print("Номер карты не действителен")
        case (False, False, False, True):
            mark_global_point(read_statistics(file_statistic), png_file)
        case _:
            print("Неизвестная команда")
