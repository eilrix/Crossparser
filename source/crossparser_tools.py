#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import os.path
import datetime
import re, string, timeit
import uuid
from transliterate import translit, get_available_language_codes


dirpath = os.path.dirname(os.path.realpath(__file__))

proj_root_dir = ''
if '/' in dirpath:
    proj_root_dir = dirpath.split('/')
if '\\' in dirpath:
    proj_root_dir = dirpath.split('\\')

proj_root_dir = ('/').join(proj_root_dir[0 : -1]) + '/'


temp_folder = proj_root_dir + 'temp/'
config_folder = proj_root_dir + 'config/'
data_folder = proj_root_dir + 'data/'

file_of_raw_catalogs = temp_folder + 'files_to_parse.txt'


if not os.path.exists(temp_folder):
    os.mkdir(temp_folder)

if not os.path.exists(data_folder):
    os.mkdir(data_folder)



file_dir_loc = dirpath + '/'


table_titles_list = []


def parse_credentials():
    credentials = {}

    with open(config_folder + 'credentials.txt', 'r') as cr_file:
        for line in cr_file:
            if not line.strip().startswith('#'):
                if line.strip():
                    k, v = line.strip().split('$$')
                    credentials[k.strip()] = v.strip()

    return credentials


def write_to_log(text):
    print(text)
    with open(temp_folder + 'log.txt', 'a+') as log_file:
        currentDT = datetime.datetime.now()
        #full_pattern = re.compile('[^a-zA-Z0-9]|-')
        #text = re.sub(full_pattern, ' ', text)
        log_file.write('[' + str(currentDT) + ']  ' + str(text) + '\n')



def read_csv(file, is_clear):
    with open(file, 'r', newline='\n', encoding="utf8") as csvimportfile:

        file_lines = csvimportfile.readlines()

        if is_clear == True:
        #replace ; and \n symbol in cells
            str_row = ''.join(file_lines)
            replace_flag = False
            i = 0
            str_row_list = list(str_row)

            for sym in str_row_list:
                if sym == '"':
                    replace_flag = not replace_flag

                if replace_flag == True:
                    if sym == ";":
                        str_row_list[i] = "|"
                    if sym == "\n":
                        str_row_list[i] = ""
                i += 1

            
            str_row = ''.join(str_row_list)
            file_lines = str_row.replace('"', "").replace('\r', "").split('\n')


        csv_header = file_lines[0].replace('\r', '').replace('\n', '').replace('\ufeff', '').split(';')
        #print('csv_header: ', csv_header)

        file_lines.pop(0)

        global table_titles_list
        table_titles_list = []
        #print("header: ", row)

        for cell in csv_header:
            table_titles_list.append(cell)

        return file_lines


def get_only_nums(string):
    string = string.replace('\n', '').replace('\r', '').replace(' ', '')
    string = ''.join(re.findall(r'\d+', string))
    return string

def get_only_letters(string):
    string = string.replace('\n', '').replace('\r', '').replace(' ', '')
    string = ''.join(re.findall(r'\w+', string))
    return string


def to_seo_url(string):
    seo_url = string.lower().replace(' ', '-').replace('"', '').replace('--', '-')
    #for c in string.punctuation:
    #    seo_url=seo_url.replace(c,"-")
    seo_url = translit(seo_url, 'ru',  reversed=True)
    full_pattern = re.compile('[^a-zA-Z0-9]|-')
    seo_url = re.sub(full_pattern, '-', seo_url).replace('--', '-')
    return seo_url

def get_uniqid_from_url(url, site):
    print('url', url)

    id = url.replace(site, '').replace('https://', '').replace('http://', '').replace('www', '').replace('jpg', '').replace('/', '')
    id = to_seo_url(id).replace('-', '')

    return id


def get_rand_uniqid(n):
    return uuid.uuid4().hex[:n]