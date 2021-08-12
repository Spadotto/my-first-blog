from django import forms
from django.utils import timezone
from .models import Post, Comment, Tag
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

class PostForm(forms.ModelForm):

    class Meta:
        model = Post
        fields = ('title', 'text', 'cover', 'attachment', 'tags', )

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.add_input(Submit('submit', 'Save'))
        
class CommentForm(forms.ModelForm):

    class Meta:
        model = Comment
        fields = ('author', 'text', )

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.add_input(Submit('submit', 'Send'))

class TagForm(forms.ModelForm):
    
    posts = forms.MultipleChoiceField(
        required=False,
        choices=[(post.pk, post.title) for post in Post.objects.filter(published_date__lte=timezone.now())],
    )

    class Meta:
        model = Tag
        fields = ('name', 'posts', )

    helper = FormHelper()
    helper.form_method = 'POST'
    helper.add_input(Submit('submit', 'Save'))
