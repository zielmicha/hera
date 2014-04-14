from hera import models
from django.contrib import admin

admin.site.register(models.VM)

admin.site.register(models.DerivativeResource)

admin.site.register(models.ResourceRefreshed)

class DiskAdmin(admin.ModelAdmin):
    list_display = ('owner', 'refcount', 'backing', 'created', 'timeout')

admin.site.register(models.Disk, DiskAdmin)

admin.site.register(models.Template)
