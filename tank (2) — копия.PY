import requests
import re

def simple_avito_parser():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    print("Парсим главную страницу Авито...")
    try:
        response = requests.get('https://www.avito.ru/', headers=headers)
        html = response.text
        
        # Парсим категории
        print("\nКатегории:")
        categories = re.findall(r'"name":"([^"]+)".*?"url":"(/[^"]+)"', html)
        for i, (name, url) in enumerate(set(categories)[:10], 1):
            print(f"{i}. {name} - https://www.avito.ru{url}")
        
        # Парсим товары
        print("\nТовары:")
        items = re.findall(r'"title":"([^"]+)".*?"price":(\d+)', html)
        for i, (title, price) in enumerate(set(items)[:5], 1):
            print(f"{i}. {title} - {price} руб.")
            
    except Exception as e:
        print(f"Ошибка: {e}")

if __name__ == "__main__":
    simple_avito_parser()
    input("\nНажмите Enter для выхода...")
