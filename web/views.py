from logging import exception
from django.shortcuts import render
from django.http import HttpResponse
from bs4 import BeautifulSoup
import requests
from .models import Category, Product, make_category, make_product
import json
import datetime
import xlwt
import pandas as pd

URL_BASE_OLX = 'https://www.olx.co.id'
URL_HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:79.0) Gecko/20100101 Firefox/79.0'}
INDEX = 'index.html'
HTML_PARSER = 'html.parser'
HASIL_PENCARIAN = 'Hasil Pencarian '
DATE_FORMAT = '%Y-%m-%d'
PAGE ='page='

# Create your views here.
def index(request):
    category = get_category_url()
    products = get_home_products()       
    title = 'Rekomendasi Terbaru'
    request.session['products'] = products
    context={
        'Products' : products,
        'Title' : title,
        'Category' : category
    } 
    return render(request,INDEX,context)

def search_product(request):
    categoy_list = get_category_url()
    search_product = request.POST.get('product')
    # print(request.POST.get('next_page'))
    jumlah_iklan =''
    next_page_url = ''
    prev_page_url = '#'
    page = ''
    products = []
    category = 'product'
    if search_product != None:
        url = 'https://www.olx.co.id/items/q-' + search_product
        data = get_product_by_api(search_product,url,0,category) 
        title = HASIL_PENCARIAN+ search_product
        page = requests.get(url, headers=URL_HEADERS)
        soup = BeautifulSoup(page.text, HTML_PARSER)
        if page.status_code==200:
            div = soup.findAll("li",{"data-aut-id": "itemBox"})
            products = set_product(div,URL_BASE_OLX)
    else:
        url = request.POST.get('next_page')
        data = get_product_by_api(search_product,url,1,category)
        try:
            title = HASIL_PENCARIAN+ data['metadata']['original_term']
        except Exception:
            title = 'Hasil Pencarian '
        
        products = set_product_by_api(data['data'],URL_BASE_OLX)    
    
    jumlah_iklan = data['metadata']['total_ads']
    next_page_url = data['metadata']['next_page_url']
    page = next_page_url.find('&clientVersion')
    hal = next_page_url.find(PAGE)+5
   
    if request.POST.get('next_page') != None:
        next_url = request.POST.get('next_page')
        prev = int(next_page_url[hal:page])-2
        next_url = next_page_url[:hal]+str(prev)+next_page_url[hal+1:]
        prev_page_url = next_url
    else:
        prev_page_url = '#'
    
    print(prev_page_url)
    page = int(next_page_url[hal:page])    
    request.session['products'] = products
    context={
        'Products' : products,
        'Title' : title,
        'Iklan' : jumlah_iklan,
        'Next_Page' : next_page_url,
        'Previous_Page' : prev_page_url,
        'Page':page,
        'Category': categoy_list
    } 
    return render(request,INDEX,context)

def set_product(div,base_url):
    products = []
    for a in div:
        harga = a.find("span",{"data-aut-id": "itemPrice"})
        if harga == None:
            harga =  a.find("span",{"data-aut-id": "itemDetails"})
        nama_barang = a.find("span",{"data-aut-id": "itemTitle"})
        link = a.find("a",href=True)
        link = base_url+link['href']
        img = a.find("img")
        img = img['src']
        waktu = a.find("span",{"class": "zLvFQ"})
        waktu = waktu.find('span')
        deskripsi = a.find("span",{"data-aut-id": "itemDetails"})
        if deskripsi != None:
            deskripsi = deskripsi.text
        else:
            deskripsi=''
        lokasi = a.find("span",{"data-aut-id": "item-location"})
        like = ''
        products.append(make_product(nama_barang.text,harga.text,link,deskripsi,lokasi.text,img,waktu.text,like).serialize())
    return products

def set_product_from_session(data):
    products =[]
    for a in data:
        products.append(make_product(a.get('nama_barang'),a.get('harga_barang'),a.get('link_barang'),a.get('deskripsi'),a.get('lokasi_barang'),a.get('tanggal_barang'),a.get('image_url'),a.get('like')).serialize())
    return products

def get_product_by_api(keyword,url,code,search_by):
    keyword = str(keyword)
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
    products = []
    for a in data:
        nama_barang=a['title']
        if a['price'] != None:
            harga_barang=a['price']['value']['display']
        else:
            harga_barang=a['main_info']
        link = base_url+"/item/"+a['title'].replace(" ","-")+'-iid-'+a['id']
        deskripsi = a['description']

        lokasi = a['location_source']
        if lokasi != None:
            try:
                lokasi = json.loads(lokasi)
                lokasi = lokasi['name']
            except Exception:
                lokasi = ''   
        img = a['images'][0]['url']
        images = []
        for b in a['images']:
            images.append(b['url'])
        waktu = ''
        waktu = date(a)
        like = a['favorites']
        if like != None:
            like = a['favorites']['count']
        products.append(make_product(nama_barang,harga_barang,link,deskripsi,lokasi,img,waktu,like).serialize())
        # print(waktu)
    return products

def date(a):
    try:
        if a['republish_date'] != None:
            waktu = a['republish_date']
        else:
            waktu = a['created_at']
    except Exception :
        if a['display_date'] != None:
            waktu = a['display_date']
        else:
            waktu = a['created_at']
    waktu = datetime.datetime.fromisoformat(waktu)
    waktu = waktu.strftime(DATE_FORMAT)
    hari_ini = datetime.date.today()
    kemaren = hari_ini -datetime.timedelta(days=1)
    kemaren = kemaren.strftime(DATE_FORMAT)
    hari_ini = hari_ini.strftime(DATE_FORMAT)
    if(waktu == hari_ini ):
        waktu = 'hari ini'
    elif(waktu == kemaren):
        waktu = 'kemaren'
    return waktu

def search_by_category(request,category_code):
    category = get_category_url()
    url=''
    title = 'Result'
    for cat in category:
        if cat.code_category == category_code:
            url = cat.link_category
            title = cat.nama_category
            break
    search_product = request.POST.get('product')
    products = []
    jumlah_iklan =''
    next_page_url = ''
    page = ''
    print(url)
    if search_product == None:
        data = get_product_by_api(category_code,url,0,category_code) 
        page = requests.get(url, headers=URL_HEADERS)
        soup = BeautifulSoup(page.text, HTML_PARSER)
        if page.status_code==200:
            div = soup.findAll("li",{"data-aut-id": "itemBox"})
            products = set_product(div,URL_BASE_OLX)
    else:
        url = request.POST.get('next_page')
        data = get_product_by_api(category_code,url,1,category_code)
        products = set_product_by_api(data['data'],URL_BASE_OLX)   

    
    jumlah_iklan = data['metadata']['total_ads']
    next_page_url = data['metadata']['next_page_url']
    page = next_page_url.find('&category')
    hal = next_page_url.find(PAGE)+5
    print()
    if request.POST.get('next_page') != None:
        prev=int(next_page_url[hal:page])-2
        next_url = next_page_url[:hal]+str(prev)+next_page_url[hal+1:]
        prev_page_url = next_url
    else:
        prev_page_url = '#'

    page = next_page_url[hal:page]
    request.session['products'] = products
    context={
        'Products' : products,
        'Title' : title,
        'Iklan' : jumlah_iklan,
        'Next_Page' : next_page_url,
        'Previous_Page' : prev_page_url,
        'Page':page,
        'Category' : category
    }
    print(category_code)
    return render(request,INDEX,context)

def get_home_products():
    products_list =[]
    page = requests.get(URL_BASE_OLX, headers=URL_HEADERS)

    soup = BeautifulSoup(page.text, HTML_PARSER)
    
    if page.status_code==200:
        div = soup.findAll("li",{"data-aut-id": "itemBox"})
        products_list = set_product(div,URL_BASE_OLX)
    return products_list

def get_category_url():
    category =[]
    page = requests.get(URL_BASE_OLX, headers=URL_HEADERS)

    soup = BeautifulSoup(page.text, HTML_PARSER)
    if page.status_code==200:
        div = soup.findAll("div",{"class": "_3AGJR _18NX_"})
        for a in div:
            nama=a.find("span").text
            link = a.find("a",href=True)
            code = int(''.join(filter(str.isdigit, link['href'])))
            link = URL_BASE_OLX+link['href']
            category.append(make_category(code,nama,link))
    return category

def export_data_xls(request):
    category_code = 198
    category = get_category_url()
    url=''
    for cat in category:
        if cat.code_category == category_code:
            url = cat.link_category
            break
    products = []
    print(url)
    page = requests.get(url, headers=URL_HEADERS)
    soup = BeautifulSoup(page.text, HTML_PARSER)
    if page.status_code==200:
        div = soup.findAll("li",{"data-aut-id": "itemBox"})
        products = set_product(div,URL_BASE_OLX)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="data.xls"'

    if 'products' in request.session:
       print("ADA session nih")
       data_session = request.session['products']
       products = set_product_from_session(data_session)
    else:
        page = requests.get(url, headers=URL_HEADERS)
        soup = BeautifulSoup(page.text, HTML_PARSER)
        if page.status_code==200:
            div = soup.findAll("li",{"data-aut-id": "itemBox"})
            products = set_product(div,URL_BASE_OLX)
    print("check di atas")
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet('Users Data') # this will make a sheet named Users Data

    # Sheet header, first row
    row_num = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = ['nama barang', 'harga barang', 'link olx', 'deskripsi','lokasi', 'tanggal','jumlah like']

    for col_num in range(len(columns)):
        ws.write(row_num, col_num, columns[col_num], font_style) # at 0 row 0 column 

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()
  
    for product in products:
        row_num += 1
        for col_num in range(len(columns)):
            data = check_data_export(col_num,product)
            ws.write(row_num, col_num, data, font_style)

    wb.save(response)

    return response

def check_data_export(col_num,product):
    data =''
    if col_num == 0:
        data = product.nama_barang
    elif col_num ==1:
        data = product.harga_barang
    elif col_num ==2:
        data = product.link_barang
    elif col_num ==3:
        data = product.deskripsi
    elif col_num ==4:
        data = product.lokasi_barang
    elif col_num ==5:
        data = product.tanggal_barang
    elif col_num ==6:
        data = product.like
    return data   
