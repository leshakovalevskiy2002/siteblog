from django.utils.translation import gettext_lazy as _

def get_women_context(request):
    menu = [{'title': _("About the site"), 'url_name': 'about'},
            {'title': _("Add article"), 'url_name': 'add_page'},
            {'title': _("Contact"), 'url_name': 'contact'},
            {'title': _("Login"), 'url_name': 'users:login', 'title2': _("Register"),
             'url_name2': "users:registration"}
            ]

    if request.user.is_authenticated:
        menu[-1] = {'title': _("Logout"), "url_name": "users:logout"}

    return {"mainmenu": menu}