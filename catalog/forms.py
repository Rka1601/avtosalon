from django import forms
from django.core.validators import RegexValidator
from .models import PurchaseAgreementRequest, Car, Feature, InspectionRequest
from django.core.exceptions import ValidationError
import re
from django.utils import timezone
import datetime

class PurchaseAgreementForm(forms.ModelForm):
    features = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Feature.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Опции'
    )

    seller_phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': '+7 (999) 123-45-67',
            'data-mask': '+7 (000) 000-00-00'
        }),
        label='Телефон продавца'
    )
    
    buyer_phone = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': '+7 (999) 123-45-67',
            'data-mask': '+7 (000) 000-00-00'
        }),
        label='Телефон покупателя'
    )
    
    class Meta:
        model = PurchaseAgreementRequest
        fields = [
            'buyer_full_name', 'buyer_passport_series', 'buyer_passport_number',
            'buyer_passport_issued', 'buyer_registration_address',
            'car_vin', 'car_license_plate',
            'seller_phone', 'buyer_phone'
        ]
        widgets = {
            'buyer_full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Иванов Иван Иванович'}),
            'buyer_passport_series': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '1234',
                'data-mask': '0000',
                'maxlength': '4'
            }),
            'buyer_passport_number': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': '567890',
                'data-mask': '000000',
                'maxlength': '6'
            }),
            'buyer_passport_issued': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'ОУФМС России по г. Москве, 01.01.2010',
                'rows': 2
            }),
            'buyer_registration_address': forms.Textarea(attrs={
                'class': 'form-control', 
                'placeholder': 'г. Москва, ул. Примерная, д. 1, кв. 1',
                'rows': 2
            }),
            'car_vin': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'XTA210990Y2765432',
                'data-mask': '_________________',
                'maxlength': '17'
            }),
            'car_license_plate': forms.TextInput(attrs={
                'class': 'form-control', 
                'placeholder': 'А123BC777 или А123BC77',
                'data-mask': 'license-plate',
                'maxlength': '12' 
            }),
        }
        labels = {
            'buyer_full_name': 'ФИО покупателя',
            'buyer_passport_series': 'Серия паспорта',
            'buyer_passport_number': 'Номер паспорта',
            'buyer_passport_issued': 'Кем и когда выдан паспорт',
            'buyer_registration_address': 'Адрес регистрации',
            'car_vin': 'VIN номер',
            'car_license_plate': 'Государственный номер',
        }
    
    def clean_car_vin(self):
        vin = self.cleaned_data.get('car_vin', '').strip().upper()
        if vin:
            if len(vin) != 17:
                raise ValidationError('VIN номер должен содержать 17 символов')
            
            if not re.match(r'^[A-HJ-NPR-Z0-9]{17}$', vin):
                raise ValidationError('VIN номер содержит недопустимые символы. Нельзя использовать I, O, Q')
        
        return vin
    
    def clean_car_license_plate(self):
        license_plate = self.cleaned_data.get('car_license_plate', '').replace(' ', '').strip().upper()
        if license_plate:
            if not re.match(r'^[АВЕКМНОРСТУХABEKMHOPCTYX]{1}\d{3}[АВЕКМНОРСТУХABEKMHOPCTYX]{2}\d{2,3}$', license_plate):
                raise ValidationError('Неверный формат госномера. Пример: А123BC777 или А123BC77')
        
        return license_plate
    
    def clean_buyer_passport_series(self):
        series = self.cleaned_data.get('buyer_passport_series', '').strip()
        if series and not series.isdigit():
            raise ValidationError('Серия паспорта должна содержать только цифры')
        return series
    
    def clean_buyer_passport_number(self):
        number = self.cleaned_data.get('buyer_passport_number', '').strip()
        if number and not number.isdigit():
            raise ValidationError('Номер паспорта должен содержать только цифры')
        return number

class CarFilterForm(forms.Form):
    min_price = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Мин. цена',
            'min': '0'
        }),
        label='Цена от'
    )
    
    max_price = forms.IntegerField(
        required=False,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': 'Макс. цена',
            'min': '0'
        }),
        label='Цена до'
    )
    
    YEAR_CHOICES = [
        ('', 'Любой год'),
        ('2020-', '2020 и новее'),
        ('2015-2019', '2015-2019'),
        ('2010-2014', '2010-2014'),
        ('-2009', '2009 и старше'),
    ]
    
    brand = forms.ChoiceField(
        required=False,
        choices=[('', 'Любая марка')],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'brand-select'
        }),
        label='Марка'
    )
    
    model = forms.ChoiceField(
        required=False,
        choices=[('', 'Любая модель')],
        widget=forms.Select(attrs={
            'class': 'form-select',
            'id': 'model-select',
            'disabled': 'disabled'
        }),
        label='Модель'
    )
    
    year_range = forms.ChoiceField(
        required=False,
        choices=YEAR_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Год выпуска'
    )
    
    transmission = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Любая'),
            ('manual', 'Механическая'),
            ('automatic', 'Автоматическая'),
            ('robot', 'Роботизированная'),
            ('variator', 'Вариатор')
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Коробка передач'
    )
    
    engine_type = forms.ChoiceField(
        required=False,
        choices=[
            ('', 'Любой'),
            ('petrol', 'Бензин'),
            ('diesel', 'Дизель'),
            ('hybrid', 'Гибрид'),
            ('electro', 'Электро')
        ],
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Тип двигателя'
    )
    features = forms.ModelMultipleChoiceField(
        required=False,
        queryset=Feature.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        label='Опции'
    )

    COUNTRY_CHOICES = [
        ('', 'Любая страна'),
        ('japan', 'Япония'),
        ('germany', 'Германия'),
        ('korea', 'Корея'),
        ('usa', 'США'),
        ('france', 'Франция'),
        ('italy', 'Италия'),
        ('russia', 'Россия'),
    ]
    
    country = forms.ChoiceField(
        required=False,
        choices=COUNTRY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Страна'
    )

    SORT_CHOICES = [
        ('-created_at', 'Сначала новые'),
        ('price', 'Цена по возрастанию'),
        ('-price', 'Цена по убыванию'),
        ('year', 'Год по возрастанию'),
        ('-year', 'Год по убыванию'),
        ('mileage', 'Пробег по возрастанию'),
        ('-mileage', 'Пробег по убыванию'),
    ]
    
    sort = forms.ChoiceField(
        required=False,
        choices=SORT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        label='Сортировка'
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        brands = Car.objects.filter(is_published=True, is_sold=False) \
                          .values_list('brand', flat=True) \
                          .distinct() \
                          .order_by('brand')
        
        brand_choices = [('', 'Любая марка')] + [(brand, brand) for brand in brands]
        self.fields['brand'].choices = brand_choices
        
        selected_brand = self.data.get('brand') if self.data else None
        if selected_brand:
            models = Car.objects.filter(brand=selected_brand, is_published=True, is_sold=False) \
                              .values_list('model', flat=True) \
                              .distinct() \
                              .order_by('model')
            model_choices = [('', 'Любая модель')] + [(model, model) for model in models]
            self.fields['model'].choices = model_choices
            self.fields['model'].widget.attrs.pop('disabled', None)

class InspectionRequestForm(forms.ModelForm):
    phone = forms.CharField(
        max_length=20,
        validators=[
            RegexValidator(
                regex=r'^(\+7|8)?[\s\-]?\(?[489][0-9]{2}\)?[\s\-]?[0-9]{3}[\s\-]?[0-9]{2}[\s\-]?[0-9]{2}$',
                message='Введите корректный номер телефона'
            )
        ],
        widget=forms.TextInput(attrs={
            'placeholder': '+7 (999) 999-99-99',
            'class': 'form-control',
            'data-mask': '+7 (999) 999-99-99'
        })
    )
    
    class Meta:
        model = InspectionRequest
        fields = ['full_name', 'phone', 'email', 'inspection_date', 'inspection_time']
        widgets = {
            'inspection_date': forms.DateInput(attrs={
                'type': 'date', 
                'min': datetime.date.today().strftime('%Y-%m-%d'),
                'class': 'form-control'
            }),
            'full_name': forms.TextInput(attrs={
                'placeholder': 'Введите ваше ФИО',
                'class': 'form-control'
            }),
            'email': forms.EmailInput(attrs={
                'placeholder': 'email@example.com',
                'class': 'form-control'
            }),
            'inspection_time': forms.Select(attrs={'class': 'form-control'})
        }
        labels = {
            'full_name': 'ФИО *',
            'phone': 'Телефон *',
            'email': 'Email',
            'inspection_date': 'Дата осмотра *',
            'inspection_time': 'Время осмотра *',
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        today = datetime.date.today()
        self.fields['inspection_date'].widget.attrs['min'] = today.strftime('%Y-%m-%d')
        
    def clean_inspection_date(self):
        date = self.cleaned_data['inspection_date']
        if date < datetime.date.today():
            raise forms.ValidationError("Нельзя выбрать прошедшую дату")
        
        if date.weekday() >= 5:
            raise forms.ValidationError("Автосалон не работает по выходным. Пожалуйста, выберите будний день.")
            
        return date
    
    def clean_phone(self):
        phone = self.cleaned_data['phone']
        phone = re.sub(r'[^\d]', '', phone)
        
        if phone.startswith('8'):
            phone = '7' + phone[1:]
        elif not phone.startswith('7'):
            phone = '7' + phone
            
        if len(phone) != 11:
            raise forms.ValidationError("Номер телефона должен содержать 11 цифр")
            
        return f"+7 ({phone[1:4]}) {phone[4:7]}-{phone[7:9]}-{phone[9:11]}"
    
    def clean(self):
        cleaned_data = super().clean()
        inspection_date = cleaned_data.get('inspection_date')
        inspection_time = cleaned_data.get('inspection_time')
        
        if inspection_date and inspection_time:
            conflicting_requests = InspectionRequest.objects.filter(
                inspection_date=inspection_date,
                inspection_time=inspection_time,
                status__in=['pending', 'confirmed']
            )
            
            if conflicting_requests.exists():
                raise forms.ValidationError(
                    f"❌ Это время уже занято. Доступные времена на {inspection_date}: " +
                    self.get_available_times(inspection_date)
                )
        
        return cleaned_data
    
    def get_available_times(self, date):
        busy_times = InspectionRequest.objects.filter(
            inspection_date=date,
            status__in=['pending', 'confirmed']
        ).values_list('inspection_time', flat=True)
        
        all_times = [choice[0] for choice in InspectionRequest.TIME_SLOTS]
        available_times = [time for time in all_times if time not in busy_times]
        
        if available_times:
            return ", ".join(available_times)
        else:
            return "На эту дату нет свободного времени"
class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class CarPhotoUploadForm(forms.Form):
    images = MultipleFileField(
        required=False,
        label="Загрузить несколько фотографий"
    )

    def save_photos(self, car):
        images = self.files.getlist('images')
        for image in images:
            CarPhoto.objects.create(car=car, image=image)