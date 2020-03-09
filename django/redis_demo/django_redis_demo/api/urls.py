from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from .views import manage_items
# from .views import manage_item

urlpatterns = {
    path('', manage_items, name="items"),
    # path('', datascience_greeting, name="datascience")
    #path('<slug:key>', manage_item, name="single_item")
}
urlpatterns = format_suffix_patterns(urlpatterns)
