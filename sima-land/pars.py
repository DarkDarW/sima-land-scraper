import requests
from bs4 import BeautifulSoup
import pandas as pd
from tabulate import tabulate
from tqdm import tqdm
from faker import Faker
import logging
from concurrent.futures import ThreadPoolExecutor
from fake_useragent import UserAgent

# Настройка логирования
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Генерация случайного имени пользователя
fake = Faker()

# Создаем объект UserAgent
ua = UserAgent()

# Функция для получения base_url из файла
def get_base_urls(file_path):
    with open(file_path, 'r') as file:
        base_urls = [line.strip() for line in file if line.strip()]
    return base_urls

# Путь к файлу links.txt
file_path = 'links.txt'

# Получаем все base_urls из файла
base_urls = get_base_urls(file_path)

# Общее количество страниц для каждой ссылки
total_pages = 500

# Список для хранения данных о товарах
products = []

# Функция для обработки каждого базового URL
def process_base_url(base_url, num_threads):
    logger.info(f'Начинаем обработку URL: {base_url}')
    url_pattern = base_url + '/p{}/'

    with ThreadPoolExecutor(max_workers=num_threads) as executor:
        futures = []
        for page in range(1, total_pages + 1):
            url = url_pattern.format(page)
            future = executor.submit(process_page, url, page, base_url)
            futures.append(future)

        for future in tqdm(futures, total=len(futures), desc=f"Processing {base_url}", unit="page"):
            page_products = future.result()
            if page_products:
                products.extend(page_products)

# Функция для обработки каждой страницы
def process_page(url, page, base_url):
    # Получаем случайный User-Agent
    user_agent = ua.random

    headers = {
        'User-Agent': user_agent
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')

        if soup.find(class_='j6KLE6') and 'Ошибка 404' in soup.find(class_='j6KLE6').text:
            logger.info(f'Страница {page} содержит ошибку 404, пропускаем её парсинг.')
            return []

        items = soup.find_all(class_='m4OA1R jCkt4I catalog__item')
        page_products = []

        for item in items:
            product = {}
            product['name'] = item.find(class_='o7U8An SAaOh9').text.strip() if item.find(class_='o7U8An SAaOh9') else None
            product['price'] = item.find(class_='KyYuOw').text.strip() if item.find(class_='KyYuOw') else None
            product['old_price'] = item.find_all(class_='KyYuOw')[1].text.strip() if len(item.find_all(class_='KyYuOw')) > 1 else None
            product['rating'] = item.find(class_='ULvtw9').text.strip() if item.find(class_='ULvtw9') else None
            product['reviews'] = item.find(class_='XJIe4q').text.strip() if item.find(class_='XJIe4q') else None
            product['user'] = fake.user_name()
            page_products.append(product)

        logger.info(f'Страница {page} из {total_pages} обработана.')
        return page_products
    else:
        logger.error(f'Ошибка при запросе страницы {page}: {response.status_code}')
        return []

# Количество потоков
num_threads = 4  # Можно указать любое другое число

# Проходим через все базовые URL из файла
for base_url in base_urls:
    process_base_url(base_url, num_threads)

# Преобразуем данные в DataFrame для удобства
df = pd.DataFrame(products)

# Выводим данные в красивом табличном формате
print(tabulate(df, headers='keys', tablefmt='grid', showindex=False))

# Сохранение данных в CSV файл
df.to_csv('sima_land_products.csv', index=False)