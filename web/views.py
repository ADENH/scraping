from django.shortcuts import render
from bs4 import BeautifulSoup
import requests
from .models import Product,make_product
import json
import datetime
import dateutil.parser

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
    # print(request.POST.get('next_page'))
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0'}
    base_url = 'https://www.olx.co.id'
    jumlah_iklan =''
    next_page_url = ''
    prev_page_url = '#'
    page = ''
    Products = []
    category = 'product'
    if search_product != None:
        url = 'https://www.olx.co.id/items/q-' + search_product
        data = get_product_by_api(search_product,url,0,category) 
        title = 'Hasil Pencarian '+ search_product
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, 'html.parser')
        if page.status_code==200:
            div = soup.findAll("li",{"data-aut-id": "itemBox"})
            Products = set_product(div,base_url)
    else:
        url = request.POST.get('next_page')
        data = get_product_by_api(search_product,url,1,category)
        try:
            title = 'Hasil Pencarian '+ data['metadata']['original_term']
        except:
            title = 'Hasil Pencarian '
        
        Products = set_product_by_api(data['data'],base_url)    

    
    jumlah_iklan = data['metadata']['total_ads']
    next_page_url = data['metadata']['next_page_url']
    page = next_page_url.find('&clientVersion')
    hal = next_page_url.find('page=')+5
   
    if request.POST.get('next_page') != None:
        next = request.POST.get('next_page')
        prev=int(next_page_url[hal:page])-2
        next = next_page_url[:hal]+str(prev)+next_page_url[hal+1:]
        prev_page_url = next
    else:
        prev_page_url = '#'
    
    print(prev_page_url)
    page = int(next_page_url[hal:page])    
   
    context={
        'Products' : Products,
        'Title' : title,
        'Iklan' : jumlah_iklan,
        'Next_Page' : next_page_url,
        'Previous_Page' : prev_page_url,
        'Page':page
    } 
    return render(request,'index.html',context)

def mobil_bekas(request):
    search_product = request.POST.get('product')
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0'}
    base_url = 'https://www.olx.co.id'
    Products = []
    jumlah_iklan =''
    next_page_url = ''
    prev_page_url = '#'
    page = ''
    category = '198'
    if search_product == None:
        url = 'https://www.olx.co.id/mobil-bekas_c198'
        data = get_product_by_api(category,url,0,category) 
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, 'html.parser')
        if page.status_code==200:
            div = soup.findAll("li",{"data-aut-id": "itemBox"})
            Products = set_product(div,base_url)
    else:
        url = request.POST.get('next_page')
        data = get_product_by_api(category,url,1,category)
        title = 'Hasil Pencarian Mobil Bekas'
        Products = set_product_by_api(data['data'],base_url)   

    title = 'Mobil Bekas'
    jumlah_iklan = data['metadata']['total_ads']
    next_page_url = data['metadata']['next_page_url']
    page = next_page_url.find('&category')
    hal = next_page_url.find('page=')+5

    if request.POST.get('next_page') != None:
        next = request.POST.get('next_page')
        prev=int(next_page_url[hal:page])-2
        next = next_page_url[:hal]+str(prev)+next_page_url[hal+1:]
        prev_page_url = next
    else:
        prev_page_url = '#'

    page = next_page_url[hal:page]
    context={
        'Products' : Products,
        'Title' : title,
        'Iklan' : jumlah_iklan,
        'Next_Page' : next_page_url,
        'Previous_Page' : prev_page_url,
        'Page':page
    } 
    return render(request,'index.html',context)

def motor_bekas(request):
    search_product = request.POST.get('product')
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0'}
    base_url = 'https://www.olx.co.id'
    Products = []
    jumlah_iklan =''
    next_page_url = ''
    prev_page_url = '#'
    page = ''
    category = '200'
    if search_product == None:
        url = 'https://www.olx.co.id/motor-bekas_c200'
        data = get_product_by_api(category,url,0,category) 
        page = requests.get(url, headers=headers)
        soup = BeautifulSoup(page.text, 'html.parser')
        if page.status_code==200:
            div = soup.findAll("li",{"data-aut-id": "itemBox"})
            Products = set_product(div,base_url)
    else:
        url = request.POST.get('next_page')
        data = get_product_by_api(category,url,1,category)
        title = 'Hasil Pencarian Motor Bekas'
        Products = set_product_by_api(data['data'],base_url)   

    title = 'Motor Bekas'
    jumlah_iklan = data['metadata']['total_ads']
    next_page_url = data['metadata']['next_page_url']
    page = next_page_url.find('&category')
    hal = next_page_url.find('page=')+5

    if request.POST.get('next_page') != None:
        next = request.POST.get('next_page')
        prev=int(next_page_url[hal:page])-2
        next = next_page_url[:hal]+str(prev)+next_page_url[hal+1:]
        prev_page_url = next
    else:
        prev_page_url = '#'

    page = next_page_url[hal:page]
    context={
        'Products' : Products,
        'Title' : title,
        'Iklan' : jumlah_iklan,
        'Next_Page' : next_page_url,
        'Previous_Page' : prev_page_url,
        'Page':page
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

def get_product_by_api(keyword,url,code,search_by):
    
    headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0'}
    if code == 1:
        url_api = url
    else:
        if search_by == 'product':
            url_api ='https://www.olx.co.id/api/relevance/search?facet_limit=100&location=1000001&location_facet_limit=20&query='+keyword+'&spellcheck=true&user=0'
        else:
            url_api = 'https://www.olx.co.id/api/relevance/search?category='+keyword+'&facet_limit=100&location=2000032&location_facet_limit=20&user=175c05da6cex1e480dcd'
    
    print(url_api)
    request_api = requests.get(url_api,headers=headers)
    json_result = request_api.json()
    return json_result

def set_product_by_api(data,base_url):
    Products = []
    for a in data:
        nama_barang=a['title']
        harga_barang=a['price']['value']['display']
        link = base_url+"/item/"+a['title'].replace(" ","-")+'-iid-'+a['id']
        deskripsi = a['description']

        lokasi = a['location_source']
        if lokasi != None:
            try:
                lokasi = json.loads(lokasi)
                lokasi = lokasi['name']
            except :
                lokasi = ''   
        img = a['images'][0]['url']
        images = []
        for b in a['images']:
            images.append(b['url'])
        waktu = ''
        try:
            if a['republish_date'] != None:
                waktu = a['republish_date']
            else:
                waktu = a['created_at']
        except :
            if a['display_date'] != None:
                waktu = a['display_date']
            else:
                waktu = a['created_at']
        waktu = datetime.datetime.fromisoformat(waktu)
        waktu = waktu.strftime('%Y-%m-%d')
        hari_ini = datetime.date.today()
        kemaren = hari_ini -datetime.timedelta(days=1)
        kemaren = kemaren.strftime('%Y-%m-%d')
        hari_ini = hari_ini.strftime('%Y-%m-%d')
        if(waktu == hari_ini ):
            waktu = 'hari ini'
        elif(waktu == kemaren):
            waktu = 'kemaren'
        Products.append(make_product(nama_barang,harga_barang,link,deskripsi,lokasi,img,waktu))
        # print(waktu)
    return Products