from django.urls import path,re_path,include
from . import views
from django.contrib.auth import views as auth_views

from .views import (
    For_Sale_Address,
    For_Sale_Post,
    Mylistings,
    PostingConfirmation,
    Login,
    For_Sale_Listings,
    PostListView,
    Sort_Post,
    VotePost,
    For_Sale_Listings_Sort,
    ShareListing,
    EditPosting
)


urlpatterns = [
    path('', views.index, name='index'),
    path('For-Sale-Listings', For_Sale_Listings.as_view(), name='For-Sale-Listings'),
    path('For-Sale-Listings/<str:city>/<str:type>', For_Sale_Listings.as_view(), name='View-For-Sale-Listings'),
    path('For-Sale-Listing/<int:id>', views.For_Sale_Listing, name='For-Sale-Listing'),
    path('For-Sale-Address', For_Sale_Address.as_view(), name='For-Sale-Address'),
    path('For-Sale-Post', For_Sale_Post.as_view(), name='For-Sale-Post'),
    path('ContactAgent', views.ContactAgent, name='ContactAgent'),
    path('ContactAgentProfile/<int:id>', views.ContactAgentProfile, name='ContactAgentProfile'),
    path('SaveListing/<int:id>', views.SaveListing, name='SaveListing'),
    path('DelSaveListing/<int:id>', views.DelSaveListing, name='DelSaveListing'),
    path('savedhomes/', views.SaveListingView, name='savedhomes'),
    path('homes/for_sale/', For_Sale_Listings_Sort.as_view(), name='View-For-Sale-Listings-Sort'),
    path('Share/<int:id>', views.ShareListing, name='Sharehome'),

    path('GoodNeighborPolicy/', views.GoodNeighborPolicy, name='GoodNeighborPolicy'),
    path('Terms/', views.Terms, name='Terms'),
    path('Quality/', views.Quality, name='Quality'),
    path('Privacy/', views.Privacy, name='Privacy'),
    path('4us-owned-homes', views.OwnedHomes, name='4us-owned-homes'),

    path('Mylistings', Mylistings.as_view(), name='Mylistings'),
    path('homedetails/<int:id_listing>', views.HomeDetails, name='homedetails'),
    path('EditPosting/<int:id_listing>',EditPosting.as_view(), name='EditPosting'),
    path('delete/<int:id_listing>', views.Listings_Delete, name='delete'),
    path('PostingConfirmation', PostingConfirmation.as_view(), name='PostingConfirmation'),

    path('accounts/', include('django.contrib.auth.urls')),
    path('login', Login.as_view(), name='login'),
    path('logout/', views.Logout, name='logout'),

    # Password reset links (ref: https://github.com/django/django/blob/master/django/contrib/auth/views.py)
    path('password_change/done/',auth_views.PasswordChangeDoneView.as_view(template_name='profile/password_change_done.html'),name='password_change_done'),

    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='profile/password_change.html'), name='password_change'),

    path('password_reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_done.html'),
         name='password_reset_done'),


    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),

    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'),
         name='password_reset_complete'),

    path('Profile', views.Profile, name='Profile'),
    path('Account', views.Account, name='Account'),
    path('ChangeEmail', views.ChangeEmail, name='ChangeEmail'),
    path('EditProfile', views.EditProfile, name='EditProfile'),

    path('Subscriptions/', views.Subscriptions, name='Subscriptions'),

    path('contact', views.Contact, name='contact'),
    path('About', views.About, name='About'),

    path('markdownx/', include('markdownx.urls')),

    path('blog/<int:topic_pk>', PostListView.as_view(), name='topic_posts'),
    path('SortPost/<int:topic_pk>', Sort_Post.as_view(), name='sort_posts'),
    path('VotePost/<int:post_pk>', VotePost.as_view(), name='vote_posts'),
]