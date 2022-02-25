from django.contrib.auth.decorators import login_required


class LoginRequiredMixin(object):  # 进行包装，保证
    @classmethod
    def as_view(cls, **initkwargs):
        # 调用父类的as view、
        view = super(LoginRequiredMixin, cls).as_view(**initkwargs)
        return login_required(view)
