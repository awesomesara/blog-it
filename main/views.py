from datetime import timedelta

from django.db.models import Q
from django.forms import modelformset_factory
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import ListView, DetailView, DeleteView, View
from .forms import PostForm, ImageForm, CommentForm
from .models import *
from django.contrib import messages


class MainPageView(ListView):
    model = Post
    template_name = 'index.html'
    context_object_name = 'posts'
    paginate_by = 2

    def get_template_names(self):
        template_name = super(MainPageView, self).get_template_names()
        search = self.request.GET.get('q')
        if search:
            template_name = 'search.html'
        return template_name

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        search = self.request.GET.get('q')
        filter = self.request.GET.get('filter')
        if search:
            context['posts'] = Post.objects.filter(Q(title__icontains=search)|
                                                       Q(description__icontains=search))
        elif filter:
            start_date = timezone.now() - timedelta(days=1)
            context['posts'] = Post.objects.filter(created__gte=start_date)
        else:
            context['posts'] = Post.objects.all()
        return context


class CategoryDetailView(DetailView):
    model = Category
    template_name = 'category-detail.html'
    context_object_name = 'category'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.slug = kwargs.get('slug', None)
        return super().get(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['posts'] = Post.objects.filter(category_id=self.slug)
        return context

# def category_detail(request, slug):
#     category = Category.objects.get(slug=slug)
#     post = Post.objects.filter(category_id=slug)
#     return render(request, 'category-detail.html', local())


class PostDetailView(View):
    model = Post
    template_name = 'post-detail.html'
    context_object_name = 'post'

    def get(self, request, *args, **kwargs):
        form = CommentForm
        self.pk = kwargs.get('pk', None)
        post = get_object_or_404(Post, pk=self.pk)
        comment = list(Comment.objects.filter(post_id=post))
        comment.reverse()
        if len(comment) > 5:
            comment = comment[:5]
        return render(request, 'post-detail.html', locals())

    def post(self, request, *args, **kwargs):
        pk = self.kwargs['pk']
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save()
        return redirect(reverse_lazy('detail', kwargs={'pk': pk}), Comment.get_absolute_url)
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     image = self.get_object().get_image
    #     context['images'] = self.get_object().images.exclude(id=image.id)
    #     return context


def add_post(request):
    ImageFormSet = modelformset_factory(Image, form=ImageForm, max_num=5)
    if request.method == 'POST':
        post_form = PostForm(request.POST)
        formset = ImageFormSet(request.POST, request.FILES, queryset=Image.objects.none())
        if post_form.is_valid() and formset.is_valid():
            post = post_form.save()

            for form in formset.cleaned_data:
                image = form['image']
                Image.objects.create(image=image, post=post)
            return redirect(post.get_absolute_url())
    else:
        post_form = PostForm()
        formset = ImageFormSet(queryset=Image.objects.none())
    return render(request, 'add-post.html', locals())


def update_post(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.user == post.user:
        ImageFormSet = modelformset_factory(Image, form=ImageForm, max_num=5,fields=('image', ))
        post_form = PostForm(request.POST or None, instance=post)
        formset = ImageFormSet(request.POST or None, request.FILES or None, queryset=Image.objects.filter(post=post))
        if post_form.is_valid() and formset.is_valid():
            recipe = post_form.save()
            images = formset.save(commit=False)
            for image in images:
                image.post = post
                image.save()
            return redirect(post.get_absolute_url())
        return render(request, 'update-post.html', locals())
    else:
        return HttpResponse('<h1>Forbidden</h1>')


class DeletePostView(DeleteView):
    model = Post
    template_name = 'delete-post.html'
    success_url = reverse_lazy('home')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        success_url = self.get_success_url()
        self.object.delete()
        messages.add_message(request, messages.SUCCESS, 'Successfully deleted!')
        return HttpResponseRedirect(success_url)


def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, slug=post,
                                   status='published',
                                   publish__year=year,
                                   publish__month=month,
                                   publish__day=day)
    # List of active comments for this post
    comments = post.comments.filter(active=True)

    if request.method == 'POST':
        # A comment was posted
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            # Create Comment object but don't save to database yet
            new_comment = comment_form.save(commit=False)
            # Assign the current post to the comment
            new_comment.post = post
            # Save the comment to the database
            new_comment.save()
    else:
        comment_form = CommentForm()
    return render(request,
                  'post-detail.html',
                 {'post': post,
                  'comments': comments,
                  'comment_form': comment_form})


class CategoryListView(ListView):
    pass
