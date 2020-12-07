from django.db import models
from django_resized import ResizedImageField

# Create your models here.
class Product(object):
    nama_barang = models.CharField(max_length=250,null=True)
    harga_barang = models.CharField(max_length=250,null=True)
    link_barang = models.CharField(max_length=250,null=True)
    deskripsi = models.TextField(null=True, blank=True)
    lokasi_barang = models.CharField(max_length=250,null=True)
    tanggal_barang = models.CharField(max_length=250,null=True)
    image_url =ResizedImageField(size=[144, 144], crop=['middle', 'center'], quality=100,null=True, blank=True)
    like = models.CharField(max_length=250,null=True)

    def __init__(self,nama, harga, link,deskripsi,lokasi,img,tanggal,like):
        self.nama_barang = nama
        self.harga_barang = harga
        self.link_barang = link
        self.lokasi_barang = lokasi
        self.deskripsi =deskripsi
        self.image_url = img
        self.tanggal_barang = tanggal
        self.like = like

def make_product(nama, harga, link,deskripsi,lokasi,img,tanggal,like):
    product = Product(nama, harga, link,deskripsi,lokasi,img,tanggal,like)
    return product

class Category(models.Model):
    code_category = models.CharField(max_length=250)
    nama_category = models.CharField(max_length=250)
    link_category = models.CharField(max_length=250)

    def __init__(self,code,nama,link):
        self.code_category =code
        self.nama_category =nama
        self.link_category = link

def make_category(code,nama,link):
    category = Category(code,nama,link)
    return category
