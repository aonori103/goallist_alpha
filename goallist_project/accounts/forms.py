from django import forms
from django.core.exceptions import ValidationError
from django.core import validators
from datetime import datetime
from .models import Users, Goals, Tasks
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth.forms import AuthenticationForm

class RegistForm(forms.ModelForm):
    username = forms.CharField(label='ユーザー名', max_length=10, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10字以内'}))
    address = forms.EmailField(label='メールアドレス', widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'xxx@mail.com'}))
    password = forms.CharField(label='パスワード', max_length=30, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '30字以内'}))
    confirm_password = forms.CharField(label='パスワード再入力', max_length=30, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '30字以内'}))
    
    class Meta:
        model = Users
        fields = ['username', 'address', 'password']

        
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data['password'] #再入力したパスワードが合っているか
        confirm_password = cleaned_data['confirm_password']
        if password != confirm_password:
            raise forms.ValidationError('パスワードが異なります')
    
    def save(self, commit=False):
        user = super().save(commit=False)
        validate_password(self.cleaned_data['password'], user)
        user.set_password(self.cleaned_data['password'])
        user.save()
        return user


class UserLoginForm(AuthenticationForm):
    username = forms.EmailField(label='メールアドレス', widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'xxx@mail.com'})) #ログイン時にメルアド必須のため
    password = forms.CharField(label='パスワード', max_length=30, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': '30字以内'}))
    remember = forms.BooleanField(label='ログイン状態を保持する', required=False)



# ユーザー編集用画面とフォーム作る。jobとかintroductionとかを追加する
class UserEditForm(forms.ModelForm):
    username = forms.CharField(label='名前', help_text="10字以内 / 必須", max_length=10, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10字以内', 'value': Users.username}))
    address = forms.EmailField(label='メールアドレス', help_text="必須", widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'xxx@mail.com'}))
    job = forms.CharField(label='職業', help_text="10字以内", max_length=10, required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '10字以内'}))
    introduction = forms.CharField(label='自己紹介', help_text="15字以内", max_length=15, required=False,  widget=forms.Textarea(attrs={'class': 'form-control', 'style': 'line-height: 1.5; height: 6em;', 'placeholder': '簡潔に'}))
    birthday = forms.DateField(label='誕生日', widget=forms.DateInput(attrs={'type': 'date'}))

    class Meta:
        model = Users
        fields = ['username', 'address', 'job', 'introduction', 'birthday']
        error_messages = {
            "username": {"required": "ユーザー名が入力されていません",},
            "address": {"required": "メールアドレスが入力されていません",},
        }
    
    def save(self, *args, **kwargs):
        user = super().save(commit=False)
        user.upload_at = datetime.now()
        user.save()
        return user
    
    
    
    # 夢編集用画面とフォーム作る。
class GoalRegistForm(forms.ModelForm):
    goal_title = forms.CharField(label='叶えたい夢', max_length=15, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '15字以内。簡潔に'}))
    goal_detail = forms.CharField(label='夢の詳細', max_length=30, widget=forms.Textarea(attrs={'class': 'form-control', 'style': 'line-height: 1.5; height: 6em;', 'placeholder': '改行も反映されます'}), required=False)
    
    class Meta:
        model = Goals
        fields = ['goal_title', 'goal_detail']
    
    def save(self, *args, **kwargs):
        obj = super(GoalRegistForm, self).save(commit=False)
        obj.created_at = datetime.now()
        obj.upload_at = datetime.now()
        obj.save()
        return obj


class GoalEditForm(forms.ModelForm):
    goal_title = forms.CharField(label='叶えたい夢', initial=Goals.goal_title, max_length=15, widget=forms.TextInput(attrs={'class': 'form-control'}))
    goal_detail = forms.CharField(label='夢の詳細', initial=Goals.goal_detail, max_length=30, required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'style': 'line-height: 1.5; height: 6em;'}))
    
    class Meta:
        model = Goals
        fields = ['goal_title', 'goal_detail']
    
    def save(self, *args, **kwargs):
        obj = super(GoalEditForm, self).save(commit=False)
        obj.upload_at = datetime.now()
        obj.save()
        return obj