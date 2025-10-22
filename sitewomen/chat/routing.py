from django.urls import path

from . import consumers


websocket_urlpatterns = [
    path('chat/', consumers.JoinAndLeave.as_asgi()),
    path('chat/groups/<uuid:uuid>/', consumers.GroupConsumer.as_asgi())
]