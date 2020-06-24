import datetime
import jwt
import requests
import markdown

from markdown.treeprocessors import Treeprocessor
from markdown.extensions import Extension

from django.conf import settings
from django.contrib.auth.models import User
from django.utils.text import slugify

from nolsatu_courses.apps.accounts.models import MemberNolsatu

def generate_unique_slug(klass, field, id):
    """
    generate unique slug.
    """
    origin_slug = slugify(field)
    unique_slug = origin_slug
    numb = 1
    obj = klass.objects.filter(slug=unique_slug).first()
    while obj:
        if obj.id == id:
            break
        unique_slug = '%s-%d' % (origin_slug, numb)
        numb += 1
        obj = klass.objects.filter(slug=unique_slug).first()
    return unique_slug


def send_notification(user, subject, content):
    url = f'{settings.NOLSATU_HOST}/api/internal/notification'
    data = {
        'user': user.nolsatu.id_nolsatu,
        'subject': subject,
        'content': content,
    }
    return call_internal_api('post', url, data=data)


def update_user(identificator, type_identificator='id', user=None):
    """
    identicator digunakan sebagai nilai yang digunakan untuk mendapatkan user
    type_identificator digunakan untuk menentukan key parameter
    user gunakan untuk passing data user tanpa harus melakukan get_user_academy
    """
    if user:
        data = user
    else:
        resp = get_user_academy(type_identificator, identificator)
        data = resp.json()

    profile = data['profile'] if data['profile'] else {}

    defaults = {
        'first_name': data['first_name'],
        'last_name': data['last_name'],
        'is_active': data['is_active'],
        'is_staff': data['is_staff'],
        'is_superuser': data['is_superuser']
    }

    # get or create user
    user, created = User.objects.get_or_create(
        username=data['username'],
        email=data['email'],
        defaults={**defaults},
    )

    if created or not hasattr(user, 'nolsatu'):
        # save other data from nolsatu to model MemberNolsatu
        MemberNolsatu.objects.create(
            user=user, id_nolsatu=data["id"],
            avatar=profile.get("avatar", ""), phone_number=data['phone']
        )

    # update data from response
    user.nolsatu.avatar = profile.get("avatar", "")
    user.nolsatu.id_nolsatu = data['id']
    user.nolsatu.phone_number = data['phone']

    return user


def call_internal_api(method, url, **kwargs):
    method_map = {
        'get': requests.get,
        'post': requests.post,
        'put': requests.put,
        'patch': requests.patch,
        'delete': requests.delete
    }

    payload = jwt.encode({
        'server_key': settings.SERVER_KEY,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(seconds=30)
    }, settings.SECRET_KEY).decode('utf-8')

    headers = {
        "authorization": f'Server {payload}'
    }

    return method_map[method](url, headers=headers, **kwargs)


def get_user_academy(type_identificator, identificator):
    if type_identificator == 'id':
        url = f"{settings.NOLSATU_HOST}/api/internal/user/{identificator}"
    elif type_identificator == 'email':
        url = f"{settings.NOLSATU_HOST}/api/internal/get-user?email={identificator}"
    else:
        url = f"{settings.NOLSATU_HOST}/api/internal/get-user?username={identificator}"
    return call_internal_api("get", url)


def md_extract_img(text) -> [str]:
    """
    function to get src image/path image
    """
    md = markdown.Markdown(extensions=[ImageExtension()])
    md.convert(text)
    return md.images


class InlineImageProcessor(Treeprocessor):
    """
    treeprocessor to get all images
    """
    def run(self, root):
        self.md.images = []
        for element in root.iter('img'):
            attrib = element.attrib
            self.md.images.append(attrib['src'])


class ImageExtension(Extension):
    """
    create markdown extensions
    """
    def extendMarkdown(self, md):
        md.treeprocessors.register(
            InlineImageProcessor(md), 'inlineimageprocessor', 15)
