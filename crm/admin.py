from django.contrib import admin
from .models import User, Client

class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'role')
    list_filter = ('role',)

admin.site.register(User, UserAdmin)


class ClientAdmin(admin.ModelAdmin):
    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

admin.site.register(Client, ClientAdmin)