from django.contrib import admin
from emoji import emojize

print('IM IN ADMIN!')
# Register your models here.
from .models import Payer, Payment, CurrencyQuote, Category, Currency

ms = [CurrencyQuote, Currency]
for i in ms:
    admin.site.register(i)

class PayerAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'telegram_id', 'show_cats')

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description', 'emoji')


class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        'amount',
        'description',
        'creator',
        'category',
        'update',
        'timestamp'
    )
    list_editable = ['category']


admin.site.register(Payer, PayerAdmin)
admin.site.register(Payment, PaymentAdmin)
admin.site.register(Category, CategoryAdmin)
