from dal import autocomplete
from django.http import JsonResponse
from .models import SubCategory, Brand

class SubCategoryAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = SubCategory.objects.all()

        if self.q:
            qs = qs.filter(name_en__icontains=self.q) | qs.filter(name_ar__icontains=self.q)

        return qs

class BrandAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = Brand.objects.all()

        if self.q:
            qs = qs.filter(name_en__icontains=self.q) | qs.filter(name_ar__icontains=self.q)

        return qs