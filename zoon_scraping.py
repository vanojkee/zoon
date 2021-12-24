from selenium import webdriver
import requests
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
import time
import re
from urllib.parse import unquote
import random
import json

headers = {
    "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.93 Safari/537.36 OPR/82.0.4227.33"
}


def collect_data():
    '''Получает страницу со всеми прогруженными карточками'''
    driver = webdriver.Chrome(r'C:\Users\user\PycharmProjects\zoon\chromedriver\chromedriver.exe')
    try:
        driver.get('https://zoon.ru/msk/beauty/')
        time.sleep(5)
        element = driver.find_element(By.CLASS_NAME, 'footer-logo')
        action = ActionChains(driver)
        action.move_to_element(element).perform()
        time.sleep(20)
        with open('source_page.html', 'w', encoding='utf-8') as file:
            file.write(driver.page_source)
        time.sleep(2)

    except Exception as ex:
        print(ex)
    finally:
        driver.close()
        driver.quit()


def get_items_html(file_path):
    '''Собирает ссылки на все карточки'''
    with open(file_path, encoding='utf-8') as file:
        src = file.read()

    urls = []
    soup = BeautifulSoup(src, "lxml")
    items_divs = soup.find_all("div", "minicard-item__info")
    for item in items_divs:
        item_url = item.find('h2', "minicard-item__title").find("a").get("href")
        urls.append(item_url)

    with open('all_list.txt', 'w') as file:
        for url in urls:
            file.write(f"{url}\n")

    return print("\n[INFO] Собираем ссылки на страницы")


def get_data(file_path):
    '''Получает из карточек: название, телефон, адресс, ссылку на сайт, сслку на соц сети'''
    with open(file_path) as file:
        urls_list = [url.strip() for url in file.readlines()]

    result_list = []
    urls_count = len(urls_list)
    count = 1
    for url in urls_list[:20]:
        response = requests.get(url=url, headers=headers)
        soup = BeautifulSoup(response.text, "lxml")

        # Забираем название
        try:
            item_name = soup.find("span", {"itemprop": "name"}).text.strip()
        except Exception as _ex:
            item_name = None

        # Забираем номер телефона
        try:
            item_phone = soup.find("div", "service-phones-list").find("a").get("href")
        except Exception as _ex:
            item_phone = None

        # Забираем адресс
        try:
            item_address = soup.find("address", "iblock").text.strip()
        except Exception as _ex:
            item_address = None

        # Забираем ссылку на сайт
        try:
            item_site = soup.find(text=re.compile("Сайт|Официальный сайт")).find_next().text.strip()
        except Exception as _ex:
            item_site = None

        social_work_list = []
        # Забираем ссылки на социальные сети
        try:
            item_social_work = soup.find(text=re.compile("Страница в соцсетях")).find_next().find_all("a")
            for item in item_social_work:
                item_url = item.get("href")
                item_url = unquote(item_url.split("?to=")[1].split("&")[0])
                social_work_list.append(item_url)
        except Exception as _ex:
            social_work_list = None

        result_list.append(
            {
                "item_name": item_name,
                "item_url": url,
                "item_phone": item_phone,
                "item_address": item_address,
                "item_site": item_site,
                "social_work_list": social_work_list,
            }
        )
        time.sleep(random.randrange(2, 5))

        if count % 10 == 0:
            time.sleep(random.randrange(5, 10))

        print(f"Мы сейчас проходим: {count} / {urls_count}")
        count += 1

    with open("finish_file.json", "w", encoding="utf-8") as file:
      json.dump(result_list, file, indent=4, ensure_ascii=False)

    return print("Всё готово, забирай свои данные")


def main():
    #    collect_data()
    #    get_items_html('source_page.html')
    #    get_data('all_list.txt')
    get_data("all_list.txt")


if __name__ == '__main__':
    main()
