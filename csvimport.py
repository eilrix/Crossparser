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
from operator import itemgetter
import os.path
import datetime
import re, string, timeit
import crossparser_tools



file_dir_loc = crossparser_tools.file_dir_loc
credentials = crossparser_tools.parse_credentials()

products_files = []
categs_files = []
token = ''
files_prod_import = file_dir_loc + 'temp/files_prod_import.txt'
files_categ_import = file_dir_loc + 'temp/files_categ_import.txt'
driver = ''



def parse_websites():
    global products_files
    with open(files_prod_import, 'r') as cr_file:
        for line in cr_file:
            if not line.strip().startswith('#'):
                if not line.strip().startswith('\n'):
                    if line.strip():
                        products_files.append(line.strip())

    global categs_files
    with open(files_categ_import, 'r') as cr_file:
        for line in cr_file:
            if not line.strip().startswith('#'):
                if not line.strip().startswith('\n'):
                    if line.strip():
                        categs_files.append(line.strip())



def open_web_site():

    global token
    global driver

    url = credentials['url']
   
    driver.get(url.strip())

    login_password_box = driver.find_element_by_id('input-username')
    login_password_box.send_keys(credentials['login'])

    passw_password_box = driver.find_element_by_id('input-password')
    passw_password_box.send_keys(credentials['password'])

    login_btn = driver.find_element_by_css_selector('#content > div > div > div > div > div.panel-body > form > div.text-right > button')
    login_btn.click()
    sleep(3)

    cur_url = str(driver.current_url)
    cur_url = cur_url.split('=')
    token = cur_url[len(cur_url) - 1]
    #print(token)



def import_products_file(file):

    global driver

    crossparser_tools.write_to_log('Start import ' + file)
    url = credentials['url_module'].strip() + 'app_product&token=' + token
    driver.get(url)

    login_btn = driver.find_element_by_id('link_tab_import')
    login_btn.click()

    input_btn = driver.find_element_by_css_selector('#form_product_import > div:nth-child(1) > div:nth-child(1) > div:nth-child(19) > div > input[type="file"]')
    input_btn.send_keys(file)

    input_btn = driver.find_element_by_css_selector('#form_product_import > div:nth-child(2) > div > div > button')
    
    actions = ActionChains(driver)
    actions.move_to_element(input_btn)
    actions.click(input_btn)
    actions.perform()

    WebDriverWait(driver, 3600).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#content > div.container-fluid.csvprice_pro_container > div.alert.alert-success.alert-dismissible > i')))
    #print('done file:', file)
    succ_text = driver.find_element_by_css_selector('#content > div.container-fluid.csvprice_pro_container > div.alert.alert-success.alert-dismissible')
    crossparser_tools.write_to_log('Successfully imported ' + file)
    crossparser_tools.write_to_log(succ_text.text.replace('μ', '').replace('\n\n', '\n').replace('×', ''))
    sleep(1)



def import_categ_file(file):

    global driver

    crossparser_tools.write_to_log('Start import ' + file)
    url = credentials['url_module'].strip() + 'app_category&token=' + token
    driver.get(url)

    link_tab_import = driver.find_element_by_id('link_tab_import')
    link_tab_import.click()

    input_btn = driver.find_element_by_css_selector('#form_category_import > div > div > div:nth-child(12) > div > input[type="file"]')
    input_btn.send_keys(file)

    input_btn = driver.find_element_by_css_selector('#form_category_import > div > div > div:nth-child(13) > div > div > button')
    
    actions = ActionChains(driver)
    actions.move_to_element(input_btn)
    actions.click(input_btn)
    actions.perform()

    WebDriverWait(driver, 3600).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#content > div.container-fluid.csvprice_pro_container > div.alert.alert-success.alert-dismissible > i')))
    #print('done file:', file)
    succ_text = driver.find_element_by_css_selector('#content > div.container-fluid.csvprice_pro_container > div.alert.alert-success.alert-dismissible')
    crossparser_tools.write_to_log('Successfully imported ' + file)
    crossparser_tools.write_to_log(succ_text.text.replace('μ', '').replace('\n\n', '\n').replace('×', ''))
    sleep(1)


def rebuild_mf_index():
    global driver
    url = credentials['url_module_mf'].strip() + '&token=' + token
    driver.get(url)
    refresh = WebDriverWait(driver, 300).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#msg-refresh_ocmod_cache > span')))
    sleep(6)
    crossparser_tools.write_to_log(refresh.text)



def import_files():

    global driver

    if os.path.isfile(files_prod_import):
        if os.path.isfile(files_categ_import):

            parse_websites()

            if len(categs_files) == 0 or len(categs_files) == 0:
                crossparser_tools.write_to_log('Nothing to import')
                return

            options = webdriver.ChromeOptions()

            if credentials['is_server'] == 'no':
                chromedriver_path = file_dir_loc + 'chromedriver.exe'
                options.add_argument('--window-size=1200,700')

            if credentials['is_server'] == 'yes':
                chromedriver_path = file_dir_loc + 'chromedriver'
                options.add_argument('--no-sandbox')
                options.add_argument("--disable-dev-shm-usage");
                options.add_argument('--headless')
                options.add_argument('--disable-gpu')

                import purge_db


            driver = webdriver.Chrome(chromedriver_path, chrome_options=options)

            open_web_site()


            for file in categs_files:
                import_categ_file(file)


            for file in products_files:
                import_products_file(file)



            rebuild_mf_index()

            driver.quit()





crossparser_tools.write_to_log(' ******* Start import files *******')
import_files()
