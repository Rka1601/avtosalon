from django.contrib import admin
from .models import Car, Feature,CarPhoto, Characteristic, InspectionRequest

class CarPhotoInline(admin.TabularInline):
    model = CarPhoto
    extra = 3 
    fields = ('image', 'is_main')
    max_num = 20 
@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    inlines = [CarPhotoInline]
    list_display = ('brand', 'model', 'year', 'price', 'country', 'is_sold', 'is_published')
    list_filter = ('brand', 'year', 'country', 'is_sold', 'is_published')
    search_fields = ('brand', 'model', 'vin')
    list_editable = ('price', 'is_sold', 'is_published')
    filter_horizontal = ('features', 'characteristics')
    def save_model(self, request, obj, form, change):
        japanese_brands = ['Toyota', 'Nissan', 'Honda', 'Mazda', 'Subaru', 'Mitsubishi', 'Suzuki']
        german_brands = ['BMW', 'Mercedes', 'Audi', 'Volkswagen', 'Opel', 'Porsche']
        korean_brands = ['Hyundai', 'Kia', 'Daewoo']
        american_brands = ['Ford', 'Chevrolet', 'Cadillac', 'Jeep', 'Chrysler']
        french_brands = ['Renault', 'Peugeot', 'Citroen']
        italian_brands = ['Fiat', 'Alfa Romeo', 'Ferrari', 'Lamborghini']
        russian_brands = ['Lada', 'GAZ', 'UAZ']
        
        if obj.brand in japanese_brands:
            obj.country = 'japan'
        elif obj.brand in german_brands:
            obj.country = 'germany'
        elif obj.brand in korean_brands:
            obj.country = 'korea'
        elif obj.brand in american_brands:
            obj.country = 'usa'
        elif obj.brand in french_brands:
            obj.country = 'france'
        elif obj.brand in italian_brands:
            obj.country = 'italy'
        elif obj.brand in russian_brands:
            obj.country = 'russia'
        else:
            obj.country = 'other'
        
        super().save_model(request, obj, form, change)

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)

@admin.register(Characteristic)
class CharacteristicAdmin(admin.ModelAdmin):
    list_display = ('name', 'value')
    search_fields = ('name', 'value')

@admin.register(InspectionRequest)
class InspectionRequestAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'car', 'inspection_date', 'inspection_time', 'status', 'created_at']
    list_filter = ['status', 'inspection_date', 'created_at']
    search_fields = ['full_name', 'phone', 'car__brand', 'car__model']
    list_editable = ['status']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Информация о клиенте', {
            'fields': ('full_name', 'phone', 'email')
        }),
        ('Информация об осмотре', {
            'fields': ('car', 'inspection_date', 'inspection_time', 'status')
        }),
        ('Дополнительно', {
            'fields': ('notes', 'created_at')
        }),
    )
    
    def has_add_permission(self, request):
        return False