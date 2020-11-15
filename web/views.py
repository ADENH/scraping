from django.shortcuts import render
from bs4 import BeautifulSoup
import requests
from .models import Product,make_product
import json

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
    jumlah_iklan =''
    Products = []
    if page.status_code==200:
        div = soup.findAll("li",{"data-aut-id": "itemBox"})
        Products = set_product(div,base_url)
        jumlah_iklan = data['metadata']['total_ads']
        
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
    base_url = 'https://www.olx.co.id/item/'
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0'}
    url_api ='https://www.olx.co.id/api/relevance/search?facet_limit=100&location=1000001&location_facet_limit=20&query='+keyword+'&spellcheck=true&user=0'
    print(url_api)
    request_api = requests.get(url_api,headers=headers)
    json_result = request_api.json()
    Data = json_result['data']
    items = []
    for a in Data:
        nama_barang=a['title']
        harga_barang=a['price']['value']['display']
        link = base_url+a['title'].replace(" ","-")+'-iid-'+a['id']
        deskripsi = a['description']

        lokasi = a['location_source']
        if lokasi != None:
            try:
                lokasi = json.loads(lokasi)
                lokasi = lokasi['name']
            except :
                lokasi = ''   
        
        images = []
        for b in a['images']:
            images.append(b['url'])
        waktu = ''
        if a['republish_date'] != None:
            waktu = a['republish_date']
        else:
            waktu = a['created_at']
        print(waktu)
              
       
        # items.append(make_product(a['title']))
    return json_result