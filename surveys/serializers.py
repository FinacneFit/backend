from rest_framework import serializers
from .models import SurveyQuestion, SurveyChoice, InvestmentProfile


class SurveyChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = SurveyChoice
        fields = ('id', 'content', 'score', 'display_order')


class SurveyQuestionSerializer(serializers.ModelSerializer):
    choices = SurveyChoiceSerializer(many=True, read_only=True)

    class Meta:
        model = SurveyQuestion
        fields = ('id', 'content', 'display_order', 'choices')


class SurveyAnswerInputSerializer(serializers.Serializer):
    question_id = serializers.IntegerField()
    choice_id = serializers.IntegerField()


class SurveyResponseCreateSerializer(serializers.Serializer):
    answers = SurveyAnswerInputSerializer(many=True)


class InvestmentProfileSerializer(serializers.ModelSerializer):
    profile_type_display = serializers.CharField(
        source='get_profile_type_display',
        read_only=True
    )

    class Meta:
        model = InvestmentProfile
        fields = (
            'id',
            'profile_type',
            'profile_type_display',
            'risk_score',
            'description',
            'strategy',
            'created_at',
            'updated_at',
        )