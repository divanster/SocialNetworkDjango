from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()


def recipe_image_file_path(instance, filename):
    """Generate file path for new recipe image"""
    import uuid
    import os
    ext = filename.split('.')[-1]
    filename = f'{uuid.uuid4()}.{ext}'
    return os.path.join('uploads/recipe/', filename)


class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    instructions = models.TextField(default='')
    image = models.ImageField(upload_to=recipe_image_file_path, null=True, blank=True,
                              default='default_images/default_recipe.jpeg')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    tags = models.ManyToManyField(Tag, related_name='recipes', blank=True)
    ingredients = models.ManyToManyField(Ingredient, related_name='recipes', blank=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recipes', default=None, null=True,
                               blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def average_rating(self):
        ratings = self.ratings.all()
        if ratings.exists():
            return sum(rating.value for rating in ratings) / ratings.count()
        return 0


class Rating(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    value = models.PositiveSmallIntegerField()

    class Meta:
        unique_together = ('recipe', 'user')

    def __str__(self):
        return f"{self.recipe.title} - {self.value} Stars"


class RecipeImage(models.Model):
    recipe = models.ForeignKey(Recipe, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='recipes/images/')
