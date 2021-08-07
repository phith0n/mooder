from django.shortcuts import redirect, reverse, get_object_or_404, render
from django.urls import reverse_lazy
from django.http.response import HttpResponseRedirect
from django.contrib.auth import get_user_model
from django.views.generic import TemplateView, ListView, UpdateView, CreateView, DetailView, DeleteView, View
from django.views.generic.edit import SingleObjectMixin
from django.views.generic.dates import DayArchiveView
from pure_pagination.mixins import PaginationMixin
from django.contrib.auth.mixins import PermissionRequiredMixin, AccessMixin
from django.utils.crypto import get_random_string
from django.db import transaction
from django.utils.timezone import now
from django.db.models.functions import TruncDay
from django.db.models import Sum, Count
from django.db.models import Q, F
from archives.models import Post, Gift, GiftLog, Link, Comment
from accounts.models import Invitecode
from datetime import timedelta
from . import models
from django.contrib.sessions.models import Session
from accounts.models import USER_LEVEL
from archives.models import LEVEL_STATUS_CHOICES
from .forms import PostForm

User = get_user_model()

# Create your views here.


class AdminPermissionMixin(PermissionRequiredMixin):
    error_403_template = 'management/403.html'

    def _response_403_template(self, template_name=None, *args, **kwargs):
        template_name = template_name if template_name else self.error_403_template
        response = render(self.request, template_name, kwargs)
        response.status_code = 403
        return response

    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if not request.user.is_staff and not request.user.is_auditor:
            return self._response_403_template(errors="你没有后台权限", template_name='403.html')
        if not self.has_permission():
            return self._response_403_template(errors="你需要 %s 权限" % (self.permission_required, ))
        return super(AdminPermissionMixin, self).dispatch(request, *args, **kwargs)


class HideDeleteView(SingleObjectMixin, View):
    jump_url = None

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.show = False
        self.object.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER') or self.jump_url)


class IndexView(AdminPermissionMixin, TemplateView):
    """
        referer http://stackoverflow.com/questions/8746014/django-group-by-date-day-month-year
    """

    date_field = "created_time"
    template_name = 'management/index.html'
    permission_required = 'archives.change_post'

    def _get_analysis_chart(self):
        dweek = now().today() - timedelta(days=7)
        query = Post.posts \
            .filter(created_time__gte=dweek) \
            .annotate(day=TruncDay('created_time')) \
            .values('verify', 'day') \
            .annotate(cnt=Count('id')) \
            .values('day', 'verify', 'cnt') \
            .order_by()
        analysis_count = {}
        for l in list(query):
            day = l['day'].strftime('%Y-%m-%d')
            analysis_count[day] = analysis_count.get(day, {})
            analysis_count[day][l['verify']] = l['cnt']

        return analysis_count

    def _get_user_chart(self):
        query = User.objects\
            .values('level') \
            .annotate(cnt=Count('id')) \
            .values('level', 'cnt') \
            .order_by()

        ret = []
        user_level = dict(USER_LEVEL)
        for user in query:
            ret.append({
                'level': user_level.get(user['level']),
                'count': user['cnt']
            })

        return ret

    def _get_post_chart(self):
        query = Post.posts \
            .values('level') \
            .annotate(cnt=Count('id')) \
            .values('level', 'cnt') \
            .order_by()

        ret = []
        user_level = dict(LEVEL_STATUS_CHOICES)
        for post in query:
            ret.append({
                'level': user_level.get(post['level']),
                'count': post['cnt']
            })

        return ret

    def get_context_data(self, **kwargs):
        kwargs['wait_count'] = Post.posts.filter(verify='wait').count()
        kwargs['all_count'] = Post.posts.count()
        kwargs['gift_count'] = GiftLog.objects.filter(delivery=False).count()
        kwargs['user_count'] = User.objects.count()

        kwargs['analysis_chart'] = self._get_analysis_chart()
        kwargs['user_chart'] = self._get_user_chart()
        kwargs['post_chart'] = self._get_post_chart()
        return super(IndexView, self).get_context_data(**kwargs)


class PostListView(AdminPermissionMixin, PaginationMixin, ListView):
    template_name = 'management/post.html'
    paginate_by = 15
    permission_required = 'archives.change_post'
    queryset = Post.posts.all()

    def get_queryset(self):
        query = self.queryset
        keyword = self.request.GET.get('keyword')
        if keyword:
            query = query.filter(title__icontains=keyword)

        return query


class VerifyPostListView(PostListView):
    queryset = Post.posts.filter(verify='wait')


class EditPostView(AdminPermissionMixin, UpdateView):
    queryset = Post.posts.all()
    template_name = 'management/post_edit.html'
    permission_required = 'archives.change_post'
    form_class = PostForm

    @property
    def success_url(self):
        return self.request.POST.get('return_url', reverse('management-post-list'))


class VerifyView(AdminPermissionMixin, UpdateView):
    fields = [
        'rank',
        'level',
        'remark'
    ]
    template_name = 'management/post_verify.html'
    success_url = reverse_lazy('management-post-list-verify')
    queryset = Post.posts.filter(verify='wait')
    permission_required = 'archives.change_post'

    @transaction.atomic
    def form_valid(self, form):
        if form.cleaned_data['rank'] <= 0:
            form.add_error('rank', 'Rank不能为0')
            return self.form_invalid(form)

        self.object = form.save(commit=False)
        self.object.verify = 'pass'

        self.object.author.rank += self.object.rank
        self.object.author.coin += self.object.rank

        self.object.save()
        self.object.author.save()
        models.log_coin(self.object.rank, self.object.author.coin, None, self.object.author)

        return HttpResponseRedirect(self.get_success_url())


class IgnoreView(AdminPermissionMixin, UpdateView):
    template_name = 'management/ignore_post.html'
    queryset = Post.posts.filter(verify='wait')
    jump_url = reverse_lazy('management-post-list-verify')
    permission_required = 'archives.change_post'
    fields = [
        'remark'
    ]

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.verify = 'failed'
        self.object.save()
        return HttpResponseRedirect(self.jump_url)


class HideView(AdminPermissionMixin, HideDeleteView):
    queryset = Post.posts.all()
    permission_required = 'archives.delete_post'

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.show = False
        self.object.save()

        return HttpResponseRedirect(request.META.get('HTTP_REFERER') or reverse('management-post-list-verify'))


class UserView(AdminPermissionMixin, PaginationMixin, ListView):
    template_name = 'management/user.html'
    queryset = User.objects.all()
    paginate_by = 15
    permission_required = 'accounts.change_member'


class UserDetailView(AdminPermissionMixin, DetailView):
    model = User
    template_name = 'management/user_detail.html'
    permission_required = 'accounts.change_member'


class BanUserView(AdminPermissionMixin, SingleObjectMixin, View):
    permission_required = 'accounts.change_member'

    def get_queryset(self):
        if self.request.user.is_superuser:
            return User.objects.filter(is_superuser=False)
        elif self.request.user.is_staff:
            return User.objects.filter(is_superuser=False, is_staff=False)
        else:
            return User.objects.filter(is_superuser=False, is_staff=False, is_auditor=False)

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        pk = self.kwargs.get(self.pk_url_kwarg)
        queryset = self.get_queryset().filter(pk=pk)

        try:
            object = queryset.get()
        except queryset.model.DoesNotExist:
            return redirect(request.META.get('HTTP_REFERER', reverse('management-user-list')))

        object.is_active = not object.is_active
        object.save()

        for s in Session.objects.all():
            data = s.get_decoded()
            if data.get('_auth_user_id', None) == str(object.id):
                s.delete()

        return redirect(request.META.get('HTTP_REFERER', reverse('management-user-list')))


class CoinLogView(AdminPermissionMixin, PaginationMixin, ListView):
    template_name = 'management/coin_log_list.html'
    paginate_by = 15
    permission_required = 'managements.change_coinlog'

    def get_context_data(self, **kwargs):
        uid = self.kwargs.get('uid')
        kwargs['member'] = get_object_or_404(User, pk=uid)
        return super(CoinLogView, self).get_context_data(**kwargs)

    def get_queryset(self):
        uid = self.kwargs.get('uid')
        return models.CoinLog.objects.filter(user_id=uid)


class CoinView(AdminPermissionMixin, CreateView):
    template_name = 'management/coin.html'
    model = models.CoinLog
    fields = [
        'coin',
        'user',
        'message'
    ]
    success_url = reverse_lazy('management-user-list')
    permission_required = 'managements.change_coinlog'

    def get_initial(self):
        return {
            'user': self.kwargs.get('uid')
        }

    @transaction.atomic
    def form_valid(self, form):
        self.object = form.save(commit=False)
        if self.object.coin < 0 and self.object.user.coin + self.object.coin < 0:
            self.object.coin = -self.object.user.coin

        self.object.admin = self.request.user
        self.object.user.coin += self.object.coin
        self.object.rest = self.object.user.coin

        self.object.user.save()
        self.object.save()
        return HttpResponseRedirect(self.get_success_url())


class InviteCodeListView(AdminPermissionMixin, PaginationMixin, ListView):
    template_name = 'management/invitecode_list.html'
    paginate_by = 10
    model = Invitecode
    permission_required = 'accounts.change_invitecode'


class GenerateInvitecodeView(AdminPermissionMixin, View):
    template_name = 'management/invitecode_list.html'
    paginate_by = 10
    model = Invitecode
    permission_required = 'accounts.add_invitecode'

    def post(self, request):
        code = Invitecode(createdby=request.user, code=get_random_string(32, '0123456789abcdef'))
        code.save()
        return redirect('management-invitecode')


class DeleteInviteCodeView(AdminPermissionMixin, DeleteView):
    success_url = reverse_lazy('management-invitecode')
    queryset = Invitecode.objects.filter(used=False)
    permission_required = 'accounts.delete_invitecode'

    get = DeleteView.http_method_not_allowed


class GiftListView(AdminPermissionMixin, PaginationMixin, ListView):
    template_name = 'management/gift_list.html'
    paginate_by = 15
    queryset = Gift.objects.filter(show=True)
    permission_required = 'archives.change_gift'


class GiftEditView(AdminPermissionMixin, UpdateView):
    template_name = 'management/gift_edit.html'
    fields = [
        'name',
        'price',
        'amount',
        'link',
        'photo',
        'description'
    ]
    success_url = reverse_lazy('management-gift-list')
    queryset = Gift.objects.filter(show=True)
    permission_required = 'archives.change_gift'


class GiftAddView(AdminPermissionMixin, CreateView):
    template_name = 'management/gift_edit.html'
    fields = [
        'name',
        'price',
        'amount',
        'link',
        'photo',
        'description'
    ]
    success_url = reverse_lazy('management-gift-list')
    model = Gift
    permission_required = 'archives.add_gift'


class GiftDeleteView(AdminPermissionMixin, HideDeleteView):
    queryset = Gift.objects.filter(show=True)
    jump_url = reverse_lazy('management-gift-list')
    permission_required = 'archives.delete_gift'


class GiftLogListView(AdminPermissionMixin, PaginationMixin, ListView):
    template_name = 'management/order_list.html'
    queryset = GiftLog.objects.all()
    paginate_by = 15
    permission_required = 'archives.change_giftlog'


class GiftLogWaitListView(GiftLogListView):
    queryset = GiftLog.objects.filter(delivery=False)


class GiftLogDetailView(AdminPermissionMixin, UpdateView):
    template_name = 'management/order.html'
    model = GiftLog
    fields = [
        'reply',
    ]
    permission_required = 'archives.change_giftlog'

    @transaction.atomic
    def form_valid(self, form):
        self.object = form.save(commit=False)
        if not self.object.delivery:
            self.object.delivery = True
            self.object.delivery_time = now()

        self.object.save()
        return redirect('management-order-detail', pk=self.object.id)


class LinkListView(AdminPermissionMixin, PaginationMixin, ListView):
    model = Link
    template_name = 'management/link_list.html'
    paginate_by = 15
    permission_required = 'archives.change_link'


class LinkEditView(AdminPermissionMixin, UpdateView):
    model = Link
    template_name = 'management/link_edit.html'
    success_url = reverse_lazy('management-link-list')
    fields = [
        'title',
        'link'
    ]
    permission_required = 'archives.change_link'


class LinkAddView(AdminPermissionMixin, CreateView):
    model = Link
    template_name = 'management/link_edit.html'
    success_url = reverse_lazy('management-link-list')
    fields = [
        'title',
        'link'
    ]
    permission_required = 'archives.add_link'


class LinkDeleteView(AdminPermissionMixin, DeleteView):
    model = Link
    success_url = reverse_lazy('management-link-list')
    permission_required = 'archives.delete_link'

    get = DeleteView.http_method_not_allowed


class DeleteCommentView(AdminPermissionMixin, DeleteView):
    queryset = Comment.objects.all()
    permission_required = 'archives.delete_comment'

    get = DeleteView.http_method_not_allowed

    def get_success_url(self):
        return self.request.META.get('HTTP_REFERER')