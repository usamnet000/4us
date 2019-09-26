from django.shortcuts import render,get_object_or_404,redirect
from django.http import HttpResponse, JsonResponse
from django.core.mail import send_mail
# Create your views here.
from django.views.generic import ListView, View,DetailView
from .forms import AddressForm,RegisterForm,EditProfileForm,UnitForm
from .models import Photo,Listing,Place,TimeOpenHouse,Email,UserProfile,Save, Post, Topic
from django.utils.decorators import method_decorator

import os
import base64
from decimal import Decimal
import json
from django.core.files.base import ContentFile
from django.core.serializers.json import DjangoJSONEncoder
import re

from django.contrib import messages
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.core.paginator import Paginator
from django.core.paginator import EmptyPage
from django.core.paginator import PageNotAnInteger

from .forms import RegisterForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login,logout
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import PasswordChangeForm

from django.http import HttpResponseRedirect

#users = User.objects.exclude(id=request.user.id)

from django.contrib.auth.decorators import login_required
from django.core import serializers

from django.db.models import Count
import datetime
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.template import loader

from django.db.models.functions import Radians, Power, Sin, Cos, ATan2, Sqrt, Radians
from django.db.models import F

from searches.models import SearchQuery

from django.shortcuts import (
render_to_response
)
from django.template import RequestContext

from django.db.models.expressions import F, Window
from django.db.models.functions.window import RowNumber
from django.utils.dateparse import parse_date

def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid

def index(request):
  return render(request, 'index.html',{})

def decimal_default(obj):
  if isinstance(obj, Decimal):
    return float(obj)
  raise TypeError

def image_as_base64(image_file, format='png'):
    """
    :param `image_file` for the complete path of image.
    :param `format` is format for image, eg: `png` or `jpg`.
    """
    if not os.path.isfile(image_file):
        return None

    encoded_string = ''
    with open(image_file, 'rb') as img_f:
        encoded_string = base64.b64encode(img_f.read()).decode()
    return 'data:image/%s;base64,%s' % (format, encoded_string)

def For_Sale_Listing(request,id):
    try:
        listing = Listing.objects.filter(pk=id)
        listing_json = serializers.serialize("json", listing)

        photos = Photo.objects.filter(listing=listing[0])
        output = []
        for photo in photos:
            output.append(image_as_base64( photo.image.path))
        photos_json =json.dumps({'photos': output}, indent=4)

        times = TimeOpenHouse.objects.filter(listing=listing[0]).values_list(
            'dateField', 'timeDropDownStart', 'timeDropDownEnd')
        times_json = json.dumps(list(times), cls=DjangoJSONEncoder)

        ListingView = Listing.objects.get(pk=id)
        session_key = 'viewed_listing_{}'.format(ListingView.pk)
        if not request.session.get(session_key, False):
            ListingView.views += 1
            ListingView.save()
            request.session[session_key] = True
        countSaved=Save.objects.filter(listing=ListingView).count()

        SimilarListings = Listing.objects.filter(is_published=True).filter(price__range=(ListingView.price-5000000,ListingView.price+5000000))
        ListingsInfo = SimilarListings.values_list('place__image_main_path', 'place__address', 'place__latitude', 'place__longitude','list_date','price','lotSize','pk')
        SimilarListings_json= json.dumps(list(ListingsInfo), cls=DjangoJSONEncoder)

        NearByListings = Listing.objects.filter(is_published=True).filter(place__latitude__range=(ListingView.place.latitude-Decimal(0.1),ListingView.place.latitude+Decimal(0.1)),place__longitude__range=(ListingView.place.longitude-Decimal(0.1),ListingView.place.longitude+Decimal(0.1)))
        ListingsInfo = NearByListings.values_list('place__image_main_path', 'place__address', 'place__latitude', 'place__longitude', 'list_date','price','lotSize','pk')
        NearByListings_json = json.dumps(list(ListingsInfo), cls=DjangoJSONEncoder)

        pro_type = ListingView.property_type
        userprofile = UserProfile.objects.filter(user=ListingView.user)
        Professional = serializers.serialize("json", userprofile)

    except Listing.DoesNotExist:
        raise Http404('places not found!')
    data = {"listing_json": listing_json,'photos_json':photos_json,'times_json':times_json,'countSaved':countSaved,'listingView':ListingView.views,'SimilarListings_json':SimilarListings_json,'NearByListings_json':NearByListings_json,'Professional':Professional,'pro_type':pro_type}
    return JsonResponse(data)

def ContactAgent(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        message = request.POST.get('message')
        user = User.objects.get(pk=request.POST.get('mo'))
        scheduleDateTime = request.POST.get('scheduleDateTime')
        if not scheduleDateTime:
            send_mail('بريد تجربي فرص- من' + name,
                      'البريد الإلكتروني التابع له:' + email + '\n\n' + phone + '\n\n' + "ما يود ذكرة:" + message,
                      'usamnet000@gmail.com', [user.username], fail_silently=False)
        else:
            send_mail('بريد تجربي فرص- من' + name, 'البريد الإلكتروني التابع له:' + email + '\n\n' + phone + '\n\n'  + "ما يود ذكرة:" + message+"يريد ان يحصل على جولة في المنزل "+scheduleDateTime,
                  'usamnet000@gmail.com', [user.username], fail_silently=False)
        responseData = {
            'status': 'ok',
            'message': 'شكرا لقد تمت العملية بنجاح !'
        }
        return JsonResponse(responseData)

def ContactAgentProfile(request,id):
    listing = Listing.objects.get(pk=id)
    pro_type = listing.property_type
    userprofile=UserProfile.objects.filter(user=listing.user)
    pro = serializers.serialize("json", userprofile)
    data = {'pro_type':pro_type,'pro':pro}
    return JsonResponse(data)

class For_Sale_Listings(DetailView):
    template_name = 'Main.html'

    def get_context_data(self, **kwargs):
        if 'formLogin' not in kwargs:
            kwargs['formLogin'] = AuthenticationForm()
            kwargs['page'] = 2
        if 'formRegister' not in kwargs:
            kwargs['formRegister'] = RegisterForm()
            kwargs['page'] = 1
        self.kwargs.setdefault('city', 'Taiz')
        if self.kwargs['city'] == "city":
            self.kwargs['city'] = 'Taiz'
        self.kwargs.setdefault('type', 'mo')
        type = self.kwargs['type']
        kwargs['type'] = type
        if type == "fsbo":
            option = 1
        elif type == "coming-soon":
            option = 2
        elif type == "new-homes":
            option = 4
        elif type == "open-house":
            option = 5
        elif type == "mo":
            option = 3
        else:
            option = False
        values = {'place__city': self.kwargs['city'], 'property_type': option}
        arguments = {}
        for k, v in values.items():
            if v:
                arguments[k] = v
        listings = Listing.objects.order_by('-list_date').filter(is_published=True).filter(
            **arguments)
        count = listings.filter(**arguments).count()
        paginator = Paginator(listings, 8)
        page = self.request.GET.get('page')
        try:
            listings = paginator.page(page)
        except PageNotAnInteger:
            listings = paginator.page(1)
        except EmptyPage:
            listings = paginator.page(paginator.num_pages)
        kwargs['listings'] = listings
        kwargs['count'] = count
        listingss = Listing.objects.filter(is_published=True).filter(**arguments).values_list(
            'pk', 'price', 'place__image_main_path', 'place__address', 'place__latitude', 'place__longitude',
            'list_date')
        kwargs['places_json'] = json.dumps(list(listingss), cls=DjangoJSONEncoder)

        if listings:
            kwargs['city'] = listings[0].place.get_city_display
            kwargs['type_display'] = listings[0].get_property_type_display
        if self.request.user.is_authenticated:
            kwargs['countSaved']= Save.objects.filter(user=self.request.user).count()
        return kwargs

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        ctxt = {}
        if 'login' in request.POST:
            formLogin = AuthenticationForm(request=request, data=request.POST)
            if formLogin.is_valid():
                username = formLogin.cleaned_data.get('username')
                password = formLogin.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.info(request, "تم تسجيل دخولك الآن باسم {username}")
                    return redirect('For-Sale-Listings')
                else:
                    messages.error(request, " هناك خطأ في اسم المستخدم أو كلمة مرور. ")
            else:
                ctxt['formLogin'] = formLogin

        elif 'register' in request.POST:
            formRegister = RegisterForm(request.POST)
            if formRegister.is_valid():
                username = formRegister.cleaned_data.get('username')
                password = formRegister.cleaned_data.get('password')
                user = formRegister.save()

                if 'proCheck' in request.POST:
                    print(request.POST.get('proSelect'))
                    userprofile = get_object_or_404(UserProfile, user=user)
                    pro = request.POST.get('proSelect')
                    if not pro:
                        pro = None

                    firstName = request.POST.get('inputs-firstName')
                    if not firstName:
                        firstName = None
                    lastName = request.POST.get('inputs-lastName')
                    if not lastName:
                        lastName = None
                    phone = request.POST.get('extension') + request.POST.get('inputs-phone')
                    if not phone:
                        phone = None
                    userprofile.pro = pro
                    userprofile.firstName = firstName
                    userprofile.lastName = lastName
                    userprofile.phone = phone
                    userprofile.save()

                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('For-Sale-Listings')
            else:
                ctxt['formRegister'] = formRegister

        return render(request, self.template_name, self.get_context_data(**ctxt))

class For_Sale_Listings_Sort(DetailView):
    template_name = 'Main.html'

    def get_context_data(self, **kwargs):
        city = self.request.GET.get('city', 'Taiz')
        type = self.request.GET.get('type', 'mo')
        kwargs['type'] = type
        if type == "fsbo":
            option = 1
        elif type == "coming-soon":
            option = 2
        elif type == "new-homes":
            option = 4
        elif type == "open-house":
            option = 5
        elif type == "mo":
            option = 3
        else:
            option = False
        values = {'place__city': city, 'property_type': option}
        arguments = {}
        for k, v in values.items():
            if v:
                arguments[k] = v
        listings = Listing.objects.filter(is_published=True).filter(**arguments)
        by = self.request.GET.get('by', 'globalrelevanceex_sort')
        if by == "priced_sort":
            listings = listings.order_by('-price')
        elif by == "pricea_sort":
            listings = listings.order_by('price')
        elif by == "days_sort":
            listings = listings.order_by('-list_date')
        elif by == "beds_sort":
            listings = listings.order_by('-bedrooms')
        elif by == "baths_sort":
            listings = listings.order_by('-Bathrooms')
        elif by == "size_sort":
            listings = listings.order_by('-livingArea')
        elif by == "lot_sort":
            listings = listings.order_by('-lotSize')
        else:
            listings = listings.order_by('-list_date')

        count = listings.count()
        listingslist = listings.values_list(
            'pk', 'price', 'place__image_main_path', 'place__address', 'place__latitude', 'place__longitude',
            'list_date')
        kwargs['places_json'] = json.dumps(list(listingslist), cls=DjangoJSONEncoder)
        paginator = Paginator(listings, 8)
        page = self.request.GET.get('page')
        try:
            listings = paginator.page(page)
        except PageNotAnInteger:
            listings = paginator.page(1)
        except EmptyPage:
            listings = paginator.page(paginator.num_pages)
        kwargs['listings'] = listings
        kwargs['count'] = count


        if listings:
            kwargs['city'] = listings[0].place.get_city_display
            kwargs['type_display'] = listings[0].get_property_type_display
        if self.request.user.is_authenticated:
            kwargs['countSaved'] = Save.objects.filter(user=self.request.user).count()

        kwargs['formLogin'] = AuthenticationForm()
        kwargs['formRegister'] = RegisterForm()
        return kwargs

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())


class For_Sale_Address(View):
    def get(self, *args, **kwargs):
      form = AddressForm()
      context = {
        'form': form
      }
      return render(self.request, "AddressForSale.html", context)

    def post(self, *args, **kwargs):
        form = AddressForm(self.request.POST or None)
        if form.is_valid():
          self.request.session['address'] = form.cleaned_data.get('address')
          self.request.session['latitude'] = json.dumps(json.dumps(form.cleaned_data.get('latitude'), cls=DjangoJSONEncoder))
          self.request.session['longitude'] = json.dumps(json.dumps(form.cleaned_data.get('longitude'), cls=DjangoJSONEncoder))
          self.request.session['city'] = self.request.POST['citySelection']
          return redirect("For-Sale-Post")
        return render(self.request, "AddressForSale.html", {form:form})

class For_Sale_Post(View):

  def get(self, *args, **kwargs):
      if (self.request.GET.get('removePhotoOnLoad', False)):

          if not 'saved' in self.request.session or not self.request.session['saved']:
              self.request.session['saved'] = []
          else:
              for id in self.request.session['saved']:
                  Photo.objects.get(pk=id).delete()
              del self.request.session['saved']
              self.request.session['saved'] = []
              return JsonResponse({'status': 'ok'})  # del request.session['saved']

      context = {
          'latitude': self.request.session['latitude'],
          'longitude': self.request.session['longitude'],
      }
      return render(self.request, 'PostForSale.html', context)

  def post(self, *args, **kwargs):
      myfile = self.request.FILES['file'] if 'file' in self.request.FILES else False
      if myfile:
          photo = Photo.objects.create(image=myfile)
          if not 'saved' in self.request.session or not self.request.session['saved']:
              self.request.session['saved'] = [photo.id]
          else:
              saved_list = self.request.session['saved']
              saved_list.append(photo.id)
              self.request.session['saved'] = saved_list


          responseData = {
              'status': 'ok',
              'path': "http://127.0.0.1:8000" + photo.image.url,
          }
          return JsonResponse(responseData)

      else:
          propertyType=self.request.POST.get('propertyType')
          price = self.request.POST.get('price')
          if price:
              price = int(float(re.sub(',', '', self.request.POST.get('price'))))

          roomsTotal = self.request.POST.get('roomsTotal')
          if not roomsTotal:
              roomsTotal = None
          Bathrooms = self.request.POST.get('Bathrooms')
          bedrooms = self.request.POST.get('bedrooms')
          Receptionrooms = self.request.POST.get('Receptionrooms')
          livingArea = self.request.POST.get('livingArea')
          lotSize = self.request.POST.get('lotSize')
          unitType = self.request.POST.get('unitType')

          yearBuilt = self.request.POST.get('yearBuilt')
          if not yearBuilt:
              yearBuilt = None
          remodelYear = self.request.POST.get('remodelYear')
          if not remodelYear:
              remodelYear = None

          hoaPrice = self.request.POST.get('hoaPrice')
          if not hoaPrice:
              hoaPrice = None
          groundTankSize = self.request.POST.get('groundTankSize')
          if not groundTankSize:
              groundTankSize = None
          garageSize = self.request.POST.get('garageSize')
          if not garageSize:
              garageSize = None
          homeDescription = self.request.POST.get('homeDescription')
          if not homeDescription:
              homeDescription = None

          whatYouLoveDescription = self.request.POST.get('whatYouLoveDescription')
          if not whatYouLoveDescription:
              whatYouLoveDescription = None

          Dishwasher = self.request.POST.get('id81481', '') == 'on'
          Dryer = self.request.POST.get('id81482', '') == 'on'
          Freezer = self.request.POST.get('id81483', '') == 'on'
          GarbageDisposal = self.request.POST.get('id81484', '') == 'on'
          Microwave = self.request.POST.get('id81485', '') == 'on'
          Oven = self.request.POST.get('id81486', '') == 'on'
          Refrigerator = self.request.POST.get('id81487', '') == 'on'
          Washer = self.request.POST.get('id81489', '') == 'on'

          RadioGroup_Rashan = self.request.POST.get('RadioGroup_Rashan')
          if not RadioGroup_Rashan:
              RadioGroup_Rashan = None

          ACarpet = self.request.POST.get('id82490', '') == 'on'
          AConcrete = self.request.POST.get('id82491', '') == 'on'
          ATiles = self.request.POST.get('id82492', '') == 'on'
          ALinoleum = self.request.POST.get('id82494', '') == 'on'
          ADSoftwood = self.request.POST.get('id82496', '') == 'on'
          ADOther = self.request.POST.get('id82498', '') == 'on'

          BreakfastNook = self.request.POST.get('id83499', '') == 'on'
          DiningRoom = self.request.POST.get('id83500', '') == 'on'
          FamilyRoom = self.request.POST.get('id83501', '') == 'on'
          LaundryRoom = self.request.POST.get('id83502', '') == 'on'
          Library = self.request.POST.get('id83503', '') == 'on'
          MasterBath = self.request.POST.get('id83504', '') == 'on'
          Office = self.request.POST.get('id83506', '') == 'on'
          Workshop = self.request.POST.get('id83509', '') == 'on'


          roomCount = self.request.POST.get('roomCount')
          if not roomCount:
              roomCount = None

          attic = self.request.POST.get('attic', '') == 'on'
          cableReady = self.request.POST.get('cableReady', '') == 'on'
          ceilingFan = self.request.POST.get('ceilingFan', '') == 'on'
          doublePaneWindows = self.request.POST.get('doublePaneWindows', '') == 'on'
          fireplace = self.request.POST.get('fireplace', '') == 'on'
          intercom = self.request.POST.get('intercom', '') == 'on'
          jettedTub = self.request.POST.get('jettedTub', '') == 'on'
          securitySystem = self.request.POST.get('securitySystem', '') == 'on'

          CCentral = self.request.POST.get('id1822', '') == 'on'
          CEvaporative = self.request.POST.get('id1823', '') == 'on'
          CGeothermal = self.request.POST.get('id1824', '') == 'on'
          CRefrigeration = self.request.POST.get('id18260', '') == 'on'
          CSolar = self.request.POST.get('id1826', '') == 'on'
          CWall = self.request.POST.get('id1827', '') == 'on'
          COther = self.request.POST.get('id1825', '') == 'on'
          CNone = self.request.POST.get('id18465', '') == 'on'
          HForcedAir = self.request.POST.get('id1749', '') == 'on'
          HGeothermal = self.request.POST.get('id17750', '') == 'on'
          HHeatPump = self.request.POST.get('id1750', '') == 'on'
          HRadiant = self.request.POST.get('id1752', '') == 'on'
          HStove = self.request.POST.get('id1754', '') == 'on'
          HWall = self.request.POST.get('id1755', '') == 'on'
          HOther = self.request.POST.get('id1751', '') == 'on'
          FCoal = self.request.POST.get('id1639', '') == 'on'
          FElectric = self.request.POST.get('id1640', '') == 'on'
          FGas = self.request.POST.get('id1641', '') == 'on'
          FOil = self.request.POST.get('id1643', '') == 'on'
          FPropaneButane = self.request.POST.get('id1645', '') == 'on'
          FSolar = self.request.POST.get('id1646', '') == 'on'
          FWoodPellet = self.request.POST.get('id1647', '') == 'on'
          FOther = self.request.POST.get('id1644', '') == 'on'
          FNone = self.request.POST.get('id16464', '') == 'on'

          basketballCourt = self.request.POST.get('basketballCourt', '') == 'on'
          doorman = self.request.POST.get('doorman', '') == 'on'
          elevator = self.request.POST.get('elevator', '') == 'on'
          fitnessCenter = self.request.POST.get('fitnessCenter', '') == 'on'
          gatedEntry = self.request.POST.get('gatedEntry', '') == 'on'
          nearTransportation = self.request.POST.get('nearTransportation', '') == 'on'
          tennisCourt = self.request.POST.get('tennisCourt', '') == 'on'

          RadioGroup_Architectural = self.request.POST.get('RadioGroup_Architectural')
          if not RadioGroup_Architectural:
              RadioGroup_Architectural = None

          Brick = self.request.POST.get('id1228', '') == 'on'
          CementConcrete = self.request.POST.get('id1229', '') == 'on'
          Stone = self.request.POST.get('id1234', '') == 'on'
          EOther = self.request.POST.get('id1232', '') == 'on'

          FloorCount = self.request.POST.get('FloorCount')
          if not FloorCount:
              FloorCount = None
          ApartmentsCount = self.request.POST.get('ApartmentsCount')
          if not ApartmentsCount:
              ApartmentsCount = None

          barbecueArea = self.request.POST.get('barbecueArea', '') == 'on'
          dock = self.request.POST.get('dock', '') == 'on'
          garden = self.request.POST.get('garden', '') == 'on'
          hotTubSpa = self.request.POST.get('hotTubSpa', '') == 'on'
          pool = self.request.POST.get('pool', '') == 'on'
          rvParking = self.request.POST.get('rvParking', '') == 'on'
          sauna = self.request.POST.get('sauna', '') == 'on'
          sprinklerSystem = self.request.POST.get('sprinklerSystem', '') == 'on'

          PGarageAttached = self.request.POST.get('id1457', '') == 'on'
          PGarageDetached = self.request.POST.get('id1458', '') == 'on'
          POffStreet = self.request.POST.get('id1460', '') == 'on'
          POnStreet = self.request.POST.get('id1461', '') == 'on'
          PNone = self.request.POST.get('id14462', '') == 'on'

          garageSpaces = self.request.POST.get('garageSpaces')
          if not garageSpaces:
              garageSpaces = None

          RAsphalt = self.request.POST.get('id1168', '') == 'on'
          RMetal = self.request.POST.get('id1171', '') == 'on'
          RTiles = self.request.POST.get('id1172', '') == 'on'

          VOnSea = self.request.POST.get('id1378', '') == 'on'
          VMountain = self.request.POST.get('id1379', '') == 'on'
          VOnStreet = self.request.POST.get('id1380', '') == 'on'
          VOther = self.request.POST.get('id1381', '') == 'on'

          fullPhoneNumber = self.request.POST.get('fullPhoneNumber')
          if not fullPhoneNumber:
              fullPhoneNumber = None

          if is_valid_form([propertyType, price, Bathrooms,bedrooms,Receptionrooms,livingArea,lotSize]):
              latitude=''.join((ch if ch in '0123456789.' else '') for ch in self.request.session['latitude'])
              longitude = ''.join((ch if ch in '0123456789.' else '') for ch in self.request.session['longitude'])
              print( "the city"+str(self.request.session['city']))

              image_main_path = None
              if 'saved' in self.request.session or self.request.session['saved']:
                  id = self.request.session['saved']
                  photo=get_object_or_404(Photo, pk=id[0])
                  image_main_path="http://127.0.0.1:8000" + photo.image.url


              place=Place(city=str(self.request.session['city']),address=self.request.session['address'],latitude=Decimal(latitude),longitude=Decimal(longitude),image_main_path=image_main_path )
              place.save()

              listing = Listing(
                  place=place,
                  user=self.request.user,
                  price=price,
                  roomsTotal=roomsTotal,
                  Bathrooms=Bathrooms,
                  bedrooms=bedrooms,
                  Receptionrooms=Receptionrooms,
                  livingArea=livingArea,
                  lotSize=lotSize,
                  unitType=unitType,
                  yearBuilt=yearBuilt,
                  remodelYear=remodelYear,
                  hoaPrice=hoaPrice,
                  groundTankSize=groundTankSize,
                  garageSize=garageSize,
                  homeDescription=homeDescription,
                  whatYouLoveDescription=whatYouLoveDescription,
                  Dishwasher=Dishwasher,
                  Dryer=Dryer,
                  Freezer=Freezer,
                  GarbageDisposal=GarbageDisposal,
                  Microwave=Microwave,
                  Oven=Oven,
                  Refrigerator=Refrigerator,
                  Washer=Washer,
                  RadioGroup_Rashan=RadioGroup_Rashan,
                  ACarpet=ACarpet,
                  AConcrete=AConcrete,
                  ATiles=ATiles,
                  ALinoleum=ALinoleum,
                  ADSoftwood=ADSoftwood,
                  ADOther=ADOther,
                  BreakfastNook=BreakfastNook,
                  DiningRoom=DiningRoom,
                  FamilyRoom=FamilyRoom,
                  LaundryRoom=LaundryRoom,
                  Library=Library,
                  MasterBath=MasterBath,
                  Office=Office,
                  Workshop=Workshop,
                  roomCount=roomCount,
                  attic=attic,
                  cableReady=cableReady,
                  ceilingFan=ceilingFan,
                  doublePaneWindows=doublePaneWindows,
                  fireplace=fireplace,
                  intercom=intercom,
                  jettedTub=jettedTub,
                  securitySystem=securitySystem,
                  CCentral=CCentral,
                  CEvaporative=CEvaporative,
                  CGeothermal=CGeothermal,
                  CRefrigeration=CRefrigeration,
                  CSolar=CSolar,
                  CWall=CWall,
                  COther=COther,
                  CNone=CNone,
                  HForcedAir=HForcedAir,
                  HGeothermal=HGeothermal,
                  HHeatPump=HHeatPump,
                  HRadiant=HRadiant,
                  HStove=HStove,
                  HWall=HWall,
                  HOther=HOther,
                  FCoal=FCoal,
                  FElectric=FElectric,
                  FGas=FGas,
                  FOil=FOil,
                  FPropaneButane=FPropaneButane,
                  FSolar=FSolar,
                  FWoodPellet=FWoodPellet,
                  FOther=FOther,
                  FNone=FNone,
                  basketballCourt=basketballCourt,
                  doorman=doorman,
                  elevator=elevator,
                  fitnessCenter=fitnessCenter,
                  gatedEntry=gatedEntry,
                  nearTransportation=nearTransportation,
                  tennisCourt=tennisCourt,
                  RadioGroup_Architectural=RadioGroup_Architectural,
                  Brick=Brick,
                  CementConcrete=CementConcrete,
                  Stone=Stone,
                  EOther=EOther,
                  FloorCount=FloorCount,
                  ApartmentsCount=ApartmentsCount,
                  barbecueArea=barbecueArea,
                  dock=dock,
                  garden=garden,
                  hotTubSpa=hotTubSpa,
                  pool=pool,
                  rvParking=rvParking,
                  sauna=sauna,
                  sprinklerSystem=sprinklerSystem,
                  PGarageAttached=PGarageAttached,
                  PGarageDetached=PGarageDetached,
                  POffStreet=POffStreet,
                  POnStreet=POnStreet,
                  PNone=PNone,
                  garageSpaces=garageSpaces,
                  RAsphalt=RAsphalt,
                  RMetal=RMetal,
                  RTiles=RTiles,
                  VOnSea=VOnSea,
                  VMountain=VMountain,
                  VOnStreet=VOnStreet,
                  VOther=VOther,
                  fullPhoneNumber=fullPhoneNumber,
              )
              listing.save()

              for key in self.request.POST.keys():
                  if key != 'csrfmiddlewaretoken':
                      if 'dateField' in key and self.request.POST[key] != '':
                          num = ''.join((ch if ch in '0123456789.' else '') for ch in key)
                          dateField = self.request.POST[key]
                          timeDropDownStart = self.request.POST.get('timeDropDownStart' + str(num))
                          timeDropDownEnd = self.request.POST.get('timeDropDownEnd' + str(num))
                          time = TimeOpenHouse(listing=listing, dateField=dateField,
                                               timeDropDownStart=timeDropDownStart, timeDropDownEnd=timeDropDownEnd)
                          time.save()

              for id in self.request.session['saved']:
                  photo = get_object_or_404(Photo, pk=id)
                  photo.listing = listing
                  photo.save()

              del self.request.session['saved']
              self.request.session['saved'] = []

              responseData = {
                  'status': 'ok',
                  'message': 'شكر! لقد تم إضافة القائمة في الموقع لدينا.'
              }
              return JsonResponse(responseData)
          else:
              responseData = {
                  'status': 'failed',
                  'message': 'يرجى ملء حقول البيع المطلوبة'
              }
              return JsonResponse(responseData)



def GoodNeighborPolicy(request):
  return render(request, 'policy/GoodNeighborPolicy.html',{})

def Terms(request):
  return render(request, 'policy/Terms.html',{})

def Quality(request):
  return render(request, 'policy/Quality.html',{})

def Privacy(request):
  return render(request, 'policy/Privacy.html',{})

def OwnedHomes(request):
  return render(request, 'policy/4us-owned-homes.html',{})

class Mylistings(LoginRequiredMixin, ListView):
    model = Listing,Topic
    template_name = "Mylistings.html"

    def get(self, *args, **kwargs):
        listings_pub = Listing.objects.filter(user=self.request.user,is_published=True)
        count = Listing.objects.filter(user=self.request.user).count()
        paginator = Paginator(listings_pub, 5)
        page = self.request.GET.get('page1')
        try:
            listings_pub = paginator.page(page)
        except PageNotAnInteger:
            listings_pub = paginator.page(1)
        except EmptyPage:
            listings_pub = paginator.page(paginator.num_pages)

        listings_nopub = Listing.objects.filter(user=self.request.user,is_published=False)
        paginator = Paginator(listings_nopub, 5)
        page = self.request.GET.get('page2')
        try:
            listings_nopub = paginator.page(page)
        except PageNotAnInteger:
            listings_nopub = paginator.page(1)
        except EmptyPage:
            listings_nopub = paginator.page(paginator.num_pages)

        topics = Topic.objects.all().order_by('-last_updated')[:5]

        context = {'listings_pub': listings_pub, 'listings_nopub': listings_nopub,'count':count,'topics':topics}
        return render(self.request, 'Mylistings.html', context)

def HomeDetails(request,id_listing):
    listing = Listing.objects.get(pk=id_listing, is_published=True)

    NearByListings = Listing.objects.filter(is_published=True).filter(
        place__latitude__range=(listing.place.latitude - Decimal(0.1), listing.place.latitude + Decimal(0.1)),
        place__longitude__range=(
        listing.place.longitude - Decimal(0.1), listing.place.longitude + Decimal(0.1))).order_by('-views')#.annotate(rank = Window(expression=RowNumber())
    rank=len(NearByListings)
    for temp in NearByListings:
        if temp.pk == listing.pk:
            break
        rank-=1
    countSaved = Save.objects.filter(listing=listing).count()
    context = {'listing':listing,'NearByListings':NearByListings,'countSaved':countSaved,'rank':rank}
    return render(request, 'homedetails.html', context)


def Listings_Delete(request,id_listing):
    listing = get_object_or_404(Listing, pk=id_listing)
    if listing.user == request.user:
        photos = Photo.objects.filter(listing=listing)
        for photo in photos:
            photo.delete()
        times = TimeOpenHouse.objects.filter(listing=listing)
        for time in times:
            time.delete()
        listing.place.delete()
        listing.delete()
        return redirect('Mylistings')

class PostingConfirmation(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        return render(self.request, 'PostingConfirmation.html', {})



class Login(View):
    template_name = 'registration/login.html'

    #def get_object(self):
        #try:
            #obj = Question.objects.get(pk=self.kwargs['pk'])
        #except Question.DoesNotExist:
            #raise Http404('Question not found!')
        #return obj

    def get_context_data(self, **kwargs):
        if 'formLogin' not in kwargs:
            kwargs['formLogin'] = AuthenticationForm()
            kwargs['page'] = 2
        if 'formRegister' not in kwargs:
            kwargs['formRegister'] =RegisterForm()
            kwargs['page'] = 1
        return kwargs

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name, self.get_context_data())

    def post(self, request, *args, **kwargs):
        ctxt = {}
        if 'login' in request.POST:
            formLogin = AuthenticationForm(request=request, data=request.POST)
            if formLogin.is_valid():
                username = formLogin.cleaned_data.get('username')
                password = formLogin.cleaned_data.get('password')
                user = authenticate(username=username, password=password)
                if user is not None:
                    login(request, user)
                    messages.info(request, "تم تسجيل دخولك الآن باسم {username}")
                    return redirect('/')
                else:
                    messages.error(request, "خطأ في اسم المستخدم أو كلمة مرور.")
            else:
                ctxt['formLogin'] = formLogin

        elif 'register' in request.POST:
            formRegister = RegisterForm(request.POST)
            if formRegister.is_valid():
                username = formRegister.cleaned_data.get('username')
                password = formRegister.cleaned_data.get('password')
                user=formRegister.save()

                if 'proCheck' in request.POST:
                    print(request.POST.get('proSelect'))
                    userprofile = get_object_or_404(UserProfile, user=user)
                    pro = request.POST.get('proSelect')
                    if not pro:
                        pro = None

                    firstName = request.POST.get('inputs-firstName')
                    if not firstName:
                        firstName = None
                    lastName = request.POST.get('inputs-lastName')
                    if not lastName:
                        lastName = None
                    phone = request.POST.get('extension') + request.POST.get('inputs-phone')
                    if not phone:
                        phone = None
                    userprofile.pro = pro
                    userprofile.firstName = firstName
                    userprofile.lastName = lastName
                    userprofile.phone = phone
                    userprofile.save()
                #user = User.objects.get(username=request.POST.get('username'))
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                return redirect('/')

            else:
                ctxt['formRegister'] = formRegister

        return render(request, self.template_name, self.get_context_data(**ctxt))

def Logout(request):
    logout(request)
    return HttpResponseRedirect(request.GET.get('next', '/'))

def Contact(request):

    if request.method == "POST":
        name=request.POST.get('name')
        place=request.POST.get('place')
        phone=request.POST.get('phone')
        email=request.POST.get('email')
        additional=request.POST.get('additional')
        chatTypeConverstion = request.POST.getlist('checkbox-299[]')
        news=request.POST.get('radio-132')
        if is_valid_form([name, additional]):
            if news == "Absolutely" and is_valid_form([email]):
                if request.user:
                    profile = UserProfile.objects.get(user=request.user)
                    profile.Subscription = True
                    profile.user.email = email
                    profile.save()
                else :
                    e=Email(email=email)
                    e.save()

            send_mail('بريد فرص- من'+name,'البريد الإلكتروني التابع :'+email+'\n\n'+phone+'\n\n'+str(chatTypeConverstion)+'\n\n'+"ما يود ذكرة:"+additional,
                      'usamnet000@gmail.com', ['usamnet000@outlook.com'],fail_silently=False)
            responseData = {
                'status': 'ok',
                'message': 'شكرا لقد تمت العملية بنجاح !'
            }

            return JsonResponse(responseData)
        else:
            responseData = {
                'status': 'failed',
                'message': 'يرجى ملء الحقول'
            }
            return JsonResponse(responseData)

    return render(request, "contact.html", {})

@login_required
def Profile(request):
    profile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        format, imgstr = request.POST.get('image').split(';base64,')
        ext = format.split('/')[-1]
        myfile = ContentFile(base64.b64decode(imgstr), name='temp.' + ext)
        if myfile:
            profile.photo = myfile
            profile.save()
            responseData = {
                'status': 'ok',
                'message': 'شكرا لقد تمت العملية بنجاح !'
            }
            return JsonResponse(responseData)
        else:
            responseData = {
                'status': 'failed',
                'message': 'يرجى اعادة المحاولة اذا استمرت المشكلة يرجى الإتصال بخدمة العملاء'
            }
            return JsonResponse(responseData)
    return render(request, 'profile/profile.html',{'profile':profile})


@login_required
def Account(request):
    if request.GET.get('allowOtherToContactMe') == str(1):
        profile = UserProfile.objects.get(user=request.user)
        profile.allowOtherToContactMe = True
        profile.save()
    elif request.GET.get('allowOtherToContactMe') == str(0):
        profile = UserProfile.objects.get(user=request.user)
        profile.allowOtherToContactMe = False
        profile.save()

    if request.GET.get('smsAllNotificationsCheckbox') == str(1):
        profile = UserProfile.objects.get(user=request.user)
        profile.smsAllNotifications = True
        profile.save()
    elif request.GET.get('smsAllNotificationsCheckbox') == str(0):
        profile = UserProfile.objects.get(user=request.user)
        profile.smsAllNotifications = False
        profile.save()

    if request.GET.get('deleteAccount') == str(1):
        user = User.objects.get(username=request.user.username)
        user.delete()

    if request.GET.get('Subscription') == str(1):
        profile = UserProfile.objects.get(user=request.user)
        profile.Subscription = False
        profile.save()

    return render(request, 'profile/Account.html',{})


@login_required
def ChangeEmail(request):
    if request.method == 'POST':
        newEmailField=request.POST.get('newEmailField')
        print(newEmailField)
        if newEmailField:
            user = User.objects.get(username=request.user.username)
            user.username = newEmailField
            user.save()
            return redirect('Account')
    return render(request, 'profile/ChangeEmail.html',{})

@login_required
def EditProfile(request):
    profile = UserProfile.objects.get(user=request.user)
    if request.method == 'POST':
        firstName = request.POST.get('firstName')
        if not firstName:
            firstName = None
        lastName = request.POST.get('lastName')
        if not lastName:
            lastName = None
        screenName = request.POST.get('screenName')
        if not screenName:
            screenName = None

        firstImage = request.FILES['firstImage'] if 'firstImage' in request.FILES else None
        print(request.FILES)
        pro = request.POST.get('proSelect')
        if not pro:
            pro = None

        Title = request.POST.get('title')
        if not Title:
            Title = None
        companyName = request.POST.get('companyName')
        if not companyName:
            companyName = None
        companyAddress = request.POST.get('companyAddress')
        if not companyAddress:
            companyAddress = None

        companyCity = request.POST.get('companyCity')
        if not companyCity:
            companyCity = None
        phoneCompany = request.POST.get('phoneCompany')
        if not phoneCompany:
            phoneCompany = None
        CellPhone = request.POST.get('CellPhone')
        if not CellPhone:
            CellPhone = None
        otherLicenseDescription = request.POST.get('otherLicenseDescription')
        if not otherLicenseDescription:
            otherLicenseDescription = None
        otherLicenseNumber = request.POST.get('otherLicenseNumber')
        if not otherLicenseNumber:
            otherLicenseNumber = None
        serviceAreas = request.POST.get('serviceAreasInput')
        if not serviceAreas:
            serviceAreas = None

        Arabic = request.POST.get('Arabic', '') == 'on'
        English = request.POST.get('English', '') == 'on'

        yearsExperience = request.POST.get('yearsExperience')
        if not yearsExperience:
            yearsExperience = None

        Appraisal = request.POST.get('Appraisal', '') == 'on'
        CommercialRE = request.POST.get('CommercialRE', '') == 'on'
        Escrow = request.POST.get('Escrow', '') == 'on'
        Insurance = request.POST.get('Insurance', '') == 'on'
        Legal = request.POST.get('Legal', '') == 'on'
        Moving = request.POST.get('Moving', '') == 'on'
        Notary = request.POST.get('Notary', '') == 'on'
        Staging = request.POST.get('Staging', '') == 'on'
        OTitle = request.POST.get('OTitle', '') == 'on'
        Other = request.POST.get('Other', '') == 'on'

        videoUrl = request.POST.get('videoUrl')
        if not videoUrl:
            videoUrl = None
        website = request.POST.get('website')
        if not website:
            website = None
        blog = request.POST.get('blog')
        if not blog:
            blog = None
        facebook = request.POST.get('facebook')
        if not facebook:
            facebook = None
        twitter = request.POST.get('twitter')
        if not twitter:
            twitter = None
        linkedIn = request.POST.get('linkedIn')
        if not linkedIn:
            linkedIn = None

        profile.firstName = firstName
        profile.lastName = lastName
        profile.screenName = screenName
        profile.photo = firstImage
        profile.pro = pro
        profile.title = Title
        profile.companyName = companyName
        profile.companyAddress = companyAddress
        profile.companyCity = companyCity
        profile.phoneCompany = phoneCompany
        profile.CellPhone = CellPhone
        profile.otherLicenseDescription = otherLicenseDescription
        profile.otherLicenseNumber = otherLicenseNumber
        profile.serviceAreas = serviceAreas
        profile.Arabic = Arabic
        profile.English = English
        profile.yearsExperience = yearsExperience
        profile.Appraisal = Appraisal
        profile.CommercialRE = CommercialRE
        profile.Escrow = Escrow
        profile.Insurance = Insurance
        profile.Legal = Legal
        profile.Moving = Moving
        profile.Notary = Notary
        profile.Staging = Staging
        profile.OTitle = OTitle
        profile.Other = Other

        profile.videoUrl = videoUrl
        profile.website = website
        profile.blog = blog
        profile.facebook = facebook
        profile.twitter = twitter
        profile.linkedIn = linkedIn
        profile.save()
        return redirect('Profile')

    form = EditProfileForm()
    return render(request, 'profile/EditProfile.html',{'form':form,'profile':profile})



def Subscriptions(request):
    if request.method == 'GET':
        email=request.GET.get('email')
        if request.user:
            profile = UserProfile.objects.get(user=request.user)
            profile.Subscription = True
            profile.user.email = email
            profile.save()
        else:
            e = Email(email=email)
            e.save()
        return HttpResponseRedirect(request.GET.get('next', '/'))

@login_required
def SaveListing(request,id):
    listing = Listing.objects.get(pk=id)
    no_obj = Save.objects.filter(user=request.user, listing=listing)
    if not no_obj.exists():
        if request.user == listing.user:
            save = Save(user=request.user, listing=listing)
            save.save()
        responseData = {
            'status': 'ok',
            'message': 'شكرا لقد تم الحفظ بنجاح !'
        }
        return JsonResponse(responseData)


@login_required
def DelSaveListing(request,id):
    listing = Listing.objects.get(pk=id)
    if request.user == listing.user:
        Save.objects.get(listing=listing).delete()
        responseData = {
            'status': 'ok',
            'message': ' تم الحذف بنجاح !'
        }
        return JsonResponse(responseData)


def SaveListingView(request):
    context = {}
    context['type'] = request.GET.get('type', 'homes')

    listings = Save.objects.filter(user=request.user).only('listing')
    context['listingsSave'] = listings
    print(listings)
    places = listings.values_list('listing__pk', 'listing__price', 'listing__place__image_main_path', 'listing__place__address',
                                      'listing__place__latitude',
                                      'listing__place__longitude')
    context['places_json'] = json.dumps(list(places), cls=DjangoJSONEncoder)

    if listings:
        context['city'] = listings[0].listing.place.get_city_display
        context['type_display'] = listings[0].listing.get_property_type_display
    if request.user.is_authenticated:
        context['countSaved'] = Save.objects.filter(user=request.user).count()

    context['formLogin'] = AuthenticationForm()
    context['formRegister'] = RegisterForm()
    count = listings.count()
    context['count'] = count

    return render(request, 'Main.html',context)


@login_required
def ShareListing(request,id):
    listing = Listing.objects.get(pk=id)
    if request.method == 'POST':
        receiver = request.POST.get('receiver-email')
        sender = request.POST.get('sender-email')
        message = request.POST.get('message-to-send')
        urlListing = request.POST.get('urlListing')

        html_message = loader.render_to_string(
            'homesShare.html',
            {
                'user_name': request.user,
                'price':listing.price,
                'lot':listing.lotSize,
                'image':listing.place.image_main_path,
                'address':listing.place.address,
                'time':listing.list_date,
                'urlListing': urlListing,
                'message': message,
                'subject': 'مع الشكر',
        }
        )

        send_mail('بريد تجربي فرص- من' + sender,'البريد الإلكتروني التابع له:' + sender  + '\n\n' + "ما يود ذكرة:" + message+'\n\n'+'وهذا هو الرابط'+'\n'+'http://'+urlListing,
                  'usamnet000@gmail.com', [receiver], fail_silently=True,html_message=html_message)
        responseData = {
            'status': 'ok',
            'message': ' تم الإرسال بنجاح !'
        }
        return JsonResponse(responseData)

@login_required
def SaveSearch(request):
    pass
@login_required
def SaveSearchList(request):
    pass
@login_required
def SaveSearchEmail(request):
    pk=request.GET.get('pk')
    ListingLink = request.GET.get('ListingLink')
    if pk :
        SearchQuery.objects.create(user=request.user, query=pk)
    listing = Listing.objects.get(pk=pk)
    html_message = loader.render_to_string(
        'homesShare.html',
        {
            'user_name': request.user,
            'price': listing.price,
            'lot': listing.lotSize,
            'image': listing.place.image_main_path,
            'address': listing.place.address,
            'time': listing.list_date,
            'urlListing': ListingLink,
            'subject': 'مع الشكر',
        }
    )
    send_mail('بريد تجربي فرص- من' ,
               '\n\n' + '\n\n' + 'وهذا هو الرابط' + '\n' + 'http://' + ListingLink,
              'usamnet000@gmail.com', [request.user.email], fail_silently=True, html_message=html_message)
    responseData = {
        'status': 'ok',
        'message': ' تم الإرسال بنجاح !'
    }
    return JsonResponse(responseData)

class PostListView(ListView):
    model = Post
    context_object_name = 'posts'
    template_name = 'blog/blog.html'


    def get_context_data(self, **kwargs):
        session_key = 'viewed_topic_{}'.format(self.topic.pk)
        if not self.request.session.get(session_key, False):
            self.topic.views += 1
            self.topic.save()
            self.request.session[session_key] = True
        kwargs['topic'] = self.topic
        kwargs['replies'] = self.topic.posts.count()-1
        kwargs['repliesAuthor'] = self.topic.posts.filter(created_by=self.topic.created_by).count()
        kwargs['topics'] = Topic.objects.all().order_by('-last_updated').annotate(replies=Count('posts') - 1)#[:5]
        return super().get_context_data(**kwargs)

    def get_queryset(self):
        self.topic = get_object_or_404(Topic, pk=self.kwargs.get('topic_pk'))
        queryset = self.topic.posts.order_by('created_at')
        return queryset

    def post(self, request, *args, **kwargs):

        topic = get_object_or_404(Topic, pk=self.kwargs.get('topic_pk'))
        message = self.request.POST.get('wc_comment')
        if is_valid_form([message]):
            post = Post()
            post.message = message
            post.topic = topic
            post.created_by = self.request.user
            post.save()
            topic.last_updated = datetime.datetime.now()
            topic.save()

            userprofile = UserProfile.objects.filter(user=request.user)
            photo_json = json.dumps({'photo': image_as_base64(userprofile[0].photo.path)}, indent=4)

            data = {'photo_json':photo_json,'name':self.request.POST.get('wc_name'),'message':post.message,'time':naturaltime(post.created_at),'username':post.created_by.username}
            return JsonResponse(data)
        else:
            responseData = {
                'status': 'failed',
                'message': 'يرجى ملء حقول البيع المطلوبة'
            }
            return JsonResponse(responseData)

class Sort_Post(View):
    def get(self, request, *args, **kwargs):
        topic = get_object_or_404(Topic, pk=self.kwargs.get('topic_pk'))
        posts = Post.objects.filter(topic=topic)
        if self.request.GET.get('sort-asc'):
            posts = posts.order_by('-created_at')[0:len(posts)-1]
        elif self.request.GET.get('sort-desc'):
            posts = posts.order_by('created_at')[1:]
        else:
            obj = posts[0]
            posts = posts.exclude(id=obj.pk).order_by('-votes')
        output = []
        for post in posts:
            output.append([post.created_by.profile.photo.url,post.created_by.username,naturaltime(post.created_at),post.message,post.pk,post.votes.count()])
        posts_json =json.dumps({'posts': output}, indent=4)
        data = {'posts_json':posts_json}
        return JsonResponse(data)

class VotePost(View):
    def get(self, request, *args, **kwargs):
        print('here')
        self.post = get_object_or_404(Post, pk=self.kwargs.get('post_pk'))
        if self.request.GET.get('votePlus'):
            self.post.votes.up(self.post.created_by.pk)
        elif self.request.GET.get('voteMins'):
            self.post.votes.down(self.post.created_by.pk)
        data = {'countVote':self.post.votes.count()}
        return JsonResponse(data)


class EditPosting(View):
    def get(self, *args, **kwargs):
        if (self.request.GET.get('removePhotoOnLoad', False)):
            if not 'saved' in self.request.session or not self.request.session['saved']:
                self.request.session['saved'] = []
            else:
                for id in self.request.session['saved']:
                    Photo.objects.get(pk=id).delete()
                del self.request.session['saved']
                self.request.session['saved'] = []
                return JsonResponse({'status': 'ok'})  # del request.session['saved']
        self.listing = Listing.objects.get(pk=self.kwargs.get('id_listing'))
        if self.request.user == self.listing.user:
            form = UnitForm()
            context = {'listing': self.listing, 'form': form}
            return render(self.request, 'EditPosting.html', context)
        else :
            return render(self.request, '4us-error-page.html', {})

    def post(self, *args, **kwargs):
        self.listing = Listing.objects.get(pk=self.kwargs.get('id_listing'))
        if self.request.user == self.listing.user:
            myfile = self.request.FILES['file'] if 'file' in self.request.FILES else False
            if myfile:
                photo = Photo.objects.create(image=myfile)
                if not 'saved' in self.request.session or not self.request.session['saved']:
                    self.request.session['saved'] = [photo.id]
                else:
                    saved_list = self.request.session['saved']
                    saved_list.append(photo.id)
                    self.request.session['saved'] = saved_list

                responseData = {
                    'status': 'ok',
                    'path': "http://127.0.0.1:8000" + photo.image.url,
                }
                return JsonResponse(responseData)

            else:
                propertyType = self.request.POST.get('propertyType')
                price = self.request.POST.get('price')
                if price:
                    price = int(float(re.sub(',', '', self.request.POST.get('price'))))

                roomsTotal = self.request.POST.get('roomsTotal')
                if not roomsTotal:
                    roomsTotal = None
                Bathrooms = self.request.POST.get('Bathrooms')
                bedrooms = self.request.POST.get('bedrooms')
                Receptionrooms = self.request.POST.get('Receptionrooms')
                livingArea = Decimal(''.join((ch if ch in '0123456789.' else '') for ch in self.request.POST.get('livingArea')))
                lotSize = Decimal(''.join((ch if ch in '0123456789.' else '') for ch in self.request.POST.get('lotSize')))
                unitType = self.request.POST.get('unitType')

                yearBuilt = self.request.POST.get('yearBuilt')
                if not yearBuilt:
                    yearBuilt = None
                remodelYear = self.request.POST.get('remodelYear')
                if not remodelYear:
                    remodelYear = None

                hoaPrice = self.request.POST.get('hoaPrice')
                if not hoaPrice:
                    hoaPrice = None
                groundTankSize = self.request.POST.get('groundTankSize')
                if not groundTankSize:
                    groundTankSize = None
                garageSize = self.request.POST.get('garageSize')
                if not garageSize:
                    garageSize = None
                homeDescription = self.request.POST.get('homeDescription')
                if not homeDescription:
                    homeDescription = None

                whatYouLoveDescription = self.request.POST.get('whatYouLoveDescription')
                if not whatYouLoveDescription:
                    whatYouLoveDescription = None

                Dishwasher = self.request.POST.get('id81481', '') == 'on'
                Dryer = self.request.POST.get('id81482', '') == 'on'
                Freezer = self.request.POST.get('id81483', '') == 'on'
                GarbageDisposal = self.request.POST.get('id81484', '') == 'on'
                Microwave = self.request.POST.get('id81485', '') == 'on'
                Oven = self.request.POST.get('id81486', '') == 'on'
                Refrigerator = self.request.POST.get('id81487', '') == 'on'
                Washer = self.request.POST.get('id81489', '') == 'on'

                RadioGroup_Rashan = self.request.POST.get('RadioGroup_Rashan')
                if not RadioGroup_Rashan:
                    RadioGroup_Rashan = None

                ACarpet = self.request.POST.get('id82490', '') == 'on'
                AConcrete = self.request.POST.get('id82491', '') == 'on'
                ATiles = self.request.POST.get('id82492', '') == 'on'
                ALinoleum = self.request.POST.get('id82494', '') == 'on'
                ADSoftwood = self.request.POST.get('id82496', '') == 'on'
                ADOther = self.request.POST.get('id82498', '') == 'on'

                BreakfastNook = self.request.POST.get('id83499', '') == 'on'
                DiningRoom = self.request.POST.get('id83500', '') == 'on'
                FamilyRoom = self.request.POST.get('id83501', '') == 'on'
                LaundryRoom = self.request.POST.get('id83502', '') == 'on'
                Library = self.request.POST.get('id83503', '') == 'on'
                MasterBath = self.request.POST.get('id83504', '') == 'on'
                Office = self.request.POST.get('id83506', '') == 'on'
                Workshop = self.request.POST.get('id83509', '') == 'on'

                roomCount = self.request.POST.get('roomCount')
                if not roomCount:
                    roomCount = None

                attic = self.request.POST.get('attic', '') == 'on'
                cableReady = self.request.POST.get('cableReady', '') == 'on'
                ceilingFan = self.request.POST.get('ceilingFan', '') == 'on'
                doublePaneWindows = self.request.POST.get('doublePaneWindows', '') == 'on'
                fireplace = self.request.POST.get('fireplace', '') == 'on'
                intercom = self.request.POST.get('intercom', '') == 'on'
                jettedTub = self.request.POST.get('jettedTub', '') == 'on'
                securitySystem = self.request.POST.get('securitySystem', '') == 'on'

                CCentral = self.request.POST.get('id1822', '') == 'on'
                CEvaporative = self.request.POST.get('id1823', '') == 'on'
                CGeothermal = self.request.POST.get('id1824', '') == 'on'
                CRefrigeration = self.request.POST.get('id18260', '') == 'on'
                CSolar = self.request.POST.get('id1826', '') == 'on'
                CWall = self.request.POST.get('id1827', '') == 'on'
                COther = self.request.POST.get('id1825', '') == 'on'
                CNone = self.request.POST.get('id18465', '') == 'on'
                HForcedAir = self.request.POST.get('id1749', '') == 'on'
                HGeothermal = self.request.POST.get('id17750', '') == 'on'
                HHeatPump = self.request.POST.get('id1750', '') == 'on'
                HRadiant = self.request.POST.get('id1752', '') == 'on'
                HStove = self.request.POST.get('id1754', '') == 'on'
                HWall = self.request.POST.get('id1755', '') == 'on'
                HOther = self.request.POST.get('id1751', '') == 'on'
                FCoal = self.request.POST.get('id1639', '') == 'on'
                FElectric = self.request.POST.get('id1640', '') == 'on'
                FGas = self.request.POST.get('id1641', '') == 'on'
                FOil = self.request.POST.get('id1643', '') == 'on'
                FPropaneButane = self.request.POST.get('id1645', '') == 'on'
                FSolar = self.request.POST.get('id1646', '') == 'on'
                FWoodPellet = self.request.POST.get('id1647', '') == 'on'
                FOther = self.request.POST.get('id1644', '') == 'on'
                FNone = self.request.POST.get('id16464', '') == 'on'

                basketballCourt = self.request.POST.get('basketballCourt', '') == 'on'
                doorman = self.request.POST.get('doorman', '') == 'on'
                elevator = self.request.POST.get('elevator', '') == 'on'
                fitnessCenter = self.request.POST.get('fitnessCenter', '') == 'on'
                gatedEntry = self.request.POST.get('gatedEntry', '') == 'on'
                nearTransportation = self.request.POST.get('nearTransportation', '') == 'on'
                tennisCourt = self.request.POST.get('tennisCourt', '') == 'on'

                RadioGroup_Architectural = self.request.POST.get('RadioGroup_Architectural')
                if not RadioGroup_Architectural:
                    RadioGroup_Architectural = None

                Brick = self.request.POST.get('id1228', '') == 'on'
                CementConcrete = self.request.POST.get('id1229', '') == 'on'
                Stone = self.request.POST.get('id1234', '') == 'on'
                EOther = self.request.POST.get('id1232', '') == 'on'

                FloorCount = self.request.POST.get('FloorCount')
                if not FloorCount:
                    FloorCount = None
                ApartmentsCount = self.request.POST.get('ApartmentsCount')
                if not ApartmentsCount:
                    ApartmentsCount = None

                barbecueArea = self.request.POST.get('barbecueArea', '') == 'on'
                dock = self.request.POST.get('dock', '') == 'on'
                garden = self.request.POST.get('garden', '') == 'on'
                hotTubSpa = self.request.POST.get('hotTubSpa', '') == 'on'
                pool = self.request.POST.get('pool', '') == 'on'
                rvParking = self.request.POST.get('rvParking', '') == 'on'
                sauna = self.request.POST.get('sauna', '') == 'on'
                sprinklerSystem = self.request.POST.get('sprinklerSystem', '') == 'on'

                PGarageAttached = self.request.POST.get('id1457', '') == 'on'
                PGarageDetached = self.request.POST.get('id1458', '') == 'on'
                POffStreet = self.request.POST.get('id1460', '') == 'on'
                POnStreet = self.request.POST.get('id1461', '') == 'on'
                PNone = self.request.POST.get('id14462', '') == 'on'

                garageSpaces = self.request.POST.get('garageSpaces')
                if not garageSpaces:
                    garageSpaces = None

                RAsphalt = self.request.POST.get('id1168', '') == 'on'
                RMetal = self.request.POST.get('id1171', '') == 'on'
                RTiles = self.request.POST.get('id1172', '') == 'on'

                VOnSea = self.request.POST.get('id1378', '') == 'on'
                VMountain = self.request.POST.get('id1379', '') == 'on'
                VOnStreet = self.request.POST.get('id1380', '') == 'on'
                VOther = self.request.POST.get('id1381', '') == 'on'

                fullPhoneNumber = self.request.POST.get('fullPhoneNumber')
                if not fullPhoneNumber:
                    fullPhoneNumber = None

                if is_valid_form([propertyType, price, Bathrooms, bedrooms, Receptionrooms, livingArea, lotSize]):
                    latitude = ''.join((ch if ch in '0123456789.' else '') for ch in self.request.POST.get('latitude'))
                    longitude = ''.join(
                        (ch if ch in '0123456789.' else '') for ch in self.request.POST.get('longitude'))

                    image_main_path = None
                    if 'saved' in self.request.session or self.request.session['saved']:
                        id = self.request.session['saved']
                        photo = get_object_or_404(Photo, pk=id[0])
                        image_main_path = "http://127.0.0.1:8000" + photo.image.url

                    place = Place.objects.get(pk=self.listing.place.pk)
                    city = self.listing.place.city
                    address = self.listing.place.address
                    latitude = Decimal(latitude)
                    longitude = Decimal(longitude)
                    image_main_path = image_main_path
                    place.save()

                    self.listing.place = place
                    self.listing.user = self.request.user
                    self.listing.price = price
                    self.listing.roomsTotal = roomsTotal
                    self.listing.Bathrooms = Bathrooms
                    self.listing.bedrooms = bedrooms
                    self.listing.Receptionrooms = Receptionrooms
                    self.listing.livingArea = livingArea
                    self.listing.lotSize = lotSize
                    self.listing.unitType = unitType
                    self.listing.yearBuilt = yearBuilt
                    self.listing.remodelYear = remodelYear
                    self.listing.hoaPrice = hoaPrice
                    self.listing.groundTankSize = groundTankSize
                    self.listing.garageSize = garageSize
                    self.listing.homeDescription = homeDescription
                    self.listing.whatYouLoveDescription = whatYouLoveDescription
                    self.listing.Dishwasher = Dishwasher
                    self.listing.Dryer = Dryer
                    self.listing.Freezer = Freezer
                    self.listing.GarbageDisposal = GarbageDisposal
                    self.listing.Microwave = Microwave
                    self.listing.Oven = Oven
                    self.listing.Refrigerator = Refrigerator
                    self.listing.Washer = Washer
                    self.listing.RadioGroup_Rashan = RadioGroup_Rashan
                    self.listing.ACarpet = ACarpet
                    self.listing.AConcrete = AConcrete
                    self.listing.ATiles = ATiles
                    self.listing.ALinoleum = ALinoleum
                    self.listing.ADSoftwood = ADSoftwood
                    self.listing.ADOther = ADOther
                    self.listing.BreakfastNook = BreakfastNook
                    self.listing.DiningRoom = DiningRoom
                    self.listing.FamilyRoom = FamilyRoom
                    self.listing.LaundryRoom = LaundryRoom
                    self.listing.Library = Library
                    self.listing.MasterBath = MasterBath
                    self.listing.Office = Office
                    self.listing.Workshop = Workshop
                    self.listing.roomCount = roomCount
                    self.listing.attic = attic
                    self.listing.cableReady = cableReady
                    self.listing.ceilingFan = ceilingFan
                    self.listing.doublePaneWindows = doublePaneWindows
                    self.listing.fireplace = fireplace
                    self.listing.intercom = intercom
                    self.listing.jettedTub = jettedTub
                    self.listing.securitySystem = securitySystem
                    self.listing.CCentral = CCentral
                    self.listing.CEvaporative = CEvaporative
                    self.listing.CGeothermal = CGeothermal
                    self.listing.CRefrigeration = CRefrigeration
                    self.listing.CSolar = CSolar
                    self.listing.CWall = CWall
                    self.listing.COther = COther
                    self.listing.CNone = CNone
                    self.listing.HForcedAir = HForcedAir
                    self.listing.HGeothermal = HGeothermal
                    self.listing.HHeatPump = HHeatPump
                    self.listing.HRadiant = HRadiant
                    self.listing.HStove = HStove
                    self.listing.HWall = HWall
                    self.listing.HOther = HOther
                    self.listing.FCoal = FCoal
                    self.listing.FElectric = FElectric
                    self.listing.FGas = FGas
                    self.listing.FOil = FOil
                    self.listing.FPropaneButane = FPropaneButane
                    self.listing.FSolar = FSolar
                    self.listing.FWoodPellet = FWoodPellet
                    self.listing.FOther = FOther
                    self.listing.FNone = FNone
                    self.listing.basketballCourt = basketballCourt
                    self.listing.doorman = doorman
                    self.listing.elevator = elevator
                    self.listing.fitnessCenter = fitnessCenter
                    self.listing.gatedEntry = gatedEntry
                    self.listing.nearTransportation = nearTransportation
                    self.listing.tennisCourt = tennisCourt
                    self.listing.RadioGroup_Architectural = RadioGroup_Architectural
                    self.listing.Brick = Brick
                    self.listing.CementConcrete = CementConcrete
                    self.listing.Stone = Stone
                    self.listing.EOther = EOther
                    self.listing.FloorCount = FloorCount
                    self.listing.ApartmentsCount = ApartmentsCount
                    self.listing.barbecueArea = barbecueArea
                    self.listing.dock = dock
                    self.listing.garden = garden
                    self.listing.hotTubSpa = hotTubSpa
                    self.listing.pool = pool
                    self.listing.rvParking = rvParking
                    self.listing.sauna = sauna
                    self.listing.sprinklerSystem = sprinklerSystem
                    self.listing.PGarageAttached = PGarageAttached
                    self.listing.PGarageDetached = PGarageDetached
                    self.listing.POffStreet = POffStreet
                    self.listing.POnStreet = POnStreet
                    self.listing.PNone = PNone
                    self.listing.garageSpaces = garageSpaces
                    self.listing.RAsphalt = RAsphalt
                    self.listing.RMetal = RMetal
                    self.listing.RTiles = RTiles
                    self.listing.VOnSea = VOnSea
                    self.listing.VMountain = VMountain
                    self.listing.VOnStreet = VOnStreet
                    self.listing.VOther = VOther
                    self.listing.fullPhoneNumber = fullPhoneNumber
                    self.listing.save()

                    for key in self.request.POST.keys():
                        if key != 'csrfmiddlewaretoken':
                            if 'dateField' in key and self.request.POST[key] != '':
                                num = ''.join((ch if ch in '0123456789.' else '') for ch in key)
                                dateField = self.request.POST[key]
                                timeDropDownStart = self.request.POST.get('timeDropDownStart' + str(num))
                                timeDropDownEnd = self.request.POST.get('timeDropDownEnd' + str(num))
                                time = TimeOpenHouse(listing=listing, dateField=dateField,
                                                     timeDropDownStart=timeDropDownStart,
                                                     timeDropDownEnd=timeDropDownEnd)
                                time.save()

                    for id in self.request.session['saved']:
                        photo = get_object_or_404(Photo, pk=id)
                        photo.listing = self.listing
                        photo.save()

                    del self.request.session['saved']
                    self.request.session['saved'] = []

                    responseData = {
                        'status': 'ok',
                        'message': 'شكر! لقد تم تعديل القائمة في الموقع لدينا.'
                    }
                    return JsonResponse(responseData)
                else:
                    responseData = {
                        'status': 'failed',
                        'message': 'يرجى ملء حقول البيع المطلوبة'
                    }
                    return JsonResponse(responseData)

def About(request):
  return render(request, 'About.html',{})