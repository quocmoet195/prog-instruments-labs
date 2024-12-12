def Luna(card_number: str) -> bool:
    """
    Проверка валидности номера карты с помощью алгоритма Луна
    card_number: Номер карты
    Return: Является ли номер карты настоящим
    """
    tmp = list(map(int, card_number))[::-1]
    for i in range(1, len(tmp), 2):
        tmp[i] *= 2
        if tmp[i] > 9:
            tmp[i] = tmp[i] % 10 + tmp[i] // 10
    return sum(tmp) % 10 == 0