from django import forms

class CustomSignupForm(forms.Form):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)

    def signup(self, request, user):
        # Delay the import to avoid circular import
        from allauth.account.forms import SignupForm

        # No need to call super() from CustomSignupForm; use the SignupForm directly if needed
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        
        # Save the user instance
        user.save()
        return user
    
class UseAdminInviteForm(forms.Form):
    """
    Dummy form that just tells admins to use the Django admin to send invites.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove any fields; we only want to show a message
        self.fields.clear()

    def as_widget(self):
        # This is not needed; we’ll just use a template
        pass