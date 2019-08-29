"""
:Created: 5 April 2015
:Author: Lucas Connors

"""

from django import forms
from django.conf import settings
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.core import validators

from accounts.models import UserAvatar


class LoginAccountForm(AuthenticationForm):

    def clean_username(self):
        username = self.cleaned_data['username']
        return username.lower()


class RegisterAccountForm(UserCreationForm):

    username = forms.CharField(
        max_length=150,
        validators=[
            validators.RegexValidator(
                r'^[a-z0-9.@+_-]+$',
                (
                    'Enter a valid username. This value may contain only lowercase letters, '
                    'numbers and @/./+/-/_ characters.'
                )
            ),
        ]
    )
    email = forms.EmailField(required=True)
    subscribe_news = forms.BooleanField(
        required=False, initial=True, label='Get exclusive updates before they\'re public'
    )

    class Meta(UserCreationForm.Meta):
        fields = ('username', 'email', 'password1', 'password2',)

    def clean_email(self):
        email = self.cleaned_data['email']

        # Verify that there are no other users already with this email address
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError(
                "The email address {email} already belongs to an existing user on PerDiem.".format(email=email)
            )

        return email

    def save(self, commit=True):
        user = super(RegisterAccountForm, self).save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class EditNameForm(forms.Form):

    username = forms.CharField(
        max_length=150,
        validators=[
            validators.RegexValidator(
                r'^[a-z0-9.@+_-]+$',
                (
                    'Enter a valid username. This value may contain only '
                    'lowercase letters, numbers and @/./+/-/_ characters.'
                )
            ),
        ]
    )
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    invest_anonymously = forms.BooleanField(required=False)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(EditNameForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data['username']
        if User.objects.exclude(id=self.user.id).filter(username=username).exists():
            raise forms.ValidationError("A user with that username already exists.")
        return username


class EditAvatarForm(forms.Form):

    custom_avatar = forms.ImageField(required=False)

    def __init__(self, user, *args, **kwargs):
        super(EditAvatarForm, self).__init__(*args, **kwargs)
        self.fields['avatar'] = forms.ChoiceField(
            choices=self.get_avatar_choices(user), required=False, widget=forms.RadioSelect
        )

    def get_avatar_choices(self, user):
        user_avatars = UserAvatar.objects.filter(user=user)
        return [('', 'Default',)] + [(avatar.id, avatar.get_provider_display(),) for avatar in user_avatars]

    def clean_avatar(self):
        avatar_id = self.cleaned_data['avatar']
        if avatar_id:
            return UserAvatar.objects.get(id=avatar_id)

    def clean_custom_avatar(self):
        custom_avatar = self.cleaned_data['custom_avatar']
        if custom_avatar and custom_avatar._size > settings.MAXIMUM_AVATAR_SIZE:
            raise forms.ValidationError("Image file too large (2MB maximum).")
        return custom_avatar


class EmailPreferencesForm(forms.Form):

    email = forms.EmailField()
    subscription_news = forms.BooleanField(required=False, label='Let me know about new updates and happenings')
    subscription_artup = forms.BooleanField(required=False, label='Subscribe to updates from artists you invest in')
    subscription_all = forms.BooleanField(
        required=False, label='Uncheck this box to unsubscribe from all emails from PerDiem'
    )

    def __init__(self, user, *args, **kwargs):
        super(EmailPreferencesForm, self).__init__(*args, **kwargs)
        self.user = user

    def clean_email(self):
        email = self.cleaned_data['email']

        # Verify that there are no other users already with this email address
        if User.objects.exclude(id=self.user.id).filter(email=email).exists():
            raise forms.ValidationError(
                "The email address {email} already belongs to an existing user on PerDiem.".format(email=email)
            )

        return email

    def clean(self):
        d = self.cleaned_data
        if (d['subscription_news'] or d['subscription_artup']) and not d['subscription_all']:
            raise forms.ValidationError(
                "You cannot subscribe to general updates or artist updates if you are unsubscribed from all emails."
            )
        return d


class ContactForm(forms.Form):

    INQUIRY_CHOICES = (
        ('Support', 'Support',),
        ('Feedback', 'Feedback',),
        ('General Inquiry',  'General Inquiry',),
    )

    inquiry = forms.ChoiceField(choices=INQUIRY_CHOICES)
    email = forms.EmailField()
    first_name = forms.CharField(required=False)
    last_name = forms.CharField(required=False)
    message = forms.CharField(widget=forms.Textarea)
