# Generated by Django 4.2.7 on 2023-11-10 01:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('boards', '0005_alter_postimage_image'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='category',
            field=models.CharField(choices=[('best_all', '#전체'), ('best_movies', '#올해의_영화'), ('best_dramas', '#올해의_드라마'), ('best_books', '#올해의_책'), ('best_music', '#올해의_음악'), ('best_moments', '#올해의_순간'), ('best_hobbies', '#올해의_취미'), ('best_discoveries', '#올해의_발견'), ('best_habits', '#올해의_습관'), ('best_sadness', '#올해의_우울'), ('best_thoughts', '#올해의_생각'), ('best_failures', '#올해의_실패'), ('best_regrets', '#올해의_후회'), ('best_humor', '#올해의_유머'), ('best_tears', '#올해의_눈물'), ('best_spending', '#올해의_소비'), ('best_emotions', '#올해의_감동'), ('best_travels', '#올해의_여행'), ('best_food', '#올해의_음식'), ('best_gifts', '#올해의_선물'), ('best_photos', '#올해의_사진'), ('next_year_me', '#내년의_나')], max_length=20, verbose_name='카테고리'),
        ),
    ]
