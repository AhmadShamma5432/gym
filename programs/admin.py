from django.contrib import admin
from .models import (
    Muscle,
    Sport,
    Exercise,
    ExerciseMuscle,
    Plan,
    ExerciseDetail,
    PlanSubscription,
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
    list_display = ('name_en', 'name_ar', 'owner', 'time')
    search_fields = ('name_en', 'name_ar', 'owner__username')
    list_filter = ('owner',)
    inlines = [ExerciseMuscleInline]

# --------------------------
# ExerciseDetail Inline (for Plan Admin)
# --------------------------
class ExerciseDetailInline(admin.TabularInline):
    model = ExerciseDetail
    extra = 1


# --------------------------
# PlanSubscription Admin
# --------------------------
@admin.register(PlanSubscription)
class PlanSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan')
    search_fields = ('user__username', 'plan__name_en')


# Optional: Customize Plan Admin with inline ExerciseDetails
@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ('name_en', 'name_ar', 'owner', 'sport', 'weeks', 'days')
    search_fields = ('name_en', 'name_ar', 'owner__username', 'sport__name_en')
    list_filter = ('sport', 'owner')
    inlines = [ExerciseDetailInline]