import hashlib
import multiprocessing as mp


def check_card_number(args) -> str:
    """
    Проверяет, соответствует ли номер карты исходному хешу.
    args: Кортеж, содержащий center_part, bins, last_four_numbers, original_hash
    Return: номер карты
    """
    center_part, bins, last_four_numbers, original_hash = args
    for bin_part in bins:
        card_number = str(bin_part)+str(center_part).zfill(6)+str(last_four_numbers)
        if hashlib.blake2b(card_number.encode()).hexdigest() == original_hash:
            return card_number 
    return None


def create_card_number(original_hash: str, bins: list, last_four_numbers: str, core_number: int = mp.cpu_count()) -> str:
    """
    Генерирует номер карты путем сравнения хешей.    original_hash: Original hash of the card
    bins: Список BINs
    last_four_numbers: Последние четыре цифры номера карты
    core_number: Количество ядер, используемых для многопроцессорной обработки
    Return: номер карты
    """
    with mp.Pool(core_number) as pool:
        args = [(i, bins, last_four_numbers, original_hash) for i in range(1000000)]
        for result in pool.map(check_card_number, args):
            if result:
                pool.terminate() 
                print(f"Trying card number: {result}, Hash: {hashlib.blake2b(result.encode()).hexdigest()}")

                return result
    return None
