from django.apps import apps
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.template import Template, Context
from django.utils import timezone
import fasttext
from googletrans import Translator

from sitewomen.celery import app
from women.models import Women, PageVisit


REPORT_TEMPLATE = """   
                        {% load women_tags %}
                        Here's how you did till now: 
                        {% for post in posts %}
                            {% get_page_count_views post.slug as count %}
                            "{{ post.title }}": viewed {{ count }} times | 
                        {% endfor %} 
                    """


@app.task
def send_view_count_report():
    for user in get_user_model().objects.filter(email_verified=True):
        posts = Women.objects.filter(author=user)
        if not posts:
            continue
        template = Template(REPORT_TEMPLATE)
        send_mail(
            'Your Django_celery Project Activity',
            template.render(context=Context({'posts': posts})),
            settings.EMAIL_HOST_USER,
            [user.email],
            fail_silently=True,
        )


@app.task
def delete_old_posts():
    now = timezone.localtime(timezone.now())
    PageVisit.objects.filter(visit_time__lt=now).delete()


@app.task
def translate_model_content(model_name: str, field_name: str, pk: int) -> None:
    model = fasttext.load_model("fasttext_models/lid.176.bin")
    translator = Translator()

    Model = apps.get_model("women", model_name)
    obj = Model.objects.get(pk=pk)
    text = getattr(obj, field_name)

    label, _ = model.predict(text.replace('"', '\\"').replace('\n', '\\n'), k=1)
    language = label[0].replace('__label__', '')
    if language == "en":
        text_ru = translator.translate(text, src='en', dest='ru').text
        text_be = translator.translate(text, src='en', dest='be').text
        setattr(obj, f"{field_name}_ru", text_ru)
        setattr(obj, f"{field_name}_be", text_be)
    if language == "ru":
        text_en = translator.translate(text, src='ru', dest='en').text
        text_be = translator.translate(text, src='ru', dest='be').text
        setattr(obj, f"{field_name}_en", text_en)
        setattr(obj, f"{field_name}_be", text_be)
    if language == "be":
        text_en = translator.translate(text, src='be', dest='en').text
        text_ru = translator.translate(text, src='be', dest='ru').text
        setattr(obj, f"{field_name}_en", text_en)
        setattr(obj, f"{field_name}_ru", text_ru)

    if language == "zh":
        language = "zh-tw"

    try:
        text_en = translator.translate(text, src=language, dest='en').text
        text_ru = translator.translate(text, src=language, dest='ru').text
        text_be = translator.translate(text, src=language, dest='be').text
        setattr(obj, f"{field_name}_en", text_en)
        setattr(obj, f"{field_name}_ru", text_ru)
        setattr(obj, f"{field_name}_be", text_be)
    except:
        print("Данный язык для перевода не поддерживается")

    obj.save()