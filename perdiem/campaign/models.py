"""
:Created: 12 March 2016
:Author: Lucas Connors

"""

from __future__ import unicode_literals
import math

from django.conf import settings
from django.db import models
from django.utils import timezone

from pinax.stripe.models import Charge


class Project(models.Model):

    artist = models.ForeignKey('artist.Artist', on_delete=models.CASCADE)
    reason = models.CharField(max_length=40, help_text='The reason why the artist is raising money, in a few words')

    def __unicode__(self):
        return u'{artist} project {reason}'.format(
            artist=unicode(self.artist),
            reason=self.reason
        )

    def total_num_shares(self):
        total_num_shares = 0
        for campaign in self.campaign_set.all():
            total_num_shares += campaign.num_shares()
        return total_num_shares

    def total_fans_percentage(self):
        return self.campaign_set.all().aggregate(fans_percentage=models.Sum('fans_percentage'))['fans_percentage']

    def total_artist_percentage(self):
        return 100 - self.total_fans_percentage()

    def artist_percentage(self):
        percentage_breakdowns = self.artistpercentagebreakdown_set.annotate(name=models.F('displays_publicly_as')).values('name').annotate(percentage=models.Sum('percentage')).order_by('-percentage')
        if not percentage_breakdowns:
            percentage_breakdowns = [{'name': self.artist.name, 'percentage': self.total_artist_percentage(),},]
        return percentage_breakdowns

    def generated_revenue(self):
        return self.revenuereport_set.all().aggregate(gr=models.Sum('amount'))['gr'] or 0

    def generated_revenue_fans(self):
        return self.generated_revenue() * (float(self.total_fans_percentage()) / 100)

    def investors(self):
        investors = {}
        investments = Investment.objects.filter(campaign__project=self, charge__paid=True).select_related('charge', 'charge__customer', 'charge__customer__user')

        for investment in investments:
            investor = investment.investor()
            if investor.id not in investors:
                investors[investor.id] = {
                    'name': investor.userprofile.get_display_name(),
                    'avatar_url': investor.userprofile.display_avatar_url(),
                    'public_profile_url': investor.userprofile.public_profile_url(),
                    'num_shares': 0,
                    'total_investment': 0,
                }
            investors[investor.id]['num_shares'] += investment.num_shares
            investors[investor.id]['total_investment'] += investment.num_shares * investment.campaign.value_per_share

        # Calculate percentage ownership for each investor
        for investor_id, investor in investors.iteritems():
            investors[investor_id]['percentage'] = (float(investor['num_shares']) / self.total_num_shares()) * self.total_fans_percentage()

        return investors


class Campaign(models.Model):

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(help_text='The amount of money the artist wishes to raise')
    value_per_share = models.PositiveIntegerField(default=1, help_text='The value (in dollars) per share the artist wishes to sell')
    start_datetime = models.DateTimeField(db_index=True, default=timezone.now, help_text='When the campaign will start accepting investors')
    end_datetime = models.DateTimeField(db_index=True, null=True, blank=True, help_text='When the campaign ends and will no longer accept investors (no end date if blank)')
    use_of_funds = models.TextField(null=True, blank=True, help_text='A description of how the funds will be used')
    fans_percentage = models.PositiveSmallIntegerField(help_text='The percentage of revenue that goes back to the fans (a value from 0-100)')

    def __unicode__(self):
        return u'{artist}: ${amount} {reason}'.format(
            artist=unicode(self.project.artist),
            amount=self.amount,
            reason=self.project.reason
        )

    def value_per_share_cents(self):
        return self.value_per_share * 100

    def total(self, num_shares):
        subtotal = num_shares * self.value_per_share
        total = (settings.PERDIEM_FEE + subtotal) * 1.029 + 0.3 # Stripe 2.9% + $0.30 fee
        return math.ceil(total * 100.0) / 100.0

    def num_shares(self):
        return self.amount / self.value_per_share

    def total_shares_purchased(self):
        return self.investment_set.filter(charge__paid=True).aggregate(total_shares=models.Sum('num_shares'))['total_shares'] or 0

    def num_shares_remaining(self):
        return self.num_shares() - self.total_shares_purchased()

    def amount_raised(self):
        return self.total_shares_purchased() * self.value_per_share

    def percentage_funded(self):
        try:
            return "{0:.0f}".format((float(self.amount_raised()) / self.amount) * 100)
        except ZeroDivisionError:
            return '100'

    def percentage_roi(self, percentage):
        return self.amount * (percentage / self.fans_percentage)

    def days_remaining(self):
        if self.end_datetime:
            return max(0, (self.end_datetime - timezone.now()).days)

    def open(self):
        started = self.start_datetime is None or self.start_datetime < timezone.now()
        ended = self.end_datetime and self.end_datetime < timezone.now()
        return started and not ended and self.amount_raised() < self.amount


class ArtistPercentageBreakdown(models.Model):

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    artist_admin = models.ForeignKey('artist.ArtistAdmin', on_delete=models.SET_NULL, null=True, blank=True)
    displays_publicly_as = models.CharField(max_length=30, help_text='The name shown on the artist\'s detail page')
    percentage = models.FloatField(help_text='The percentage of revenue that goes back to this group/individual (a value from 0-100)')

    def __unicode__(self):
        return u'{project}: {displays_publicly_as} - {percentage}%'.format(
            project=unicode(self.project),
            displays_publicly_as=self.displays_publicly_as,
            percentage=self.percentage
        )


class Expense(models.Model):

    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    expense = models.CharField(max_length=30, help_text='A description of one of the expenses for the artist (eg. Studio cost)')

    class Meta:
        unique_together = (('campaign', 'expense',))

    def __unicode__(self):
        return u'{campaign} ({expense})'.format(
            campaign=unicode(self.campaign),
            expense=self.expense
        )


class Investment(models.Model):

    charge = models.OneToOneField(Charge, on_delete=models.CASCADE)
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE)
    transaction_datetime = models.DateTimeField(db_index=True, auto_now_add=True)
    num_shares = models.PositiveSmallIntegerField(default=1, help_text='The number of shares an investor made in a transaction')

    def __unicode__(self):
        return u'{num_shares} shares in {campaign} to {investor}'.format(
            num_shares=self.num_shares,
            campaign=unicode(self.campaign),
            investor=unicode(self.investor())
        )

    def investor(self):
        return self.charge.customer.user

    def generated_revenue(self):
        relevant_revenue_reports = RevenueReport.objects.filter(
            project=self.campaign.project,
            reported_datetime__gt=self.transaction_datetime
        )
        total_relevant_revenue = relevant_revenue_reports.aggregate(total_revenue=models.Sum('amount'))['total_revenue'] or 0
        return total_relevant_revenue * (float(self.campaign.fans_percentage) / 100) * (float(self.num_shares) / self.campaign.num_shares())


class RevenueReport(models.Model):

    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(help_text='The amount of revenue generated (in dollars) being reported (since last report)')
    reported_datetime = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return u'${amount} for {project}'.format(
            amount=self.amount,
            project=unicode(self.project)
        )
