from selenium import webdriver
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
import time
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from operator import itemgetter
import os.path
import datetime
import re, string, timeit
import crossparser_tools


credentials = crossparser_tools.parse_credentials()
temp_folder = crossparser_tools.temp_folder
config_folder = crossparser_tools.config_folder

websites = {}
weblinks = {}
catalogs = []
websites_parsed = {}
window_handles = {}
file_of_catalogs = temp_folder + 'files_to_parse.txt'

counter_links_total = 0
counter_links_parsed = 0

driver = ''



def check_exists_by_css_selector(css_selector):
    global driver
    try:
        driver.find_element_by_css_selector(css_selector)
    except NoSuchElementException:
        return False
    return True


def parse_websites():
    with open(config_folder + 'websites.txt', 'r') as cr_file:
        for line in cr_file:
            if not line.strip().startswith('#'):
                if line.strip():
                    k, v = line.strip().split('$$')
                    websites[k.strip()] = v.strip()


    with open(config_folder + 'weblinks.txt', 'r') as cr_file:
        for line in cr_file:
            if not line.strip().startswith('#'):
                if line.strip():
                    k, v = line.strip().split('$$')
                    weblinks[k.strip()] = v.strip()


def get_nextlink_forsite(current_site):
    links = weblinks[current_site]
    if links == '':
        return ''


    links = links.split('||')
    link_to_parse = links[0]

    global counter_links_total
    counter_links_total += 1

    if len(links) == 1 :
        weblinks[current_site] = ''

    if len(links) > 1 :
        links.pop(0)
        weblinks[current_site] = '||'.join(links)

    return link_to_parse


def cloud_login():

    global driver
    url = credentials['cloudparser_url']
    driver.get(url.rstrip())
        
    log_in_button  = driver.find_element_by_link_text(u'Войти')
    log_in_button.click()
    login_email_box = driver.find_element_by_name('LoginEmail')
    login_email_box.send_keys(credentials['cloudparser_mail'])
    login_password_box = driver.find_element_by_name('LoginPassword')
    login_password_box.send_keys(credentials['cloudparser_pass'])
    auth_button = driver.find_element_by_class_name('auth-form__btns')
    auth_button.click()


def start_parse_all():
    global driver

    #form websites parsed map
    websites_parsed = {}
    for site, url in websites.items():
        websites_parsed[site] = False

    for attr, value in websites.items():

        site = attr
        link = get_nextlink_forsite(site)

        if link != '':


            driver.execute_script('''window.open();''')

            handles = driver.window_handles
            size = len(handles)
            print('handles: ', size)
            for x in range(size):
                if handles[x] != driver.current_window_handle:
                    if handles[x] not in window_handles:
                        driver.switch_to.window(handles[x]);

            window_handles[site] = driver.current_window_handle

            parse_link(site, link)



def parse_link(site, link):

    try:

        global driver
        url = websites[site]
        driver.get(url.strip())

        input = driver.find_element_by_css_selector('div.inputfields input.textbox.urlinput')
        input.send_keys(link)

        strt_btn = driver.find_element_by_css_selector('#startDemoBtn')
        #strt_btn = driver.find_element_by_css_selector('#startBtn')
        strt_btn.click()

        WebDriverWait(driver, 33).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#progressBar')))
        crossparser_tools.write_to_log('Initiated parsing of ' + link)

    except Exception as e:
        crossparser_tools.write_to_log('Failed initiate parsing of ' + link)
        crossparser_tools.write_to_log(e)



def start_checking():

    is_done = True

    for site, handle in window_handles.items():

        if websites_parsed[site] == True:
            continue

        driver.switch_to.window(handle);

        if check_exists_by_css_selector('#content .products-menu .export-button') == False:
            #Tab still parsing, skip
            is_done = False
        else:
            #Parsing complete. Download catalog
            download_btn = WebDriverWait(driver, 3600).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#content .products-menu .export-button")))
        
            download_btn.click()
            before = dict ([(f, None) for f in os.listdir (temp_folder)])
            final_download_btn = WebDriverWait(driver, 100).until(EC.presence_of_element_located((By.CSS_SELECTOR, "#exportBtn")))
            final_download_btn.click()
            sleep(5)
            after = dict ([(f, None) for f in os.listdir (temp_folder)])
            added = [f for f in after if not f in before]

            filename = temp_folder + ''.join(added)
            print(filename)
            global counter_links_parsed
            counter_links_parsed += 1

            crossparser_tools.write_to_log('Downloaded file of ' + site + '. Saved to ' + filename)
            with open(file_of_catalogs, 'a', newline='', encoding="utf8") as files_toimport:
                files_toimport.write(filename + '\n')

            #Start parse new link:
            link = get_nextlink_forsite(site)
            if link != '':
                parse_link(site, link)
                is_done = False
            else:
                crossparser_tools.write_to_log('Done parse all links for site: ' + site)
                #window_handles.pop(site)
                websites_parsed[site] = True



    sleep(5)
    if is_done == False:
        start_checking()



def parsnew():

    #Clear import catalog files (files of files)
    with open(file_of_catalogs, 'w+', newline='', encoding="utf8") as files_toimport:
        files_toimport.close()


    global driver


    parse_websites()

    global websites_parsed

    for attr, value in websites.items():
        websites_parsed[attr] = False


    options = webdriver.ChromeOptions()

    prefs = {"download.default_directory" : temp_folder, "browser.link.open_newwindow" : 3, "browser.link.open_newwindow.restriction" : 2}
    options.add_experimental_option("prefs", prefs)

    if credentials['is_server'] == 'no':
        chromedriver_path = config_folder + 'chromedriver.exe'
        options.add_argument('--window-size=1200,700')

    if credentials['is_server'] == 'yes':
        chromedriver_path = config_folder + 'chromedriver'
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-dev-shm-usage");
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')


    driver = webdriver.Chrome(chromedriver_path, chrome_options=options)


    cloud_login()
    start_parse_all()
    start_checking()

    crossparser_tools.write_to_log('Done with cloudparser')
    crossparser_tools.write_to_log('Totally links found: ' + counter_links_total)
    crossparser_tools.write_to_log('Successfully parsed: ' + counter_links_parsed)




if __name__ == '__main__':


    parsnew()

