from django import forms

from .models import Group, PushInformation, SubscriptionInfo


class WebPushForm(forms.Form):
    group = forms.CharField(max_length=255, required=False)
    status_type = forms.ChoiceField(choices=[
                                      ('subscribe', 'subscribe'),
                                      ('unsubscribe', 'unsubscribe'),
                                      ('check', 'check')
                                    ])

    def check(self, subscription, user, group_name):
        data = {"user": None, "group": None, "subscription": subscription}

        if user.is_authenticated:
            data["user"] = user

        if group_name:
            group, created = Group.objects.get_or_create(name=group_name)
            data["group"] = group

        return 201 if PushInformation.objects.filter(**data).exists() else 202

    def save_or_delete(self, subscription, user, status_type, group_name):
        # Ensure get_or_create matches exactly
        data = {"user": None, "group": None}

        if user.is_authenticated:
            data["user"] = user

        if group_name:
            group, created = Group.objects.get_or_create(name=group_name)
            data["group"] = group

        data["subscription"] = subscription

        push_info, created = PushInformation.objects.get_or_create(**data)

        # If unsubscribe is called, that means need to delete the browser
        # and notification info from server. 
        if status_type == "unsubscribe":
            push_info.delete()


class SubscriptionForm(forms.ModelForm):

    class Meta:
        model = SubscriptionInfo
        fields = ('endpoint', 'auth', 'p256dh', 'browser')

    def get_or_save(self):
        subscription, created = SubscriptionInfo.objects.get_or_create(**self.cleaned_data)
        return subscription
