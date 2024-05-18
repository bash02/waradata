from django.contrib import admin
from . import models

@admin.register(models.PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    exclude = ('promo_code',)  # Exclude promo_code field from the admin form
    list_display = ['title', 'description', 'promo_code', 'amount', 'validity_days', 'created_at']

    def save_model(self, request, obj, form, change):
        if not obj.promo_code:
            # Generate promo code only if it's not set
            obj.promo_code = models.generate_referral_code()
        super().save_model(request, obj, form, change)


@admin.register(models.Bonuce)
class ReferralBonuceAdmin(admin.ModelAdmin):
    list_display = ['bonuce_type', 'amount']



