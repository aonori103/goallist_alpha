from datetime import datetime
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView, View
from . import forms
from .forms import RegistForm, UserLoginForm, UserEditForm, GoalRegistForm, GoalEditForm
from django.contrib.auth import authenticate, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.messages.views import SuccessMessageMixin
from .models import Users, Goals, Tasks
from django.shortcuts import render, redirect, get_object_or_404
import cv2
import numpy as np
from PIL import ImageFont, ImageDraw, Image
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.urls import reverse
from django.contrib import messages


class HomeView(TemplateView):
    template_name = 'home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['time'] = datetime.now()
        return context


class RegisterUserView(CreateView):
    template_name = 'user_regist.html'
    form_class = RegistForm
    success_url = reverse_lazy('accounts:user_login')
    
    def form_valid(self, form):
        form.instance.created_at = datetime.now()
        form.instance.upload_at = datetime.now()
        
        # Form validation and password validation
        cleaned_data = form.cleaned_data
        username = cleaned_data.get('username')
        address = cleaned_data.get('address')
        password = cleaned_data.get('password')

        user = Users(username=username, address=address)
        try:
            validate_password(password, user)
        except ValidationError as e:
            form.add_error('password', e.messages)
            return self.form_invalid(form)
        
        messages.success(self.request, '登録に成功しました')

        return super().form_valid(form)


class UserLoginView(LoginView):
    template_name = 'user_login.html'
    authentication_form = UserLoginForm
    
    def form_valid(self, form):
        remember = form.cleaned_data['remember']
        if remember:
            self.request.session.set_expiry(1209600) #ログイン保持状態にチェックがあれば2週間(1209600)保持する
        return super().form_valid(form)
    
    def form_invalid(self, form):
        # カスタムエラーメッセージを追加
        return super().form_invalid(form)
        

class UserLogoutView(View):
    
    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('accounts:user_login')
    

class UserEditView(UpdateView, SuccessMessageMixin, LoginRequiredMixin): #ログインしないと実行できなくする
    template_name = 'user_edit.html'
    model = Users
    form_class = forms.UserEditForm
    
    def get_success_url(self):
        return reverse_lazy('accounts:home')
    
    def form_valid(self, form):
        form.instance.user = self.request.user # 現在のユーザーを指定
        form.instance.upload_at = datetime.now()
        messages.success(self.request, 'ユーザー情報を変更しました')
        return super().form_valid(form)
    
    
    
# 夢一覧画面作る
class GoalListView(ListView, LoginRequiredMixin):
    template_name = 'goal_list.html'
    model = Goals
    context_object_name = 'goals'


# 夢作成用画面作る（フォームあり）
class GoalRegistView(CreateView, LoginRequiredMixin):
    template_name = 'goal_regist.html'
    model = Goals
    form_class = GoalRegistForm
    
    
    def form_valid(self, form):
        form.instance.user = self.request.user # 現在のユーザーを指定
        form.instance.created_at = datetime.now()
        form.instance.upload_at = datetime.now()
        goal = form.save(commit=False)
        goal.save()
        messages.success(self.request, '登録に成功しました')
        return super().form_valid(form)
    
    def get_success_url(self):
        return reverse('accounts:goal_list', kwargs={'pk': self.object.pk})


class GoalDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'goal_delete.html'
    model = Goals
    
    def delete(self, request, *args, **kwargs):
        response = super().delete(request, *args, **kwargs)
        messages.success(self.request, '削除しました')
        return response
    
    def get_success_url(self):
        return reverse('accounts:goal_list', kwargs={'pk': self.object.pk})



# 夢編集画面
class GoalEditView(UpdateView, SuccessMessageMixin, LoginRequiredMixin):
    template_name = 'goal_edit.html'
    model = Goals
    form_class = GoalEditForm
    
    def form_valid(self, form):
        form.instance.user = self.request.user # 現在のユーザーを指定
        form.instance.upload_at = datetime.now()
        messages.success(self.request, '夢の内容を変更しました')
        return super().form_valid(form)
    
    
    def get_success_url(self):
        return reverse('accounts:goal_list', kwargs={'pk': self.object.pk})


# 夢の個別画面つくる
class GoalDetailView(View, LoginRequiredMixin):
    models = Goals
    queryset = Goals.objects.all()
    template_name = 'goal_detail.html'
    
    def get(self, request, pk, **kwargs):
        context = {}
        context["goal"] = Goals.objects.filter(id=pk).first()
        obj = Goals.objects.filter(id=pk).first()
        obj.save()
        return render(request, "goal_detail.html", context)


# 画像生成画面つくる
class PictGenerate(View, LoginRequiredMixin):
    template_name = 'pict_generate.html'

    def putText_japanese(self, img, text, point, size, color): # 日本語で描画できるようにする
        font = ImageFont.truetype('/home/aonori103/fonts/UDDigiKyokashoN-R.ttc', size)
        img_pil = Image.fromarray(img) # imgをndarrayからPILに変換
        draw = ImageDraw.Draw(img_pil) # #drawインスタンス生成
        draw.text(point, text, fill=color, font=font) # テキスト描画
        return np.array(img_pil) # PILからndarrayに変換して返す


    def get(self, request, pk):
        profile_goal = Goals.objects.get(pk=pk)
        user_profile = profile_goal.user
        image_file = '/home/aonori103/goallist_alpha/goallist_project/static/test.png'
        img = cv2.imread(image_file)
        img = self.putText_japanese(img, user_profile.username, (130, 150), 40, (25, 131, 255))
        img = self.putText_japanese(img, user_profile.job, (140, 220), 25, (25, 131, 255))
        img = self.putText_japanese(img, str(user_profile.birthday), (140, 260), 25, (25, 131, 255))
        img = self.putText_japanese(img, user_profile.introduction, (140, 300), 25, (25, 131, 255))
        img = self.putText_japanese(img, profile_goal.goal_title, (140, 340), 30, (25, 131, 255))
        img = self.putText_japanese(img, profile_goal.goal_detail, (140, 380), 30, (25, 131, 255))

    # 画像を保存するパスを指定
        save_path = '/home/aonori103/goallist_alpha/goallist_project/static/kakouzumi.png'
        cv2.imwrite(save_path, img)

    # テンプレートに渡すコンテキストを作成
        context = {
            'image_url': save_path.replace('/home/aonori103/goallist_alpha/goallist_project/static/', '/static/')
        }

        # テンプレートをレンダリング
        return render(request, self.template_name, context)