from django import forms
from .models import Post, Comment


class PostForm(forms.ModelForm):
    text = forms.CharField(
        widget=forms.Textarea,
        label="Введите текст",
        required=True,
        help_text="Текст поста",
    )

    class Meta:
        model = Post
        fields = model.fields
        labels = {"group": "Выберите группу"}

class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
        labels = {
            'text': 'Тект комментария',
        }
        help_texts = {
            'text': 'Введите текст вашего комментария',
        }
