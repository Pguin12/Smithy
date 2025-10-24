from django.shortcuts import render, Q
from .models import Item, CraftingRecipe
# Create your views here.

def combineItems(item1, item2):
    try:
        query = Q(item_a=item1, item_b=item2)|Q(item_a=item2, item_b=item1)
        recipe = CraftingRecipe.objects.get(query)
        return recipe.result
    except CraftingRecipe.DoesNotExist:
        return None
