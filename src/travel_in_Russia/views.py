from typing import Any
from django.contrib.auth.models import User
from django.db.models import Avg
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect
from django.views import generic, View

from travel_in_Russia.forms import (
    CityForm,
    InteriorPhotoForm,
    PhotoAttractionsForm,
    RatingForm,
    RestForm,
    ReviewForm,
    SightForm,
    UserForm,
    ProfileForm,
)
from travel_in_Russia.logic import (
    removing_duplicates,
    get_client_ip,
    get_founding_date_from_century,
)
from travel_in_Russia.models import (
    City,
    InteriorPhoto,
    PhotoAttractions,
    Rating,
    Restaurants,
    Sight,
)


class CenturyFounder:
    """Даты основания и основатели городов"""

    def get_century(self):
        year_list = [
            date["founding_date"][-7:-4]
            for date in City.objects.values("founding_date")
        ]
        century_list = []
        for century in year_list:
            if int(century[:2]) <= 9:
                century_list.append((0, "X век и старше"))
            elif century[:2] == "10":
                century_list.append((1, "XI век"))
            elif century[:2] == "11":
                century_list.append((2, "XII век"))
            elif century[:2] == "12":
                century_list.append((3, "XIII век"))
            elif century[:2] == "13":
                century_list.append((4, "XIV век"))
            elif century[:2] == "14":
                century_list.append((5, "XV век"))
            elif century[:2] == "15":
                century_list.append((6, "XVI век"))
            elif century[:2] == "16":
                century_list.append((7, "XVII век"))
            elif century[:2] == "17":
                century_list.append((8, "XVIII век"))
            elif century[:2] == "18":
                century_list.append((9, "XIX век"))
            elif century[:2] == "19":
                century_list.append((10, "XX век"))
            elif century[:2] == "20":
                century_list.append((11, "XXI век"))
        return sorted(list(set(century_list)))

    def get_founder(self):
        return removing_duplicates("founder")


class CityListView(CenturyFounder, generic.ListView):
    """Список городов"""

    model = City
    queryset = City.objects.all()
    # paginate_by = 6
    template_name = "travel_in_Russia/city_list.html"

    def get_queryset(self):
        queryset = City.objects.all().annotate(
            middle_star=Avg("rating__star__value", default=0)
        )
        return queryset


class CityDetailView(CenturyFounder, generic.DetailView):
    """Город"""

    model = City
    slug_field = "url"
    template_name = "travel_in_Russia/city_detail.html"

    def get_context_data(self, **kwargs):
        city = City.objects.filter(url=self.request.path_info[1:])
        context = super().get_context_data(**kwargs)
        context["star_form"] = RatingForm()
        context["form"] = ReviewForm()
        if Rating.objects.filter(
            ip=get_client_ip(self.request), city__url=self.request.path_info[1:]
        ).exists():
            context["rating_user"] = str(
                Rating.objects.filter(
                    ip=get_client_ip(self.request), city__url=self.request.path_info[1:]
                )
                .get()
                .star
            )
        else:
            context["rating_user"] = "0"
        context["middle_star"] = round(
            city.aggregate(Avg("rating__star", default=0))["rating__star__avg"],
            1,
        )
        return context


class AddStarRating(View):
    """Добавление рейтинга городу"""

    def post(self, request):
        form = RatingForm(request.POST)
        if form.is_valid():
            Rating.objects.update_or_create(
                ip=get_client_ip(request),
                city_id=int(request.POST.get("city")),
                defaults={"star_id": int(request.POST.get("star"))},
            )
            return HttpResponse(status=201)
        else:
            return HttpResponse(status=400)


class FilterCityView(CenturyFounder, generic.ListView):
    """Фильтр городов"""

    paginate_by = 4

    def get_queryset(self):
        if r"|".join(
            get_founding_date_from_century(self.request.GET.getlist("founding_date"))
        ):
            queryset = City.objects.filter(
                founder__in=self.request.GET.getlist("founder")
            ) | City.objects.filter(
                founding_date__iregex=r"|".join(
                    get_founding_date_from_century(
                        self.request.GET.getlist("founding_date")
                    )
                )
            )
        else:
            queryset = City.objects.filter(
                founder__in=self.request.GET.getlist("founder")
            ) | City.objects.filter(
                founding_date__in=self.request.GET.getlist("founding_date")
            )
        queryset = queryset.annotate(
            middle_star=Avg("rating__star", default=0)
        ).distinct()
        return queryset

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["founding_date"] = "".join(
            [f"founding_date={x}&" for x in self.request.GET.getlist("founding_date")]
        )
        context["founder"] = "".join(
            [f"founder={x}&" for x in self.request.GET.getlist("founder")]
        )
        return context


class Search(CenturyFounder, generic.ListView):
    """Поиск по названию"""

    paginate_by = 4

    def get_queryset(self):
        return City.objects.filter(name__icontains=self.request.GET.get("q"))

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(*args, **kwargs)
        context["q"] = f'q={self.request.GET.get("q")}&'
        return context


class AddReview(View):
    """Оставить отзыв"""

    def post(self, request, pk):
        form = ReviewForm(request.POST)
        city = City.objects.get(id=pk)
        if form.is_valid():
            form = form.save(commit=False)
            if request.POST.get("parent", None):
                form.parent_id = int(request.POST.get("parent"))
            form.city = city
            form.name_id = request.user.id
            form.save()
        return redirect(city.get_absolute_url())


class ProfileView(generic.DetailView):
    """Профиль пользователя"""

    model = User
    slug_field = "pk"
    template_name = "travel_in_Russia/profile.html"


class UpdateProfile(View):
    """Обновить профиль"""

    def post(self, request):
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(
            request.POST, request.FILES, instance=request.user.profile
        )
        profile_form.avatar = request.POST.get("avatar")
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()

            return redirect("/")
        else:
            return HttpResponse(status=400)


class RedactProfile(generic.DetailView):
    """Редактировать профиль"""

    model = User
    slug_field = "pk"
    template_name = "travel_in_Russia/update_profile.html"

    def get_context_data(self, **kwargs):
        user = self.request.user
        context = super().get_context_data(**kwargs)
        context["user_form"] = UserForm(instance=user)
        context["profile_form"] = ProfileForm(instance=user)
        return context


class AddCity(generic.FormView):
    """"""

    form_class = CityForm
    template_name = "travel_in_Russia/new_city.html"


class NewCity(View):
    """Добавление нового города"""

    def post(self, request):
        form = CityForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect("/")
        else:
            return HttpResponse(status=400)


class DeleteCity(generic.DetailView):
    """Удалить город"""

    model = City
    slug_field = "url"
    template_name = "travel_in_Russia/city_delete.html"


class ConfirmDeleteCity(View):
    """Подтверждение удаления города"""

    model = City

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        url = request.path_info.split("/")[2]
        city = City.objects.get(url=url)
        city.delete()
        return redirect("/")


class AddRest(generic.DetailView):
    """"""

    model = City
    slug_field = "url"
    template_name = "travel_in_Russia/new_rest.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = RestForm()
        return context


class NewRest(View):
    """Добавление нового ресторана"""

    model = City
    slug_field = "url"

    def post(self, request, slug):
        form = RestForm(request.POST, request.FILES)
        city = City.objects.get(url=slug)
        if form.is_valid():
            form = form.save(commit=False)
            form.city = city
            form.save()
            return redirect("/")
        else:
            return HttpResponse(status=400)


class DeleteRest(generic.DetailView):
    """Удалить ресторан"""

    model = Restaurants
    slug_field = "pk"
    template_name = "travel_in_Russia/rest_delete.html"


class ConfirmDelRest(View):
    """Подтверждение удаления ресторана"""

    model = Restaurants

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        id = request.path_info.split("/")[1]
        rest = Restaurants.objects.get(id=id)
        rest.delete()
        return redirect("/")


class AddSight(generic.DetailView):
    """"""

    model = City
    slug_field = "url"
    template_name = "travel_in_Russia/new_sight.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = SightForm()
        return context


class NewSight(View):
    """Добавление новой достопримечательости"""

    model = City
    slug_field = "url"

    def post(self, request, slug):
        form = SightForm(request.POST)
        city = City.objects.get(url=slug)
        if form.is_valid():
            form = form.save(commit=False)
            form.city = city
            form.save()
            return redirect("/")
        else:
            return HttpResponse(status=400)


class DeleteSight(generic.DetailView):
    """Удалить достопримечательность"""

    model = Sight
    slug_field = "pk"
    template_name = "travel_in_Russia/sight_delete.html"


class ConfirmDelSight(View):
    """Подтверждение удаления достопримечательности"""

    model = Sight

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        id = request.path_info.split("/")[1]
        sight = Sight.objects.get(id=id)
        sight.delete()
        return redirect("/")


class AddPhotoSight(generic.DetailView):
    """Добавление фото достопримечательности"""

    model = Sight
    slug_field = "pk"
    template_name = "travel_in_Russia/add_photo_sight.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = PhotoAttractionsForm()
        return context


class NewPhotoSight(View):
    """Добавление фото достопримечательости"""

    model = Sight
    slug_field = "pk"

    def post(self, request, pk):
        form = PhotoAttractionsForm(request.POST, request.FILES)
        sight = Sight.objects.get(id=pk)
        if form.is_valid():
            form = form.save(commit=False)
            form.sight = sight
            form.save()
            return redirect("/")
        else:
            return HttpResponse(status=400)


class DelPhotoSight(generic.DetailView):
    """Удалить фото достопримечательности"""

    model = PhotoAttractions
    slug_field = "pk"
    template_name = "travel_in_Russia/sight_photo_delete.html"


class ConfirmDelPhotoSight(View):
    """Подтверждение удаления фото достопримечательности"""

    model = PhotoAttractions

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        id = request.path_info.split("/")[1]
        photo = PhotoAttractions.objects.get(id=id)
        photo.delete()
        return redirect("/")


class AddPhotoRest(generic.DetailView):
    """Добавление фото ресторана"""

    model = Restaurants
    slug_field = "pk"
    template_name = "travel_in_Russia/add_photo_rest.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["form"] = InteriorPhotoForm()
        return context


class NewPhotoRest(View):
    """Добавление фото ресторана"""

    model = Restaurants
    slug_field = "pk"

    def post(self, request, pk):
        form = InteriorPhotoForm(request.POST, request.FILES)
        rest = Restaurants.objects.get(id=pk)
        print(form)
        if form.is_valid():
            form = form.save(commit=False)
            form.restaurant = rest
            form.save()
            return redirect("/")
        else:
            return HttpResponse(status=400)


class DelPhotoRest(generic.DetailView):
    """Удалить фото ресторана"""

    model = InteriorPhoto
    slug_field = "pk"
    template_name = "travel_in_Russia/rest_photo_delete.html"


class ConfirmDelPhotoRest(View):
    """Подтверждение удаления фото ресторан"""

    model = InteriorPhoto

    def post(self, request: HttpRequest, *args: str, **kwargs: Any) -> HttpResponse:
        id = request.path_info.split("/")[1]
        photo = InteriorPhoto.objects.get(id=id)
        photo.delete()
        return redirect("/")
