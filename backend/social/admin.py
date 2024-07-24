from django.contrib import admin
from .models import Recipe, Tag, Ingredient, Rating, RecipeImage


class RecipeAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'created_at', 'updated_at', 'average_rating']
    list_filter = ['author', 'tags', 'ingredients']
    search_fields = ['title', 'description']
    readonly_fields = ['created_at', 'updated_at', 'average_rating']
    fieldsets = (
        (None, {'fields': ('title', 'description', 'instructions', 'image', 'author')}),
        ('Associations', {'fields': ('tags', 'ingredients')}),
        ('Dates', {'fields': ('created_at', 'updated_at')}),
        ('Ratings', {'fields': ('average_rating',)}),
    )


class TagAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name']
    search_fields = ['name']


class RatingAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'user', 'value']
    list_filter = ['recipe', 'user']
    search_fields = ['recipe__title', 'user__email']


class RecipeImageAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'image']
    list_filter = ['recipe']
    search_fields = ['recipe__title']


admin.site.register(Recipe, RecipeAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Rating, RatingAdmin)
admin.site.register(RecipeImage, RecipeImageAdmin)
