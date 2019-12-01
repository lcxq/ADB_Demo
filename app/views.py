from django.shortcuts import render

# Create your views here.
# -*- coding: utf-8 -*-
# from __future__ import unicode_literals
from app import models
from app.models import Reddit
from django.shortcuts import render
from django.http import HttpResponse

# 包装csrf请求，避免django认为其实跨站攻击脚本
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

# 分页
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

# 用于词云生成的包
import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_agg import FigureCanvasAgg
from wordcloud import *
from imageio import imread
bg_pic = imread('timg.jpg')

def getWordCloud(request):
    # 补充停用词
    f = open("stopwords-en.txt", mode='r', encoding="UTF-8")
    li = []
    for word in f.readlines():
        li.append(word.replace('\n', ''))
    stopwords = set(STOPWORDS)
    stopword_list = ['fuck', 'fucking', 'shit', 'good', 'bad', 'think', 'make', 'know', 'even', 'really', 'one',
                     'going', 'need', 'got', 'look', 'still']
    for word in stopword_list:
        stopwords.add(word)
    for word in li:
        stopwords.add(word)
    # 连接数据库
    sql_conn = sqlite3.connect('reddit_new.sqlite')
    # 读取post
    reddit_id = request.GET['id']
    subreddit = request.GET['subreddit']
    author = request.GET['author']
    if reddit_id == "" and subreddit == "" and author == "":
        messages.warning(request, "Please input something!")
        return render(request, "query.html")
    # 查找
    if reddit_id != "" and subreddit == "" and author == "":
        sql_query = "select body from reddit where id = '%s'"%(reddit_id)
    elif reddit_id == "" and subreddit != "" and author == "":
        sql_query = "select body from reddit where subreddit = '%s'"%(subreddit)
    elif reddit_id == "" and subreddit == "" and author != "":
        sql_query = "select body from reddit where author = '%s'"%(author)
    elif reddit_id != "" and subreddit != "" and author == "":
        sql_query = "select body from reddit where subreddit = '%s' and id = '%s'"%(subreddit,reddit_id)
    elif reddit_id == "" and subreddit != "" and author != "":
        sql_query = "select body from reddit where subreddit = '%s' and author = '%s'"%(subreddit,author)
    elif reddit_id != "" and subreddit == "" and author != "":
        sql_query = "select body from reddit where id = '%s' and author = '%s'"%(reddit_id,author)
    elif reddit_id != "" and subreddit != "" and author != "":
        sql_query = "select body from reddit where id = '%s' and author = '%s' and subreddit = '%s'"%(reddit_id,author,subreddit)
    df = pd.read_sql(sql_query, sql_conn)
    # 文本生成
    text = "".join(list(df['body'])).lower()
    # 词云生成
    wc = WordCloud(background_color="white",
                   stopwords=stopwords,
                   max_words=200,
                   max_font_size=120,
                   mask=bg_pic,
                   random_state=42)
    wc.generate(text)
    fig = plt.figure()
    plt.imshow(wc, interpolation="bilinear")
    plt.axis("off")
    # 转HTML
    canvas = FigureCanvasAgg(fig)
    response = HttpResponse(content_type='image/png')
    canvas.print_jpg(response)
    plt.close(fig)
    return response

def mainindex(request):
    return render(request, "query.html")

def insert_index(request):
    return render(request, "insert.html")

def update_index(request):
    return render(request, "update.html")

def delete(request):
    reddit_id = request.GET['id']
    subreddit = request.GET['subreddit']
    author = request.GET['author']
    if reddit_id == "" and subreddit == "" and author == "":
        return render(request, 'query.html')
    else:
        reddit_list = models.Reddit.objects\
            .filter(id__icontains=reddit_id)\
            .filter(subreddit__icontains=subreddit)\
            .filter(author__icontains=author)[:1000]
        if reddit_list.__len__() == 1000:
            messages.warning(request, "Over 1000 records!")
        elif reddit_list.__len__() == 0:
            messages.warning(request, "This record does not exist!")
        else:
            models.Reddit.objects \
                .filter(id__icontains=reddit_id) \
                .filter(subreddit__icontains=subreddit) \
                .filter(author__icontains=author).delete()
            messages.success(request, "Success!")
    return render(request, 'query.html')

def query(request):
    reddit_id = request.GET['id']
    subreddit = request.GET['subreddit']
    author = request.GET['author']
    page = request.GET.get('page')
    if reddit_id == "" and subreddit == "" and author == "":
        return render(request, "query.html")
    else:
        if reddit_id != "" and subreddit == "" and author == "":
            reddit_list = models.Reddit.objects\
                .filter(id=reddit_id)
        elif reddit_id == "" and subreddit != "" and author == "":
            reddit_list = models.Reddit.objects\
                .filter(subreddit=subreddit)        
        elif reddit_id == "" and subreddit == "" and author != "":
            reddit_list = models.Reddit.objects\
                .filter(author=author)
        elif reddit_id != "" and subreddit != "" and author == "":
            reddit_list = models.Reddit.objects\
                .filter(id=reddit_id)\
                .filter(subreddit=subreddit)
        elif reddit_id == "" and subreddit != "" and author != "":
            reddit_list = models.Reddit.objects\
                .filter(subreddit=subreddit)\
                .filter(author=author)
        elif reddit_id != "" and subreddit == "" and author != "":
            reddit_list = models.Reddit.objects\
                .filter(id=reddit_id)\
                .filter(author=author)
        elif reddit_id != "" and subreddit != "" and author != "":
            reddit_list = models.Reddit.objects\
                .filter(id=reddit_id)\
                .filter(author=author)\
                .filter(subreddit=subreddit)
    paginator = Paginator(reddit_list, 50)
    try:
        reddit_list_paginate = paginator.page(page)
    except PageNotAnInteger:
        reddit_list_paginate = paginator.page(1)
    except EmptyPage:
        reddit_list_paginate = paginator.page(paginator.num_pages)
    return render(request, 'query.html',
                  {'reddit_list': reddit_list_paginate,
                   "reddit_id": reddit_id,
                   "subreddit": subreddit,
                   "author": author})

@csrf_exempt
def update(request):
    reddit_id = request.POST.get('id')
    body = request.POST.get('body')
    if reddit_id == "" or body == "":
        messages.warning(request, "Please input reddit_id and text!")
        return render(request, 'update.html')
    subreddit = request.POST.get('subreddit')
    if subreddit == "":
        subreddit = "default"
    author = request.POST.get('author')
    if author == "":
        author = "default"
    ups = request.POST.get('ups', None)
    if ups == "":
        ups = 0
    downs = request.POST.get('downs', None)
    if downs == "":
        downs = 0
    if Reddit.objects.filter(id=reddit_id).__len__() == 0:
        messages.warning(request, "This record does not exist!")
        return render(request, 'update.html')
    reddit=Reddit()
    reddit.id=reddit_id
    reddit.subreddit=subreddit
    reddit.body=body
    reddit.author = author
    reddit.ups = ups
    reddit.downs = downs
    reddit.save()
    messages.success(request, "Success！")
    return render(request, 'update.html')

@csrf_exempt
def insert(request):
    reddit_id = request.POST.get('id')
    body = request.POST.get('body')
    if reddit_id == "" or body == "":
        messages.warning(request, "Please input reddit_id and text!")
        return render(request, "insert.html")
    subreddit = request.POST.get('subreddit')
    if subreddit == "":
        subreddit = "default"
    author = request.POST.get('author')
    if author == "":
        author = "default"
    ups = request.POST.get('ups', None)
    if ups == "":
        ups = 0
    downs = request.POST.get('downs', None)
    if downs == "":
        downs = 0
    if Reddit.objects.filter(id=reddit_id).__len__() != 0:
        messages.warning(request, "Duplicate record exists!")
        return render(request, 'insert.html')
    reddit=Reddit()
    reddit.id=reddit_id
    reddit.subreddit=subreddit
    reddit.body=body
    reddit.author = author
    reddit.ups = ups
    reddit.downs = downs
    reddit.save()
    messages.success(request, "Success！")
    return render(request, 'insert.html')
