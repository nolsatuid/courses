from quiz.admin import QuizAdminForm


class FormQuiz(QuizAdminForm):

    class Media:
       css = {'all':('admin/css/widgets.css',),}
       js = ('admin/jquery.js','/admin/jsi18n/')
       