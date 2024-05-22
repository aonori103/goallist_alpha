from datetime import datetime
from django.db.models.query import QuerySet
from django.http import HttpRequest
from django.http.response import HttpResponse as HttpResponse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.views.generic.base import TemplateView, View
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
        return super(RegisterUserView, self).form_valid(form)


class UserLoginView(LoginView):
    template_name = 'user_login.html'
    authentication_form = UserLoginForm

    def form_valid(self, form):
        remember = form.cleaned_data['remember']
        if remember:
            self.request.session.set_expiry(1209600) #ログイン保持状態にチェックがあれば2週間(1209600)保持する
        return super().form_valid(form)


class UserLogoutView(View):

    def get(self, request, *args, **kwargs):
        logout(request)
        return redirect('accounts:user_login')

# class UserLogoutView(LogoutView):
#     pass


class UserEditView(UpdateView, SuccessMessageMixin, LoginRequiredMixin): #ログインしないと実行できなくする
    template_name = 'user_edit.html'
    model = Users
    form_class = UserEditForm
    success_message = '更新しました'

    def get_success_url(self):
        return reverse_lazy('accounts:home')

    def get_success_message(self, cleaned_data):
        return cleaned_data.get('username') + 'を更新しました'



    def model_form_upload(request):
        user = None
        if request.method == 'POST':
            form = UserEditForm(request.POST, request.FILES)
            if form.is_valid():
                user = form.save()
        return render(request, 'home.html', context={'form': form, 'user': user})



# 夢一覧画面作る
class GoalListView(ListView, LoginRequiredMixin):
    template_name = 'goal_list.html'
    model = Goals
    context_object_name = 'goals'

    def get_queryset(self):
        return Goals.objects.filter(user=self.request.user)

    def get(self, request, pk=None, *args, **kwargs):
        self.object_list = self.get_queryset()
        context = self.get_context_data()

        if pk is not None:
            goal = Goals.objects.filter(id=pk).first()
            if goal is not None:
                context['goals'] = goal
                goal.save()
            else:
                context['error'] = 'Goal not found.'

        return self.render_to_response(context)


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
        return super().form_valid(form)

    def get_success_url(self):
        # URLに動的にpkを渡して設定する
        user_pk = self.request.user.pk
        return reverse_lazy('accounts:goal_list', kwargs={'pk': user_pk})


class GoalDeleteView(LoginRequiredMixin, DeleteView):
    template_name = 'goal_delete.html'
    model = Goals

    def get_success_url(self):
        # URLに動的にpkを渡して設定する
        pk = self.object.pk
        return reverse_lazy('accounts:goal_list', kwargs={'pk': pk})



# 夢編集画面
class GoalEditView(UpdateView, SuccessMessageMixin, LoginRequiredMixin):
    template_name = 'goal_edit.html'
    model = Goals
    form_class = GoalEditForm

    def get_success_message(self, cleaned_data):
        return f"{self.object.goal_title} を更新しました"

    def get_success_url(self):
        # URLに動的にpkを渡して設定する
        user_pk = self.object.user.pk  # 編集したゴールの所有者のpkを取得
        return reverse_lazy('accounts:goal_list', kwargs={'pk': user_pk})


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
        # cv2.imshow('image', img)

        # cv2.waitKey(0)
        # cv2.destroyAllWindows()
    # 画像を保存するパスを指定
        save_path = '/home/aonori103/goallist_alpha/goallist_project/static/kakouzumi.png'
        cv2.imwrite(save_path, img)

    # テンプレートに渡すコンテキストを作成
        context = {
            'image_url': save_path.replace('/home/aonori103/goallist_alpha/goallist_project/static/', '/static/')
        }

        # テンプレートをレンダリング
        return render(request, self.template_name, context)