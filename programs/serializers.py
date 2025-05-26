from rest_framework import serializers
from .models import Exercise, Plan, ExerciseDetail,Sport

class ExerciseSerializer(serializers.ModelSerializer):
    targeted_muscles_en = serializers.SerializerMethodField()
    targeted_muscles_ar = serializers.SerializerMethodField()

    class Meta:
        model = Exercise
        fields = [
            'id', 'name_en', 'name_ar','description_en', 'description_ar','time',
            'image', 'video', 'targeted_muscles_en','targeted_muscles_ar','how_to_play'
        ]

    def get_targeted_muscles_en(self, obj):
        return [muscle.muscle.name_en for muscle in obj.targeted_muscles.all()]
    def get_targeted_muscles_ar(self, obj):
        return [muscle.muscle.name_ar for muscle in obj.targeted_muscles.all()]
    

    def create(self, validated_data):
        coach = self.context['coach']
        sport = validated_data.pop('sport')
        print(sport)
        return Exercise.objects.create(sport=sport,coach=coach, **validated_data)

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

    class Meta:
        model = Plan
        fields = [
            'id','name_en', 'name_ar','advice_en', 'advice_ar','description_en', 'description_ar','plan_goal_en', 'plan_goal_ar','weeks', 
            'image', 'days', 'daily_time','kalories','sport_en','sport_ar','sport_id','details'
        ]

    def get_sport_en(self, obj):
        return obj.sport.name_en
    def get_sport_ar(self, obj):
        return obj.sport.name_ar
    
    def create(self, validated_data):
        user = self.context['user']
        sport = validated_data.pop('sport_id')
        sport = Sport.objects.get(pk=sport)
        details_data = validated_data.pop('details')
        plan = Plan.objects.create(**validated_data,user=user,sport=sport)

        for detail_data in details_data:
            ExerciseDetail.objects.create(plan=plan, **detail_data)

        return plan
    
    def update(self, instance, validated_data):
        instance.delete()
        return self.create(validated_data)