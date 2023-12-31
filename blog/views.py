from django.shortcuts import render, get_object_or_404
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import User
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.utils.text import slugify
from .models import Category, Post


class CategoryPostsView(ListView):
    model = Post
    template_name = 'blog/category_posts.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']

    def get_queryset(self):
        category = get_object_or_404(Category, slug=self.kwargs['category_slug'], id=self.kwargs['category_id'])
        return Post.objects.filter(category=category)


class PostListView(ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = 5

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['post'] = Post.objects.order_by('-date_posted').first()
        return context


class UserPostListView(ListView):
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    paginate_by = 5

    def get_queryset(self):
        user = get_object_or_404(User, username=self.kwargs['username'])
        return Post.objects.filter(author=user).order_by('-date_posted')


class PostDetailView(DetailView):
    model = Post
    context_object_name = 'post'
    template_name = 'blog/post_detail.html'


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['title', 'category', 'post_image', 'content']
    template_name = 'blog/post-form.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        category_id = self.request.POST.get('category')

        category = get_object_or_404(Category, id=category_id)
        form.instance.category = category
        form.instance.category_slug = slugify(category.name)
        return super().form_valid(form)


class PostUpdateDeleteMixin(LoginRequiredMixin, UserPassesTestMixin):
    model = Post
    fields = ['title', 'category', 'post_image', 'content']

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_object(self, queryset=None):
        return get_object_or_404(self.model, pk=self.kwargs['pk'])

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author


class PostUpdateView(PostUpdateDeleteMixin, UpdateView):
        model = Post
        fields = ['title', 'category', 'post_image', 'content']
        template_name = 'blog/post_confirm.html'
        pass


class PostDeleteView(PostUpdateDeleteMixin, DeleteView):
        model = Post
        fields = ['title', 'category', 'post_image', 'content']
        template_name = 'blog/post_confirm.html'
        success_url = '/'


def home(request):
    categories = Category.objects.all()
    posts = Post.objects.all()[:5]
    context = {
        'categories': categories,
        'posts': posts,
        'post': posts.first(),
    }
    return render(request, 'blog/home.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    return render(request, 'blog/post_detail.html', {'post': post})


def category_posts(request, category_slug, category_id):
    category = get_object_or_404(Category, slug=category_slug, id=category_id)
    posts = Post.objects.filter(category=category).order_by('-date_posted')
    return render(request, 'blog/category_posts.html', {'posts': posts})


def about(request):
    return render(request, 'blog/about.html', {'title': 'About'})
