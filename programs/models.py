from django.db import models
from project.settings import AUTH_USER_MODEL


class Muscle(models.Model):
    name_en = models.CharField(max_length=100, unique=True)
    name_ar = models.CharField(max_length=100, unique=True)
    
class Sport(models.Model):
    name_en = models.CharField(max_length=100, unique=True)
    name_ar = models.CharField(max_length=100, unique=True)
    
class Exercise(models.Model):
    coach = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    name_en = models.CharField(max_length=100, unique=True)
    name_ar = models.CharField(max_length=100, unique=True)
    
    description_en = models.TextField()
    description_ar = models.TextField()
    how_to_play = models.TextField()
    
    time = models.SmallIntegerField()
    image = models.ImageField(upload_to='exercises/images/', blank=True, null=True)
    video = models.FileField(upload_to='exercises/videos/', blank=True, null=True)
    # sport = models.ForeignKey(Sport,on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class ExerciseMuscle(models.Model):
    muscle = models.ForeignKey(Muscle,on_delete=models.CASCADE,related_name='muscle')
    exercise = models.ForeignKey(Exercise,on_delete=models.CASCADE,related_name='targeted_muscles')
    
class Plan(models.Model):
    name_en = models.CharField(max_length=255)
    name_ar = models.CharField(max_length=255)
    
    advice_en = models.TextField(blank=True, null=True)
    advice_ar = models.TextField(blank=True, null=True)

    days = models.IntegerField()
    description_en = models.TextField()
    description_ar = models.TextField()
    daily_time = models.CharField(max_length=255)
    
    kalories = models.IntegerField()
    plan_goal_en = models.CharField(max_length=50)
    plan_goal_ar = models.CharField(max_length=50)
    
    weeks = models.PositiveSmallIntegerField()
    image = models.ImageField(upload_to='plans/images/', blank=True, null=True)
    user = models.ForeignKey(AUTH_USER_MODEL,on_delete=models.CASCADE)
    sport = models.ForeignKey(Sport,on_delete=models.CASCADE,related_name='sport_plan')
    def __str__(self):
        return self.name
    
class ExerciseDetail(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='details')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='exercise_detail')
    week = models.PositiveSmallIntegerField()
    day = models.PositiveSmallIntegerField()
    
    sets = models.PositiveSmallIntegerField()
    reps_en = models.CharField(max_length=255)
    reps_ar = models.CharField(max_length=255)

    class Meta:
        unique_together = ('plan', 'exercise', 'week', 'day')