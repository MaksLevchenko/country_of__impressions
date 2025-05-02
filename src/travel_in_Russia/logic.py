from travel_in_Russia.models import City


def removing_duplicates(duplicat):
    list_dict = ([founding_date for founding_date in City.objects.values(duplicat)])
    list_no_duplicates = sorted(list(set([i[duplicat] for i in list_dict])))
    return list_no_duplicates


def get_client_ip(request):
    """Получение IP пользователя"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_founding_date_from_century(century):
    founding_date = []
    for cen in century:
        if cen == 'X век':
            founding_date.append(' 9.. г.')
        elif cen == 'XI век':
            founding_date.append('10.. г.')
        elif cen == 'XII век':
            founding_date.append('11.. г.')
        elif cen == 'XIII век':
            founding_date.append('12.. г.')
        elif cen == 'IV век':
            founding_date.append('13.. г.')
        elif cen == 'V век':
            founding_date.append('14.. г.')
        elif cen == 'XVI век':
            founding_date.append('15.. г.')
        elif cen == 'XVII век':
            founding_date.append('16.. г.')
        elif cen == 'XVIII век':
            founding_date.append('17.. г.')
        elif cen == 'XIX век':
            founding_date.append('18.. г.')
        elif cen == 'XX век':
            founding_date.append('19.. г.')
        elif cen == 'XXI век':
            founding_date.append('20.. г.')
    return founding_date
