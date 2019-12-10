# -*- coding: utf-8 -*-

from image_match.goldberg import ImageSignature
from elasticsearch import Elasticsearch
from image_match.elasticsearch_driver import SignatureES
from os import listdir
from os.path import isfile, join


def add_imgs():
    gis = ImageSignature()
    a = gis.generate_signature('https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa,_by_Leonardo_da_Vinci,_from_C2RMF_retouched.jpg/687px-Mona_Lisa,_by_Leonardo_da_Vinci,_from_C2RMF_retouched.jpg')
    b = gis.generate_signature('https://upload.wikimedia.org/wikipedia/commons/thumb/9/99/Gioconda_%28copia_del_Museo_del_Prado_restaurada%29.jpg/800px-Gioconda_%28copia_del_Museo_del_Prado_restaurada%29.jpg')
    res = gis.normalized_distance(a, b)
    print(res)


    es = Elasticsearch()
    ses = SignatureES(es)

    
    mypath = '/var/www/html/boots-market/image/catalog/product'

    ses.add_image(mypath + '/' + 'almcdnruimg389x562frfr030awdzpc579240581v1.jpg')
    #ses.add_image('/var/www/html/boots-market/image/catalog/almcdnruimg389x562frfr030awdzpc579240581v1.jpg')
    #ses.add_image('/var/www/html/boots-market/image/catalog/12616562_12123107_800.jpg')

    return



    onlyfiles = [f for f in listdir(mypath) if isfile(join(mypath, f))]

    for file in onlyfiles:
        filedir = mypath + '/' + str(file)
        print('add: ' + filedir)
        ses.add_image(filedir)

if __name__ == '__main__':


    add_imgs()

    #ses.add_image('https://upload.wikimedia.org/wikipedia/commons/thumb/e/ec/Mona_Lisa,_by_Leonardo_da_Vinci,_from_C2RMF_retouched.jpg/687px-Mona_Lisa,_by_Leonardo_da_Vinci,_from_C2RMF_retouched.jpg')
    #ses.add_image('https://upload.wikimedia.org/wikipedia/commons/3/33/Raffaello_Sanzio_-_Portrait_of_a_Woman_-_WGA18948.jpg')
    #ses.add_image('https://upload.wikimedia.org/wikipedia/commons/e/e0/Caravaggio_-_Cena_in_Emmaus.jpg')
    #ses.add_image('https://upload.wikimedia.org/wikipedia/commons/6/64/Leonardo_di_ser_Piero_da_Vinci_-_Portrait_de_Mona_Lisa_%28dite_La_Joconde%29_-_Louvre_779_-_Detail_%28hands%29.jpg')




    #ses.search_image('https://pixabay.com/static/uploads/photo/2012/11/28/08/56/mona-lisa-67506_960_720.jpg')