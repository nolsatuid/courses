from django.conf import settings
from nolsatu_courses.backoffice.courses.forms import FormCourses


class FormVendorCourse(FormCourses):
    class Meta(FormCourses.Meta):
        exclude = ("users", "quizzes", 'vendor', 'author',)

    def save(self, user):
        course = super().save(commit=False)
        course.author = user
        course.vendor = user.vendors.first()
        course.save()
        return course
