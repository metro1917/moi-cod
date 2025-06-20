import requests
from bs4 import BeautifulSoup

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

url = 'https://pikabu.ru/'

try:
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    
    posts = []
    for article in soup.find_all('article', class_='story')[:10]:
        try:
            title_elem = article.find('h2', class_='story__title')
            title = title_elem.text.strip() if title_elem else 'Без названия'
            
            rating_elem = article.find('div', class_='story__rating-count')
            rating = rating_elem.text.strip() if rating_elem else '0'
            
            link_elem = article.find('a', class_='story__title-link')
            link = link_elem['href'] if link_elem else '#'
            full_link = f"https://pikabu.ru{link}" if link.startswith('/') else link
            
            posts.append({
                'title': title,
                'rating': rating,
                'link': full_link
            })
        except Exception as e:
            print(f"Ошибка при обработке поста: {e}")
            continue
    
    for i, post in enumerate(posts, 1):
        print(f"{i}. {post['title']} (Рейтинг: {post['rating']})")
        print(f"   Ссылка: {post['link']}\n")

except Exception as e:
    print(f"Ошибка при загрузке страницы: {e}")
