from django.db import models
import datetime
from django.conf import settings

import os
from django.utils.crypto import get_random_string
from django.dispatch import receiver

from phonenumber_field.modelfields import PhoneNumberField
from django.core.validators import MinValueValidator, MaxValueValidator

from django.contrib.auth.models import User
from django.db.models.signals import post_save

import math

from django.db import models
from django.utils.html import mark_safe
from django.utils.text import Truncator

from markdown import markdown
from markdownx.models import MarkdownxField


from django.db.models import Q
from django.utils import timezone
from vote.models import VoteModel

User = settings.AUTH_USER_MODEL

CITY_CHOICES = (
    ('Omran', 'عمران'),
    ('AlBayda ', 'البيضاء'),
    ('Hodeidah', 'الحديدة'),
    ('Hollow', 'الجوف'),
    ('AlMahweet', 'المحويت'),
    ('Dhamar', 'ذمار'),
    ('Hajjah', 'حجة'),
    ('Ibb', 'إب'),
    ('Marib', 'مأرب'),
    ('Rima', 'ريمة'),
    ('Sa\'ada', 'صعدة'),
    ('Sana\'a', 'صنعاء'),
    ('Taiz', 'تعز'),
    ('Aden', 'عدن'),
    ('Abyan', 'أبين'),
    ('Dali', 'الضالع'),
    ('ALamrah', 'المهرة'),
    ('Hadramout', 'حضرموت'),
    ('Socotra', 'سقطرى'),
    ('Lahj', 'لحج'),
    ('Shabwah', 'شبوة'),
)

PROPERTY_TYPE_CHOICES = (
  (1, 'للبيع من قبل المالك'),
  (2, 'سينهيء البناء قريباً'),
  (3, "للبيع من قبل الوكيل"),
  (4, 'بناء جديد'),
  (5, 'بيت مفتوح'),
)

UNIT_TYPE_CHOICES = (
  (1, 'متر مربع'),
  (2, 'قدم مربع'),
  (3, "فدان"),
)

TIME_CHOICES = (
  (0, '8:00 AM'),
  (1, '8:30 AM'),
  (2, "9:00 AM"),
  (3, '9:30 AM'),
  (4, '10:00 AM'),
  (5, "10:30 AM"),
  (6, '11:00 AM'),
  (7, '11:30 AM'),
  (8, "12:00 PM"),
  (9, '12:30 PM'),
  (10, '1:00 PM'),
  (11, "1:30 PM"),
  (12, '2:00 PM'),
  (13, '2:30 PM'),
  (14, "3:00 PM"),
  (15, '3:30 PM'),
  (16, '4:00 PM'),
  (17, "4:30 PM"),
  (18, '5:00 PM'),
  (19, '5:30 PM'),
  (20, "6:00 PM"),
  (21, '6:30 PM'),
  (22, '7:00 PM'),
  (23, "7:30 PM"),
  (24, '8:00 PM'),
  (25, '8:30 PM'),
)

PRO_TYPE_CHOICES = (
  (0, ''),
  (1, 'وكيل عقارات / وسيط'),
  (2, "مقرض عقاري"),
  (3, 'خدمات تحسين المنزل'),
  (4, 'مالك'),
  (5, 'مصور فوتوغرافي'),
  (6, 'باني منازل'),
  (7, 'مدير الملكية'),
  (8, 'العقارات المهنية الأخرى'),
)

class ListingQuerySet(models.QuerySet):

    def search(self, query):
        city_reverse = dict((v, k) for k, v in CITY_CHOICES)
        result = query
        if query in city_reverse:
            result = city_reverse[''+query]
        lookup = (
                    Q(place__city__icontains=result) |
                    Q(place__address__icontains=query) |
                    Q(user__profile__firstName__icontains=query) |
                    Q(user__profile__lastName__icontains=query) |
                    Q(user__username__icontains=query)
                    )

        return self.filter(is_published=True).filter(lookup)

class ListingManager(models.Manager):
    def get_queryset(self):
        return ListingQuerySet(self.model, using=self._db)

    def search(self, query=None):
        if query is None:
            return self.get_queryset().none()
        return self.get_queryset().search(query)

class UserProfile(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,primary_key=True,related_name="profile")
    firstName= models.CharField(max_length=100, default='',null=True, blank=True)
    lastName= models.CharField(max_length=100, default='',null=True, blank=True)
    photo = models.ImageField(upload_to='UserProfile/%Y/%m/%d/',null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    hire_date = models.DateTimeField(default=datetime.datetime.now())
    allowOtherToContactMe = models.BooleanField(default=False, blank=True)
    smsAllNotifications = models.BooleanField(default=True, blank=True)
    Subscription = models.BooleanField(default=False, blank=True)

    screenName=models.CharField(max_length=100, default='',null=True, blank=True)

    pro = models.IntegerField(choices=PRO_TYPE_CHOICES, default=0)
    title = models.CharField(max_length=100, default='',null=True, blank=True)
    companyName = models.CharField(max_length=100, default='',null=True, blank=True)
    companyAddress = models.CharField(max_length=100, default='',null=True, blank=True)
    companyCity = models.CharField(max_length=100, default='',null=True, blank=True)
    phoneCompany = PhoneNumberField(null=True,blank=True, unique=True)
    CellPhone = PhoneNumberField(null=True,blank=True, unique=True)
    otherLicenseDescription = models.TextField(blank=True,null=True)
    otherLicenseNumber = models.CharField(max_length=100, default='',null=True, blank=True)
    serviceAreas = models.CharField(max_length=100, default='',null=True, blank=True)

    Arabic = models.BooleanField(default=False, blank=True)
    English = models.BooleanField(default=False, blank=True)

    yearsExperience =  models.CharField(max_length=30, default='',null=True, blank=True)

    Appraisal = models.BooleanField(default=False, blank=True)
    CommercialRE = models.BooleanField(default=False, blank=True)
    Escrow = models.BooleanField(default=False, blank=True)
    Insurance = models.BooleanField(default=False, blank=True)
    Legal = models.BooleanField(default=False, blank=True)
    Moving = models.BooleanField(default=False, blank=True)
    Notary = models.BooleanField(default=False, blank=True)
    Staging = models.BooleanField(default=False, blank=True)
    OTitle = models.BooleanField(default=False, blank=True)
    Other = models.BooleanField(default=False, blank=True)

    videoUrl = models.CharField(max_length=300, default='',null=True, blank=True)

    website = models.CharField(max_length=300, default='',null=True, blank=True)
    blog = models.CharField(max_length=300, default='',null=True, blank=True)
    facebook = models.CharField(max_length=300, default='',null=True, blank=True)
    twitter = models.CharField(max_length=300, default='',null=True, blank=True)
    linkedIn = models.CharField(max_length=300, default='',null=True, blank=True)

    def __str__(self):
        return "(%s) %s" % (self.user.username, self.companyCity)

    def __unicode__(self):
        return u'(%s) %s' % (self.user.username, self.companyCity)

def create_profile(sender, **kwargs):
    if kwargs['created']:
        user_profile = UserProfile.objects.create(user=kwargs['instance'])

post_save.connect(create_profile, sender=User)



class Place(models.Model):
  city = models.CharField(choices=CITY_CHOICES, max_length=20)
  address = models.CharField(max_length=100)
  latitude = models.DecimalField(max_digits=19, decimal_places=17, default=None)
  longitude = models.DecimalField(max_digits=19, decimal_places=17, default=None)
  created = models.DateTimeField(auto_now_add=True)
  updated = models.DateTimeField(auto_now=True)
  image_main_path = models.CharField(max_length=500)

  @property
  def uncommad(self):
      return self.address.replace(',', '-')


  def __str__(self):
      return "(%s) %s" % (self.city, self.address)

  def __unicode__(self):
      return u'(%s) %s' % (self.city, self.address)

class Listing(models.Model):
  place = models.OneToOneField(Place,on_delete=models.CASCADE,primary_key=True,related_name='listing')
  property_type = models.IntegerField(choices=PROPERTY_TYPE_CHOICES, default=1)
  user = models.ForeignKey(settings.AUTH_USER_MODEL,
                           on_delete=models.CASCADE)

  price = models.BigIntegerField()
  roomsTotal = models.PositiveSmallIntegerField(null=True)
  Bathrooms = models.PositiveSmallIntegerField(default=None)
  bedrooms = models.PositiveSmallIntegerField(default=None)
  Receptionrooms = models.PositiveSmallIntegerField(default=None)
  livingArea = models.DecimalField(max_digits=19, decimal_places=3)
  lotSize = models.DecimalField(max_digits=19, decimal_places=3)
  unitType = models.IntegerField(choices=UNIT_TYPE_CHOICES, default=1)
  yearBuilt = models.PositiveIntegerField(null=True,blank=True,
            validators=[
                MinValueValidator(1900),
                MaxValueValidator(datetime.datetime.now().year)],
            help_text="Use the following format: <YYYY>")
  remodelYear = models.PositiveIntegerField(null=True,blank=True,
            validators=[
                MinValueValidator(1900),
                MaxValueValidator(datetime.datetime.now().year)],
            help_text="Use the following format: <YYYY>")

  hoaPrice = models.BigIntegerField(null=True,blank=True)
  groundTankSize = models.DecimalField(max_digits=6, decimal_places=3,null=True,blank=True)
  garageSize = models.DecimalField(max_digits=6, decimal_places=3,null=True,blank=True)
  homeDescription = models.TextField(blank=True,null=True)

  whatYouLoveDescription = models.TextField(null=True,blank=True)

  Dishwasher = models.BooleanField(default=False, blank=True)
  Dryer = models.BooleanField(default=False, blank=True)
  Freezer = models.BooleanField(default=False, blank=True)
  GarbageDisposal = models.BooleanField(default=False, blank=True)
  Microwave = models.BooleanField(default=False, blank=True)
  Oven = models.BooleanField(default=False, blank=True)
  Refrigerator = models.BooleanField(default=False, blank=True)
  Washer = models.BooleanField(default=False, blank=True)

  RadioGroup_Rashan = models.CharField(max_length=5,null=True,blank=True)

  ACarpet = models.BooleanField(default=False, blank=True)
  AConcrete = models.BooleanField(default=False, blank=True)
  ATiles = models.BooleanField(default=False, blank=True)
  ALinoleum = models.BooleanField(default=False, blank=True)
  ADSoftwood = models.BooleanField(default=False, blank=True)
  ADOther = models.BooleanField(default=False, blank=True)

  BreakfastNook = models.BooleanField(default=False, blank=True)
  DiningRoom = models.BooleanField(default=False, blank=True)
  FamilyRoom = models.BooleanField(default=False, blank=True)
  LaundryRoom = models.BooleanField(default=False, blank=True)
  Library = models.BooleanField(default=False, blank=True)
  MasterBath = models.BooleanField(default=False, blank=True)
  Office = models.BooleanField(default=False, blank=True)
  Workshop = models.BooleanField(default=False, blank=True)

  roomCount = models.PositiveSmallIntegerField(null=True,blank=True)

  attic = models.BooleanField(default=False, blank=True)
  cableReady = models.BooleanField(default=False, blank=True)
  ceilingFan = models.BooleanField(default=False, blank=True)
  doublePaneWindows = models.BooleanField(default=False, blank=True)
  fireplace = models.BooleanField(default=False, blank=True)
  intercom = models.BooleanField(default=False, blank=True)
  jettedTub = models.BooleanField(default=False, blank=True)
  securitySystem = models.BooleanField(default=False, blank=True)

  CCentral = models.BooleanField(default=False, blank=True)
  CEvaporative = models.BooleanField(default=False, blank=True)
  CGeothermal = models.BooleanField(default=False, blank=True)
  CRefrigeration = models.BooleanField(default=False, blank=True)
  CSolar = models.BooleanField(default=False, blank=True)
  CWall = models.BooleanField(default=False, blank=True)
  COther = models.BooleanField(default=False, blank=True)
  CNone = models.BooleanField(default=False, blank=True)

  HForcedAir = models.BooleanField(default=False, blank=True)
  HGeothermal = models.BooleanField(default=False, blank=True)
  HHeatPump = models.BooleanField(default=False, blank=True)
  HRadiant = models.BooleanField(default=False, blank=True)
  HStove = models.BooleanField(default=False, blank=True)
  HWall = models.BooleanField(default=False, blank=True)
  HOther = models.BooleanField(default=False, blank=True)

  FCoal = models.BooleanField(default=False, blank=True)
  FElectric = models.BooleanField(default=False, blank=True)
  FGas = models.BooleanField(default=False, blank=True)
  FOil = models.BooleanField(default=False, blank=True)
  FPropaneButane = models.BooleanField(default=False, blank=True)
  FSolar = models.BooleanField(default=False, blank=True)
  FWoodPellet = models.BooleanField(default=False, blank=True)
  FOther = models.BooleanField(default=False, blank=True)
  FNone = models.BooleanField(default=False, blank=True)

  basketballCourt = models.BooleanField(default=False, blank=True)
  doorman = models.BooleanField(default=False, blank=True)
  elevator = models.BooleanField(default=False, blank=True)
  fitnessCenter = models.BooleanField(default=False, blank=True)
  gatedEntry = models.BooleanField(default=False, blank=True)
  nearTransportation = models.BooleanField(default=False, blank=True)
  tennisCourt = models.BooleanField(default=False, blank=True)

  RadioGroup_Architectural = models.CharField(max_length=6,null=True,blank=True)

  Brick = models.BooleanField(default=False, blank=True)
  CementConcrete = models.BooleanField(default=False, blank=True)
  Stone = models.BooleanField(default=False, blank=True)
  EOther = models.BooleanField(default=False, blank=True)

  FloorCount = models.PositiveSmallIntegerField(null=True,blank=True)
  ApartmentsCount = models.PositiveSmallIntegerField(null=True,blank=True)

  barbecueArea = models.BooleanField(default=False, blank=True)
  dock = models.BooleanField(default=False, blank=True)
  garden = models.BooleanField(default=False, blank=True)
  hotTubSpa = models.BooleanField(default=False, blank=True)
  pool = models.BooleanField(default=False, blank=True)
  rvParking = models.BooleanField(default=False, blank=True)
  sauna =models.BooleanField(default=False, blank=True)
  sprinklerSystem = models.BooleanField(default=False, blank=True)

  PGarageAttached = models.BooleanField(default=False, blank=True)
  PGarageDetached = models.BooleanField(default=False, blank=True)
  POffStreet = models.BooleanField(default=False, blank=True)
  POnStreet = models.BooleanField(default=False, blank=True)
  PNone = models.BooleanField(default=False, blank=True)

  garageSpaces = models.DecimalField(max_digits=6, decimal_places=1,null=True,blank=True)

  RAsphalt = models.BooleanField(default=False, blank=True)
  RMetal = models.BooleanField(default=False, blank=True)
  RTiles = models.BooleanField(default=False, blank=True)

  VOnSea = models.BooleanField(default=False, blank=True)
  VMountain = models.BooleanField(default=False, blank=True)
  VOnStreet = models.BooleanField(default=False, blank=True)
  VOther = models.BooleanField(default=False, blank=True)

  fullPhoneNumber = PhoneNumberField(null=True,blank=True, unique=True)#django-phonenumber-field

  list_date = models.DateTimeField(default=datetime.datetime.now())
  is_published = models.BooleanField(default=False)
  views = models.PositiveIntegerField(default=0)

  # Manager
  objects = ListingManager()


  def __str__(self):
      return "(%s) (%s)%s" % (self.user.username, self.get_property_type_display(),self.place.address)

  def __unicode__(self):
      return u'(%s) (%s)%s' % (self.user.username,self.get_property_type_display(),self.place.address)

def user_directory_path(instance, filename):
    return '/'.join(['media', get_random_string(length=32), filename])
    #return 'media/_{0}/%Y/%M/%D/{1}'.format(instance.created_by.username, filename)

class Photo(models.Model):
    image = models.ImageField(default="default.png", blank=True, null=True,upload_to=user_directory_path)
    listing = models.ForeignKey(Listing, related_name='Photos',blank=True, null=True, on_delete=models.CASCADE)


    def __str__(self):
        return "(%s) %s" % (self.image, self.listing.place.address)

    def __unicode__(self):
        return u'(%s) %s' % (self.image, self.listing.place.address)



@receiver(models.signals.post_delete, sender=Photo)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)

@receiver(models.signals.pre_save, sender=Photo)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = sender.objects.get(pk=instance.pk).image
    except sender.DoesNotExist:
        return False

    new_file = instance.image
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)



class TimeOpenHouse(models.Model):
    dateField = models.DateField(null=True, blank=True)
    timeDropDownStart = models.IntegerField(choices=TIME_CHOICES, default=0)
    timeDropDownEnd = models.IntegerField(choices=TIME_CHOICES, default=0)
    listing = models.ForeignKey(Listing, related_name='TimeOpenHouse',blank=True, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return "(%s) %s" % (self.dateField, self.listing.place.address)

    def __unicode__(self):
        return u'(%s) %s' % (self.dateField, self.listing.place.address)

class Email(models.Model):
    email = models.CharField(max_length=100)

class Save(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    listing = models.ForeignKey(Listing, related_name='Save',on_delete=models.CASCADE)



class Topic(models.Model):
    subject = models.CharField(max_length=255)
    background_image = models.ImageField(default='img/header.jpg',upload_to=datetime.datetime.now().strftime('backgrounds/%Y/%m/%d'))
    last_updated = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, related_name='topics',on_delete=models.CASCADE)
    views = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.subject

    def get_last_ten_posts(self):
        return self.posts.order_by('-created_at')[:10]


class Post(VoteModel,models.Model):
    message = MarkdownxField()
    topic = models.ForeignKey(Topic, related_name='posts',on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True)
    created_by = models.ForeignKey(User, related_name='postsUser',on_delete=models.CASCADE)
    updated_by = models.ForeignKey(User, null=True, related_name='+',on_delete=models.CASCADE)
    subtitle = models.CharField(max_length=255)

    def __str__(self):
        truncated_message = Truncator(self.message)
        return truncated_message.chars(30)

    def get_message_as_markdown(self):
        return mark_safe(markdown(self.message, safe_mode='escape'))
