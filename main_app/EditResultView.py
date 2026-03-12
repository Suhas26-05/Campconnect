from django.shortcuts import redirect
from django.urls import reverse
from django.views import View


class EditResultView(View):
    def get(self, request, *args, **kwargs):
        return redirect(f"{reverse('staff_add_result')}?mode=edit")

    def post(self, request, *args, **kwargs):
        return redirect(f"{reverse('staff_add_result')}?mode=edit")
