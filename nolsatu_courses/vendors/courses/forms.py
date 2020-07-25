from nolsatu_courses.apps.courses.models import Courses, Batch
from nolsatu_courses.backoffice.courses.forms import FormCourses, FormFilterRegistrants


class FormVendorCourse(FormCourses):
    class Meta(FormCourses.Meta):
        exclude = ("users", "quizzes", 'vendor', 'author',)

    def save(self, user):
        course = super().save(commit=False)
        course.author = user
        course.vendor = user.vendors.first()
        course.save()
        return course


class FormFilterRegistrantsVendors(FormFilterRegistrants):
    def __init__(self, *args, **kwargs):
        user_email = kwargs.pop('user_email', None)
        super(FormFilterRegistrantsVendors, self).__init__(*args, **kwargs)
        self.fields['course'].queryset = Courses.objects.filter(vendor__users__email=user_email)
        self.fields['batch'].queryset = Batch.objects.filter(course__vendor__users__email=user_email)
