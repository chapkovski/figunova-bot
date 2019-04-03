from django.contrib import admin
from emoji import emojize

print('IM IN ADMIN!')
# Register your models here.
from .models import Payer, Payment, CurrencyQuote, Category, Currency

ms = [Payer, CurrencyQuote, Currency]
for i in ms:
    admin.site.register(i)


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


admin.site.register(Payment, PaymentAdmin)
admin.site.register(Category, CategoryAdmin)
