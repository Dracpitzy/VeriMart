from django.contrib import admin
from .models import Payment, SellerBalance, Payout

admin.site.register(Payment)
admin.site.register(SellerBalance)
admin.site.register(Payout)
