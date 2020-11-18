import time
import random
from pymongo import MongoClient
from selenium import webdriver


client = MongoClient('localhost', 27017)
db = client['FarPost']
collection = db['Flats']


def create_session():
    global driver
    driver = webdriver.Chrome()
    driver.maximize_window()
    driver.get(BASE_URL)
    
    
def get_total_pages(driver):
    pags = driver.find_element_by_class_name('pageCount').text.split(' ')[2]
    return pags


def delay():
    minTime = 7
    maxTime = 15
    delay_time = random.randint(minTime, maxTime)
    print('Выполняется задержка ----')
    time.sleep(delay_time)


def switch_window():
    driver.execute_script('window.open()')
    driver.switch_to_window(driver.window_handles[1])
    driver.get(urlAds)


def close_switch_w():
    driver.execute_script('window.close()')
    driver.switch_to_window(driver.window_handles[0])


def check_in_db(url, name):
    dict2 = {'url': url}
    data = collection.find_one(dict2)
    if data:
        collection.update_one({'url': url}, {'$set': name})
        print('Данная запись найдена' + str(name))
    else:
        collection.insert_one(name)
        print('Запись добавлена в БД' + ' ' + str(name))



if __name__ == "__main__":
    BASE_URL = 'https://www.farpost.ru/vladivostok/realty/sell_flats/'
    create_session()
    pages = int(get_total_pages(driver))

    for page in range(1, pages):
        url = 'https://www.farpost.ru/vladivostok/realty/sell_flats/?page=' + str(page) + '/'
        driver.get(url)
        delay()
        data_table = driver.find_elements_by_class_name('viewdirBulletinTable')
        if len(data_table) == 0:
            print('Таблица с данными не найдена')
            exit()
        data_table = data_table[0]
        flats = data_table.find_elements_by_class_name('bull-item-content')
        if len(flats) == 0:
            print('Нет элементов таблицы')
            continue

        for elem in flats:
            LinkAds = elem.find_elements_by_class_name('bull-item__self-link')
            if len(LinkAds) == 0:
                print('Ошибка! Ссылка на объявление не найдена')
                continue
            urlAds = LinkAds[0].get_attribute('href')
            price = elem.find_elements_by_class_name('price-block__price')
            if len(price) == 0:
                switch_window()
                delay()
                fieldsetView = driver.find_elements_by_id('fieldsetView')
                fieldsetView = fieldsetView[0]
                field = fieldsetView.find_elements_by_class_name('value')
                Flat = {
                    'area': field[0].text,
                    'address': field[1].text,
                    'url': urlAds
                }
                check_in_db(urlAds, Flat)
            else:
                cost = price[0].text
                switch_window()
                delay()
                fieldsetView = driver.find_elements_by_id('fieldsetView')
                fieldsetView = fieldsetView[0]
                field = fieldsetView.find_elements_by_class_name('value')
                Flat = {
                    'price': cost,
                    'area': field[1].text,
                    'address': field[2].text,
                    'flat_type': field[3].text,
                    'space': field[5].text,
                    'url': urlAds
                }
                check_in_db(urlAds, Flat)

            close_switch_w()

        
            #print(cost)
