from django.contrib import admin
import nested_admin
from .models import (
    Muscle,
    Sport,
    Exercise,
    ExerciseMuscle,
    Plan,
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