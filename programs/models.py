from django.db import models
from project.settings import AUTH_USER_MODEL

DAY_CHOICES = [
    ('MON', 'Monday'),
    ('TUE', 'Tuesday'),
    ('WED', 'Wednesday'),
    ('THU', 'Thursday'),
    ('FRI', 'Friday'),
    ('SAT', 'Saturday'),
    ('SUN', 'Sunday'),
]


class Exercise(models.Model):
    coach = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    description = models.TextField()
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
    
class ExerciseDetail(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='details')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='exercise_detail')
    week = models.PositiveSmallIntegerField()
    day = models.CharField(max_length=3, choices=DAY_CHOICES)
    sets = models.PositiveSmallIntegerField()
    reps = models.CharField(max_length=255)

    class Meta:
        unique_together = ('plan', 'exercise', 'week', 'day')