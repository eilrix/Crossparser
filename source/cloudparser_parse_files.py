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
img_db_info = {}

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

    if os.path.isfile(data_folder + 'img_db_info.txt'):
        with open(data_folder + 'img_db_info.txt', 'r') as cr_file:
            for line in cr_file:
                if not line.strip().startswith('#'):
                    if line.strip():
                        k, v = line.strip().split('$$')
                        img_db_info[k.strip()] = v.strip()
    else:
        with open(data_folder + 'img_db_info.txt', 'w+') as cr_file:
            cr_file.write('items $$ 0 \nsize  $$ 0 Mb')
            img_db_info['items'] = 0
            img_db_info['size'] = '0 Mb'


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



def to_seo_url(string):
    seo_url = string.lower().replace(' ', '-').replace('"', '').replace('--', '-')
    #for c in string.punctuation:
    #    seo_url=seo_url.replace(c,"-")
    seo_url = translit(seo_url, 'ru',  reversed=True)
    full_pattern = re.compile('[^a-zA-Z0-9]|-')
    seo_url = re.sub(full_pattern, '-', seo_url).replace('--', '-')
    return seo_url




def parse_header(row, csvexportfile):

    global table_titles_list
    table_titles_list = []

    row_out = []
    #print("header: ", row)

    for cell in row:
        table_titles_list.append(cell)


    for attr, value in export_fields.items():
        row_out.append(value)
    
    csvexportfile.write(';'.join(row_out) + '\n')


def create_category(prod_categs, prod_brand, prod_name, prod_price, prod_image):
    global categories_names
    global categories_ids
    global categories_max_id
    global global_prod_gender
    prod_categs = prod_categs.split(',')
    prod_brand = prod_brand.replace('"', '')
    prod_name = prod_name.replace('"', '')

    if prod_categs == '' or prod_categs == ' ' or prod_categs is None:
        print('no prod_categs for ' + prod_name)
        return ''

    if prod_brand == '' or prod_brand == ' ' or prod_brand is None:
        print('no prod_brand for ' + prod_name)
        return ''

    if prod_price == '' or prod_price == ' ' or prod_price is None:
        print('no prod_price for ' + prod_name)
        return ''

    #Format categs
    empty_cells_i = []
    for i in range(len(prod_categs)):
        prod_categs[i] = prod_categs[i].strip().replace('\n', '').replace('\r', '')
        #Clear empty cells
        if prod_categs[i] == '' or prod_categs[i] == ' ':
            empty_cells_i.append(i)

    #Clear empty cells
    empty_cells_i.sort(reverse=True)
    for i in empty_cells_i:
        prod_categs.pop(i)

    if len(prod_categs) == 0:
         print('no prod_categs for ' + prod_name)
         return ''


    #print('prod_categs1: ', prod_categs)

    # The purpose is:
    # 1. Define gender of item. It can be two values: (Мужские) and (Женские)
    prod_gender = '?Мужские|Женские'

    for cat in prod_categs:
        if 'женск' in cat or 'Женск' in cat or 'Женщинам' in cat:
            prod_gender = 'Женские'
        if 'мужск' in cat or 'Мужск' in cat or 'Мужчинам' in cat:
            prod_gender = 'Мужские'

    if prod_gender == '?Мужские|Женские':
        print('cant define prod gender for ' + prod_name)
        return ''

    global_prod_gender = prod_gender

    # 2. Create two chains: (gender|type|brand) and (brand|type)
    cat_gender_chain = prod_gender + '|' + '|'.join(prod_categs) + '|' + prod_brand
    cat_brand_chain = 'Бренды' + '|' + prod_brand + '|' + '|'.join(prod_categs)



    # Customize chains search for certain shops
    # <Optional loop>

    if current_site == 'lamoda.ru':

        if 'Обувь' not in prod_categs:
            return ''

        index = prod_categs.index('Обувь')
        prod_categs = prod_categs[index + 1 : len(prod_categs)]
        if 'Кроссовки и кеды' in prod_categs:
            prod_categs.pop(prod_categs.index('Кроссовки и кеды'))


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

        categs = categs.split(' ')
        cat_type = categs[0].lower()

        cat_gender_chain = prod_gender + '|' + cat_type + '|' + prod_brand
        cat_brand_chain = 'Бренды' + '|' + prod_brand + '|' + cat_type



    # </>
        
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



def parse_row(row, csvwriter):

    #print("in row: ", row)
    if row == '':
        return

    n_import = len(table_titles_list)
    n_export = len(export_fields)
    row_out = [''] * n_export


    row = row.split(';')

    #First 4 cells is usually categories
    row[0] = row[0] + ',' + row[1] + ',' + row[2] + ',' + row[3]

    #Format export row
    i = 0
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
    # From 'cell' to 'row_out[i]'
    i = -1
    #print('row_out', row_out)

    for cell in row_out:
        i += 1
        current_row_title = export_fields_array[i]


        if current_row_title == '_DESCRIPTION_' or current_row_title == '_NAME_' or current_row_title == '_MANUFACTURER_':
            row_out[i] = '"' + cell.strip() + '"'

        #Format Size:
        if current_row_title == '_OPTIONS_':
            new_size_cell = '"'
            cell = cell.replace('\n', '').replace('\r', '')
            sizes_arr = cell.split(',')
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


        #Parse and download all images:
        if current_row_title == '_IMAGES_':
            #Decline product without imgs:
            if cell == '':
                return

            imgs = cell.split(",")
            checked_imgs = []
            for img in imgs:
                check = image_check(img)
                if check != '':
                    checked_imgs.append(check)

            if len(checked_imgs) == 0:
                row_out[i] = ''
                #Decline product without imgs:
                return
            else:
                row_out[i] = (',').join(checked_imgs)


        #Set primary (first) image:
        if current_row_title == '_IMAGE_':
            sku_index = export_fields_array.index('_IMAGES_')
            curr_sku = row_out[sku_index]
            if curr_sku == '':
                sku_index = export_fields_array.index('_LOCATION_')
                curr_sku = row_out[sku_index]
                crossparser_tools.write_to_log('No images collected for product: ' + curr_sku + ' (failed to download)')
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
            #print(cell)
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

            if categs_ids == '':
                #Decline product without categories:
                url_index = export_fields_array.index('_LOCATION_')
                url = row_out[url_index]
                crossparser_tools.write_to_log('No categories created for product: ' + url)
                return

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

        #Save this store link
        if current_row_title == '_EAN_':
            row_out[i] = current_site

    
    # </>

    #print("out row: ", ';'.join(row_out) + '\n')     

    for i in range(len(row_out)):
        row_out[i] = str(row_out[i])

    csvwriter.write(';'.join(row_out) + '\n')

    global items_counter_converted
    items_counter_converted += 1
    global csv_out_data_counter
    csv_out_data_counter += 1



def json_to_csv(data, csvexportfile):
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




def make_csv(file):

    filename = file + '-import.csv'

    global items_counter_parsed
    global csv_out_data_counter
    csv_out_data_counter = 0


    with open(filename, 'w+', newline='', encoding="utf8") as csvexportfile:
        with open(file, 'r', newline='', encoding="utf8") as csvimportfile:

            #replace ; and \n symbol in cells
            str_row = ''.join(csvimportfile.readlines())
            replace_flag = False
            i = 0
            str_row_list = list(str_row)

            for sym in str_row_list:
                if sym == '"':
                    replace_flag = not replace_flag

                if replace_flag == True:
                    if sym == ";":
                        str_row_list[i] = ","
                    if sym == "\n":
                        str_row_list[i] = ""

                i += 1

            
            str_row = ''.join(str_row_list)
            file_lines = str_row.replace('"', "").split('\n')

            csv_header = file_lines[0].replace('\r', '').replace('\ufeff', '').split(';')
            #print('csv_header: ', csv_header)
            parse_header(csv_header, csvexportfile)

            file_lines.pop(0)


            for row in file_lines:
                if row == '':
                    continue

                items_counter_parsed += 1

                row = row.strip().replace('\n', '').replace('\r', '')

                if credentials['is_server'] == 'no':
                    parse_row(row, csvexportfile)
                if credentials['is_server'] == 'yes':
                    try:
                        parse_row(row, csvexportfile)
                    except Exception as e:
                        crossparser_tools.write_to_log('failed to parse row of file:' + file + '. row: ' + row)
                        crossparser_tools.write_to_log(e)


    if csv_out_data_counter == 0:
        crossparser_tools.write_to_log('Failed to make csv file of ' + current_site + '. No entries ')
        os.remove(filename)
        return

    with open(temp_folder + 'files_prod_import.txt', 'a', newline='', encoding="utf8") as files_toimport:
        files_toimport.write(filename + '\n')

    crossparser_tools.write_to_log('Made csv file with ' + str(csv_out_data_counter) + ' items of ' + current_site 
                  + '. Saved to file: ' + filename)




def parse_new():

    file_of_raw_catalogs = crossparser_tools.file_of_raw_catalogs

    files_to_parse = {}

    with open(file_of_raw_catalogs, 'r', newline='', encoding="utf8") as files_toimport:
        for line in files_toimport:
            line = line.split('$$')
            files_to_parse[line[1].strip()] = line[0].strip().replace('\n', '')


    if len(files_to_parse) == 0:
        return

    for file, site in files_to_parse.items():
        if os.path.isfile(file):
            crossparser_tools.write_to_log('Start processing file: ' + file)
            global current_site
            current_site = site
            make_csv(file)





parse_export_fields()
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


parse_new()

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



img_db_info_items = int(img_db_info['items']) + img_counter_dowloaded
img_db_info_size = float(img_db_info['size'].replace(' Mb', '')) * 1000000 + img_counter_dowloaded_size_compressed

crossparser_tools.write_to_log('imgs in db: ' + str(img_db_info_items))
crossparser_tools.write_to_log('size of imgs in db: ' + str(round(img_db_info_size / 1000000, 2)) + ' Mb')


with open(data_folder + 'img_db_info.txt', 'w+', newline='', encoding="utf8") as img_db_info:
    img_db_info.write('items $$ ' + str(img_db_info_items) + '\nsize  $$ ' + str(round(img_db_info_size / 1000000, 2)) + ' Mb')


import csvimport