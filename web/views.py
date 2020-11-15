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
        Products = set_product(div,url)
           
    # for b in Products:
    #     print(b.link_barang)
    title = 'Rekomendasi Terbaru'
    context={
        'Products' : Products,
        'Title' : title
    } 
    return render(request,'index.html',context)

def search_product(request):
    search_product = request.POST.get('product')
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0'}
    base_url = 'https://www.olx.co.id'
    url = 'https://www.olx.co.id/items/q-' + search_product
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    print(url)
    data = get_product_by_api(search_product)    
    
    Products = []
    if page.status_code==200:
        div = soup.findAll("li",{"data-aut-id": "itemBox"})
        Products = set_product(div,base_url)
        jumlah_iklan = data['metadata']['total_ads']
        print(jumlah_iklan)
        
    # for b in Products:
    #     print(b.link_barang)
    title = 'Hasil Pencarian '+search_product
    context={
        'Products' : Products,
        'Title' : title,
        'Iklan' : jumlah_iklan
    } 
    return render(request,'index.html',context)

def mobil_bekas(request):
    search_product = request.POST.get('product')
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0'}
    base_url = 'https://www.olx.co.id'
    url = 'https://www.olx.co.id/mobil-bekas_c198'
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    Products = []
    if page.status_code==200:
        div = soup.findAll("li",{"data-aut-id": "itemBox"})
        Products = set_product(div,base_url)
    title = 'Mobil Bekas'
    context={
        'Products' : Products,
        'Title' : title
    } 
    return render(request,'index.html',context)

def motor_bekas(request):
    search_product = request.POST.get('product')
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0'}
    base_url = 'https://www.olx.co.id'
    url = 'https://www.olx.co.id/motor-bekas_c200'
    # url_api ='https://www.olx.co.id/api/relevance/search?facet_limit=100&location=1000001&location_facet_limit=20&page=1&query='+search_product+'&spellcheck=true&user=0'
    page = requests.get(url, headers=headers)
    soup = BeautifulSoup(page.text, 'html.parser')
    Products = []
    if page.status_code==200:
        div = soup.findAll("li",{"data-aut-id": "itemBox"})
        Products = set_product(div,base_url)
    title = 'Motor Bekas'
    context={
        'Products' : Products,
        'Title' : title
    } 
    return render(request,'index.html',context)

def set_product(div,base_url):
    Products = []
    for a in div:
        harga = a.find("span",{"data-aut-id": "itemPrice"})
        if harga == None:
            harga =  a.find("span",{"data-aut-id": "itemDetails"})
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
    return Products

def get_product_by_api(keyword):
    # print(keyword)
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0'}
    url_api ='https://www.olx.co.id/api/relevance/search?facet_limit=100&location=1000001&location_facet_limit=20&page=1&query='+keyword+'&spellcheck=true&user=0'
    request_api = requests.get(url_api,headers=headers)
    json_result = request_api.json()
    return json_result