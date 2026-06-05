from django.contrib import admin
from .models import (
    SurveyQuestion,
    SurveyChoice,
    SurveyResponse,
    SurveyAnswer,
    InvestmentProfile,
)


class SurveyChoiceInline(admin.TabularInline):
    model = SurveyChoice
    extra = 3


@admin.register(SurveyQuestion)
class SurveyQuestionAdmin(admin.ModelAdmin):
    list_display = ('id', 'content', 'display_order', 'is_active')
    inlines = [SurveyChoiceInline]


@admin.register(SurveyResponse)
class SurveyResponseAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'total_score', 'submitted_at')


@admin.register(SurveyAnswer)
class SurveyAnswerAdmin(admin.ModelAdmin):
    list_display = ('id', 'response', 'question', 'choice', 'score_snapshot')


@admin.register(InvestmentProfile)
class InvestmentProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'profile_type', 'risk_score', 'updated_at')