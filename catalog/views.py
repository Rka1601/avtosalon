from django.shortcuts import render, get_object_or_404, redirect
from django.conf import settings
from django.http import HttpResponse
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Car, PurchaseAgreementRequest, InspectionRequest
from .forms import PurchaseAgreementForm, InspectionRequestForm, CarPhotoUploadForm
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from .forms import CarFilterForm
from io import BytesIO
import os
from django.db.models import Q
import random
from django.http import JsonResponse
from PyPDF2 import PdfReader, PdfWriter
import datetime

def index(request):
    all_cars = list(Car.objects.filter(is_published=True, is_sold=False))
    random_cars = random.sample(all_cars, min(6, len(all_cars)))
    
    quick_filters = [
        {
            'title': 'До 1 млн ₽',
            'description': 'Бюджетные автомобили',
            'url': '/catalog/?max_price=1000000',
            'button_text': 'Смотреть'
        },
        {
            'title': 'Японские авто',
            'description': 'Toyota, Nissan, Honda',
            'url': '/catalog/?country=japan',
            'button_text': 'Смотреть'
        },
        {
            'title': 'Пробег до 50к',
            'description': 'Почти новые',
            'url': '/catalog/?max_mileage=50000',
            'button_text': 'Смотреть'
        },
        {
            'title': 'Немецкие авто',
            'description': 'BMW, Mercedes, Audi',
            'url': '/catalog/?country=germany',
            'button_text': 'Смотреть'
        },
        {
            'title': 'Автомат',
            'description': 'Комфорт в городе',
            'url': '/catalog/?transmission=automatic',
            'button_text': 'Смотреть'
        },
        {
            'title': 'Внедорожники',
            'description': 'SUV и кроссоверы',
            'url': '/catalog/?body_type=suv',
            'button_text': 'Смотреть'
        },
        {
            'title': '2020+ год',
            'description': 'Современные модели',
            'url': '/catalog/?min_year=2020',
            'button_text': 'Смотреть'
        },
        {
            'title': 'Эконом-класс',
            'description': 'До 500 тыс. руб.',
            'url': '/catalog/?max_price=500000',
            'button_text': 'Смотреть'
        }
    ]
    
    return render(request, 'catalog/index.html', {
        'random_cars': random_cars,
        'showroom_phone': settings.SHOWROOM_PHONE,
        'quick_filters': quick_filters
    })

def car_list(request):
    cars = Car.objects.filter(is_published=True, is_sold=False)
    

    filter_form = CarFilterForm(request.GET or None)
    

    max_price = request.GET.get('max_price')
    min_year = request.GET.get('min_year')
    max_mileage = request.GET.get('max_mileage')
    brand = request.GET.get('brand')
    transmission = request.GET.get('transmission')
    body_type = request.GET.get('body_type')
    brands = request.GET.getlist('brand') 
    
    if brands:
        cars = cars.filter(brand__in=brands)
    

    if max_price:
        cars = cars.filter(price__lte=int(max_price))
    if min_year:
        cars = cars.filter(year__gte=int(min_year))
    if max_mileage:
        cars = cars.filter(mileage__lte=int(max_mileage))
    if brand:
        cars = cars.filter(brand=brand)
    if transmission:
        cars = cars.filter(transmission=transmission)
    if body_type:
        cars = cars.filter(body_type=body_type)
    

    if filter_form.is_valid():
        brand_form = filter_form.cleaned_data.get('brand')
        model = filter_form.cleaned_data.get('model')
        min_price_form = filter_form.cleaned_data.get('min_price')
        max_price_form = filter_form.cleaned_data.get('max_price')
        year_range = filter_form.cleaned_data.get('year_range')
        transmission_form = filter_form.cleaned_data.get('transmission')
        engine_type = filter_form.cleaned_data.get('engine_type')
        features = filter_form.cleaned_data.get('features')
        sort = filter_form.cleaned_data.get('sort') or '-created_at'
        country = request.GET.get('country')
        

        if brand_form and not brand: 
            cars = cars.filter(brand=brand_form)

        if country:
            cars = cars.filter(country=country)
        

        if model:
            cars = cars.filter(model=model)
        

        if min_price_form:
            cars = cars.filter(price__gte=min_price_form)
        if max_price_form:
            cars = cars.filter(price__lte=max_price_form)
        

        if year_range:
            if year_range == '2020-':
                cars = cars.filter(year__gte=2020)
            elif year_range == '2015-2019':
                cars = cars.filter(year__range=(2015, 2019))
            elif year_range == '2010-2014':
                cars = cars.filter(year__range=(2010, 2014))
            elif year_range == '-2009':
                cars = cars.filter(year__lte=2009)
        

        if transmission_form and not transmission:
            cars = cars.filter(transmission=transmission_form)
        

        if engine_type:
            cars = cars.filter(engine_type=engine_type)
        

        if features:
            cars = cars.filter(features__in=features).distinct()
        

        cars = cars.order_by(sort)
    else:

        cars = cars.order_by('-created_at')
    

    paginator = Paginator(cars, 12)
    page = request.GET.get('page')
    try:
        cars = paginator.page(page)
    except PageNotAnInteger:
        cars = paginator.page(1)
    except EmptyPage:
        cars = cars.page(paginator.num_pages)
    
    return render(request, 'catalog/car_list.html', {
        'cars': cars,
        'filter_form': filter_form
    })
    
def upload_car_photos(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    
    if request.method == 'POST':
        form = CarPhotoUploadForm(request.POST, request.FILES)
        if form.is_valid():
            form.save_photos(car)
            return redirect('car_detail', car_id=car.id)
    else:
        form = CarPhotoUploadForm()
    
    return render(request, 'catalog/upload_photos.html', {
        'form': form,
        'car': car
    })

def get_models(request):
    brand = request.GET.get('brand', '')
    if brand:
        models = Car.objects.filter(brand=brand, is_published=True, is_sold=False) \
                          .values_list('model', flat=True) \
                          .distinct() \
                          .order_by('model')
        return JsonResponse({'models': list(models)})
    return JsonResponse({'models': []})

def car_detail(request, car_id):
    car = get_object_or_404(Car, id=car_id, is_published=True)
    context = {
        'car': car,
        'showroom_phone': settings.SHOWROOM_PHONE
    }
    return render(request, 'catalog/car_detail.html', context)

def get_russian_font():
    try:

        font_path_regular = os.path.join(settings.BASE_DIR, 'catalog', 'static', 'fonts', 'times.ttf')
        font_path_bold = os.path.join(settings.BASE_DIR, 'catalog', 'static', 'fonts', 'timesbd.ttf')
        

        if os.path.exists(font_path_regular):
            pdfmetrics.registerFont(TTFont('Times-Roman', font_path_regular))
        

        if os.path.exists(font_path_bold):
            pdfmetrics.registerFont(TTFont('Times-Bold', font_path_bold))
            
        return 'Times-Roman'
        
    except Exception as e:
        print(f"Ошибка регистрации шрифта: {e}")
    
    return 'Helvetica'

def purchase_agreement(request, car_id):
    car = get_object_or_404(Car, id=car_id, is_published=True)
    
    if request.method == 'POST':
        form = PurchaseAgreementForm(request.POST)
        if form.is_valid():
            try:
                agreement = form.save(commit=False)
                agreement.car = car
                
                agreement.seller_full_name = settings.SELLER_INFO['full_name']
                agreement.seller_passport_series = settings.SELLER_INFO['passport_series']
                agreement.seller_passport_number = settings.SELLER_INFO['passport_number']
                agreement.seller_passport_issued = settings.SELLER_INFO['passport_issued']
                agreement.seller_registration_address = settings.SELLER_INFO['registration_address']
                
                agreement.car_brand = car.brand
                agreement.car_model = car.model
                agreement.car_year = car.year
                agreement.car_price = car.price
                
                agreement.save()
                
                return generate_agreement_pdf(agreement)
                
            except Exception as e:
                return HttpResponse(f"Ошибка при создании договора: {str(e)}")
    else:
        form = PurchaseAgreementForm()
    
    return render(request, 'catalog/purchase_agreement.html', {
        'form': form,
        'car': car
    })

def generate_agreement_pdf(agreement):
    try:
        template_path = os.path.join(settings.BASE_DIR, 'catalog', 'static', 'dkp.pdf')
        
        if not os.path.exists(template_path):
            return generate_simple_agreement_pdf(agreement)
        
        buffer = BytesIO()
        
        reader = PdfReader(template_path)
        writer = PdfWriter()
        
        page = reader.pages[0]
        
        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=A4)
        
        font_name = get_russian_font()
        can.setFont(font_name, 10)
        
        can.drawString(40, 743, agreement.seller_full_name)
        can.drawString(40, 722, f"Паспорт: {agreement.seller_passport_series} {agreement.seller_passport_number}")
        can.drawString(40, 700, f"Выдан: {agreement.seller_passport_issued}")
        can.drawString(40, 679, f"Адрес: {agreement.seller_registration_address}")
        
        can.drawString(40, 640, agreement.buyer_full_name)
        can.drawString(40, 618, f"Паспорт: {agreement.buyer_passport_series} {agreement.buyer_passport_number}")
        can.drawString(40, 597, f"Выдан: {agreement.buyer_passport_issued}")
        can.drawString(40, 576, f"Адрес: {agreement.buyer_registration_address}")
        
        can.drawString(40, 475, f"{agreement.car_brand} {agreement.car_model}")
        can.drawString(50, 454, agreement.car_vin or "не указан")
        can.drawString(410, 454, str(agreement.car_year))
        
        car_color = agreement.car.color if hasattr(agreement.car, 'color') and agreement.car.color else 'не указан'
        can.drawString(250, 410, car_color)
        
        can.drawString(250, 454, agreement.car_license_plate or "не указан")
        
        can.drawString(55, 303, f"{agreement.car_price:,} руб.".replace(',', ' '))
        can.drawString(200, 303, num2words(agreement.car_price) + " рублей")
        
        can.drawString(240, 809, "Барнаул")
        can.drawString(285, 809, timezone.now().strftime('%d.%m.%Y'))
        
        can.save()
        
        packet.seek(0)
        new_pdf = PdfReader(packet)
        
        page.merge_page(new_pdf.pages[0])
        writer.add_page(page)
        
        writer.write(buffer)
        buffer.seek(0)
        
        response = HttpResponse(buffer, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="dogovor-kupli-prodazhi-{agreement.car_brand}-{agreement.car_model}.pdf"'
        return response
        
    except Exception as e:
        return generate_simple_agreement_pdf(agreement)

def generate_simple_agreement_pdf(agreement):
    buffer = BytesIO()
    p = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    
    font_name = get_russian_font()
    
    y_position = height - 50
    line_height = 14

    p.setFont('Times-Bold', 16)
    p.drawCentredString(width/2, y_position, "ДОГОВОР КУПЛИ-ПРОДАЖИ АВТОМОБИЛЯ")
    y_position -= 40
    

    p.setFont('Times-Roman', 12)
    p.drawString(100, y_position, "Город Барнаул")
    p.drawString(250, y_position, f"{timezone.now().strftime('%d.%m.%Y')} г.")
    y_position -= 40
    

    p.drawString(50, y_position, f"Продавец: {agreement.seller_full_name}")
    y_position -= line_height
    p.drawString(50, y_position, f"Паспорт: {agreement.seller_passport_series} № {agreement.seller_passport_number}")
    y_position -= line_height
    p.drawString(50, y_position, f"Выдан: {agreement.seller_passport_issued}")
    y_position -= line_height
    p.drawString(50, y_position, f"Адрес: {agreement.seller_registration_address}")
    y_position -= line_height * 2
    
    p.drawString(50, y_position, f"Покупатель: {agreement.buyer_full_name}")
    y_position -= line_height
    p.drawString(50, y_position, f"Паспорт: {agreement.buyer_passport_series} № {agreement.buyer_passport_number}")
    y_position -= line_height
    p.drawString(50, y_position, f"Выдан: {agreement.buyer_passport_issued}")
    y_position -= line_height
    p.drawString(50, y_position, f"Адрес: {agreement.buyer_registration_address}")
    y_position -= line_height * 2
    

    p.drawString(50, y_position, f"Автомобиль: {agreement.car_brand} {agreement.car_model}, {agreement.car_year} г.в.")
    y_position -= line_height
    p.drawString(50, y_position, f"VIN: {agreement.car_vin or 'не указан'}")
    y_position -= line_height
    p.drawString(50, y_position, f"Госномер: {agreement.car_license_plate or 'не указан'}")
    y_position -= line_height
    p.drawString(50, y_position, f"Стоимость: {agreement.car_price:,} руб. ({num2words(agreement.car_price)} рублей)".replace(',', ' '))
    y_position -= line_height * 2
    

    p.drawString(50, y_position, "Продавец: _________________________")
    y_position -= line_height
    p.drawString(50, y_position, f"Ф.И.О.: {agreement.seller_full_name}")
    y_position -= line_height * 2
    
    p.drawString(50, y_position, "Покупатель: _________________________")
    y_position -= line_height
    p.drawString(50, y_position, f"Ф.И.О.: {agreement.buyer_full_name}")
    
    p.showPage()
    p.save()
    
    buffer.seek(0)
    response = HttpResponse(buffer, content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="dogovor-kupli-prodazhi-{agreement.car_brand}-{agreement.car_model}.pdf"'
    return response

def num2words(num, lang='ru'):
    """Функция для преобразования числа в слова (упрощенная версия)"""
    if num == 0:
        return 'ноль'
    

    units = ['', 'один', 'два', 'три', 'четыре', 'пять', 'шесть', 'семь', 'восемь', 'девять']
    teens = ['десять', 'одиннадцать', 'двенадцать', 'тринадцать', 'четырнадцать', 'пятнадцать', 
             'шестнадцать', 'семнадцать', 'восемнадцать', 'девятнадцать']
    tens = ['', '', 'двадцать', 'тридцать', 'сорок', 'пятьдесят', 'шестьдесят', 'семьдесят', 'восемьдесят', 'девяносто']
    hundreds = ['', 'сто', 'двести', 'триста', 'четыреста', 'пятьсот', 'шестьсот', 'семьсот', 'восемьсот', 'девятьсот']
    
    def convert_triplet(n):
        """Конвертирует трехзначное число"""
        result = []
        

        if n >= 100:
            result.append(hundreds[n // 100])
            n %= 100
        

        if n >= 20:
            result.append(tens[n // 10])
            if n % 10 > 0:
                result.append(units[n % 10])
        elif n >= 10:
            result.append(teens[n - 10])
        elif n > 0:
            result.append(units[n])
        
        return ' '.join(result)
    
    result_parts = []
    n = num
    

    if n >= 1000000:
        millions_part = n // 1000000
        result_parts.append(convert_triplet(millions_part))
        result_parts.append('миллионов')
        n %= 1000000
    

    if n >= 1000:
        thousands_part = n // 1000
        result_parts.append(convert_triplet(thousands_part))
        result_parts.append('тысяч')
        n %= 1000
    

    if n > 0:
        result_parts.append(convert_triplet(n))
    
    return ' '.join(result_parts)

def inspection_request(request, car_id):
    """Запись на осмотр автомобиля"""
    car = get_object_or_404(Car, id=car_id, is_published=True)
    
    if request.method == 'POST':
        form = InspectionRequestForm(request.POST)
        if form.is_valid():
            inspection_request = form.save(commit=False)
            inspection_request.car = car
            

            if not inspection_request.is_time_slot_available():
                form.add_error('inspection_time', 'Это время уже занято. Пожалуйста, выберите другое время.')
            else:
                inspection_request.save()
                return render(request, 'catalog/inspection_success.html', {
                    'car': car,
                    'inspection_request': inspection_request
                })
    else:
        form = InspectionRequestForm()
    
    return render(request, 'catalog/inspection_request.html', {
        'form': form,
        'car': car
    })

def get_available_times(request):
    """API для получения доступных временных слотов"""
    date = request.GET.get('date')
    if date:
        try:
            selected_date = datetime.datetime.strptime(date, '%Y-%m-%d').date()

            busy_times = InspectionRequest.objects.filter(
                inspection_date=selected_date,
                status__in=['pending', 'confirmed']
            ).values_list('inspection_time', flat=True)
            
            all_times = [choice[0] for choice in InspectionRequest.TIME_SLOTS]
            available_times = [time for time in all_times if time not in busy_times]
            
            return JsonResponse({'available_times': available_times})
        except ValueError:
            pass
    
    return JsonResponse({'available_times': []})