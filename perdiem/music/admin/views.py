"""
:Created: 9 October 2016
:Author: Lucas Connors

"""

from django.views.generic import TemplateView


class DailyReportAdminView(TemplateView):

    template_name = 'admin/music/activityestimate/daily-report.html'

    def get_context_data(self, **kwargs):
        context = super(DailyReportAdminView, self).get_context_data(**kwargs)
        context.update({
            'title': 'Enter Daily Report',
            'has_permission': self.request.user.is_superuser,
        })
        return context
