from django.conf.urls import url, include
from django.views.generic import TemplateView
from . import views

urlpatterns = [
    url(r'^$', views.IndexView.as_view(), name='management-index'),
    url(r'^post/$', views.PostListView.as_view(), name='management-post-list'),
    url(r'^post/verify/$', views.VerifyPostListView.as_view(), name='management-post-list-verify'),
    url(r'^post/edit/(?P<pk>\d+)/$', views.EditPostView.as_view(), name='management-post-edit'),
    url(r'^post/verify/(?P<pk>\d+)/$', views.VerifyView.as_view(), name='management-post-verify'),
    url(r'^post/ignore/(?P<pk>\d+)/$', views.IgnoreView.as_view(), name='management-post-ignore'),
    url(r'^post/hide/(?P<pk>\d+)/$', views.HideView.as_view(), name='management-post-hide'),

    url(r'^user/$', views.UserView.as_view(), name='management-user-list'),
    url(r'^user/coin/(?P<uid>\d+)/$', views.CoinView.as_view(), name='management-user-coin'),
    url(r'^user/(?P<pk>\d+)/$', views.UserDetailView.as_view(), name='management-user-detail'),
    url(r'^user/(?P<uid>\d+)/log/$', views.CoinLogView.as_view(), name='management-user-coin-log'),
    url(r'^user/(?P<pk>\d+)/ban/$', views.BanUserView.as_view(), name='management-user-ban'),

    url(r'^invitecode/$', views.InviteCodeListView.as_view(), name='management-invitecode'),
    url(r'^invitecode/generate/$', views.GenerateInvitecodeView.as_view(), name='management-generate-invitecode'),
    url(r'^invitecode/delete/(?P<pk>\d+)/$', views.DeleteInviteCodeView.as_view(), name='management-delete-invitecode'),

    url(r'^gift/$', views.GiftListView.as_view(), name='management-gift-list'),
    url(r'^gift/add/$', views.GiftAddView.as_view(), name='management-gift-add'),
    url(r'^gift/(?P<pk>\d+)/$', views.GiftEditView.as_view(), name='management-gift-edit'),
    url(r'^gift/(?P<pk>\d+)/delete/$', views.GiftDeleteView.as_view(), name='management-gift-delete'),

    url(r'^order/$', views.GiftLogListView.as_view(), name='management-order-list'),
    url(r'^order/(?P<pk>\d+)/$', views.GiftLogDetailView.as_view(), name='management-order-detail'),
    url(r'^order/wait/$', views.GiftLogWaitListView.as_view(), name='management-order-wait-list'),

    url(r'^link/$', views.LinkListView.as_view(), name='management-link-list'),
    url(r'^link/(?P<pk>\d+)/$', views.LinkEditView.as_view(), name='management-link-edit'),
    url(r'^link/(?P<pk>\d+)/delete/$', views.LinkDeleteView.as_view(), name='management-link-delete'),
    url(r'^link/add/$', views.LinkAddView.as_view(), name='management-link-add'),
]