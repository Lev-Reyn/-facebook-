"""программа по сбору информации из facebook, а имеенно имени, ссылки, города и номера телефона ( если
конечно данные присутсвтуют)

!!!  ИНОГДА ПРОГРАММА ВЫДАЁТ ОШИБКУ, НУЖНО ПРОСТО ПЕРЕЗАПУСТИТЬ КОД, ПРОГРАММА ПРОДОЛЖИТ РАБОТУ С ТОГО ЖЕ МЕСТА  !!!


пометка для себя: нужно как-то доработать функцию get_information_about_user
она в соменте поиска горола не может иногда перейти в раздел информации и выдаёт ошибку в дальнейшем
"""
import time
import os.path
import random
from typing import Dict, List
import json
import pickle
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException

# подключаем опции для браузера
options = webdriver.ChromeOptions()
# options.headless = True
options.add_argument('user-agent=AppleCoreMedia/1.0.0.20F71 (Macintosh; U; Intel Mac OS X 11_4; da_dk)')
options.add_argument('--disable-blink-features=AutomationControlled')
driver = webdriver.Chrome(executable_path='/Users/levreyn/Yandex.Disk.localized/python/selenium/driver/chromedriver',
                          options=options)

#  необходимо ввести  логин и пароль
LOGIN = ''
PASSWORD = ''

driver.get('https://www.facebook.com')
driver.implicitly_wait(10)


def log_in_account(login: str, password: str) -> None:
    """вход в аккант facebook
    gпринимает на вход логин и пароль"""
    # вводим ссылку пользователя

    # логин
    email_input = driver.find_element_by_id('email')
    email_input.clear()
    email_input.send_keys(login)

    # пароль
    password_input = driver.find_element_by_id('pass')
    password_input.clear()
    password_input.send_keys(password)
    password_input.send_keys(Keys.ENTER)

    driver.implicitly_wait(10)
    pickle.dump(driver.get_cookies(), open(f'{login.replace(".", "_")}_cookies', 'wb'))


def we_take_the_user_id(link: str) -> str:
    """достаём из ссылки id пользователя
    принимает:
     1) ссылку
    возвращает:
     1) id пользователя
    """
    if 'id=' in link and '&' not in link:
        index_id = link.find('id=') + 3  # ищем в какой момент начинается id пользователя
        id_account = link[index_id::]  # сам индекс пользователя
        return id_account

    # собираем буквенный id пользователя
    if 'notif_id=' not in link:
        id_account = link.split('/')[-1]  # буквенный id пользователя
        return id_account

    if 'notif_id=' in link:
        index_notif_id = link.find('notif_id=') + 9
        # так как у нас с конца два амперсанда, то мы второй справа амперанд ищем
        index_first_ampersand = link.rfind('&')
        index_ampersand = link[0:index_first_ampersand].rfind('&')
        id_account = link[index_notif_id: index_ampersand]
        return id_account
    # если ни один не подпшёл, то как бы вот никакая строка так сказать
    return ''


# специально создал для того что бы в глобальную переменную сохранять данные
friends_links_set = set()


def get_links_followers(html: str) -> None:
    """собираем ссылки на страницы друзей
    и закидыввет их в множество friends_links_set"""
    soup = BeautifulSoup(html, 'lxml')
    items = soup.find_all('a', {'role': 'link'})

    # сначала создаём словарь, так как могут повторяться элементы
    for item in items:
        link = item['href']
        # собираем ссылки, если это ссылка на чей-то аккаунт facebook
        if link.count('/') == 3 and 'https://www.facebook.com/' in link and LINK_USER not in link:
            # print(link)
            friends_links_set.add(link)


def get_information_about_user(user_page: str) -> Dict[str, str]:
    """
    собираем иформацию:

    Ссылку на профиль
    Имя, Фамилию
    Город
    Телефон
    Почту

    (принимает на вход ссылку на пользователя)
    """

    # словарь, в который будем сохранять данные о пользователе, сразу поместим ссылку
    information_about_user_dict = {'url': user_page}

    # имя
    driver.get(user_page)
    driver.implicitly_wait(10)
    time.sleep(random.randint(1, 2))
    name = driver.find_element_by_tag_name('h1')
    name = name.text
    if name == '':
        name = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/di\
v/div[3]/div/div/div[1]/div[1]/div/div/div[1]/div[2]/div/div/div[2]/div/div/div/div[1]/div/div/span/h1').text

    print(name)
    information_about_user_dict['name'] = name
    time.sleep(random.randint(1, 2))

    # город
    for i in range(5):
        # он будет пять раз пытаться найти кнопку с местом проживания и информацией, если не сможет найти...
        try:
            button_information = driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/di\
v/div/div[1]/div[1]/div/div/div[3]/div/div/div/div[1]/div/div/div[1]/div/div/div/div/div/div/a[2]')
            button_information.click()
            time.sleep(random.randint(3, 4))
            driver.implicitly_wait(10)

            driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/di\
v/div[4]/div/div/div/div[1]/div/div/div/div/div[1]/div[4]/a').click()
            break
        except NoSuchElementException:
            print(f'опять эта штука не может найтись, нужно ему больше времени, заколебалО ----- {i}')
            # тогда обновляем страницу и пробуем те же самые действия провести
            driver.refresh()
            time.sleep(random.randint(3, 4))

        except StaleElementReferenceException:
            # тогда обновляем страницу и пробуем те же самые действия провести
            driver.refresh()
            time.sleep(random.randint(3, 4))

    driver.implicitly_wait(10)
    time.sleep(2)
    xpath_for_city_1 = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/di\
v[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div/div/div[2]/div/div/div[2]/di\
v[1]/a/span/span'
    if checking_the_xpath_on_the_page(xpath_for_city_1):
        city = driver.find_element_by_xpath(xpath_for_city_1).text
    else:
        print('город не указан')
        city = None
    print(city)
    information_about_user_dict['city'] = city

    # номер телефона
    driver.find_element_by_xpath('/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/di\
v/div/div[4]/div/div/div/div[1]/div/div/div/div/div[1]/div[5]/a/span').click()
    time.sleep(random.randint(1, 3))
    xpath_for_number_phone_1 = '/html/body/div[1]/div/div[1]/div/div[3]/div/div/di\
v[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[2]/div/div/div/div[1]/div[2]/di\
v/div/div[2]/div/div/div/div/div[1]/span'
    if checking_the_xpath_on_the_page(xpath_for_number_phone_1):
        number_phone = driver.find_element_by_xpath(xpath_for_number_phone_1).text
    else:
        print('номер телефона не указан и нужно бы собрать xpath для этих данных')
        number_phone = None
    print(number_phone)
    information_about_user_dict['number phone'] = number_phone

    return information_about_user_dict


def checking_the_xpath_on_the_page(xpath: str) -> bool:
    """проверяем есть ли данный xpath на странице
    если еесть выдаёт True, иначе False"""
    try:
        driver.find_element_by_xpath(xpath)
        return True
    except NoSuchElementException:
        return False


def collecting_friends_links(id_user_page='test') -> List:
    """собирает ссылки друзей данного пользователя
    и закидываем в json (все json файлики находятся в папке data_links
    принимает:
     1) driver
     2) id пользователя, у кого собираем друзей"""
    friends_xpath = '/html/body/div[1]/div/div[1]/div/div[3]/di\
v/div/div[1]/div[1]/div/div/div[3]/div/div/div/div[1]/div/div/div[1]/div/div/div/div/div/div/a[3]/div[1]/span/span[2]'
    if checking_the_xpath_on_the_page(friends_xpath):
        friends = driver.find_element_by_xpath(friends_xpath)
        friends.click()
        count_friends = int(friends.text)
        print(count_friends)
    else:
        print('похоже друзей нет :/')
        return []  # пока что не знаю что бы прлписать, просто нужно закончить тогда данную программу

    # скролл страницы
    for scroll in range(count_friends // 16 + 2):
        driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
        # собираем ссылки подписчиков
        if scroll != 0:
            get_links_followers(driver.page_source)
        print(f'скрол {scroll}')
        print(f'{len(friends_links_set)} ссылок на друзей собрал')
        time.sleep((random.randrange(3, 5)))

    # если пакпки, в которую будем сохранять все ссылки не создана, то создаём
    if not os.path.exists('data_links'):
        os.mkdir('data_links')

    with open(f'data_links/link_friends_json_{id_user_page}.json', 'w') as file:
        json.dump(list(friends_links_set), file, indent=4, ensure_ascii=False)

    return list(friends_links_set)


def adding_user_information_to_json(info_dict_about_one_user: Dict[str, str], id_user_page='test',
                                    only_create=False) -> bool:
    """добавляет информацию в json файлик с данными, если файлика нет, то создаёт его
    (все json файлики в папке data)
    принимает на вход:
     1) словарик с данными об одном пользователе
     2) id пользователя, у которого взяли друзей
     3) если изменить значение only_create, то просто мы создадим данный файлик
    возвращает:
    True - если данных об этом пользователе не было в файле и их добавили / либо просто создали файл
    False - если данные уже там были и нет смысла добавлять их"""
    # создаём папку data если таковой нет
    if not os.path.exists('data'):
        os.mkdir('data')
    if os.path.exists(
            f'data/information_about_users_from_{id_user_page}.json') and not only_create:
        with open(f'data/information_about_users_from_{id_user_page}.json') as file:
            info_list_about_users = json.load(file)
        info_list_about_users: List[Dict[str, str]]
        #  добавляем словарик с данными о пользователе
        if info_dict_about_one_user not in info_list_about_users:
            info_list_about_users.append(info_dict_about_one_user)
            with open(f'data/information_about_users_from_{id_user_page}.json', 'w') as file:
                json.dump(info_list_about_users, file, indent=4, ensure_ascii=False)
            return True
        return False
    # если нет данного файла, то создаём
    info_list_about_users = list()
    if not only_create:
        info_list_about_users.append(info_dict_about_one_user)
    with open(f'data/information_about_users_from_{id_user_page}.json', 'w') as file:
        json.dump(info_list_about_users, file, indent=4, ensure_ascii=False)
    return False


def check_if_there_is_data_already_on_this_link(url_user: str, id_user_page='test') -> bool:
    """проверяет есть ли по этой ссылке информация о пользователе (в данном файле)
    принимает на вход:
    1) ссылку пользователя
    2) id пользователя, у которого взяли друзей
    возвращает:
    True - если есть уже в файлике ифа о данном ползователе
    False - если нет инфы"""
    # сначала проверяем есть ли вообще папка data
    if not os.path.exists('data'):
        return False
    if os.path.exists(f'data/information_about_users_from_{id_user_page}.json'):
        with open(f'data/information_about_users_from_{id_user_page}.json') as file:
            info_list_about_users = json.load(file)
        for info_dict_about_one_user in info_list_about_users:
            if info_dict_about_one_user['url'] == url_user:
                return True
        return False
    return False


def parse(link_user: str) -> None:
    """осуществляем парсинг данных, основная функция
    на вход принимает ссылку на пользователя"""
    # осуществляем авторизацию
    log_in_account(LOGIN, PASSWORD)
    time.sleep(random.randint(2, 4))

    # переходим на аккаунт пользователя
    driver.get(link_user)
    driver.implicitly_wait(10)

    # получаем id пользователя, у которого собираем друзей
    id_user_page = we_take_the_user_id(link=link_user)

    # собираем ссылки друзей у данного прльзователя и передаэм список в friends_links_lst
    friends_links_lst = collecting_friends_links(id_user_page=id_user_page)
    with open(f'data_links/link_friends_json_{id_user_page}.json') as file:
        friends_links_lst = json.load(file)

    for i, link_friend in enumerate(friends_links_lst):
        # проверяем сначала, если нет инфы об этом ползователе, то собираем инфу, иначе нет
        if not check_if_there_is_data_already_on_this_link(link_friend, id_user_page=id_user_page):
            # собираем инфу о друге принимает ссылку на аккаунт
            info_dict_about_one_user = get_information_about_user(link_friend)
            # добавляет инфу в json файлик об этом друге
            test_create_or_not_my_jsonfile = adding_user_information_to_json(info_dict_about_one_user, id_user_page)
            print(i, link_friend, info_dict_about_one_user, test_create_or_not_my_jsonfile)
        else:
            print(f'уже есть инфа об этом пользователе: {link_friend}')

    time.sleep(300)

    driver.close()
    driver.quit()


# здесь вставляем ссылку на пользователя, у которого ходим собрать данные о его друщьях
# не забудьте вставить логин и пароль в начале кода!!!
LINK_USER = 'https://www.facebook.com/maxrillbrix.eusaff'
if __name__ == '__main__':
    parse(link_user=LINK_USER)
