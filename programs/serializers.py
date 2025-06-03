from rest_framework import serializers
from core.serializers import UserSerializer
from core.models import User
from .models import Exercise, Plan, ExerciseDetail,Sport,PlanSubscription,PlanRequest,Muscle,ExerciseMuscle
from django.db import transaction

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
    exercise = ExerciseSerializer(read_only=True)
    exercise_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = ExerciseDetail
        fields = [
            'id', 'exercise', 'week', 'day',
            'sets', 'reps_en', 'reps_ar','exercise_id'
        ]

class PlanSerializer(serializers.ModelSerializer):
    details = ExerciseDetailSerializer(many=True)
    sport_id = serializers.IntegerField(write_only=True)
    sport_en = serializers.SerializerMethodField(read_only=True)
    sport_ar = serializers.SerializerMethodField(read_only=True)
    user_id = serializers.IntegerField(write_only=True,required=False)
    owner = UserSerializer(read_only=True)

    class Meta:
        model = Plan
        fields = [
            'id','name_en', 'name_ar','advice_en', 'advice_ar','description_en', 'description_ar','plan_goal_en', 'plan_goal_ar','weeks', 
            'image', 'days', 'daily_time','kalories','sport_en','sport_ar','sport_id','details','owner','user_id'
        ]

    def get_sport_en(self, obj):
        return obj.sport.name_en
    def get_sport_ar(self, obj):
        return obj.sport.name_ar
    
    def create(self, validated_data):
        with transaction.atomic(): 
            owner = self.context['user']
            sport = validated_data.pop('sport_id')
            try: 
                user_id = validated_data.pop('user_id')
            except: 
                user_id = None
            sport = Sport.objects.get(pk=sport)
            details_data = validated_data.pop('details')
            plan = Plan.objects.create(**validated_data,owner=owner,sport=sport)

            if( user_id ):
                PlanSubscription.objects.create(plan_id=plan.id,user_id=user_id)

            for detail_data in details_data:
                ExerciseDetail.objects.create(plan=plan, **detail_data)

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


class PlanRequestSerializer(serializers.ModelSerializer):
    # Read-only nested representations
    sport = SportSerializer(read_only=True)
    owner = UserSerializer(read_only=True)
    user = UserSerializer(read_only=True)

    # Write-only IDs for input
    sport_id = serializers.IntegerField(write_only=True)
    coach_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = PlanRequest
        fields = [
            'id', 'user', 'owner', 'coach_id',
            'sport', 'sport_id', 'plan_type',
            'requested_at', 'is_completed'
        ]
        read_only_fields = ['user', 'requested_at']

    def create(self, validated_data):
        user = self.context['user']
        if user == None:
            raise serializers.ValidationError("you can't make a request if you are not authenticated")
        sport_id = validated_data.pop('sport_id', None)
        coach_id = validated_data.pop('coach_id', None)

        # Validate presence of IDs
        if sport_id is None:
            raise serializers.ValidationError({"sport_id": "This field is required."})
        if coach_id is None:
            raise serializers.ValidationError({"coach_id": "This field is required."})

        # Fetch related objects
        try:
            sport = Sport.objects.get(id=sport_id)
        except Sport.DoesNotExist:
            raise serializers.ValidationError({"sport_id": "Sport does not exist."})

        try:
            coach = User.objects.get(id=coach_id)
        except User.DoesNotExist:
            raise serializers.ValidationError({"coach_id": "Coach does not exist."})

        return PlanRequest.objects.create(
            user=user,
            sport=sport,
            owner=coach,
            **validated_data
        )