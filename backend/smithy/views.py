from django.db.models import Q
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from .models import CraftingRecipe, Item, UserList
from .serializer import ItemSerializer
from typing import Optional
# Create your views here.


def get_guest_profile():
    """Get or create guest user profile"""
    guest_user, _ = User.objects.get_or_create(username="guest")
    user_profile, _ = UserList.objects.get_or_create(user=guest_user)
    return user_profile


def combineItems(item1, item2) -> Optional[Item]:
    """Check if two items can be combined and return result"""
    try:
        query = Q(item_a=item1, item_b=item2) | Q(item_a=item2, item_b=item1)
        recipe = CraftingRecipe.objects.get(query)
        return recipe.result
    except CraftingRecipe.DoesNotExist:
        return None


@api_view(['GET'])
def get_all_items(request):
    """Get all items in the game"""
    items = Item.objects.all()
    serializer = ItemSerializer(items, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def get_all_recipes(request):
    """Get all crafting recipes"""
    recipes = CraftingRecipe.objects.all()
    recipe_data = []
    for recipe in recipes:
        recipe_data.append({
            "id": recipe.id,
            "item_a": recipe.item_a.name,
            "item_b": recipe.item_b.name,
            "result": recipe.result.name,
            "discovered": recipe.discovered
        })
    return Response(recipe_data)


@api_view(['GET'])
def get_user(request):
    """Get current user's discovered items"""
    guest_profile = get_guest_profile()
    discovered = guest_profile.discovered_items.all()
    serializer = ItemSerializer(discovered, many=True)
    return Response({
        "username": guest_profile.user.username,
        "discovered_items": serializer.data,
        "total_discovered": discovered.count()
    })


@csrf_exempt
@api_view(['POST'])
def combine_items(request):
    """Combine two items and return the result"""
    item1_check = request.data.get('item1_name')
    item2_check = request.data.get('item2_name')
    
    if not item1_check or not item2_check:
        return Response(
            {"error": "Both item1_name and item2_name are required."},
            status=status.HTTP_400_BAD_REQUEST            
        )
    
    try:
        item1 = Item.objects.get(name=item1_check)
        item2 = Item.objects.get(name=item2_check)
    except Item.DoesNotExist:
        return Response(
            {"error": "One or both items do not exist."},
            status=status.HTTP_404_NOT_FOUND            
        )
    
    result_item = combineItems(item1, item2)
    if result_item is None:
        return Response(
            {"message": "These items don't create anything new."},
            status=status.HTTP_200_OK
        )  
    
    guest_profile = get_guest_profile()
    if guest_profile is None:
        return Response(
            {"error": "Guest profile not found."},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    # Check if already discovered
    if guest_profile.discovered_items.filter(pk=result_item).exists():
        message = f"You already discovered {result_item.name}!"
        is_new_discovery = False
    else:
        guest_profile.discovered_items.add(result_item)
        message = f"New discovery! You made {result_item.name}!"
        is_new_discovery = True
    
    return Response({
        "message": message,
        "new_item": result_item.name,
        "is_new": is_new_discovery
    }, status=status.HTTP_200_OK)