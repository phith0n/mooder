from django.urls import path, re_path, include
from . import views


app_name = 'archives'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('list/', views.ArchiveView.as_view(), name='list'),
    path('user/', views.UserView.as_view(), name='user'),
    path('add/', views.CreateArchiveView.as_view(), name='add'),
    path('upload-images/', views.UploadImageView.as_view(), name='upload-images'),

    path('profile/', views.ProfileView.as_view(), name='profile-me'),
    path('profile/<int:uid>/', views.ProfileView.as_view(), name='profile'),
    path('profile/detail/', views.ProfileDetailView.as_view(), name='profile-detail'),
    path('profile/order/', views.ProfileOrderView.as_view(), name='profile-order'),
    path('profile/edit/', views.ProfileEditView.as_view(), name='profile-edit'),
    path('profile/post/', views.ProfilePostView.as_view(), name='profile-post'),

    path('post/<int:pk>/', views.ArchiveDetailView.as_view(), name='detail'),
    path('post/<int:pk>/buy/', views.ArchiveBuyView.as_view(), name='buy'),
    path('post/attach/<int:pk>/', views.AttachmentView.as_view(), name='attachment'),

    path('gift/', views.GiftListView.as_view(), name='shop'),
    path('gift/<int:pk>/', views.GiftDetailView.as_view(), name='gift'),
    path('gift/<int:pk>/buy/', views.OrderCreateView.as_view(), name='order-create'),
    path('gift/order/<int:pk>/', views.OrderDetailView.as_view(), name='order'),

    path('js/', view=views.JavascriptView.as_view(content_type='text/javascript'), name='js'),
]
