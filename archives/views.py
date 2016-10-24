import os
from django.shortcuts import render, redirect, reverse, get_object_or_404
from django.views.generic import ListView, DetailView, View, TemplateView, CreateView, UpdateView
from django.views.generic.detail import SingleObjectMixin
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from pure_pagination.mixins import PaginationMixin
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db import transaction
from django.db.models import Q, F
from django.http import Http404
from django.http import StreamingHttpResponse
from wsgiref.util import FileWrapper
from django.urls import reverse_lazy
from managements.models import log_coin
from urllib.parse import urlparse
from accounts import forms as accounts_form
from . import models
from . import forms
from managements.models import CoinLog

User = get_user_model()


class IndexView(LoginRequiredMixin, TemplateView):
    template_name = 'archive/index.html'

    def get_context_data(self, **kwargs):
        kwargs['member_list'] = User.objects.order_by('-rank')[0:10]
        kwargs['post_list'] = models.Post.posts.filter(verify='pass')[0:10]
        return super(IndexView, self).get_context_data(**kwargs)


class CreateArchiveView(LoginRequiredMixin, CreateView):
    template_name = 'archive/edit.html'
    model = models.Post
    form_class = forms.PostForm

    def form_valid(self, form):
        post = form.save(commit=False)
        post.author = self.request.user
        if self.request.POST.get('preview', None):
            return render(self.request, 'archive/detail.html', dict(post=post, is_preview=True))

        post.save()
        return redirect('archive:list')


class UploadImageView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        form = forms.PostImageForm(request.POST or None, request.FILES or None)
        if form.is_valid():
            img = form.save(commit=False)
            img.uploaded_by = request.user
            img.save()
            return JsonResponse(dict(status='success', url=img.file.url, name=img.name))

        return JsonResponse(dict(status='failed'))


class ProfilePostView(LoginRequiredMixin, PaginationMixin, ListView):
    template_name = 'archive/my_post.html'
    paginate_by = 15

    def get_queryset(self):
        return models.Post.posts.filter(author=self.request.user)


class ProfileView(LoginRequiredMixin, PaginationMixin, ListView):
    template_name = 'archive/profile.html'
    name = 'archive:profile'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        uid = self.kwargs.get('uid')
        member = get_object_or_404(User, pk=uid)
        kwargs['member'] = member
        return super(ProfileView, self).get_context_data(**kwargs)

    def dispatch(self, request, *args, **kwargs):
        self.kwargs.setdefault('uid', request.user.id)
        return super(ProfileView, self).dispatch(request, *args, **kwargs)

    def get_queryset(self):
        uid = self.kwargs.get('uid')
        return models.Post.posts.filter(author_id=uid, verify='pass')


class ProfileEditView(LoginRequiredMixin, UpdateView):
    form_class = accounts_form.ProfileForm
    model = User
    template_name = 'user/edit.html'

    def get_object(self, queryset=None):
        return self.request.user


class ProfileDetailView(LoginRequiredMixin, PaginationMixin, ListView):
    template_name = 'archive/profile_detail.html'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        kwargs['object'] = User.objects.get(pk=self.request.user.id)
        return super(ProfileDetailView, self).get_context_data(**kwargs)

    def get_queryset(self):
        return CoinLog.objects.filter(user=self.request.user)


class ArchiveView(LoginRequiredMixin, PaginationMixin, ListView):
    template_name = 'archive/list.html'
    name = 'archive:list'
    paginate_by = 15
    queryset = models.Post.posts.filter(verify='pass')


class ArchiveDetailView(LoginRequiredMixin, DetailView):
    template_name = "archive/detail.html"

    def get_queryset(self):
        if self.request.user.has_perm('post-change'):
            return models.Post.posts.all()
        else:
            return models.Post.posts.filter((Q(author_id=self.request.user.id)) | (Q(verify='pass') & ~Q(author_id=self.request.user.id)))

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form = forms.CommentForm(request.POST or None)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.author = request.user
            comment.post = self.object
            comment.save()
            return redirect(request.get_full_path())

        context = self.get_context_data(object=self.object, comment_form=form)
        return self.render_to_response(context)

    def get_context_data(self, **kwargs):
        if 'comment_form' not in kwargs:
            kwargs['comment_form'] = forms.CommentForm()
        return super(ArchiveDetailView, self).get_context_data(**kwargs)


class ArchiveBuyView(LoginRequiredMixin, SingleObjectMixin, View):
    def get_queryset(self):
        return models.Post.posts.filter(Q(verify='pass') & Q(visible='sell') & ~Q(author_id=self.request.user.id))

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        post = self.get_object()

        if post.price > request.user.coin:
            return render(request, 'error.html', context={
                'errors': '你没有那么多金币啦！',
                'return_url': reverse('archive:detail', kwargs=dict(pk=post.id))
            })

        request.user.coin -= post.price
        request.user.save()

        post.author.coin += post.price
        post.author.save()

        post.buyers.add(request.user)

        log_coin(-post.price, request.user.coin, None, request.user, '购买《%s》' % (post.title, ))
        log_coin(post.price, post.author.coin, None, post.author, '出售《%s》' % (post.title, ))

        return redirect('archive:detail', pk=post.id)


class UserView(LoginRequiredMixin, PaginationMixin, ListView):
    template_name = 'archive/user.html'
    name = 'archive:user'
    paginate_by = 15
    queryset = User.objects.order_by('-rank')


class GiftListView(LoginRequiredMixin, PaginationMixin, ListView):
    template_name = 'archive/gift_list.html'
    name = 'archive:shop'
    paginate_by = 36
    queryset = models.Gift.objects.filter(show=True)


class GiftDetailView(LoginRequiredMixin, PaginationMixin, DetailView):
    template_name = 'archive/gift_detail.html'
    queryset = models.Gift.objects.filter(show=True)


class OrderCreateView(LoginRequiredMixin, CreateView):
    template_name = 'archive/order_edit.html'
    model = models.GiftLog
    fields = [
        'address',
        'remark'
    ]

    def get_context_data(self, **kwargs):
        kwargs['gift'] = get_object_or_404(models.Gift, show=True, pk=self.kwargs['gift_id'])
        return super(OrderCreateView, self).get_context_data(**kwargs)

    @transaction.atomic
    def form_valid(self, form):
        gift = get_object_or_404(models.Gift, show=True, pk=self.kwargs['gift_id'])
        return_url = reverse('archive:gift', kwargs=dict(pk=gift.id))

        if gift.amount <= 0:
            return render(self.request, 'error.html', context={
                'errors': '没货了，请提醒管理员上货！',
                'return_url': return_url
            })

        if gift.price > self.request.user.coin:
            return render(self.request, 'error.html', context={
                'errors': '你没有那么多金币，快去提交贡献赚钱吧！',
                'return_url': return_url
            })

        self.object = form.save(commit=False)
        self.object.buyer = self.request.user
        self.object.gift = gift
        self.object.cost = gift.price
        self.object.save()

        self.request.user.coin -= gift.price
        self.request.user.save()

        gift.amount = F('amount') - 1
        gift.save()

        log_coin(-gift.price, self.request.user.coin, None, self.request.user, "购买“%s”" % (gift.name, ))

        return redirect(self.get_success_url())

    def get_success_url(self):
        return reverse('archive:order', kwargs=dict(pk=self.object.id))


class ProfileOrderView(LoginRequiredMixin, PaginationMixin, ListView):
    template_name = 'archive/my_order.html'
    paginate_by = 20

    def get_queryset(self):
        return models.GiftLog.objects.filter(buyer=self.request.user)


class OrderDetailView(LoginRequiredMixin, DetailView):
    template_name = 'archive/order.html'

    def get_queryset(self):
        return models.GiftLog.objects.filter(buyer=self.request.user)


class AttachmentView(LoginRequiredMixin, View):
    def get_queryset(self):
        if self.request.user.has_perm('post-change'):
            return models.Post.posts.all()
        else:
            return models.Post.posts.filter((Q(author_id=self.request.user.id)) | (Q(verify='pass') & ~Q(author_id=self.request.user.id)))

    def get(self, request, *args, **kwargs):
        post = get_object_or_404(self.get_queryset(), pk=self.kwargs['pk'])
        if request.user.is_superuser or post.author_id == request.user.id:
            pass
        elif post.visible == 'private' or post.visible == 'sell' and not post.buyers.filter(id=request.user.id).exists():
            raise Http404

        chunk_size = 8192
        response = StreamingHttpResponse(FileWrapper(open(post.attachment.path, 'rb'), chunk_size),
                                         content_type='application/octet-stream')
        response['Content-Length'] = post.attachment.size
        response['Content-Disposition'] = "attachment; filename=%s" % os.path.basename(post.attachment.name)
        return response


class JavascriptView(LoginRequiredMixin, TemplateView):
    template_name = 'js/management.js'
    raise_exception = True

    def dispatch(self, request, *args, **kwargs):
        referer = request.META.get('HTTP_REFERER', '')

        try:
            u1 = urlparse(referer)
            u2 = urlparse(request.build_absolute_uri())

            if u1.scheme != u2.scheme or u1.netloc != u2.netloc:
                raise BaseException()
        except:
            return self.handle_no_permission()

        return super(JavascriptView, self).dispatch(request, *args, **kwargs)