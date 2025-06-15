from django.db import models
from project.settings import AUTH_USER_MODEL

PLAN_TYPE_CHOICES = [
        ('fitness', 'Fitness'),
        ('nutrition', 'Nutrition'),
        ('fitness&nutrition', 'Fitness&Nutrition'),
    ]

PLAN_PAY_LEVEL_CHOICES = [
    ('free','free'),
    ('gold','gold'),
    ('platinum','platinum')
]

EXERCISE_TYPE_CHOICES = [
        ('warm_up', 'warm_up'),
        ('main_exercise', 'main_exercise'),
        ('stretching', 'stretching'),
    ]


class Muscle(models.Model):
    name_en = models.CharField(max_length=100, unique=True)
    name_ar = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name_en
    
class Sport(models.Model):
    name_en = models.CharField(max_length=100, unique=True)
    name_ar = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name_en
class Exercise(models.Model):
    owner = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    name_en = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100)
    
    description_en = models.TextField()
    description_ar = models.TextField()
    how_to_play_en = models.TextField()
    how_to_play_ar = models.TextField()
    
    time = models.SmallIntegerField()
    image = models.ImageField(upload_to='exercises/images/', blank=True, null=True)
    video = models.FileField(upload_to='exercises/videos/', blank=True, null=True)
    # sport = models.ForeignKey(Sport,on_delete=models.CASCADE)

    def __str__(self):
        return self.name_en

class ExerciseMuscle(models.Model):
    muscle = models.ForeignKey(Muscle,on_delete=models.CASCADE,related_name='muscle')
    exercise = models.ForeignKey(Exercise,on_delete=models.CASCADE,related_name='targeted_muscles')
    
class Plan(models.Model):
    name_en = models.CharField(max_length=255)
    name_ar = models.CharField(max_length=255)
    
    advice_en = models.TextField(blank=True, null=True)
    advice_ar = models.TextField(blank=True, null=True)

    plan_pay_level =  models.CharField(max_length=100,choices=PLAN_PAY_LEVEL_CHOICES)

    days = models.IntegerField()
    description_en = models.TextField()
    description_ar = models.TextField()
    daily_time = models.CharField(max_length=255)
    
    kalories = models.IntegerField()
    plan_goal_en = models.CharField(max_length=50)
    plan_goal_ar = models.CharField(max_length=50)
    
    weeks = models.PositiveSmallIntegerField()
    image = models.ImageField(upload_to='plans/images/', blank=True, null=True)
    owner = models.ForeignKey(AUTH_USER_MODEL,on_delete=models.CASCADE)
    sport = models.ForeignKey(Sport,on_delete=models.CASCADE,related_name='sport_plan')
    def __str__(self):
        return self.name_en
    
class Week(models.Model):
    plan = models.ForeignKey(Plan, on_delete=models.CASCADE, related_name='plan_weeks')
    number = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=255)

    class Meta:
        unique_together = ('plan', 'number')


class Day(models.Model):
    week = models.ForeignKey(Week, on_delete=models.CASCADE, related_name='plan_days')
    number = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=255)
    rest_between_exercises = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('week', 'number')


class ExerciseDetail(models.Model):
    day = models.ForeignKey(Day, on_delete=models.CASCADE, related_name='exercises',blank=True,null=True,default=None)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    sets = models.PositiveSmallIntegerField()
    reps_en = models.CharField(max_length=255)
    reps_ar = models.CharField(max_length=255)
    exercise_type = models.CharField(choices=EXERCISE_TYPE_CHOICES,default="main_exercise")
    rest_between_sets = models.PositiveSmallIntegerField()

class PlanSubscription(models.Model):
    plan = models.ForeignKey(Plan,on_delete=models.CASCADE)
    user = models.ForeignKey(AUTH_USER_MODEL,on_delete=models.CASCADE)
    # plan_type = models.CharField(choices=PLAN_TYPE_CHOICES,max_length=50)
    #start_date = models.DateTimeField(auto_now_add=True)
    #end_date = models.DateTimeField(null=True, blank=True)
    class Meta:
        unique_together = ('plan', 'user')

class PlanRequest(models.Model):
    """
    Represents a request from a user to a coach for a custom plan.
    """
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
    coach = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='received_plan_requests')
    sport = models.ForeignKey(Sport, on_delete=models.CASCADE)
    plan_type = models.CharField(max_length=255,choices=PLAN_TYPE_CHOICES)
    requested_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} → {self.coach} ({self.sport})"

class CoachQuestion(models.Model):
    """
    Questions defined by a coach to gather info before creating a plan.
    """
    coach = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='questions')
    plan_type = models.CharField(max_length=255,choices=PLAN_TYPE_CHOICES)
    question_en = models.TextField()
    question_ar = models.TextField()

    def __str__(self):
        return self.question_en

class UserAnswer(models.Model):
    """
    Stores user answers to coach questions.
    """
    plan_request = models.ForeignKey(PlanRequest, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(CoachQuestion, on_delete=models.CASCADE)
    answer = models.TextField()

    class Meta:
        unique_together = ('plan_request', 'question')

    def __str__(self):
        return f"Answer to: {self.question}"
    

class NutritionPlan(models.Model):
    name_en = models.CharField(max_length=255)
    name_ar = models.CharField(max_length=255)

    target = models.CharField(max_length=255)

    description_en = models.TextField()
    description_ar = models.TextField()

    advice_en = models.TextField(blank=True, null=True)
    advice_ar = models.TextField(blank=True, null=True)

    plan_pay_level =  models.CharField(max_length=100,choices=PLAN_PAY_LEVEL_CHOICES)
    weeks = models.PositiveSmallIntegerField()


    image = models.ImageField(upload_to='nutrition/images/', blank=True, null=True)

    owner = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='nutrition_plans'
    )
    # kalories = models.IntegerField()
    # protein = models.FloatField()  
    # carbs = models.FloatField()    
    # fats = models.FloatField()     

    # meals_daily_number = models.PositiveSmallIntegerField()
    # date_of_begin = models.DateField()



    def __str__(self):
        return self.name_en
    
class MealDetail(models.Model):
    plan = models.ForeignKey(
        NutritionPlan,
        on_delete=models.CASCADE,
        related_name='meals'
    )
    week = models.PositiveSmallIntegerField()
    day = models.PositiveSmallIntegerField()

    meal_number = models.PositiveSmallIntegerField() 
    meal_name_en = models.CharField(max_length=100)
    meal_name_ar = models.CharField(max_length=100)

    calories = models.IntegerField()
    protein = models.FloatField() 
    carbs = models.FloatField()
    fats = models.FloatField()

    class Meta:
        unique_together = ('plan', 'week', 'day', 'meal_number')

    # def __str__(self):
    #     return f"Week {self.week}, Day {self.day}, Meal {self.meal_number}"
    
class FoodItem(models.Model):
    meal = models.ForeignKey(
        MealDetail,
        on_delete=models.CASCADE,
        related_name='food_items'
    )
    name_en = models.CharField(max_length=100)
    name_ar = models.CharField(max_length=100)

    quantity = models.SmallIntegerField()

    def __str__(self):
        return f"{self.name_en} ({self.quantity})"