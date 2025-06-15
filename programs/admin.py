from django.contrib import admin
import nested_admin
from .models import (
    Muscle,
    Sport,
    Exercise,
    ExerciseMuscle,
    Plan,
    Week,
    Day,
    ExerciseDetail,
    PlanSubscription,
    NutritionPlan,
    MealDetail,
    FoodItem
)

# --------------------------
# Muscle Admin
# --------------------------
@admin.register(Muscle)
class MuscleAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_ar')
    search_fields = ('name_en', 'name_ar')
# --------------------------
# Sport Admin
# --------------------------
@admin.register(Sport)
class SportAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_ar')
    search_fields = ('name_en', 'name_ar')


# --------------------------
# ExerciseMuscle Inline (for Exercise Admin)
# --------------------------
class ExerciseMuscleInline(admin.TabularInline):
    model = ExerciseMuscle
    extra = 1
# --------------------------
# Exercise Admin
# --------------------------
@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ('id','name_en', 'name_ar', 'owner', 'time')
    search_fields = ('name_en', 'name_ar', 'owner__username')
    list_filter = ('owner',)
    inlines = [ExerciseMuscleInline]

# --------------------------
# ExerciseDetail Inline (for Plan Admin)
# --------------------------
class ExerciseDetailInline(nested_admin.NestedTabularInline):
    model = ExerciseDetail
    extra = 1

class DayInline(nested_admin.NestedTabularInline):
    model = Day
    extra = 1
    fields = ('number', 'name', 'rest_between_exercises')
    inlines = [ExerciseDetailInline]   
class WeekInline(nested_admin.NestedTabularInline):
    model = Week
    extra = 1
    fields = ('number', 'name')
    inlines = [DayInline]


@admin.register(Plan)
class PlanAdmin(nested_admin.NestedModelAdmin):
    list_display = (
        'name_en', 'name_ar', 'owner', 'sport', 'weeks',
        'days', 'daily_time', 'kalories', 'plan_pay_level'
    )
    list_filter = ('plan_pay_level', 'sport', 'owner')
    inlines = [WeekInline]
    save_on_top = True

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'sport', 'owner'
        ).prefetch_related(
            'plan_weeks__plan_days__exercises'
        )

@admin.register(ExerciseDetail)
class ExerciseDetailAdmin(admin.ModelAdmin):
    list_display = (
        'day', 'exercise', 'sets', 'reps_en', 'reps_ar', 'rest_between_sets'
    )
    list_filter = ('day__week__plan',)

    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'exercise', 'day__week__plan'
        )
# --------------------------
# PlanSubscription Admin
# --------------------------
@admin.register(PlanSubscription)
class PlanSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan')
    search_fields = ('user__username', 'plan__name_en')



class FoodItemInline(nested_admin.NestedTabularInline):
    model = FoodItem
    extra = 1
    fields = ['name_en', 'name_ar', 'quantity']

class MealDetailInline(nested_admin.NestedTabularInline):
    model = MealDetail
    extra = 1
    fields = ['week', 'day', 'meal_number', 'meal_name_en', 'meal_name_ar', 'calories', 'protein', 'carbs', 'fats']
    inlines = [FoodItemInline]

@admin.register(NutritionPlan)
class NutritionPlanAdmin(nested_admin.NestedModelAdmin):
    inlines = [MealDetailInline]
    list_display = ['name_en', 'target', 'weeks', 'owner']
    search_fields = ['name_en', 'name_ar']
    list_filter = ['owner']