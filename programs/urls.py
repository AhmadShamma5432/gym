# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *

router = DefaultRouter()
router.register(r'exercises', ExerciseViewSet, basename='exercise')
router.register(r'plans', PlanViewSet, basename='plans')
router.register(r'plan_subscriptions', PlanSubscriptionView, basename='plan_subscription')
router.register(r'plan_request', PlanRequestView, basename='plan_request')
router.register(r'coach_question', CoachQuestionsView, basename='coach_question')
router.register(r'sport', SportView, basename='sport')
router.register(r'muscle', MuscleView, basename='muscle')
router.register(r'nutrition-plan', NutritionPlanViewSet, basename='nutrition-plan')

urlpatterns = [
    path('', include(router.urls)),
]