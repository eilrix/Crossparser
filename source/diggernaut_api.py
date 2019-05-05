#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import requests
from time import sleep
from operator import itemgetter
import re, string, timeit
import regex
from transliterate import translit, get_available_language_codes
import os.path
import urllib.request
from PIL import Image
import crossparser_tools


#location of server folders
temp_folder = crossparser_tools.temp_folder
config_folder = crossparser_tools.config_folder
data_folder = crossparser_tools.data_folder
img_folder = 'image/catalog/product/'
img_module_folder = 'catalog/product/'



#token of diggernaut api:
token = "shi8z84yyfev2nkxfvox2r9189mshk5tfgi99wj0"

digger_id = '5934'
#digger_id = '6463'
is_checking = True
current_site = 'lamoda.ru'
#current_site = 'sportmaster.ru'
credentials = crossparser_tools.parse_credentials()
table_titles = {}
table_titles_list = []
export_fields = {}
export_fields_nums = {}
export_fields_array = []
websites = {}
weblinks = {}
categories_names = []
categories_ids = []
categories_qnt = []
categories_qnt.append(0)
categories_lower_price = []
categories_lower_price.append(99999)
categories_images = []
categories_images.append(0)
categories_parent_ids = []
categories_max_id = 0
print_rows_formating = False
global_prod_gender = ''
img_db = {}

#Counters for statistic
img_counter_existed = 0
img_counter_dowloaded = 0
img_counter_dowloaded_size = 0
img_counter_dowloaded_size_compressed = 0
img_counter_failed_to_dowload = 0
items_counter_parsed = 0
items_counter_converted = 0
csv_out_data_counter = 0



def parse_img_db():
    if os.path.isfile(data_folder + 'img_db'):
        with open(data_folder + 'img_db', 'r') as cr_file:
            for line in cr_file:
                if not line.strip().startswith('#'):
                    if line.strip():
                        k, v = line.strip().split('$$')
                        img_db[k.strip()] = v.strip()


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




def parse_export_fields():
    i = 0
    with open(config_folder + 'export_fields.txt', 'r') as cr_file:
        for line in cr_file:
            if not line.strip().startswith('#'):
                if line.strip():
                    k, v = line.replace('\n', '').split('$$')
                    export_fields[k] = v
                    export_fields_nums[k] = i
                    export_fields_array.append(v)
                    i = i + 1


def parse_categories():
    with open(temp_folder + 'category_export.csv', 'r', newline='', encoding="utf8") as cat_file:
        category_export = cat_file.readlines()
        category_export.pop(0)
        global categories_names
        global categories_ids
        global categories_max_id

        for row in category_export:
            row = row.split(';')
            if len(row) < 10:
                continue

            categories_names.append(row[2])
            categories_ids.append(int(row[0]))

        categories_max_id = max(categories_ids)


def to_seo_url(string):
    seo_url = string.lower().replace(' ', '-').replace('"', '').replace('--', '-')
    #for c in string.punctuation:
    #    seo_url=seo_url.replace(c,"-")
    seo_url = translit(seo_url, 'ru',  reversed=True)
    full_pattern = re.compile('[^a-zA-Z0-9]|-')
    seo_url = re.sub(full_pattern, '-', seo_url).replace('--', '-')
    return seo_url


def check_status(digger_id, is_checking):
    headers = {'Authorization': 'Token ' + token}
    URL = 'https://www.diggernaut.com/api/diggers/' + digger_id + '/sessions'
    r = requests.get(url = URL, headers = headers) 
    data = r.json()
    if len(data) == 0:
        print('Diggernaut doesnt respond properly')
        return []

    session_info = data[len(data) - 1]
    print(session_info)
    #return data[len(data) - 1]

    if is_checking == False:
        return session_info

    if is_checking == True:
        if session_info['state'] == 'running':
            sleep(10)
            check_status(digger_id, is_checking)
        if session_info['state'] == 'success':
            return session_info
        else:
            print('session failed')
            return session_info


def start_digger(digger_id, link_to_parse):
    headers = {'Authorization': 'Token ' + token, 'Content-type': 'application/json'}
    URL = 'https://www.diggernaut.com/api/diggers/' + digger_id + '/start'
    PARAMS = '{"variables":{"target_page":"' + link_to_parse  +'"}}'

    r = requests.post(url = URL, headers = headers, data = PARAMS)
    data = r.json()
    crossparser_tools.write_to_log(data)

    
def get_session_data(digger_id, session_id):
    headers = {'Authorization': 'Token ' + token}
    URL = 'https://www.diggernaut.com/api/diggers/' + digger_id + '/sessions/' + str(session_id) + '/data'
    r = requests.get(url = URL, headers = headers) 
    data = r.json()
    return data


def parse_header(row, csvexportfile):

    global table_titles_list
    row_out = []
    #print("header: ", row)

    for cell in row:
        table_titles_list.append(cell)


    for attr, value in export_fields.items():
        row_out.append(value)
    
    csvexportfile.write(';'.join(row_out) + '\r\n')


def create_category(prod_categs, prod_brand, prod_name, prod_price, prod_image):
    global categories_names
    global categories_ids
    global categories_max_id
    global global_prod_gender
    prod_categs = prod_categs.split(',')
    prod_brand = prod_brand.replace('"', '')
    prod_name = prod_name.replace('"', '')
    for i in range(len(prod_categs)):
        prod_categs[i] = prod_categs[i].strip().replace('\n', '').replace('\r', '')

    #print('prod_categs1: ', prod_categs)
    prod_gender = '?Мужские|Женские'


    if current_site == 'lamoda.ru':

        if 'Обувь' not in prod_categs:
            return ''

        if prod_categs[1] == 'Женщинам':
            prod_gender = 'Женские'
        if prod_categs[1] == 'Мужчинам':
            prod_gender = 'Мужские'

        if prod_gender == '?Мужские|Женские':
            return ''

        global_prod_gender = prod_gender

        index = prod_categs.index('Обувь')
        prod_categs = prod_categs[index + 1 : len(prod_categs)]
        if 'Кроссовки и кеды' in prod_categs:
            prod_categs.pop(prod_categs.index('Кроссовки и кеды'))

        #Purpose is to create two chains: (gender|type|brand) and (brand|type)
        cat_gender_chain = prod_gender + '|' + '|'.join(prod_categs) + '|' + prod_brand
        cat_brand_chain = 'Бренды' + '|' + prod_brand + '|' + '|'.join(prod_categs)
        
        prod_cats1 = check_new_chain(cat_gender_chain, prod_price, prod_image)
        prod_cats2 = check_new_chain(cat_brand_chain, prod_price, prod_image)

        return prod_cats1 + prod_cats2


    if current_site == 'sportmaster.ru':

        categs = prod_name.split(prod_brand.strip())
        if len(categs) != 2:
            return ''

        categs = categs[0]

        if 'женские' in categs:
            prod_gender = 'Женские'
        if 'мужские' in categs:
            prod_gender = 'Мужские'

        if prod_gender == '?Мужские|Женские':
            return ''

        global_prod_gender = prod_gender

        categs = categs.split(' ')
        cat_type = categs[0].lower()

        cat_gender_chain = prod_gender + '|' + cat_type + '|' + prod_brand
        cat_brand_chain = 'Бренды' + '|' + prod_brand + '|' + cat_type
        
        prod_cats1 = check_new_chain(cat_gender_chain, prod_price, prod_image)
        prod_cats2 = check_new_chain(cat_brand_chain, prod_price, prod_image)

        return prod_cats1 + prod_cats2
        




def check_new_chain(chain, prod_price, prod_image):
    global categories_names
    global categories_ids
    global categories_max_id

    prod_cats = []


    cat_gender_chain_list = chain.split('|')
    parent_id = 0
    for i in range(len(cat_gender_chain_list)):
        i += 1
        cat_check = cat_gender_chain_list[0 : i]
        cat_check_chain = '|'.join(cat_check)

        if cat_check_chain in categories_names:
            index = categories_names.index(cat_check_chain)
            parent_id = categories_ids[index]

        if cat_check_chain not in categories_names:
            add_new_category(cat_check_chain, parent_id, prod_image)
            parent_id = categories_max_id

        prod_cats.append(parent_id)

    
    i = 0
    for cat in prod_cats:
        categories_qnt[cat] += 1

        if prod_price < categories_lower_price[cat]:
            categories_lower_price[cat] = prod_price

        prod_cats[i] = str(cat)
        i += 1

    return prod_cats



def add_new_category(cat_check_chain, parent_id, prod_image):
    global categories_names
    global categories_ids
    global categories_max_id
    global categories_parent_ids
    categories_max_id += 1

    categories_names.append(cat_check_chain)
    categories_ids.append(categories_max_id)
    categories_parent_ids.append(parent_id)
    categories_qnt.append(0)
    categories_lower_price.append(999999)
    categories_images.append(prod_image)


    #with open(temp_folder + 'category_export.csv', 'a+', newline='', encoding="utf8") as cat_file:
    #    cat_file.write(';'.join(row_out) + '\n')


def make_categories_csv():
    global categories_names
    global categories_ids
    global categories_max_id
    global categories_parent_ids

    if len(categories_names) == 0:
        crossparser_tools.write_to_log('Failed to make categories csv. No entries')
        return


    res_eng = regex.search(r'\p{IsCyrillic}', 'lala')

    categs_for_menu = []
    categs_for_menu_urls = []
    categs_filename = temp_folder + 'category_export.csv'

    with open(temp_folder + 'files_categ_import.txt', 'w+', newline='', encoding="utf8") as files_toimport:
        files_toimport.write(categs_filename)

    with open(categs_filename, 'w+', newline='', encoding="utf8") as cat_file:
        row_out = '_ID_;_PARENT_ID_;_NAME_;_META_H1_;_META_TITLE_;_META_KEYWORDS_;_META_DESCRIPTION_;_DESCRIPTION_;_IMAGE_;_SEO_KEYWORD_;_SORT_ORDER_\n'
        cat_file.write(row_out)


        #print('categories_qnt: ', categories_qnt)

        for i_cat in range(len(categories_names)):

            #Form up H1 header:
            categs = categories_names[i_cat].split('|')

            main_subcat = ''
            if len(categs) == 2:
                main_subcat = ';'.join(categs)

            for i in range(len(categs)):
                res = regex.search(r'\p{IsCyrillic}', categs[i])
                if res != res_eng:
                    categs[i] = categs[i].lower()


            for i in range(len(categs)):
                for j in range(i + 1 , len(categs)):
                    if i > (len(categs) - 1) or j > (len(categs) - 1):
                        break
                    if categs[i] in categs[j]:
                        categs.pop(i)

            seo_title = ''
            is_brand_cat = False

            if categs[0] == 'бренды':
                categs.pop(0)
                is_brand_cat = True
                #Form up SEO Title for brands:
                if len(categs) > 0:
                    seo_title = 'Купить ' + ' '.join(categs) + '. Каталог ' + categs[0] + ' оригинал, цены'

            if len(categs) > 0:
                #Form up SEO Title for gender categs:
                categs[0] = categs[0].capitalize()
                if is_brand_cat == False:
                    seo_title = ' '.join(categs) + ' купить по цене от ' + str(categories_lower_price[categories_ids[i_cat]]) + ' руб. Фото, каталог'

            h1header = ' '.join(categs)

            #SEO URL:
            seo_url = to_seo_url(h1header)


            #Categs for menu:
            if main_subcat != '' :
                if main_subcat not in categs_for_menu:
                    num = str(categories_qnt[categories_ids[i_cat]])
                    categs_for_menu.append([main_subcat.capitalize(), seo_url, num])




            row_out = [''] * 11
            row_out[0] = str(categories_ids[i_cat])
            row_out[1] = str(categories_parent_ids[i_cat])
            row_out[2] = categories_names[i_cat]
            #print('new category:', categories_names[i_cat])

            row_out[3] = h1header
            row_out[4] = seo_title

            row_out[8] = str(categories_images[categories_ids[i_cat]])
            row_out[9] = seo_url
            row_out[10] = str(categories_qnt[categories_ids[i_cat]])
            #print('adding new category:', row_out)

            cat_file.write(';'.join(row_out) + '\n')



    crossparser_tools.write_to_log('Made scv of categories with ' + str(len(categories_names)) + ' items. Saved to ' + categs_filename)
    categs_for_menu = sorted(categs_for_menu, key=lambda x: x[0], reverse=False)
    #print(categs_for_menu)

    #make menu file for web-site
    with open(data_folder + 'category_menu.txt', 'w+', newline='', encoding="utf8") as cat_file:
        for cat in categs_for_menu:
            cat_file.write(';'.join(cat) + '$$')






def parse_row(row, csvwriter):

    global csv_out_data_counter

    n_import = len(table_titles_list)
    n_export = len(export_fields)
    i = 0
    row_out = [''] * n_export

    #Format export row

    for cell in row:

        if i >= n_import:
            print("col out of range of header: ", cell)
            break

        for attr, value in export_fields.items():
            if attr == table_titles_list[i]:
                row_out[export_fields_nums[attr]] = cell.replace('"', '').replace('\n', '')

        i = i + 1

    if print_rows_formating == True:
        print("row formated for export: ", row_out)

    # Customize special fields (such as Size, etc)
    # <Optional loop>
    i = -1
    for cell in row_out:
        i += 1
        current_row_title = export_fields_array[i]

        if current_row_title == '_DESCRIPTION_' or current_row_title == '_NAME_' or current_row_title == '_MANUFACTURER_':
            row_out[i] = '"' + cell.strip() + '"'

        #Format Size:
        if current_row_title == '_OPTIONS_':
            new_size_cell = '"'
            cell = cell.replace('\n', '').replace('\r', '')
            sizes_arr = cell.split('|')
            for size in sizes_arr:
                new_size_cell += 'select|Размер|'
                new_size_cell += size
                new_size_cell += '|1|1000|1|+|0.0000|+|0|+|0.00\n'

            row_out[i] = new_size_cell + '"'
        
        #Format Price:
        if current_row_title == '_PRICE_':
            row_out[i] = ''.join(re.findall(r'\d+', cell.replace(' ', '')))

        if current_row_title == '_SPECIAL_':
            special_price = ''.join(re.findall(r'\d+', cell.replace(' ', '')))
            if special_price != '':
                price_index = export_fields_array.index('_PRICE_')
                curr_price = row_out[price_index]
                row_out[price_index] = special_price
                special_price = '.'.join(re.findall(r'\d+', curr_price.replace(' ', '').replace('\n', '').replace('\r', '')))
                row_out[i] = '1,0,' + str(special_price) + '.00,0000-00-00,0000-00-00'

        #Copy SKU to Model:
        if current_row_title == '_MODEL_':
            sku_index = export_fields_array.index('_SKU_')
            curr_sku = row_out[sku_index]
            row_out[i] = curr_sku

        #Set primary (first) image:
        if current_row_title == '_IMAGE_':
            sku_index = export_fields_array.index('_IMAGES_')
            curr_sku = row_out[sku_index]
            if curr_sku == '':
                sku_index = export_fields_array.index('_LOCATION_')
                curr_sku = row_out[sku_index]
                crossparser_tools.write_to_log('No images collected for product: ' + curr_sku)
                #Decline product without imgs:
                return

            curr_sku = curr_sku.split(',')
            row_out[i] = curr_sku[0]
            curr_sku.pop(0)
            row_out[sku_index] = ','.join(curr_sku)

        if current_row_title == '_QUANTITY_': 
            row_out[i] = str(99999)

        #Create category:
        if current_row_title == '_CATEGORY_ID_': 
            index = export_fields_array.index('_MANUFACTURER_')
            prod_brand = row_out[index]
            index = export_fields_array.index('_NAME_')
            prod_name = row_out[index]
            prod_categs = cell
            index = export_fields_array.index('_PRICE_')
            prod_price = 999999
            if row_out[index] != '':
                prod_price = int(row_out[index])

            index = export_fields_array.index('_IMAGE_')
            prod_image = row_out[index]

            categs_ids = create_category(prod_categs, prod_brand, prod_name, prod_price, prod_image)
            if categs_ids is None:
                categs_ids = ''
            row_out[i] = ','.join(categs_ids)

        #SEO URL:
        if current_row_title == '_SEO_KEYWORD_': 
            index = export_fields_array.index('_SKU_')
            prod_sku = row_out[index]
            index = export_fields_array.index('_NAME_')
            prod_name = row_out[index]

            seo_url = to_seo_url(prod_name)

            row_out[i] = seo_url + '-' + prod_sku.lower()

        #Set up attributes: Brand, Gender, Season:
        if current_row_title == '_ATTRIBUTES_':
            global global_prod_gender
            row = '"Обувь|Пол|' + global_prod_gender.replace('"', '') + '\n'

            index = export_fields_array.index('_MANUFACTURER_')
            prod_brand = row_out[index].replace('"', '')
            row += 'Обувь|Бренд|' + prod_brand + '\n'

            prod_season = 'Лето'
            row += 'Обувь|Сезон|' + prod_season + '"'

            row_out[i] = row


    
    # </>
    if print_rows_formating == True:
        print("out row: ", ';'.join(row_out) + '\n')     
    for i in range(len(row_out)):
        row_out[i] = str(row_out[i])
    csvwriter.write(';'.join(row_out) + '\n')
    global items_counter_converted
    items_counter_converted += 1
    csv_out_data_counter += 1


def json_to_csv(data, csvexportfile):

    csv_out_data = []
    csv_header = []

    if len(data) == 1:
        crossparser_tools.write_to_log(data['detail'])
        return ''


    for product in data:
        product = product['post']
        #print('product: ', product['prod_name'])

        row_out = [''] * max([len(product), len(csv_header)])

        for attr, value in product.items():
            if attr not in csv_header:
                csv_header.append(attr)

            if attr in csv_header:
                #Optional PRE-processing of input fields


                if attr == 'products_imgs' or attr == 'prod_categories':
                    value = ','.join(value)

                if attr == 'all_native_sizes' :
                    # Clear disabled sized from all natives:
                    if 'disabled_native_sizes' in product:
                        disabled_native_sizes = product['disabled_native_sizes']
                        if disabled_native_sizes != '' :
                            for size in disabled_native_sizes:
                                if size in value:
                                    value.pop(value.index(size))

                    value = '|'.join(value)

                if current_site == 'sportmaster.ru':
                    if attr == 'products_imgs' :
                        value = value.split("'")
                        imgs = []
                        for chunk in value:
                            if 'https://cdn.sptmr.ru' in chunk:
                                chunk = chunk.replace('resize_cache/','').replace('/${width}_${height}_1','')
                                imgs.append(chunk)

                        value = (',').join(imgs)
                        #print(value)


                if attr == 'products_imgs':
                    imgs = value.split(",")
                    checked_imgs = []
                    for img in imgs:
                        check = image_check(img)
                        if check != '':
                            checked_imgs.append(check)

                    if len(checked_imgs) == 0:
                        value = ''
                    else:
                        value = (',').join(checked_imgs)
                    
                    
                row_out[csv_header.index(attr)] = value

        #print('csv_header: ', csv_header)
        #print('row_out: ', row_out)
        csv_out_data.append(row_out)


    parse_header(csv_header, csvexportfile)
    return csv_out_data


def image_check(img):
    global img_counter_existed
    global img_counter_dowloaded
    global img_counter_failed_to_dowload
    global img_counter_dowloaded_size
    global img_counter_dowloaded_size_compressed

    if img in img_db.keys():
        img_counter_existed += 1
        return img_db[img]

    try:
        #print('downloading img:', img)

        img_name = img.replace('https://', '').replace('http://', '').replace('www', '').replace('jpg', '').replace('/', '')
        img_name = to_seo_url(img_name).replace('-', '')
        img_name = img_name + '.jpg'

        file_path = website_root + img_folder + img_name
        urllib.request.urlretrieve(img, file_path)

        size = os.stat(file_path).st_size
        img_counter_dowloaded_size += size
        #print('size in: ' , size)

        compression = 100

        if size > 2000000:
            compression = 10
        if size > 1000000 and size < 2000000:
            compression = 20
        if size > 500000 and size < 1000000:
            compression = 50
        if size > 200000 and size < 500000:
            compression = 70

        if size > 200000:
            image = Image.open(file_path)
            image.save(file_path, quality=compression)
        else:
           compression = 0

        size = os.stat(file_path).st_size
        img_counter_dowloaded_size_compressed += size

        #print('compression: ' , compression)
        #print('size out: ' , size)

        img_db[img] = img_module_folder + img_name

        with open(data_folder + 'img_db', 'a+', newline='', encoding="utf8") as img_dbfile:
            img_dbfile.write(img + '$$' + img_module_folder + img_name + '\n')

        img_counter_dowloaded += 1

        return img_module_folder + img_name

    except Exception as e: 
        print('unable to download img:', img)
        print(e)
        img_counter_failed_to_dowload += 1
        return ''



def make_csv(data, current_site):

    filename = temp_folder + current_site + '-' + digger_id + '-import.csv'

    with open(filename, 'w+', newline='', encoding="utf8") as csvexportfile:

        csv_out_data = json_to_csv(data, csvexportfile)
        if csv_out_data == '':
            crossparser_tools.write_to_log('No csv_out_data fetched')
            return

        #print(csv_out_data)
        global csv_out_data_counter
        csv_out_data_counter = 0

        for row in csv_out_data:
            #for i in range(len(row)):
                #row[i] = str(row[i])

            #csvexportfile.write(';'.join(row) + '\n')
            parse_row(row, csvexportfile)


    if csv_out_data_counter == 0:
        crossparser_tools.write_to_log('Failed to make csv file of ' + current_site + '. No entries. Digger id: ' + digger_id)
        return

    with open(temp_folder + 'files_prod_import.txt', 'a', newline='', encoding="utf8") as files_toimport:
        files_toimport.write(filename + '\n')

    crossparser_tools.write_to_log('Made csv file with ' + str(csv_out_data_counter) + ' items of ' + current_site 
                 + '. Digger id: ' + digger_id + '. Saved to file: ' + filename)




def parse_new():

    session_info = check_status(digger_id, is_checking)
    if len(session_info) == 0:
        crossparser_tools.write_to_log('Digger ' + str(digger_id) + ' doesnt respond properly')
        return

    session_id = session_info['id']
    print('session_id:', session_id)

    session_data = get_session_data(digger_id, session_id)
    crossparser_tools.write_to_log('Successfully retrieved session ' + str(session_id) + ' data of digger ' + str(digger_id)
                 + '. Items in session: ' + str(len(session_data)))

    global items_counter_parsed
    items_counter_parsed += len(session_data)
    #print('session_data', len(session_data))


    #parse_categories()
    
    make_csv(session_data, current_site)




def get_nextlink_forsite(current_site):
    links = weblinks[current_site]
    if links == '':
        return ''

    if len(links) > 1 :
        links = links.split('||')
    link_to_parse = links[0]

    if len(links) == 1 :
        weblinks[current_site] = ''

    if len(links) > 1 :
        links.pop(0)
        weblinks[current_site] = links

    return link_to_parse


def start_all_diggers():
    global current_site
    global digger_id

    for attr, value in websites.items():
        digger_id = value
        current_site = attr

        link_to_parse = get_nextlink_forsite(current_site)

        crossparser_tools.write_to_log('start parsing: ' + current_site + 'digger_id: ' + digger_id)

        start_digger(digger_id, link_to_parse)


def checking_all_diggers():
    global current_site
    global digger_id

    is_done = True

    for attr, value in websites.items():
        digger_id = value
        current_site = attr

        session_info = check_status(digger_id, False)
        if session_info['state'] == 'running':
            is_done = False
        else:
            parse_session(session_info)

            link_to_parse = get_nextlink_forsite(current_site)

            if link_to_parse != '':
                crossparser_tools.write_to_log('start digger on link: ' + link_to_parse + ', digger_id: ' + digger_id)
                start_digger(digger_id, link_to_parse)
                is_done = False


    sleep(10)
    if is_done == False:
        checking_all_diggers()



def parse_session(session_info):

    if len(session_info) == 0:
        crossparser_tools.write_to_log('Digger ' + str(digger_id) + ' doesnt respond properly')
        return

    session_id = session_info['id']
    print('session_id:', session_id)

    session_data = get_session_data(digger_id, session_id)
    crossparser_tools.write_to_log('Successfully retrieved session ' + str(session_id) + ' data of digger ' + str(digger_id)
                 + '. Items in session: ' + str(len(session_data)))

    global items_counter_parsed
    items_counter_parsed += len(session_data)
    #print('session_data', len(session_data))


    #parse_categories()
    
    make_csv(session_data, current_site)



        


if not os.path.exists(temp_folder):
    os.mkdir(temp_folder)

if not os.path.exists(data_folder):
    os.mkdir(data_folder)


parse_export_fields()
parse_websites()
parse_img_db()


website_root = credentials['website_root']

if not os.path.exists(website_root + img_folder):
    os.makedirs(website_root + img_folder)



#Clear import catalog files (files of files)
with open(temp_folder + 'files_prod_import.txt', 'w+', newline='', encoding="utf8") as files_toimport:
    files_toimport.close()
with open(temp_folder + 'files_categ_import.txt', 'w+', newline='', encoding="utf8") as files_toimport:
    files_toimport.close()
    

crossparser_tools.write_to_log('\n\n ********** Script started *********** \n\n')

#start_all_diggers()
#start_digger(digger_id)
#sleep(10)

#parse_new()

checking_all_diggers()

make_categories_csv()


crossparser_tools.write_to_log('parsing process completed')
crossparser_tools.write_to_log('totally parsed: ' + str(items_counter_parsed) + ' items' )
crossparser_tools.write_to_log('successfully converted: ' + str(items_counter_converted) + ' items' )

imgs_num = img_counter_existed + img_counter_dowloaded + img_counter_failed_to_dowload
crossparser_tools.write_to_log('totally images: ' + str(imgs_num))
crossparser_tools.write_to_log('already in db: ' + str(img_counter_existed))
crossparser_tools.write_to_log('successfully downloaded: ' + str(img_counter_dowloaded))
crossparser_tools.write_to_log('total size of downloaded: ' + str(img_counter_dowloaded_size / 1000000) + ' Mb')
crossparser_tools.write_to_log('total size of downloaded after compression: ' + str(img_counter_dowloaded_size_compressed / 1000000) + ' Mb')
crossparser_tools.write_to_log('failed to download: ' + str(img_counter_failed_to_dowload))


import csvimport






  

