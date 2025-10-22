from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _

from .models import Group


@login_required
def home_view(request):
    groups = Group.objects.all()
    user = request.user
    context = {
        "groups": groups,
        "user": user,
        "title": _("Chat Home Page")
    }
    return render(request, template_name="chat/home.html", context=context)


@login_required
def group_chat_view(request, uuid):
    group = get_object_or_404(Group, uuid=uuid)
    if not group.members.filter(username=request.user).exists():
        message = _("You are not a member of this group. Kindly use the join button")
        return render(request, "chat/error.html", context={
            "message": message,
            "title": _("Chat Room - error")
        }, status=403)

    messages = group.message_set.all()
    events = group.event_set.all()

    message_and_event_list = [*messages, *events]
    sorted_message_event_list = sorted(message_and_event_list, key=lambda x: x.timestamp)

    group_members = group.members.all()

    context = {
        "message_and_event_list": sorted_message_event_list,
        "group_members": group_members,
        "title": _("Chat Room - %(room)s") % {"room": group.name}
    }

    return render(request, template_name="chat/groupchat.html", context=context)