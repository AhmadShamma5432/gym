from rest_framework import serializers
from django.db import transaction
from .models import Plan, Day, Exercise, PlanDay, PlanDayExercise
from django.contrib.auth import get_user_model

User = get_user_model()

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'name', 'description', 'sets', 'reps', 'image', 'video']

class PlanDayExerciseSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
    sets = serializers.IntegerField(required=False)
    reps = serializers.CharField(required=False)
    image = serializers.ImageField(required=False)
    video = serializers.FileField(required=False)

    def validate(self, data):
        if 'id' in data:
            if not Exercise.objects.filter(id=data['id']).exists():
                raise serializers.ValidationError("Exercise with this ID does not exist.")
        elif not data:
            raise serializers.ValidationError("Empty exercise data is not allowed.")
        else:
            required_fields = ['name', 'description', 'sets', 'reps']
            missing_fields = [field for field in required_fields if field not in data]
            if missing_fields:
                raise serializers.ValidationError(f"Missing required fields: {', '.join(missing_fields)}")
        return data


class PlanDaySerializer(serializers.Serializer):
    day_id = serializers.IntegerField()
    exercises = serializers.SerializerMethodField()

    def get_exercises(self, obj):
        # obj is a PlanDay instance
        # Access related PlanDayExercise instances, then get the Exercise from each
        exercises = [pde.exercise for pde in obj.exercises.all()]
        return ExerciseSerializer(exercises, many=True).data

class PlanSerializer(serializers.ModelSerializer):
    days = PlanDaySerializer(source='plan_days',many=True)

    class Meta:
        model = Plan
        fields = ['name', 'advice', 'plan_goal', 'weeks', 'image', 'days']

    @transaction.atomic
    def create(self, validated_data):
        print(validated_data)
        days_data = validated_data.pop('plan_days')
        user = self.context['request'].user
        plan = Plan.objects.create(**validated_data)

        for day_data in days_data:
            day = Day.objects.get(id=day_data['day_id'])
            plan_day = PlanDay.objects.create(plan=plan, day=day)

            for exercise_data in day_data['plan_exercises']:
                print(exercise_data)
                if 'id' in exercise_data:
                    try:
                        exercise = Exercise.objects.get(id=exercise_data['id'])
                    except Exercise.DoesNotExist:
                        raise serializers.ValidationError(f"Exercise with ID {exercise_data['id']} does not exist or is not owned by the user.")
                else:
                    exercise_serializer = ExerciseSerializer(data=exercise_data)
                    exercise_serializer.is_valid(raise_exception=True)
                    exercise = exercise_serializer.save(user=user)

                PlanDayExercise.objects.create(plan_day=plan_day, exercise=exercise)

        return plan