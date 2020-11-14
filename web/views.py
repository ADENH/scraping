from django.shortcuts import render
from bs4 import BeautifulSoup
import requests
from .models import Product,make_product

# Create your views here.
def index(request):
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0'}
    url = 'https://www.olx.co.id'
    page = requests.get(url, headers=headers)

    soup = BeautifulSoup(page.text, 'html.parser')
    Products = []
    if page.status_code==200:
        div = soup.findAll("li",{"data-aut-id": "itemBox"})
        for a in div:
            harga = a.find("span",{"data-aut-id": "itemPrice"})
            namaBarang = a.find("span",{"data-aut-id": "itemTitle"})
            lokasi = a.find("span",{"data-aut-id": "item-location"})
            link = a.find("a",href=True)
            link = url+link['href']
            img = a.find("img")
            img = img['src']
            waktu = a.find("span",{"class": "zLvFQ"})
            waktu = waktu.find('span')
            deskripsi = a.find("span",{"data-aut-id": "itemDetails"})
            lokasi = a.find("span",{"data-aut-id": "item-location"})
            Products.append(make_product(namaBarang.text,harga.text,link,deskripsi,lokasi.text,img,waktu.text))
           
    # for b in Products:
    #     print(b.link_barang)
    context={
        'Products' : Products
    } 
    return render(request,'index.html',context)

def search_product(request):
    search_product = request.POST.get('product')
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0'}
    base_url = 'https://www.olx.co.id'
    url = 'https://www.olx.co.id/items/q-' + search_product
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    Products = []
    if page.status_code==200:
        div = soup.findAll("li",{"data-aut-id": "itemBox"})
        for a in div:
            harga = a.find("span",{"data-aut-id": "itemPrice"})
            namaBarang = a.find("span",{"data-aut-id": "itemTitle"})
            lokasi = a.find("span",{"data-aut-id": "item-location"})
            link = a.find("a",href=True)
            link = base_url+link['href']
            img = a.find("img")
            img = img['src']
            waktu = a.find("span",{"class": "zLvFQ"})
            waktu = waktu.find('span')
            deskripsi = a.find("span",{"data-aut-id": "itemDetails"})
            lokasi = a.find("span",{"data-aut-id": "item-location"})
            Products.append(make_product(namaBarang.text,harga.text,link,deskripsi,lokasi.text,img,waktu.text))
    # for b in Products:
    #     print(b.link_barang)
    context={
        'Products' : Products
    } 
    return render(request,'index.html',context)
