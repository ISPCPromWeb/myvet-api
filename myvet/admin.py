from django.contrib import admin
from .models import Product, Pet, Client, ProductType, PetType, Vaccine, VaccineType
from .forms import PetForm, ClientForm

class VaccineInline(admin.TabularInline):
    model = Vaccine
    extra = 1

class PetInline(admin.TabularInline):
    form = PetForm
    model = Pet
    extra = 1

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'get_product_type_name', 'get_pet_type_name']
    list_filter = ['name', 'type__name', 'pet_type__name']

    def get_product_type_name(self, obj):
        return obj.type.name
    get_product_type_name.short_description = 'Product Type'

    def get_pet_type_name(self, obj):
        return obj.pet_type.name
    get_pet_type_name.short_description = 'Pet Type'

class PetAdmin(admin.ModelAdmin):
    form: PetForm
    list_display = ['name', 'breed', 'get_pet_type_name', 'owner']
    list_filter = ['name', 'breed', 'type__name', 'owner']
    inlines = [VaccineInline]

    def get_pet_type_name(self, obj):
        return obj.type.name
    get_pet_type_name.short_description = 'Type'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['vaccines'] = PetForm.base_fields['vaccines']
        return form

class ClientAdmin(admin.ModelAdmin):
    form: ClientForm
    list_display = ['email', 'name', 'surname', 'address']
    list_filter = ['name', 'surname', 'address']
    inlines = [PetInline]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.base_fields['pets'] = ClientForm.base_fields['pets']
        return form
    
    def save_model(self, request, obj, form, change):
        if form.cleaned_data['password']:
            obj.set_password(form.cleaned_data['password'])
        super().save_model(request, obj, form, change)

class VaccineAdmin(admin.ModelAdmin):
    list_display = ['get_vaccine_type_name', 'pet', 'app_date']
    list_filter = ('type', 'pet', 'pet__type', 'app_date')

    def get_vaccine_type_name(self, obj):
        return obj.type.name
    get_vaccine_type_name.short_description = 'Vaccine Name'

admin.site.register(PetType)
admin.site.register(ProductType)
admin.site.register(VaccineType)

admin.site.register(Client, ClientAdmin)
admin.site.register(Pet, PetAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Vaccine, VaccineAdmin)