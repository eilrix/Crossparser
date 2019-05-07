#!/usr/bin/env python
# -*- coding: utf-8 -*- 

import os.path
import datetime


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
    with open(temp_folder + 'log.txt', 'a+') as cr_file:
        currentDT = datetime.datetime.now()
        #full_pattern = re.compile('[^a-zA-Z0-9]|-')
        #text = re.sub(full_pattern, ' ', text)
        cr_file.write('[' + str(currentDT) + ']  ' + str(text) + '\n')