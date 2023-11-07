from django.db import models
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()

class Post(models.Model):
    writer = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(verbose_name='수상 제목', max_length=50)
    content = models.TextField(verbose_name='내용', max_length=255)
    created_at = models.DateTimeField(verbose_name='작성일', auto_now_add=True)
    like_count = models.IntegerField(verbose_name='좋아요 수', default=0)
    CATEGORY_CHOICES = [
        ('best_movies', '올해의_영화'),
        ('best_dramas', '올해의_드라마'),
        ('best_books', '올해의_책'),
        ('best_music', '올해의_음악'),
        ('best_moments', '올해의_순간'),
        ('best_hobbies', '올해의_취미'),
        ('best_discoveries', '올해의_발견'),
        ('best_habits', '올해의_습관'),
        ('best_sadness', '올해의_우울'),
        ('best_thoughts', '올해의_생각'),
        ('best_failures', '올해의_실패'),
        ('best_regrets', '올해의_후회'),
        ('best_humor', '올해의_유머'),
        ('best_tears', '올해의_눈물'),
        ('best_spending', '올해의_소비'),
        ('best_emotions', '올해의_감동'),
        ('best_travels', '올해의_여행'),
        ('best_food', '올해의_음식'),
        ('best_gifts', '올해의_선물'),
        ('next_year_me', '내년의_나')
    ]
    category = models.CharField(verbose_name='카테고리', max_length=20, choices=CATEGORY_CHOICES)
    category_id = models.PositiveIntegerField()  # 별도의 카테고리별 ID
    
    def __str__(self):
        return self.title

@receiver(post_save, sender=Post) # Post 모델 객체가 저장될 때 호출
def assign_category_id(sender, instance, created, **kwargs):
    if created: # 새로운 글 생성된 경우
        # 카테고리에서 가장 큰 category_id 값 찾기
        last_post = Post.objects.filter(category=instance.category).order_by('-category_id').first()
        if last_post:
            instance.category_id = last_post.category_id + 1 # category_id에 1을 더해 중복 피하고, 고유한 id 갖게 함
        else:
            instance.category_id = 1
        instance.save()

class PostImage(models.Model):
   post = models.ForeignKey(Post, on_delete=models.CASCADE, default=None)
   image = models.ImageField(upload_to="post/%Y/%m/%d")
   
   def __str__(self):
        return str(self.post)