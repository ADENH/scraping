from logging import exception
from django.shortcuts import render
from django.http import HttpResponse
from bs4 import BeautifulSoup
import requests
from .models import Category, Product, make_category, make_product
import json
import datetime
import xlwt
from django.contrib.auth.decorators import login_required

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
        'Category': categoy_list,
        'Category_Code' : '0'
    } 
    return render(request,INDEX,context)

def set_product(div,base_url):
    products = []
    for a in div:
        harga =''
        harga_price = a.find("span",{"data-aut-id": "itemPrice"})
        harga_details =  a.find("span",{"data-aut-id": "itemDetails"})
        if harga_details == None and harga_price == None:
            harga=''
        elif harga_price != None:
            harga = harga_price.text
        elif harga_details != None:
            harga = harga_details.text

        nama_barang = a.find("span",{"data-aut-id": "itemTitle"})
        link = a.find("a",href=True)
        link = base_url+link['href']
        img = a.find("img")
        img = img['src']
        waktu = a.find("span",{"class": "zLvFQ"})
        waktu = waktu.find('span')
        if waktu != None:
            waktu = waktu.text
        else:
            waktu = None
        deskripsi = a.find("span",{"data-aut-id": "itemDetails"})
        if deskripsi != None:
            deskripsi = deskripsi.text
        else:
            deskripsi=''
        lokasi = a.find("span",{"data-aut-id": "item-location"})
        if lokasi == None:
            lokasi =''
        else:
            lokasi = lokasi.text
        like = 0
        products.append(make_product(nama_barang.text,harga,link,deskripsi,lokasi,img,waktu,like).serialize())
    return products

def set_product_from_session(data):
    products =[]
    for a in data:
        waktu = a.get('tanggal_barang')
        if waktu == 'Hari ini':
            waktu = datetime.datetime.now().astimezone().replace(microsecond=0).isoformat()
            print(waktu)
        products.append(make_product(a.get('nama_barang'),a.get('harga_barang'),a.get('link_barang'),a.get('deskripsi'),a.get('lokasi_barang'),a.get('image_url'),waktu,a.get('like')).serialize())
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

        lokasi =''
        try:
            lokasi = a['location_source']
        except Exception:
            lokasi = a['locations_resolved']['ADMIN_LEVEL_1_name'] 
        
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
        waktu = tanggal_barang(a)
        like = a['favorites']
        if like != None:
            like = a['favorites']['count']
        products.append(make_product(nama_barang,harga_barang,link,deskripsi,lokasi,img,waktu,like).serialize())
        # print(waktu)
    return products

def tanggal_barang(a):
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
    if request.POST.get('next_page') != None:
        prev=int(next_page_url[hal:page])-2
        next_url = next_page_url[:hal]+str(prev)+next_page_url[hal+1:]
        prev_page_url = next_url
    else:
        prev_page_url = '#'

    page = next_page_url[hal:page]
    request.session['products'] = products
    request.session['next_page_url'] = next_page_url
    context={
        'Products' : products,
        'Title' : title,
        'Iklan' : jumlah_iklan,
        'Next_Page' : next_page_url,
        'Previous_Page' : prev_page_url,
        'Page':page,
        'Category' : category,
        'Category_Code' : category_code
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

@login_required
def export_data_xls(request,category_code,data):
    category = get_category_url()
    url=''
    for cat in category:
        if cat.code_category == category_code:
            url = cat.link_category
            break
    products = []
    print(url)
    response = HttpResponse(content_type='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="data.xls"'

    search_product = request.POST.get('product')
    data_session = request.session['products']
    next_page_url = request.session['next_page_url']
    
    if 'products' in request.session and data == 20:
        products = set_product_from_session(data_session)
    elif data == 0:
        products = set_product_from_session(data_session)
        if search_product != None:
            url = 'https://www.olx.co.id/items/q-' + search_product
            list_product = get_product_by_api(search_product,url,0,category)
        else:
            list_product = get_product_by_api(category_code,next_page_url,1,category_code)
        
        while next_page_url != None:
            products_by_api = set_product_by_api(list_product['data'],URL_BASE_OLX)
            products = products + products_by_api
            try:
                next_page_url = list_product['metadata']['next_page_url']
            except Exception:
                break

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
        data = product.get('nama_barang')
    elif col_num ==1:
        data = product.get('harga_barang')
    elif col_num ==2:
        data = product.get('link_barang')
    elif col_num ==3:
        data = product.get('deskripsi')
    elif col_num ==4:
        data = product.get('lokasi_barang')
    elif col_num ==5:
        data = product.get('tanggal_barang')
    elif col_num ==6:
        data = product.get('like')
    return data   
