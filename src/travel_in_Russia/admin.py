from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django import forms
from django.contrib import admin
from django.contrib.admin.models import LogEntry
from django.utils.safestring import mark_safe

from travel_in_Russia.models import (
    City,
    Sight,
    Reviews,
    Rating,
    RatingStar,
    PhotoAttractions,
    Restaurants,
    InteriorPhoto,
    Profile,
)


class CityAdminForm(forms.ModelForm):
    description = forms.CharField(label="Описание", widget=CKEditorUploadingWidget())

    class Meta:
        model = City
        fields = "__all__"


@admin.register(Sight)
class SightAdmin(admin.ModelAdmin):
    """Достопримечательности"""

    list_display = ("city", "name")
    list_display_links = ("name",)


class ReviewInline(admin.TabularInline):
    """Отзывы на странице города"""

    model = Reviews
    extra = 1
    readonly_fields = ("name", "email")


@admin.register(City)
class CityAdmin(admin.ModelAdmin):
    """Города"""

    list_display = ("name", "founding_date", "url")
    list_filter = ("founding_date",)
    search_fields = ("description", "founding_date__name")
    inlines = [ReviewInline]
    save_on_top = True
    save_as = True
    form = CityAdminForm
    actions = ["publish", "unpublish"]
    fieldsets = (
        (None, {"fields": (("name", "description"),)}),
        (None, {"fields": (("city_emblem", "image"),)}),
        (None, {"fields": (("founding_date", "founder"),)}),
        ("Options", {"fields": (("url",),)}),
    )

    def unpublish(self, request, queryset):
        """Снять с публикации"""
        row_update = queryset.update(draft=True)
        if row_update == 1:
            message_bit = "1 запись была обновленна"
        else:
            message_bit = f"{row_update} записей были обновленны"

        self.message_user(request, f"{message_bit}")

    def publish(self, request, queryset):
        """Опубликовать"""
        row_update = queryset.update(draft=False)
        if row_update == 1:
            message_bit = "1 запись была обновленна"
        else:
            message_bit = f"{row_update} записей были обновленны"

        self.message_user(request, f"{message_bit}")

    publish.short_description = "Опубликовать"
    publish.allowed_permissions = ("change",)

    unpublish.short_description = "Снять с публикации"
    unpublish.allowed_permissions = ("change",)


@admin.register(Reviews)
class ReviewsAdmin(admin.ModelAdmin):
    """Отзывы"""

    list_display = ("name", "email", "parent", "city", "id")
    # readonly_fields = ("name", "email")


@admin.register(Rating)
class RatingAdmin(admin.ModelAdmin):
    """Рейтинг"""

    list_display = ("city", "star", "ip")


@admin.register(PhotoAttractions)
class MovieShotsAdmin(admin.ModelAdmin):
    """Фото достопримечательности"""

    list_display = ("title", "sight", "get_image")
    readonly_fields = ("get_image",)

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.photo.url} width="auto" height="60">')

    get_image.short_description = "Фото"


@admin.register(Restaurants)
class RestaurantsAdmin(admin.ModelAdmin):
    """Рестораны"""

    list_display = ("name", "city", "link")
    list_display_links = ("name",)


@admin.register(InteriorPhoto)
class InteriorPhotoAdmin(admin.ModelAdmin):
    """Фото интерьера"""

    list_display = ("restaurant", "title", "get_image")
    list_display_links = ("restaurant",)
    readonly_fields = ("get_image",)

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.image.url} width="auto" height="60">')

    get_image.short_description = "Фото"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """Профили пользователей"""

    list_display = ("user", "birth_date", "get_image")
    list_display_links = ("user",)
    readonly_fields = ("get_image",)

    def get_image(self, obj):
        return mark_safe(f'<img src={obj.avatar.url} width="auto" height="60">')


admin.site.register(RatingStar)
admin.site.register(LogEntry)

admin.site.site_title = "Панель администратора"
admin.site.site_header = "Панель администратора"
