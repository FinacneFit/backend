from django.conf import settings
from django.db import models


class SurveyQuestion(models.Model):
    content = models.CharField(max_length=255)
    display_order = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.content


class SurveyChoice(models.Model):
    question = models.ForeignKey(
        SurveyQuestion,
        on_delete=models.CASCADE,
        related_name='choices'
    )
    content = models.CharField(max_length=255)
    score = models.PositiveIntegerField()
    display_order = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.question.content} - {self.content}'


class SurveyResponse(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='survey_responses'
    )
    total_score = models.PositiveIntegerField(default=0)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.total_score}점'


class SurveyAnswer(models.Model):
    response = models.ForeignKey(
        SurveyResponse,
        on_delete=models.CASCADE,
        related_name='answers'
    )
    question = models.ForeignKey(SurveyQuestion, on_delete=models.CASCADE)
    choice = models.ForeignKey(SurveyChoice, on_delete=models.CASCADE)
    score_snapshot = models.PositiveIntegerField()

    def __str__(self):
        return f'{self.question.content} -> {self.choice.content}'


class InvestmentProfile(models.Model):
    PROFILE_CHOICES = [
        ('STABLE', '안정형'),
        ('STABLE_SEEKING', '안정추구형'),
        ('NEUTRAL', '위험중립형'),
        ('ACTIVE', '적극투자형'),
        ('AGGRESSIVE', '공격투자형'),
    ]

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='investment_profile'
    )
    response = models.ForeignKey(
        SurveyResponse,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    profile_type = models.CharField(max_length=30, choices=PROFILE_CHOICES)
    risk_score = models.PositiveIntegerField()
    description = models.TextField()
    strategy = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_profile_type_display_korean(self):
        return self.get_profile_type_display()

    def __str__(self):
        return f'{self.user} - {self.get_profile_type_display()}'