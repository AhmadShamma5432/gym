from django.db import models
from project.settings import AUTH_USER_MODEL

class Day(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Exercise(models.Model):
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
    sets = models.PositiveSmallIntegerField()
    reps = models.CharField(max_length=255)
    image = models.ImageField(upload_to='exercises/images/', blank=True, null=True)
    video = models.FileField(upload_to='exercises/videos/', blank=True, null=True)

    def __str__(self):
        return self.name

class Plan(models.Model):
    name = models.CharField(max_length=255)
    advice = models.TextField(blank=True, null=True)
    plan_goal = models.CharField(max_length=50)
    weeks = models.PositiveSmallIntegerField()
    image = models.ImageField(upload_to='plans/images/', blank=True, null=True)
    user = models.ForeignKey(AUTH_USER_MODEL,on_delete=models.CASCADE)
    def __str__(self):
        return self.name

class PlanDay(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='plan_days')
    day = models.ForeignKey(Day, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('plan', 'day')

    def __str__(self):
        return f"{self.plan} - {self.day}"


class PlanDayExercise(models.Model):
    plan_day = models.ForeignKey(PlanDay, on_delete=models.CASCADE, related_name='plan_exercises')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('plan_day', 'exercise')

    def __str__(self):
        return f"{self.plan_day} - {self.exercise}"