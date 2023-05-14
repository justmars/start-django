from django.contrib import admin

from .models import Agreement, UserConsent


@admin.register(Agreement)
class AgreementDocumentAdmin(admin.ModelAdmin):
    pass


@admin.register(UserConsent)
class UserConsentDocumentAdmin(admin.ModelAdmin):
    pass
