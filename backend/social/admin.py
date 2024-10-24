# from django.contrib import admin
# from django import forms
# from django.utils.html import format_html
# from .models import Post, PostImage, Rating
# from django.contrib.auth import get_user_model
# from django.contrib.admin.widgets import FilteredSelectMultiple
#
# User = get_user_model()
#
#
# class PostImageInline(admin.TabularInline):
#     model = PostImage
#     extra = 1  # Number of extra forms to display
#
#
# class PostAdminForm(forms.ModelForm):
#     tagged_users = forms.ModelMultipleChoiceField(
#         queryset=User.objects.all(),
#         required=False,
#         widget=FilteredSelectMultiple("Users", is_stacked=False)
#     )
#
#     class Meta:
#         model = Post
#         fields = '__all__'
#
#     def __init__(self, *args, **kwargs):
#         super(PostAdminForm, self).__init__(*args, **kwargs)
#         if self.instance.pk:
#             self.fields['tagged_users'].initial = self.instance.taggeduser_set.all()
#
#     def save(self, commit=True):
#         post = super().save(commit=False)
#         if commit:
#             post.save()
#         if post.pk:
#             post.taggeduser_set.set(self.cleaned_data['tagged_users'])
#             self.save_m2m()
#         return post
#
#
# @admin.register(Post)
# class PostAdmin(admin.ModelAdmin):
#     form = PostAdminForm
#     list_display = ['id', 'title', 'author', 'created_at', 'view_images']
#     inlines = [PostImageInline]
#     list_filter = ['author', 'created_at']
#     search_fields = ['title', 'author__username']
#
#     def view_images(self, obj):
#         images = obj.images.all()
#         if images:
#             return format_html(''.join(
#                 f'<img src="{image.image.url}" style="height: 50px; margin-right: 5px;" />'
#                 for image in images))
#         return "No images"
#
#     view_images.short_description = "Images"
#
#
# @admin.register(Rating)
# class RatingAdmin(admin.ModelAdmin):
#     list_display = ['id', 'post', 'user', 'value']
#     list_filter = ['post', 'user', 'value']
#     search_fields = ['post__title', 'user__username']
#
#
# @admin.register(PostImage)
# class PostImageAdmin(admin.ModelAdmin):
#     list_display = ['id', 'thumbnail', 'post']
#     list_filter = ['post']
#     search_fields = ['post__title']
#
#     def thumbnail(self, obj):
#         if obj.image:
#             return format_html(f'<img src="{obj.image.url}" style="height: 50px;" />')
#         return "No Image"
#
#     thumbnail.short_description = 'Preview'
