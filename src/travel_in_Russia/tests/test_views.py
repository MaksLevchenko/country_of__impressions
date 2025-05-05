from django.test import Client, TestCase, RequestFactory
from django.db.models import Avg
from django.urls import reverse
from travel_in_Russia.views import CityListView
from travel_in_Russia.models import City, Rating, RatingStar


class CityListViewTest(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.city1 = City.objects.create(
            name="Москва",
            url="Mosk",
            founding_date="1240 год",
            city_emblem="3.png",
        )
        cls.city2 = City.objects.create(
            name="Санкт-Петербург",
            url="Piterbur",
            founding_date="1703 год",
            city_emblem="3.png",
        )

        # Создаём значения звёзд рейтинга
        stars_3 = RatingStar.objects.create(value=3)
        stars_4 = RatingStar.objects.create(value=4)
        stars_5 = RatingStar.objects.create(value=5)

        # Создаем оценки для городов
        Rating.objects.create(city=cls.city1, star=stars_4)
        Rating.objects.create(city=cls.city1, star=stars_5)
        Rating.objects.create(city=cls.city2, star=stars_3)

    def test_get_queryset_returns_all_cities_with_average_rating(self):
        """Проверяет, что представление возвращает полный список городов с вычисленным средним рейтингом"""
        factory = RequestFactory()
        request = factory.get("/cities/")
        response = CityListView.as_view()(request)
        self.assertEqual(response.status_code, 200)

        cities = list(response.context_data["object_list"])

        # Среднее значение из представлений
        moscow_avg_rating = next(
            (c.middle_star for c in cities if c.name == "Москва"), None
        )
        spb_avg_rating = next(
            (c.middle_star for c in cities if c.name == "Санкт-Петербург"), None
        )

        # Средний рейтинг Москвы должен быть примерно равен 4.5
        self.assertAlmostEqual(moscow_avg_rating, 4.5, places=1)
        # Средний рейтинг СПб должен быть примерно равен 3
        self.assertAlmostEqual(spb_avg_rating, 3, places=1)

    def test_template_used_is_correct(self):
        """Проверяем, что используется верный шаблон для отображения страниц"""
        client = Client()
        response = client.get("/")
        self.assertTemplateUsed(response, "travel_in_Russia/city_list.html")
