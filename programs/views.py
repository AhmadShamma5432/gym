# views.py
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Plan
from .serializers import * 
from .permissions import * 

# class PlanViewSet(viewsets.ModelViewSet):
#     serializer_class = PlanSerializer

#     def get_queryset(self):
#         return Plan.objects.filter(user=self.request.user)

#     def perform_create(self, serializer):
#         serializer.save(user=self.request.user)

class ExerciseViewSet(viewsets.ModelViewSet):
    serializer_class = ExerciseSerializer
    permission_classes = [IsCoachOrStaff]

    def get_queryset(self):
        return Exercise.objects.select_related('coach')\
                               .prefetch_related('exercise_detail').filter(coach=self.request.user)
    
    def get_serializer_context(self):
        return {"coach": self.request.user}
    
class PlanViewSet(viewsets.ModelViewSet):
    queryset = Plan.objects.all()
    serializer_class = PlanSerializer
    # permission_classes = [IsCoachOrStaff]

    def get_serializer_context(self):
        try: plan_id = self.kwargs['pk']
        except: plan_id = None
        return {'user': self.request.user,
                'plan_id': plan_id
                }

                