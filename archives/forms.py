from django import forms
from . import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django .shortcuts import get_object_or_404
from captcha.fields import CaptchaField


class PostForm(forms.ModelForm):
    price = forms.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        max_value=10,
        min_value=0,
        label='价格',
        initial=0
    )

    def __init__(self, *args, **kwargs):
        super(PostForm, self).__init__(*args, **kwargs)
        for field in self:
            field.view_length = 4

        self['title'].view_length = self['content'].view_length = self['description'].view_length = 12
        self['content'].field.widget.require = False
        self['description'].field.widget.attrs['rows'] = 3

        self['content'].help_text = '使用Markdown编写详情'
        self['description'].help_text = '简要描述一下你的问题，不要透露详情'
        self['attachment'].help_text = '没有附件则无需选择'
        self['price'].help_text = '不出售则无需填写，最多10'

    def clean_price(self):
        if self.cleaned_data['visible'] == 'sell' and self.cleaned_data['price'] <= 0:
            raise forms.ValidationError('出售的贡献必须填写价格')
        return self.cleaned_data['price']

    class Meta:
        model = models.Post
        fields = [
            'title',
            'category',
            'visible',
            'level',
            'price',
            'attachment',
            'description',
            'content',
        ]


class CommentForm(forms.ModelForm):
    class Meta:
        model = models.Comment
        fields = [
            'content',
            'parent'
        ]

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)

        self['content'].field.widget.attrs['rows'] = 5
        self['parent'].field.widget = forms.HiddenInput()


class PostImageForm(forms.ModelForm):
    class Meta:
        model = models.PostImage
        fields = [
            'file',
        ]