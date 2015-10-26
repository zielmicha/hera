from hera import models
from django.contrib import admin

class VMAdmin(admin.ModelAdmin):
    list_display = ('creator', 'vm_id', 'address')

admin.site.register(models.VM, VMAdmin)

class DerivativeResourceAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'owner', 'created', 'expiry', 'closed_at', 'base_price_per_second')

admin.site.register(models.DerivativeResource, DerivativeResourceAdmin)

class DerivativeResourceUsedAdmin(admin.ModelAdmin):
    list_display = ('resource', 'start_time', 'end_time', 'price')

admin.site.register(models.DerivativeResourceUsed, DerivativeResourceUsedAdmin)

class AccountAdmin(admin.ModelAdmin):
    list_display = ('billing_owner', 'is_main', 'name', 'price_per_second_limit',
                    'price_used', 'price_transferred_to')

admin.site.register(models.Account, AccountAdmin)

class DiskAdmin(admin.ModelAdmin):
    list_display = ('owner', 'refcount', 'backing', 'created', 'timeout')

admin.site.register(models.Disk, DiskAdmin)

class TemplateAdmin(admin.ModelAdmin):
    list_display = ('owner', 'public', 'disk', 'name')

admin.site.register(models.Template, TemplateAdmin)

class QueuedCreationAdmin(admin.ModelAdmin):
    list_display = ('created', 'owner')

admin.site.register(models.QueuedCreation, QueuedCreationAdmin)
