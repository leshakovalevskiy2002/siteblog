from django.contrib.auth.models import Group


def new_users_handler(backend, user, response, *args, **kwargs):
    group = Group.objects.get(name="social")
    user.groups.add(group)


def save_user_data(backend, user, response, *args, **kwargs):
    return {
        "user_data": {
            "first_name": user.first_name,
            "last_name": user.last_name
        }
    }


def receive_user_data(backend, user, response, *args, **kwargs):
    data = kwargs["user_data"]
    if data:
        user.first_name = data["first_name"]
        user.last_name = data["last_name"]
        user.save()
    return {'user': user}
