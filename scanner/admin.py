from django.contrib import admin

# Register your models here.
from .models import QRCode
@admin.register(QRCode)
class AdminQRCode(admin.ModelAdmin):
    list_display = ['data','mobile_number']