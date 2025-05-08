from rest_framework import serializers
from .models import Exercise, Plan, ExerciseDetail

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'name', 'description', 'image', 'video']

class ExerciseDetailSerializer(serializers.ModelSerializer):
    exercise = ExerciseSerializer(read_only=True)

    class Meta:
        model = ExerciseDetail
        fields = ['id', 'exercise', 'week', 'day', 'sets', 'reps']

class PlanSerializer(serializers.ModelSerializer):
    details = ExerciseDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Plan
        fields = ['id', 'name', 'advice', 'plan_goal', 'weeks', 'image', 'details']