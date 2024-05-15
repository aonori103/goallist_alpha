from django.db import models
from django.contrib.auth.models import (BaseUserManager, AbstractBaseUser, PermissionsMixin)
from django.urls import reverse_lazy
from datetime import datetime
from django.utils import timezone
from django.core.exceptions import ValidationError

class UserManager(BaseUserManager):
    
    def get_queryset(self):
        return super().get_queryset()
    
    def create_user(self, username, address, password=None):
        if not username:
            raise ValueError('ユーザー名を入力してください')
        
        if not address:
            raise ValueError('メールアドレスを入力してください')
        
        if not password:
            raise ValueError('パスワードを入力してください')
        
        user = self.model(
            username = username,
            address = address
        )
        user.set_password(password) #パスワードをハッシュ化
        user.save(using=self._db) #ユーザーを保存
        return user
    
    def create_superuser(self, username, address, password=None):
        user = self.model(
            username = username,
            address = address
        )
        user.set_password(password) #パスワードをハッシュ化
        user.is_active = True
        user.is_staff = True
        user.save(using=self._db) #ユーザーを保存
        return user


class Users(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=10)
    address = models.EmailField(unique=True, blank=False)
    job = models.CharField(max_length=10, blank=True)
    introduction = models.CharField(max_length=15, blank=True)
    birthday = models.DateField(default='1900-01-01')
    picture = models.FileField(upload_to='picture/%Y/%m/%d/', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    upload_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True) #ログインしているか
    is_staff = models.BooleanField(default=False) #管理権限
    
    USERNAME_FIELD = 'address' #ログイン時にメルアドが必要
    REQUIRED_FIELDS = ['username'] #superuser作成時に必要なフィールド
    
    objects = UserManager()
    
    def __str__(self):
        return self.name
    
    # def get_absolute_url(self):
    #     return reverse_lazy('accounts:user_login')



class BaseMeta(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    upload_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class Goals(BaseMeta):
    user = models.ForeignKey(Users, on_delete=models.CASCADE)
    
    goal_title = models.CharField(max_length=15)
    goal_detail = models.CharField(max_length=30)
    goal_condition = models.IntegerField(blank=True, default=0)
    
    class Meta:
        db_table = 'goals'
    
    def get_absolute_url(self):
        return reverse_lazy('accounts:goal_detail', kwargs={'pk': self.pk})
    
    def save(self, *args, **kwargs):
        user_goals = Goals.objects.filter(user=self.pk)
        max_goals = 100  # 上限数
        if self.pk is None and user_goals.count() >= max_goals:
            raise ValidationError("夢リストの上限に達しました。")
        super().save(*args, **kwargs)
        
    
    def __str__(self):
        return self.name
    


class Tasks(BaseMeta):
    goals = models.ForeignKey(Goals, on_delete=models.CASCADE)
    
    task_title = models.CharField(max_length=50)
    task_condition = models.BooleanField(default='0', blank=False, null=False)
    task_priority = models.IntegerField(default='0', blank=False, null=False)
    task_due = models.DateField(default=timezone.now)
    
    class Meta:
        db_table = 'tasks'
        
    
    def __str__(self):
        return self.name