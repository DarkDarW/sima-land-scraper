import requests
from bs4 import BeautifulSoup

# URL страницы
url = 'https://www.sima-land.ru/catalog/'

# Отправляем запрос к странице
response = requests.get(url)

# Проверяем статус ответа
if response.status_code == 200:
    # Создаем объект BeautifulSoup для парсинга HTML
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Ищем все элементы с классом jzq4NZ
    elements = soup.find_all(class_='jzq4NZ')
    
    # Открываем файл для записи ссылок
    with open('links.txt', 'w') as file:
        # Проходим по всем найденным элементам
        for element in elements:
            # Ищем все теги <a> внутри элемента и извлекаем ссылки
            links = element.find_all('a', href=True)
            for link in links:
                # Получаем URL ссылки и формируем полный URL
                href = link['href']
                full_url = f'https://www.sima-land.ru{href}'
                # Пишем ссылку в файл
                file.write(full_url + '\n')

    print('Ссылки успешно сохранены в файл links.txt')
else:
    print('Не удалось получить доступ к странице')
