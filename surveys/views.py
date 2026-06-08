from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from .models import (
    SurveyQuestion,
    SurveyChoice,
    SurveyResponse,
    SurveyAnswer,
    InvestmentProfile,
)
from .serializers import (
    SurveyQuestionSerializer,
    SurveyResponseCreateSerializer,
    InvestmentProfileSerializer,
)


def calculate_profile(total_score):
    if total_score <= 10:
        return {
            'profile_type': 'STABLE',
            'description': '손실 회피 성향이 강하고 안정적인 투자를 선호하는 유형입니다.',
            'strategy': '예금성 상품, 채권형 상품, 대형 우량주 중심의 안정적 구성이 적합합니다.',
        }
    elif total_score <= 15:
        return {
            'profile_type': 'STABLE_SEEKING',
            'description': '안정성을 중시하되 일부 수익성도 고려하는 유형입니다.',
            'strategy': '대형주와 배당주 중심으로 구성하되 일부 성장주를 소폭 편입하는 전략이 적합합니다.',
        }
    elif total_score <= 20:
        return {
            'profile_type': 'NEUTRAL',
            'description': '위험과 수익의 균형을 추구하는 유형입니다.',
            'strategy': '업종을 분산하고 안정성과 성장성을 균형 있게 고려하는 포트폴리오가 적합합니다.',
        }
    elif total_score <= 25:
        return {
            'profile_type': 'ACTIVE',
            'description': '수익성을 위해 일정 수준의 변동성을 감수할 수 있는 유형입니다.',
            'strategy': '성장주 비중을 높이되 일부 우량주로 위험을 조절하는 전략이 적합합니다.',
        }
    else:
        return {
            'profile_type': 'AGGRESSIVE',
            'description': '높은 수익을 위해 큰 변동성도 감수할 수 있는 유형입니다.',
            'strategy': '성장주, 신산업, 고변동성 자산 중심의 적극적인 포트폴리오가 적합합니다.',
        }


@api_view(['GET'])
@permission_classes([AllowAny])
def question_list(request):
    questions = SurveyQuestion.objects.filter(is_active=True).order_by('display_order')
    serializer = SurveyQuestionSerializer(questions, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_response(request):
    serializer = SurveyResponseCreateSerializer(data=request.data)

    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    answers_data = serializer.validated_data['answers']

    if not answers_data:
        return Response(
            {'detail': '답변이 없습니다.'},
            status=status.HTTP_400_BAD_REQUEST
        )

    total_score = 0
    selected_answers = []

    for answer in answers_data:
        question_id = answer['question_id']
        choice_id = answer['choice_id']

        try:
            question = SurveyQuestion.objects.get(id=question_id, is_active=True)
            choice = SurveyChoice.objects.get(id=choice_id, question=question)
        except (SurveyQuestion.DoesNotExist, SurveyChoice.DoesNotExist):
            return Response(
                {'detail': '유효하지 않은 질문 또는 선택지입니다.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        total_score += choice.score
        selected_answers.append((question, choice))

    response = SurveyResponse.objects.create(
        user=request.user,
        total_score=total_score
    )

    for question, choice in selected_answers:
        SurveyAnswer.objects.create(
            response=response,
            question=question,
            choice=choice,
            score_snapshot=choice.score
        )

    profile_data = calculate_profile(total_score)

    profile, created = InvestmentProfile.objects.update_or_create(
        user=request.user,
        defaults={
            'response': response,
            'risk_score': total_score,
            'profile_type': profile_data['profile_type'],
            'description': profile_data['description'],
            'strategy': profile_data['strategy'],
        }
    )

    result_serializer = InvestmentProfileSerializer(profile)

    return Response(
        {
            'message': '투자성향 분석이 완료되었습니다.',
            'profile': result_serializer.data,
        },
        status=status.HTTP_201_CREATED
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_profile(request):
    try:
        profile = request.user.investment_profile
    except InvestmentProfile.DoesNotExist:
        return Response(
            {'detail': '아직 투자성향 분석 결과가 없습니다.'},
            status=status.HTTP_404_NOT_FOUND
        )

    serializer = InvestmentProfileSerializer(profile)
    return Response(serializer.data)