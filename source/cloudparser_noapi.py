#!/usr/bin/env python
# -*- coding: utf-8 -*- 

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
file_of_raw_catalogs = crossparser_tools.file_of_raw_catalogs

websites = {}
weblinks = {}
catalogs = []
websites_parsed = {}
window_handles = {}

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



def wait_for_download(filename):

     size1 = os.stat(filename).st_size
     sleep(3)
     size2 = os.stat(filename).st_size

     if int(size1) != int(size2):
         print('waiting for dowloading...')
         sleep(3)
         wait_for_download(filename)




def download_catalogs(site, is_save):
    global driver

    #Dowload primary prices catalog

    download_btn = WebDriverWait(driver, 3600).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#content .products-menu .export-button")))
        
    download_btn.click()
    before = dict ([(f, None) for f in os.listdir (temp_folder)])
    final_download_btn = WebDriverWait(driver, 100).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#exportBtn")))
    final_download_btn.click()
    sleep(5)
    after = dict ([(f, None) for f in os.listdir (temp_folder)])
    added = [f for f in after if not f in before]

    if len(added) == 0:
        crossparser_tools.write_to_log('Failed to download file. Website: ' + site )
        driver.save_screenshot("/var/www/html/boots-market/crossparser/temp/screenshot" + site + ".png")
        return ''


    filename = temp_folder + ''.join(added)

    wait_for_download(filename)

    if is_save == True:
        global counter_links_parsed
        counter_links_parsed += 1
        crossparser_tools.write_to_log('Downloaded primary file of ' + site + '. Saved to ' + filename)
        with open(file_of_raw_catalogs, 'a', newline='', encoding="utf8") as files_toimport:
            files_toimport.write(site + '$$' + filename + '\n')
    else:
        crossparser_tools.write_to_log('Downloaded secondary file of ' + site + '. Saved to ' + filename)

    return filename


def unite_prices(filename1, filename2):

    #print(filename1, filename2)
    with open(filename1, 'r', newline='', encoding="utf8") as file_prim:
        with open(filename2, 'r', newline='', encoding="utf8") as file_sec:

            file_lines_prim = crossparser_tools.read_csv(filename1, True)
            file_lines_sec = crossparser_tools.read_csv(filename2, True)

            table_titles_list = crossparser_tools.table_titles_list

            table_titles_list.append('Цена2')

            price_index = table_titles_list.index('Цена')

            i = -1
            for line in file_lines_prim:
                i += 1
                if line == '':
                    continue

                line = line.split(';')
                price1 = line[price_index]

                line2 = file_lines_sec[i]
                line2 = line2.split(';')
                price2 = line2[price_index]
                price2 = crossparser_tools.get_only_nums(price2)

                line.append(price2)
                line = ';'.join(line)
                file_lines_prim[i] = line


    #Save file
    with open(filename1, 'w', newline='', encoding="utf8") as file_prim:
        file_prim.write(';'.join(table_titles_list) + '\n')
        for line in file_lines_prim:
            file_prim.write(line + '\n')

    os.remove(filename2)



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
            filename1 = download_catalogs(site, True)

            #Dowload secondary prices catalog
            if filename1 != '':
                btn = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.ui-dialog.ui-widget button.ui-dialog-titlebar-close")))
                btn.click()
                btn = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#changePrice")))
                btn.click()
                btn = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#price > option:nth-child(2)")))
                btn.click()
                btn = WebDriverWait(driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#applyChangePriceBtn")))
                btn.click()
                sleep(2)
                filename2 = download_catalogs(site, False)
                #unite prices:
                if filename2 != '':
                    unite_prices(filename1, filename2)


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
    with open(file_of_raw_catalogs, 'w+', newline='', encoding="utf8") as files_toimport:
        files_toimport.close()


    global driver

    parse_websites()

    global websites_parsed

    for attr, value in websites.items():
        websites_parsed[attr] = False


    if credentials['is_server'] == 'no':

        options = webdriver.ChromeOptions()
        prefs = {"download.default_directory" : temp_folder, "download.prompt_for_download": False, "download.directory_upgrade": True, "safebrowsing.enabled": True }
        options.add_experimental_option("prefs", prefs)
        chromedriver_path = config_folder + 'chromedriver.exe'
        options.add_argument('--window-size=1200,700')

        driver = webdriver.Chrome(chromedriver_path, chrome_options=options)


    if credentials['is_server'] == 'yes':
        #chromedriver_path = config_folder + 'chromedriver'
        #options.add_argument('--no-sandbox')
        #options.add_argument("--disable-dev-shm-usage");
        #options.add_argument('--headless')
        #options.add_argument('--disable-gpu')

        profile = webdriver.FirefoxProfile()
        profile.set_preference('browser.download.folderList', 2) # custom location
        profile.set_preference('browser.download.manager.showWhenStarting', False)
        profile.set_preference('browser.download.dir', temp_folder)
        profile.set_preference('browser.helperApps.neverAsk.saveToDisk', 'text/csv')

        from selenium.webdriver.firefox.options import Options
        firefox_options = Options()
        firefox_options.add_argument('-headless')
        driver = webdriver.Firefox(firefox_profile=profile, options = firefox_options)


    cloud_login()
    start_parse_all()
    start_checking()

    crossparser_tools.write_to_log('Done with cloudparser')
    crossparser_tools.write_to_log('Totally links found: ' + str(counter_links_total))
    crossparser_tools.write_to_log('Successfully parsed: ' + str(counter_links_parsed))

    driver.quit()




if __name__ == '__main__':


    parsnew()

    import cloudparser_parse_files

