HALLS = {
    "Зал внимания (Найди лишний)": 3,
    "Зал знакомства (Найди такую же)": 4,
    "Зал мастера (Подбери цвета по картинке)": 4,
    "Зал реставратора (Заплатки)": 4,
    "Зал хранителя (Сортировка по коллекциям)": 1
}

ALL_HALLS = list(HALLS.keys())

def get_next_hall(current_hall):
    try:
        idx = ALL_HALLS.index(current_hall)
        if idx + 1 < len(ALL_HALLS):
            return ALL_HALLS[idx + 1]
    except ValueError:
        pass
    return None