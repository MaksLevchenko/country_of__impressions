from django import forms
from django.contrib.auth.models import User

from travel_in_Russia.models import InteriorPhoto, PhotoAttractions, Rating, RatingStar, Restaurants, Reviews, Profile, City, Sight


class ReviewForm(forms.ModelForm):
    """Форма отзывов"""

    class Meta:
        model = Reviews
        fields = ("text",)
        widgets = {
            "text": forms.Textarea(attrs={"class": "form-control border", "id": "contactcomment"}),
        }


class RatingForm(forms.ModelForm):
    """Форма добавления рейтинга"""
    star = forms.ModelChoiceField(
        queryset=RatingStar.objects.all(), widget=forms.RadioSelect(), empty_label=None
    )

    class Meta:
        model = Rating
        fields = ("star",)


class UserForm(forms.ModelForm):
    """Форма пользователя"""

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")


class ProfileForm(forms.ModelForm):
    """Форма профиля пользователя"""

    class Meta:
        model = Profile
        fields = ("birth_date", "avatar")


class CityForm(forms.ModelForm):
    """Форма города"""

    class Meta:
        model = City
        fields = "__all__"


class RestForm(forms.ModelForm):
    """Форма ресторана"""

    class Meta:
        model = Restaurants
        fields = ("name", "kitchen", "description", "photo", "link", "place")
        # fields = "__all__"


class SightForm(forms.ModelForm):
    """Форма достопримечательности"""

    class Meta:
        model = Sight
        fields = ('name', 'description', 'place')


class PhotoAttractionsForm(forms.ModelForm):
    """Форма фото достопримечательности"""

    class Meta:
        model = PhotoAttractions
        fields = ('title', 'photo')


class InteriorPhotoForm(forms.ModelForm):
    """Форма фото ресторана"""

    class Meta:
        model = InteriorPhoto
        fields = ('title', 'image')
