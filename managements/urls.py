from django.urls import path, re_path, include
from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='management-index'),
    path('post/', views.PostListView.as_view(), name='management-post-list'),
    path('post/verify/', views.VerifyPostListView.as_view(), name='management-post-list-verify'),
    path('post/edit/<int:pk>/', views.EditPostView.as_view(), name='management-post-edit'),
    path('post/verify/<int:pk>/', views.VerifyView.as_view(), name='management-post-verify'),
    path('post/ignore/<int:pk>/', views.IgnoreView.as_view(), name='management-post-ignore'),
    path('post/hide/<int:pk>/', views.HideView.as_view(), name='management-post-hide'),

    path('user/', views.UserView.as_view(), name='management-user-list'),
    path('user/coin/<int:uid>/', views.CoinView.as_view(), name='management-user-coin'),
    path('user/<int:pk>/', views.UserDetailView.as_view(), name='management-user-detail'),
    path('user/<int:uid>/log/', views.CoinLogView.as_view(), name='management-user-coin-log'),
    path('user/<int:pk>/ban/', views.BanUserView.as_view(), name='management-user-ban'),

    path('invitecode/', views.InviteCodeListView.as_view(), name='management-invitecode'),
    path('invitecode/generate/', views.GenerateInvitecodeView.as_view(), name='management-generate-invitecode'),
    path('invitecode/delete/<int:pk>/', views.DeleteInviteCodeView.as_view(), name='management-delete-invitecode'),

    path('gift/', views.GiftListView.as_view(), name='management-gift-list'),
    path('gift/add/', views.GiftAddView.as_view(), name='management-gift-add'),
    path('gift/<int:pk>/', views.GiftEditView.as_view(), name='management-gift-edit'),
    path('gift/<int:pk>/delete/', views.GiftDeleteView.as_view(), name='management-gift-delete'),

    path('order/', views.GiftLogListView.as_view(), name='management-order-list'),
    path('order/<int:pk>/', views.GiftLogDetailView.as_view(), name='management-order-detail'),
    path('order/wait/', views.GiftLogWaitListView.as_view(), name='management-order-wait-list'),

    path('link/', views.LinkListView.as_view(), name='management-link-list'),
    path('link/<int:pk>/', views.LinkEditView.as_view(), name='management-link-edit'),
    path('link/<int:pk>/delete/', views.LinkDeleteView.as_view(), name='management-link-delete'),
    path('link/add/', views.LinkAddView.as_view(), name='management-link-add'),

    path('comment/delete/<int:pk>/', views.DeleteCommentView.as_view(), name='management-comment-delete'),
]
