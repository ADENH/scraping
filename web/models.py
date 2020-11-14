from django.db import models
from django_resized import ResizedImageField

# Create your models here.
class Product(object):
    nama_barang = models.CharField(max_length=250)
    harga_barang = models.CharField(max_length=250)
    link_barang = models.CharField(max_length=250)
    deskripsi = models.TextField(null=True, blank=True)
    lokasi_barang = models.CharField(max_length=250)
    tanggal_barang = models.CharField(max_length=250)
    image_url =ResizedImageField(size=[144, 144], crop=['middle', 'center'], quality=100,null=True, blank=True)

    def __init__(self,nama, harga, link,deskripsi,lokasi,img,tanggal):
        self.nama_barang = nama
        self.harga_barang = harga
        self.link_barang = link
        self.lokasi_barang = lokasi
        self.deskripsi =deskripsi
        self.image_url = img
        self.tanggal_barang = tanggal

def make_product(nama, harga, link,deskripsi,lokasi,img,tanggal):
    product = Product(nama, harga, link,deskripsi,lokasi,img,tanggal)
    return product
