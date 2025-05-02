import os

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.urls import reverse


class City(models.Model):
    """Модель города"""

    name = models.CharField(max_length=50, verbose_name="Название города")
    description = models.TextField(verbose_name="Краткое описание города")
    city_emblem = models.ImageField(verbose_name="Герб", upload_to="city_emblem/")
    image = models.ImageField(verbose_name="Фото города", upload_to="city_photo/")
    url = models.SlugField(max_length=50, unique=True)
    founding_date = models.CharField(
        max_length=30, verbose_name="Дата основания города"
    )
    founder = models.CharField(max_length=30, verbose_name="Основатель города")

    def get_name(self):
        return self.name

    def get_absolute_url(self):
        return reverse("city_detail", kwargs={"slug": self.url})

    def __str__(self):
        return self.name

    def get_review(self):
        return self.reviews_set.filter(parent__isnull=True)

    class Meta:
        verbose_name = "Город"
        verbose_name_plural = "Города"


class Sight(models.Model):
    """Модель достопримечательности"""

    name = models.CharField(
        max_length=50, verbose_name="Название достопримечательности"
    )
    description = models.TextField(max_length=1500, verbose_name="Описание")
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    place = models.CharField(max_length=150, verbose_name="Месторасположения")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Достопримечательность"
        verbose_name_plural = "Достопримечательности"


class PhotoAttractions(models.Model):
    """Фото достопримечательности"""

    title = models.CharField(max_length=75, verbose_name="Заголовок")
    photo = models.ImageField(
        verbose_name="Фото достопримечательности", upload_to="photo_attractions/"
    )
    sight = models.ForeignKey(Sight, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Фото достопримечательности"
        verbose_name_plural = "Фото достопримечательностей"


class Restaurants(models.Model):
    """Рестораны города"""

    name = models.CharField(max_length=75, verbose_name="Название")
    city = models.ForeignKey(City, on_delete=models.CASCADE)
    kitchen = models.CharField(max_length=300, verbose_name="Кухня")
    description = models.TextField(max_length=1550, verbose_name="Описание")
    photo = models.ImageField(verbose_name="Основное фото", upload_to="restaurants/")
    link = models.URLField(verbose_name="Ссылка", default="Нет сайта")
    place = models.CharField(max_length=300, verbose_name="Адрес")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Ресторан"
        verbose_name_plural = "Рестораны"


class InteriorPhoto(models.Model):
    """Фото интерьера ресторана"""

    title = models.CharField(max_length=75, verbose_name="Заголовок")
    image = models.ImageField(
        verbose_name="Фото интерьера", upload_to="interior_photo/"
    )
    restaurant = models.ForeignKey(Restaurants, on_delete=models.CASCADE)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Фото интерьера"
        verbose_name_plural = "Фото интерьера"


class RatingStar(models.Model):
    """Звезда рейтинга"""

    value = models.SmallIntegerField("Значение", default=0)

    def __str__(self):
        return f"{self.value}"

    class Meta:
        verbose_name = "Звезда рейтинга"
        verbose_name_plural = "Звезды рейтинга"
        ordering = ["-value"]


class Rating(models.Model):
    """Рейтинг"""

    ip = models.CharField("IP адрес", max_length=15)
    star = models.ForeignKey(
        RatingStar, on_delete=models.CASCADE, verbose_name="звезда"
    )
    city = models.ForeignKey(
        City, on_delete=models.CASCADE, verbose_name="город", related_name="rating"
    )

    def __str__(self):
        return f"{self.star}"

    class Meta:
        verbose_name = "Рейтинг"
        verbose_name_plural = "Рейтинги"


class Reviews(models.Model):
    """Отзывы"""

    email = models.EmailField(editable=True)
    name = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField("Сообщение", max_length=5000)
    parent = models.ForeignKey(
        "self",
        verbose_name="родитель",
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
    )
    city = models.ForeignKey(City, verbose_name="город", on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.name} - {self.city}"

    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"


class Profile(models.Model):
    """Профиль пользователя"""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar = models.ImageField(
        verbose_name="Аватар пользователя",
        upload_to="profile/",
        default="../static/images/te2.jpg",
    )
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата рождения")

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"


class TelegramSubscriber(models.Model):
    """Подписчики в телеграме"""

    user_id = models.BigIntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.user_id)
