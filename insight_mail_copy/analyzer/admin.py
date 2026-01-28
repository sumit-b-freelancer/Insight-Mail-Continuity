from django.contrib import admin
from .models import Email, AnalysisResult

@admin.register(Email)
class EmailAdmin(admin.ModelAdmin):
    list_display = ('subject', 'sender', 'is_analyzed', 'received_at')

@admin.register(AnalysisResult)
class AnalysisResultAdmin(admin.ModelAdmin):
    list_display = ('email', 'sentiment', 'risk_score', 'suggested_category')
