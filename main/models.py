from django.db import models
from django.shortcuts import render

from account.models import User
from django.urls import reverse_lazy


class Category(models.Model):
    slug = models.SlugField(primary_key=True, max_length=50)
    name = models.CharField(max_length=50)
    image = models.ImageField(upload_to='categories', blank=True, null=True)
    parent = models.ForeignKey('self', related_name='children', null=True, blank=True, on_delete=models.CASCADE)

    def __str__(self):
        if self.parent:
            return f'{self.parent} -> {self.name}'
        return self.name

    @property
    def get_children(self):
        if self.children:
            return self.children.all()
        return False

    @property
    def get_image_all(self):
        return self.images.all()


class Post(models.Model):
    title = models.CharField(max_length=300)
    description = models.TextField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='post')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    created = models.DateTimeField()

    likes = models.ManyToManyField(User, related_name='likes', blank=True)
    favourite = models.ManyToManyField(User, related_name='favourite', blank=True)

    # class Meta:
    #     ordering = ['-pub_date', ]

    def __str__(self):
        return self.title

    @property
    def get_image(self):
        return self.images.first()

    @property
    def get_image_all(self):
        return self.images.all()


    def get_all(self):
        return Post.objects.all()

    def get_absolute_url(self):
        from django.shortcuts import reverse
        return reverse('detail', kwargs={'pk': self.pk})


class Image(models.Model):
    image = models.ImageField(upload_to='post')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')

    def __str__(self):
        if self.image:
            return self.image.url
        return ''


class Comment(models.Model):
    post = models.ForeignKey(Post, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='user', on_delete=models.CASCADE)
    body = models.TextField()
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('created',)

    def __str__(self):
        return f'Comment {self.body} by {self.user}'

    def get_absolute_url(self):
        return reverse_lazy("blog_detail", args=[str(self.pk)])

    def get_absolute_url2(self):
        from django.shortcuts import reverse
        return reverse('detail', kwargs={'pk': self.pk})



