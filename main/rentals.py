import json
import os

def load_rental_items(file_name):
    if os.path.exists(file_name):
        with open(file_name, "r") as json_file:
            rental_items = json.load(json_file)
    else:
        rental_items = []
    return rental_items


def add_renter(new_renter, file_name="rental_items.json"):

    rental_items = load_rental_items(file_name)
    rental_items.append(new_renter)
    with open(file_name, "w") as json_file:
        json.dump(rental_items, json_file, indent=4)

# Обновленные данные о товарах для аренды
rental_items = [
    {
        "name": "Иванов",
        "contact_info": "ivanov@example.com",
        "rented_items": [
            {
                "name": "Велосипед",
                "description": "Dелосипед для активного отдыха",
                "price_per_day": 500
            },
            {
                "name": "Барбекю гриль",
                "description": "Мини-гриль для приготовления блюд",
                "price_per_day": 200
            }
        ]
    },
    {
        "name": "Петров",
        "contact_info": "petrov@example.com",
        "rented_items": [
            {
                "name": "Палатка",
                "description": "Двухместная палатка для кемпинга",
                "price_per_day": 300
            },
            {
                "name": "Пляжный мячик",
                "description": "Для веселья детей и спокоцствия родителей",
                "price_per_day": 75
            }

        ]
    },
    {
        "name": "Сидоров",
        "contact_info": "sidorov@example.com",
        "rented_items": [
            {
                "name": "Лодка",
                "description": "Для прогулок по воде",
                "price_per_day": 400
            }
        ]
    }
]

# Сохраняем обновленные данные в JSON файл
file_name = "rental_items.json"
with open(file_name, "w") as json_file:
    json.dump(rental_items, json_file, indent=4)

print(f"Обновленные данные о товарах для аренды успешно сохранены в файле {file_name}")
