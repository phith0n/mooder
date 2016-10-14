from django.conf.urls import url, include
from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='index'),
    url(r'^list/$', views.ArchiveView.as_view(), name='list'),
    url(r'^user/$', views.UserView.as_view(), name='user'),
    url(r'^add/$', views.CreateArchiveView.as_view(), name='add'),
    url(r'^upload-images/$', views.UploadImageView.as_view(), name='upload-images'),

    url(r'^profile/$', views.ProfileView.as_view(), name='profile-me'),
    url(r'^profile/(?P<uid>\d+)/$', views.ProfileView.as_view(), name='profile'),
    url(r'^profile/detail/$', views.ProfileDetailView.as_view(), name='profile-detail'),
    url(r'^profile/order/$', views.ProfileOrderView.as_view(), name='profile-order'),
    url(r'^profile/edit/$', views.ProfileEditView.as_view(), name='profile-edit'),
    url(r'^profile/post/$', views.ProfilePostView.as_view(), name='profile-post'),

    url(r'^post/(?P<pk>\d+)/$', views.ArchiveDetailView.as_view(), name='detail'),
    url(r'^post/(?P<pk>\d+)/buy/$', views.ArchiveBuyView.as_view(), name='buy'),

    url(r'^gift/$', views.GiftListView.as_view(), name='shop'),
    url(r'^gift/(?P<pk>\d+)/$', views.GiftDetailView.as_view(), name='gift'),
    url(r'^gift/(?P<gift_id>\d+)/buy/$', views.OrderCreateView.as_view(), name='order-create'),
    url(r'^gift/order/(?P<pk>\d+)/$', views.OrderDetailView.as_view(), name='order'),

    url(r'^js/$', view=views.JavascriptView.as_view(content_type='text/javascript'), name='js'),
]