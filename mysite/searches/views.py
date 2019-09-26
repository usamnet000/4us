from django.shortcuts import render

from listings.models import Listing,Save

from .models import SearchQuery

import json
from django.core.files.base import ContentFile
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.auth.forms import AuthenticationForm
from listings.forms import RegisterForm

def search_view(request):
    query = request.GET.get('q', None)
    user = None
    if request.user.is_authenticated:
        user = request.user
    context =  {"query": query,'search':1}
    if query is not None:
        SearchQuery.objects.create(user=user, query=query)
        listing_list = None
        if query.isnumeric():
            listing_list = Listing.objects.filter(is_published=True).filter(pk=int(query))
        else:
            listing_list = Listing.objects.filter(is_published=True).search(query=query)

        context['listing_list'] = listing_list
        context['count']=listing_list.count()
        context['type'] = request.GET.get('type', None)

        places = listing_list.values_list('pk', 'price', 'place__image_main_path', 'place__address', 'place__latitude', 'place__longitude')
        context['places_json'] = json.dumps(list(places), cls=DjangoJSONEncoder)
    else:
        type = request.GET.get('type', None)
        if type == "fsbo":
            option = 1
        elif type == "coming-soon":
            option = 2
        elif type == "mo":
            option = 3
        elif type == "new-homes":
            option = 4
        elif type == "open-house":
            option = 5
        else:
            option = False

        max_price=None
        min_price=None
        if request.GET.get('price-exposed-max') or request.GET.get('price-exposed-min'):
            max_price = int(request.GET.get('price-exposed-max', 0)) * int('1000000')
            min_price = int(request.GET.get('price-exposed-min', 0)) * int('1000000')

        values={}
        bedsoption=request.GET.get('options')
        if request.GET.get('exact'):
            values = {'place__city': request.GET.get('city',None), 'property_type': option, 'price__range' :(min_price, max_price),'bedrooms':request.GET.get('beds-options')}
        else:
            if bedsoption == 0:
                values = {'place__city': request.GET.get('city', None), 'property_type': option,
                          'price__range': (min_price, max_price)}
            else:
                values = {'place__city': request.GET.get('city', None), 'property_type': option,
                      'price__range': (min_price, max_price), 'bedrooms__gte': bedsoption}

        arguments = {}
        for k, v in values.items():
            if v:
                if isinstance(v, tuple):
                    if all(v):
                        arguments[k] = v
                else:
                    arguments[k] = v
        print(arguments)

        listing_list = Listing.objects.filter(is_published=True).filter(**arguments)
        context['count'] = listing_list.count()
        context['listing_list'] = listing_list
        context['type'] = type
        places = listing_list.values_list('pk', 'price', 'place__image_main_path', 'place__address',
                                          'place__latitude',
                                          'place__longitude')
        context['places_json'] = json.dumps(list(places), cls=DjangoJSONEncoder)
        if request.user.is_authenticated:
            context['countSaved']= Save.objects.filter(user=request.user).count()

    context['formLogin'] = AuthenticationForm()
    context['formRegister'] = RegisterForm()

    return render(request, 'Main.html',context)