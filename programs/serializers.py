from rest_framework import serializers
from core.serializers import UserSerializer
from core.models import User
from .models import Exercise,Week,Day, Plan, ExerciseDetail,Sport,PlanSubscription,PlanRequest,Muscle,ExerciseMuscle,MealDetail,FoodItem,NutritionPlan,CoachQuestion,UserAnswer
from django.db import transaction
import json
class SportSerializer(serializers.ModelSerializer):

    class Meta:
        model = Sport
        fields = [
            'id','name_en','name_ar'
        ]

class MuscleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Muscle
        fields = [
            'id','name_en','name_ar'
        ]


class ExerciseSerializer(serializers.ModelSerializer):
    targeted_muscles_en = serializers.SerializerMethodField()
    targeted_muscles_ar = serializers.SerializerMethodField()
    
    muscles = serializers.PrimaryKeyRelatedField(queryset=Muscle.objects.all(), many=True, write_only=True)
    class Meta:
        model = Exercise
        fields = [
            'id', 'name_en', 'name_ar','description_en', 'description_ar','time','muscles',
            'image', 'video', 'targeted_muscles_en','targeted_muscles_ar','how_to_play_en','how_to_play_ar'
        ]

    def get_targeted_muscles_en(self, obj):
        return [muscle.muscle.name_en for muscle in obj.targeted_muscles.all()]
    def get_targeted_muscles_ar(self, obj):
        return [muscle.muscle.name_ar for muscle in obj.targeted_muscles.all()]
    

    def create(self, validated_data):
        with transaction.atomic():
            owner = self.context['owner']
            muscles = validated_data.pop('muscles')  # list of Muscle instances

            exercise = Exercise.objects.create(owner=owner, **validated_data)

            # Create ExerciseMuscle entries
            exercise_muscles = [
                ExerciseMuscle(exercise=exercise, muscle=muscle)
                for muscle in muscles
            ]

            ExerciseMuscle.objects.bulk_create(exercise_muscles)

            return exercise

    def update(self, instance, validated_data):
        with transaction.atomic():
            muscles = validated_data.pop('muscles', None)

            # Update other fields of the exercise
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()

            if muscles is not None:
                # Delete existing ExerciseMuscle relationships
                ExerciseMuscle.objects.filter(exercise=instance).delete()

                # Bulk create new ExerciseMuscle relationships
                exercise_muscles = [
                    ExerciseMuscle(exercise=instance, muscle=muscle)
                    for muscle in muscles
                ]
                ExerciseMuscle.objects.bulk_create(exercise_muscles)

            return instance

class ExerciseDetailSerializer(serializers.ModelSerializer):
    exercise_id = serializers.IntegerField(write_only=True)
    exercise = ExerciseSerializer(read_only=True)

    class Meta:
        model = ExerciseDetail
        fields = ['id', 'sets', 'reps_en', 'reps_ar','exercise','exercise_id', 'rest_between_sets']

class DaySerializer(serializers.Serializer):
    day_number = serializers.IntegerField(source='number')
    day_name = serializers.CharField(source='name')
    rest_between_exercises = serializers.IntegerField()
    exercises = ExerciseDetailSerializer(many=True)

class WeekSerializer(serializers.Serializer):
    week_number = serializers.IntegerField(source='number')
    week_name = serializers.CharField(source='name')
    plan_days = DaySerializer(many=True)

class PlanSerializer(serializers.ModelSerializer):
    plan_weeks = WeekSerializer(many=True)
    sport_id = serializers.IntegerField(write_only=True)
    sport_en = serializers.SerializerMethodField(read_only=True)
    sport_ar = serializers.SerializerMethodField(read_only=True)
    user_id = serializers.IntegerField(write_only=True,required=False)
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Plan
        fields = [
            'id','name_en', 'name_ar','advice_en', 'advice_ar','description_en', 'description_ar','plan_goal_en', 'plan_goal_ar','weeks', 
            'image', 'days', 'daily_time','kalories','sport_en','sport_ar','sport_id','plan_weeks','owner','user_id','plan_pay_level'
        ]

    def get_sport_en(self, obj):
        return obj.sport.name_en
    def get_sport_ar(self, obj):
        return obj.sport.name_ar
    def get_image(self, obj):
        request = self.context.get("request")
        try: 
            return request.build_absolute_uri(obj.image.url) 
        except: return ""


    def create(self, validated_data):
        with transaction.atomic():
            owner = self.context['request'].user
            sport_id = validated_data.pop('sport_id')

            try:
                sport = Sport.objects.get(pk=sport_id)
            except Sport.DoesNotExist:
                raise serializers.ValidationError({"sport_id": "Invalid sport ID."})

            print(validated_data)

            plan_details = validated_data.pop('plan_weeks')
            plan = Plan.objects.create(owner=owner, sport=sport, **validated_data)

            # Optional: handle user subscription
            if user_id := validated_data.pop("user_id", None):
                PlanSubscription.objects.create(plan_id=plan.id, user_id=user_id)

            for week_data in plan_details:
                week_number = week_data["number"]
                week_name = week_data["name"]

                week = Week.objects.create(plan=plan, number=week_number, name=week_name)
                print(week_data)
                for day_data in week_data.get("plan_days", []):
                    day_number = day_data["number"]
                    day_name = day_data["name"]
                    rest_between_exercises = day_data["rest_between_exercises"]
                    print(day_data)
                    day = Day.objects.create(
                        week=week,
                        number=day_number,
                        name=day_name,
                        rest_between_exercises=rest_between_exercises
                    )

                    for exercise_data in day_data.get("exercises", []):
                        ExerciseDetail.objects.create(
                            day=day,
                            exercise_id=exercise_data["exercise_id"],
                            sets=exercise_data["sets"],
                            reps_en=exercise_data["reps_en"],
                            reps_ar=exercise_data["reps_ar"],
                            rest_between_sets=exercise_data["rest_between_sets"]
                        )

            return plan
    
    def update(self, instance, validated_data):
        instance.delete()
        return self.create(validated_data)
    

class PlanSubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    user = UserSerializer(read_only=True)
    plan_id = serializers.IntegerField(write_only=True)
    user_id = serializers.IntegerField(write_only=True)
    
    class Meta:
        model = PlanSubscription
        fields = ['plan','user','plan_id','user_id']
class CoachQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoachQuestion
        fields = ['id', 'question_en', 'question_ar', 'plan_type']

class UserAnswerSerializer(serializers.ModelSerializer):
    question = serializers.SerializerMethodField()
    class Meta:
        model = UserAnswer
        fields = ['question', 'answer']
    
    def get_question(self,obj):
        print(obj.question)
        return {
            "id": obj.question.id,
            "question_en": obj.question.question_en,
            "question_ar": obj.question.question_ar
        }

class PlanRequestSerializer(serializers.ModelSerializer):
    # Read-only nested representations
    sport = SportSerializer(read_only=True)
    owner = UserSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    # Write-only IDs
    sport_id = serializers.IntegerField(write_only=True)
    coach_id = serializers.IntegerField(write_only=True)
    answers = UserAnswerSerializer(many=True)

    class Meta:
        model = PlanRequest
        fields = [
            'id', 'user', 'owner', 'coach_id',
            'sport', 'sport_id', 'plan_type',
            'requested_at', 'is_completed', 'answers'
        ]
        read_only_fields = ['user', 'requested_at', 'owner']

    def create(self, validated_data):
        with transaction.atomic():
            user = self.context['user']
            if not user.is_authenticated:
                raise serializers.ValidationError("You must be logged in to make a plan request.")

            sport_id = validated_data.pop('sport_id')
            coach_id = validated_data.pop('coach_id')
            answers_data = validated_data.pop('answers')

            # Fetch related objects
            try:
                sport = Sport.objects.get(id=sport_id)
            except Sport.DoesNotExist:
                raise serializers.ValidationError({"sport_id": "Invalid sport ID."})

            try:
                coach = User.objects.get(id=coach_id)
            except User.DoesNotExist:
                raise serializers.ValidationError({"coach_id": "Coach does not exist."})

            plan_request = PlanRequest.objects.create(
                user=user,
                sport=sport,
                coach=coach,
                **validated_data
            )

            user_answers = [
                UserAnswer(
                    plan_request=plan_request,
                    question=answer['question'],
                    answer=answer['answer']
                ) for answer in answers_data
            ]

            UserAnswer.objects.bulk_create(user_answers)

            return plan_request

class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = [
            'id', 'name_en', 'name_ar', 'quantity'
        ]

class MealDetailSerializer(serializers.ModelSerializer):
    food_items = FoodItemSerializer(many=True)

    class Meta:
        model = MealDetail
        fields = [
            'id', 'week', 'day', 'meal_number',
            'meal_name_en', 'meal_name_ar',
            'calories', 'protein', 'carbs', 'fats',
            'food_items'
        ]

class NutritionPlanSerializer(serializers.ModelSerializer):
    meals = MealDetailSerializer(many=True)
    owner = UserSerializer(read_only=True)  # assuming UserSerializer is defined

    class Meta:
        model = NutritionPlan
        fields = [
            'id', 'name_en', 'name_ar', 'target',
            'description_en', 'description_ar',
            'advice_en', 'advice_ar','plan_pay_level',
            'weeks', 'image', 'owner', 'meals'
        ]

    def validate(self, data):
        meals_data = data.get('meals')
        if not meals_data:
            raise serializers.ValidationError("At least one meal must be provided.")
        return data

    def create(self, validated_data):
        with transaction.atomic():
            meals_array = []
            food_items_array = []
            final_array = []

            owner = self.context['owner']
            meals_data = validated_data.pop('meals')
            plan = NutritionPlan.objects.create(owner=owner, **validated_data)


            for meal in meals_data:
                food_items = meal.pop('food_items')
                meals_array.append(MealDetail(plan=plan,**meal))
                food_items_array.append(food_items)

            MealDetail.objects.bulk_create(meals_array)
            saved_meals = MealDetail.objects.filter(plan_id=plan.id)
            print(saved_meals)
            cnt = 0 ; 
            for saved_meal in saved_meals:
                for food_item in food_items_array[cnt]: 
                    print(saved_meal.id)
                    final_array.append(FoodItem(meal_id=saved_meal.id,**food_item))
                cnt += 1 ; 

            FoodItem.objects.bulk_create(final_array)

            
            return plan

    def update(self, instance, validated_data):
        with transaction.atomic():
            instance.delete()
            # instance.owner = self.context['owner_id']
            return self.create(validated_data)