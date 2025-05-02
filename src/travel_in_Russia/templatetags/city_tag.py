from django import template
from django.db.models import Avg

from travel_in_Russia.models import City

register = template.Library()


@register.inclusion_tag('travel_in_Russia/tags/best_ratings.html')
def get_cities_with_best_rating(count=5):
    """Вывод городов с лучшим рейтингом"""
    cities = City.objects.all().annotate(
            middle_star=Avg('rating__star', default=0)
        ).order_by("-middle_star")[:count]
    return {"cities_with_best_rating": cities}
