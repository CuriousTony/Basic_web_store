import requests
from bs4 import BeautifulSoup
import json
from urllib.parse import urljoin
import time
from tqdm import tqdm
from random import randint


def parse_catalog_page(url):
    try:
        response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return soup
    except Exception as e:
        print(f"Ошибка при загрузке страницы: {e}")
        return None


def extract_product_data(product_block, base_url):
    product = {}

    name_tag = product_block.find('a', class_='catalog__name')
    product['title'] = name_tag.text.strip() if name_tag else None

    price_tag = product_block.find('span', class_='mindbox-price-custom')
    if price_tag:
        product['price'] = price_tag.text.replace('р.', '').strip()
    else:
        product['price'] = None

    composition_tag = product_block.find('span', class_='product__composition')
    product['composition'] = composition_tag.text.strip() if composition_tag else None

    img_tag = product_block.find('img', class_='catalog__image')
    if img_tag:
        img_path = img_tag.get('data-origin') or img_tag.get('src')
        product['image_url'] = urljoin(base_url, img_path) if img_path else None
    else:
        product['image_url'] = None

    return product


def parse_all_pages(base_url, max_pages=5):
    all_products = []
    page = 1
    delay = randint(1, 5)

    with tqdm(desc="Парсинг страниц") as pbar:
        while page <= max_pages:
            current_url = f"{base_url}?PAGEN_1={page}" if page > 1 else base_url
            soup = parse_catalog_page(current_url)

            if not soup:
                break

            catalog_content = soup.find('div', class_='catalog__items')
            if not catalog_content:
                break

            product_blocks = catalog_content.find_all('div', class_='catalog__content_main')

            if not product_blocks:
                break

            for block in product_blocks:
                product_data = extract_product_data(block, base_url)
                if product_data:
                    all_products.append(product_data)

            next_page = soup.find('a', class_='pagination__item', text=str(page + 1))
            if not next_page:
                break

            page += 1
            time.sleep(delay)
            pbar.update(1)

    return all_products


def save_to_json(data, filename='pions.json'):
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


if __name__ == '__main__':
    BASE_URL = 'https://tsvetomania.ru/catalog/piony/'
    MAX_PAGES = 3

    print(f"Начинаем парсинг каталога: {BASE_URL}")
    products = parse_all_pages(BASE_URL, MAX_PAGES)

    if products:
        save_to_json(products)
        print(f"\nУспешно собрано {len(products)} товаров")
        print(f"Данные сохранены в pions.json")
    else:
        print("Не удалось собрать данные")
