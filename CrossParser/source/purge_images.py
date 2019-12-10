
import shutil
import os.path
import crossparser_tools


data_folder = crossparser_tools.data_folder

credentials = crossparser_tools.parse_credentials()
website_root = credentials['website_root']


#shutil.rmtree(website_root + 'system/storage/cache')
#os.mkdir(website_root + 'system/storage/cache')

shutil.rmtree(website_root + 'image/catalog/product')
os.mkdir(website_root + 'image/catalog/product')

shutil.rmtree(website_root + 'image/cache/catalog/product')
os.mkdir(website_root + 'image/cache/catalog/product')

os.remove(data_folder + 'img_db')
os.remove(data_folder + 'img_db_info.txt')

if credentials['is_server'] == 'yes':
    import image_match_add
    image_match_add.purge_imgs()
    os.system('sudo chmod -R 777 /var/www/html/boots-market/image')