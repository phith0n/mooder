from django import forms
from django.core.validators import MinValueValidator, MaxValueValidator
from archives.models import Post


class PostForm(forms.ModelForm):
    price = forms.IntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        max_value=10,
        min_value=0,
        label='价格',
        initial=0
    )

    def clean_price(self):
        if self.cleaned_data['visible'] == 'sell' and self.cleaned_data['price'] <= 0:
            raise forms.ValidationError('出售的贡献必须填写价格')
        return self.cleaned_data['price']

    class Meta:
        model = Post
        fields = [
            'title',
            'category',
            'visible',
            'price',
            'level',
            'description',
            'content',
            'attachment',
            'remark',
        ]