import json
import requests
import os
from bs4 import BeautifulSoup
from fake_headers import Headers
from logger2 import logger


def get_headers():
    return Headers(browser="chrome", os="win").generate()


def get_text(url):
    return requests.get(url, headers=get_headers()).text


def main_f():
    path = 'log_scrap.log'

    if os.path.exists(path):
        os.remove(path)

    @logger(path)
    def parse_page(page_num):
        url = f"https://spb.hh.ru/search/vacancy?text=python&area=1&area=2&items_on_page=20&page={page_num}"
        html = get_text(url)
        soup = BeautifulSoup(html, 'lxml')
        mn = soup.find('main', class_='vacancy-serp-content')
        div = mn.find_all('div', class_='vacancy-serp-item-body__main-info')
        page_span = []
        for d in div:
            title = d.find('a', class_='serp-item__title')
            title_text = title.text
            price = d.find('span', class_='bloko-header-section-3')
            if price:
                price = price.text.strip().replace("\u202f", "")
                if ('django' in title_text.lower() or 'flask' in title_text.lower()) and price[-3:] != 'USD':
                    city = d.find_all('div', class_='bloko-text')
                    if city:
                        city = city[-1]
                        page_span.append({'title': title_text,
                                          'link': title.attrs.get('href'),
                                          'price': price,
                                          'company': d.find('a', class_='bloko-link bloko-link_kind-tertiary').text.strip(),
                                          'city': city.text.strip()})
        return page_span

    res = []
    for page in range(0, 5):
        print('Number of page:', page)
        parsed = parse_page(page)
        if parsed:
            res += parsed

    with open("output_data.json", "w", encoding='windows-1251') as f:
        json.dump(res, f, ensure_ascii=False)


if __name__ == '__main__':
    main_f()
