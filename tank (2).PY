import requests
from bs4 import BeautifulSoup
import time
import random
import csv
from datetime import datetime

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7"
}

def get_page(url, params=None):
    try:
        response = requests.get(url, headers=HEADERS, params=params, timeout=30)
        response.raise_for_status()
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Ошибка запроса: {e}")
        return None

def parse_item(item):
    try:
        title_elem = item.find('h3', class_='title-root-zZCwT')
        title = title_elem.get_text(strip=True) if title_elem else "Нет названия"
        
        price_elem = item.find('span', class_='price-text-_YGDY')
        price = price_elem.get_text(strip=True) if price_elem else "Нет цены"
        
        link_elem = item.find('a', class_='link-link-MbQDP')
        url = "https://www.avito.ru" + link_elem['href'] if link_elem else "Нет ссылки"
        
        address_elem = item.find('div', class_='geo-georeferences-SEtee')
        address = address_elem.get_text(strip=True) if address_elem else "Нет адреса"
        
        date_elem = item.find('div', class_='date-text-KmWDf')
        date = date_elem.get_text(strip=True) if date_elem else "Нет даты"
        
        return {
            "title": title,
            "price": price,
            "url": url,
            "address": address,
            "date": date,
            "parse_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
    except Exception as e:
        print(f"Ошибка парсинга объявления: {e}")
        return None

def save_to_csv(data, filename="avito_data.csv"):
    if not data:
        return
        
    with open(filename, mode="a", encoding="utf-8-sig", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys())
        if file.tell() == 0:
            writer.writeheader()
        writer.writerows(data)

def parse_avito(category="avtomobili", location="moskva", pages=1):
    base_url = f"https://www.avito.ru/{location}/{category}"
    all_ads = []
    
    for page in range(1, pages + 1):
        params = {"p": page}
        print(f"Парсинг страницы {page}...")
        
        html = get_page(base_url, params=params)
        if not html:
            continue
            
        soup = BeautifulSoup(html, 'html.parser')
        items = soup.find_all('div', {'data-marker': 'item'})
        
        for item in items:
            parsed_item = parse_item(item)
            if parsed_item:
                all_ads.append(parsed_item)
        
        time.sleep(random.uniform(2, 5))
    
    if all_ads:
        save_to_csv(all_ads)
        print(f"Сохранено {len(all_ads)} объявлений в файл avito_data.csv")
    else:
        print("Не удалось получить данные")
    
    return all_ads

if __name__ == "__main__":
    parse_avito(pages=2)
