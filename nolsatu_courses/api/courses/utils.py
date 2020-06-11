from django.conf import settings


def prepare_markdown(markdown_content):
    return markdown_content.replace("(/media", f"({settings.HOST}/media")