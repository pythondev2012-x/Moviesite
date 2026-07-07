from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django import forms


class CustomSocialSignupForm(SocialSignupForm):
    password1 = forms.CharField(
        label="Parol",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Parol',
            'required': True,
            'minlength': '6'
        })
    )
    password2 = forms.CharField(
        label="Parolni tasdiqlash",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Parolni qayta kiriting',
            'required': True,
            'minlength': '6'
        })
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Parollar mos kelmaydi")
        return password2

    def signup(self, request, user):
        # User allaqachon yaratilgan, faqat parolni o'rnatamiz
        password = self.cleaned_data.get('password1')
        if password:
            user.set_password(password)
            user.save()
        return user
