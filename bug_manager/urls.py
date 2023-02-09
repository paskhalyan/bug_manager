from django.contrib import admin
from django.urls import path

from bugs import views as bugs_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('bugs/', bugs_views.BugList.as_view()),
    path('bugs/<int:pk>/', bugs_views.BugDetail.as_view()),
    path('bugs/<int:pk>/assign/', bugs_views.BugAssign.as_view()),
    path('bugs/<int:pk>/resolve/', bugs_views.BugResolve.as_view()),
    path('bugs/<int:pk>/comments/', bugs_views.CommentCreate.as_view()),
    path('bugs/<int:pk>/comments/<int:comment_pk>/', bugs_views.CommentRetrieveDelete.as_view()),
]
