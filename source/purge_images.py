
import shutil
import os.path
import crossparser_tools


config_folder = crossparser_tools.config_folder

credentials = crossparser_tools.parse_credentials()
website_root = credentials['website_root']


#shutil.rmtree(website_root + 'system/storage/cache')
#os.mkdir(website_root + 'system/storage/cache')

shutil.rmtree(website_root + 'image/catalog/product')
os.mkdir(website_root + 'image/catalog/product')

shutil.rmtree(website_root + 'image/cache/catalog/product')
os.mkdir(website_root + 'image/cache/catalog/product')

os.remove(config_folder + 'img_db')