# -*- coding: utf-8 -*-

from image_match.goldberg import ImageSignature
from elasticsearch import Elasticsearch
from image_match.elasticsearch_driver import SignatureES

es = Elasticsearch()
ses = SignatureES(es)


def add_img(img_path, prod_id):

    ses.add_image(img_path, metadata={'prod_id': prod_id})


def purge_imgs():
    es.indices.delete("*")