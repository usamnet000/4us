
from django.contrib import admin
from .models import Photo,Listing,Place,TimeOpenHouse,Email,UserProfile,Save,Topic,Post
from markdownx.admin import MarkdownxModelAdmin
# Register your models here.

class ListingAdmin(admin.ModelAdmin):
    fieldsets = ((None,{'fields':('place','property_type','user','price','roomsTotal','Bathrooms','bedrooms','Receptionrooms','livingArea','lotSize','unitType','yearBuilt','remodelYear','is_published')}),
                 ('Advanced options',{
                     'classes':('Listing',),
                     'fields':['hoaPrice','groundTankSize','garageSize','homeDescription','whatYouLoveDescription','Dishwasher']
                 }),
                 )
    list_display = ['user','is_published','place','property_type']
    list_display_links = ['user','is_published','place','property_type']
    list_filter = ['user','is_published','property_type' ]
    search_fields = [
        'user__username',
        'price',
        'is_published',
        'yearBuilt',
        'remodelYear'
    ]

class PlaceAdmin(admin.ModelAdmin):
    list_display = [
        'address',
        'city',
    ]
    list_filter = ['address', 'city']
    search_fields = ['address', 'city']




class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'companyCity', 'phoneCompany')

    def user_info(self, obj):
        return obj.description

    def get_queryset(self, request):
        queryset = super(UserProfileAdmin, self).get_queryset(request)
        queryset = queryset.order_by('-phoneCompany', 'user')
        return queryset

    user_info.short_description = 'Info'


admin.site.register(TimeOpenHouse)
admin.site.register(Place,PlaceAdmin)
admin.site.register(Photo)
admin.site.register(Listing,ListingAdmin)
admin.site.register(Email)
admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Save)
admin.site.register(Topic)
admin.site.register(Post,MarkdownxModelAdmin)