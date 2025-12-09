from django.db import models
from django.conf import settings
from django.utils import timezone
        
class Feature(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название опции")
    category = models.CharField(max_length=50, blank=True, verbose_name="Категория", help_text="Например: Салон, Комфорт, Безопасность")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Опция"
        verbose_name_plural = "Опции"

class Characteristic(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название характеристики")
    value = models.CharField(max_length=100, verbose_name="Значение")

    def __str__(self):
        return f"{self.name}: {self.value}"

    class Meta:
        verbose_name = "Характеристика"
        verbose_name_plural = "Характеристики"

class Car(models.Model):
    brand = models.CharField(max_length=50, verbose_name="Марка")
    model = models.CharField(max_length=50, verbose_name="Модель")
    generation = models.CharField(max_length=100, blank=True, verbose_name="Поколение")
    price = models.PositiveIntegerField(verbose_name="Цена (руб.)")
    year = models.PositiveSmallIntegerField(verbose_name="Год выпуска")
    mileage = models.PositiveIntegerField(verbose_name="Пробег (км)")
    color = models.CharField(max_length=30, verbose_name="Цвет")
    BODY_TYPE_CHOICES = [
        ('sedan', 'Седан'),
        ('suv', 'Внедорожник'),
        ('hatchback', 'Хэтчбек'),
        ('liftback', 'Лифтбек'),
        ('coupe', 'Купе'),
        ('estate', 'Универсал'),
        ('minivan', 'Минивэн'),
        ('pickup', 'Пикап'),
    ]
    COUNTRY_CHOICES = [
        ('japan', 'Япония'),
        ('germany', 'Германия'),
        ('korea', 'Корея'),
        ('usa', 'США'),
        ('france', 'Франция'),
        ('italy', 'Италия'),
        ('russia', 'Россия'),
        ('other', 'Другая'),
    ]
    country = models.CharField(max_length=10, choices=COUNTRY_CHOICES, default='other', verbose_name="Страна")
    
    body_type = models.CharField(max_length=10, choices=BODY_TYPE_CHOICES, verbose_name="Тип кузова")
    ENGINE_TYPE_CHOICES = [
        ('petrol', 'Бензин'),
        ('diesel', 'Дизель'),
        ('hybrid', 'Гибрид'),
        ('electro', 'Электро'),
    ]
    engine_type = models.CharField(max_length=10, choices=ENGINE_TYPE_CHOICES, verbose_name="Тип двигателя")
    engine_volume = models.FloatField(verbose_name="Объем двигателя (л)")
    engine_power = models.PositiveSmallIntegerField(verbose_name="Мощность (л.с.)")
    TRANSMISSION_CHOICES = [
        ('manual', 'Механическая'),
        ('automatic', 'Автоматическая'),
        ('robot', 'Роботизированная'),
        ('variator', 'Вариатор'),
    ]
    transmission = models.CharField(max_length=10, choices=TRANSMISSION_CHOICES, verbose_name="Коробка передач")
    DRIVE_CHOICES = [
        ('fwd', 'Передний'),
        ('rwd', 'Задний'),
        ('awd', 'Полный'),
    ]
    drive = models.CharField(max_length=3, choices=DRIVE_CHOICES, verbose_name="Привод")
    CONDITION_CHOICES = [
        ('excellent', 'Отличное'),
        ('good', 'Хорошее'),
        ('satisfactory', 'Удовлетворительное'),
    ]
    condition = models.CharField(max_length=15, choices=CONDITION_CHOICES, default='good', verbose_name="Состояние")
    owners = models.PositiveSmallIntegerField(default=1, verbose_name="Количество владельцев")
    documents = models.CharField(max_length=100, default="Без ограничений", verbose_name="Документы")
    steering = models.CharField(max_length=10, choices=[('left', 'Левый'), ('right', 'Правый')], default='left', verbose_name="Руль")
    description = models.TextField(blank=True, verbose_name="Описание")
    features = models.ManyToManyField(Feature, blank=True, verbose_name="Опции и комплектации")
    characteristics = models.ManyToManyField(Characteristic, blank=True, verbose_name="Дополнительные характеристики")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")
    is_sold = models.BooleanField(default=False, verbose_name="Продано")
    is_published = models.BooleanField(default=True, verbose_name="Опубликовано")

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year}), {self.price} руб."

    class Meta:
        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"
    
class CarPhoto(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='photos', verbose_name="Автомобиль")
    image = models.ImageField(upload_to='car_photos/', verbose_name="Фотография")
    is_main = models.BooleanField(default=False, verbose_name="Главная фотография")
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name="Дата добавления")
    def __str__(self):
        return f"Фото {self.car.brand} {self.car.model}"

    class Meta:
        verbose_name = "Фотография автомобиля"
        verbose_name_plural = "Фотографии автомобилей"

class PurchaseAgreementRequest(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name="Автомобиль")
    
    buyer_full_name = models.CharField(max_length=200, verbose_name="ФИО покупателя")
    buyer_passport_series = models.CharField(max_length=4, verbose_name="Серия паспорта")
    buyer_passport_number = models.CharField(max_length=6, verbose_name="Номер паспорта")
    buyer_passport_issued = models.TextField(verbose_name="Кем и когда выдан паспорт")
    buyer_registration_address = models.TextField(verbose_name="Адрес регистрации")
    buyer_phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон покупателя")
    
    seller_full_name = models.CharField(max_length=200, verbose_name="ФИО продавца")
    seller_passport_series = models.CharField(max_length=4, verbose_name="Серия паспорта продавца")
    seller_passport_number = models.CharField(max_length=6, verbose_name="Номер паспорта продавца")
    seller_passport_issued = models.TextField(verbose_name="Кем и когда выдан паспорт продавца")
    seller_registration_address = models.TextField(verbose_name="Адрес регистрации продавца")
    seller_phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон продавца")
    
    car_brand = models.CharField(max_length=50, verbose_name="Марка автомобиля")
    car_model = models.CharField(max_length=50, verbose_name="Модель автомобиля")
    car_year = models.PositiveSmallIntegerField(verbose_name="Год выпуска")
    car_vin = models.CharField(max_length=17, blank=True, verbose_name="VIN номер")
    car_license_plate = models.CharField(max_length=9, blank=True, verbose_name="Гос номер")
    car_price = models.PositiveIntegerField(verbose_name="Цена автомобиля")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")

    def __str__(self):
        return f"Договор для {self.buyer_full_name} - {self.car_brand} {self.car_model}"

    class Meta:
        verbose_name = "Заявка на договор"
        verbose_name_plural = "Заявки на договоры"

class InspectionRequest(models.Model):
    TIME_SLOTS = [
        ('09:00-10:00', '09:00 - 10:00'),
        ('10:00-11:00', '10:00 - 11:00'),
        ('11:00-12:00', '11:00 - 12:00'),
        ('12:00-13:00', '12:00 - 13:00'),
        ('13:00-14:00', '13:00 - 14:00'),
        ('14:00-15:00', '14:00 - 15:00'),
        ('15:00-16:00', '15:00 - 16:00'),
        ('16:00-17:00', '16:00 - 17:00'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Ожидает подтверждения'),
        ('confirmed', 'Подтверждена'),
        ('cancelled', 'Отменена'),
        ('completed', 'Завершена'),
    ]

    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name='Автомобиль')
    full_name = models.CharField(max_length=200, verbose_name='ФИО клиента')
    phone = models.CharField(max_length=20, verbose_name='Телефон')
    email = models.EmailField(blank=True, verbose_name='Email')
    inspection_date = models.DateField(verbose_name='Дата осмотра')
    inspection_time = models.CharField(max_length=20, choices=TIME_SLOTS, verbose_name='Время осмотра')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='Статус')
    notes = models.TextField(blank=True, verbose_name='Примечания администратора')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата создания')
    
    class Meta:
        verbose_name = 'Заявка на осмотр'
        verbose_name_plural = 'Заявки на осмотр'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.full_name} - {self.car.brand} {self.car.model} - {self.inspection_date} {self.inspection_time}"
    
    def is_time_slot_available(self):
        return not InspectionRequest.objects.filter(
            inspection_date=self.inspection_date,
            inspection_time=self.inspection_time,
            status__in=['pending', 'confirmed']
        ).exclude(id=self.id).exists()