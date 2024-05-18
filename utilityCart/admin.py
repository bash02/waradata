from django.contrib import admin
from .models import DataAPISetting, AirtimeAPISetting, CableAPISetting, ElectricityAPISetting, CablePlan, DataPlan

@admin.register(DataAPISetting)
class DataAPISettingAdmin(admin.ModelAdmin):
    list_display = ('network', 'plan_type', 'api_name', 'plans_url', 'validate_url', 'purchase_url', 'token')
    

@admin.register(AirtimeAPISetting)
class AirtimeAPISettingAdmin(admin.ModelAdmin):
    list_display = ('api', 'network', 'purchase_url', 'token')

@admin.register(CableAPISetting)
class CableAPISettingAdmin(admin.ModelAdmin):
    list_display = ('cable', 'api_name', 'plans_url', 'validate_url', 'purchase_url', 'token')

@admin.register(ElectricityAPISetting)
class ElectricityAPISettingAdmin(admin.ModelAdmin):
    llist_display = ('api', 'network', 'purchase_url', 'token')


@admin.register(CablePlan)
class CablePlanAdmin(admin.ModelAdmin):
    list_display = ('cableplan_id', 'cable', 'package', 'plan_amount')
    list_filter = ('cable',)
    search_fields = ('cableplan_id', 'cable', 'package', 'plan_amount')


@admin.register(DataPlan)
class DataPlanAdmin(admin.ModelAdmin):
    list_display = ('id', 'plan_type', 'network', 'data_size', 'price', 'validity_period')
    list_filter = ('plan_type', 'network')
    search_fields = ('plan_type', 'network', 'data_size', 'price', 'validity_period')
