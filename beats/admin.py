from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Beat, Sample, Orden, TransaccionPago, CustomUser

admin.site.register(Beat)
admin.site.register(Sample)



admin.site.register(Orden)
admin.site.register(TransaccionPago)


class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    readonly_fields = ('date_joined', 'last_login')

admin.site.register(CustomUser, CustomUserAdmin)