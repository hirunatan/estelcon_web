from django import forms


class ActivitySubscribeForm(forms.Form):
    id = forms.IntegerField(
        min_value = 0, required=True,
        widget = forms.HiddenInput,
    )
    title = forms.CharField(
        max_length=100, required=True,
        widget = forms.HiddenInput,
    )


class ProposalForm(forms.Form):
    title = forms.CharField(
        max_length=100, required=True, widget=forms.TextInput(attrs={ 'class': 'form-control'}),
    )
    subtitle = forms.CharField(
        required = False,
        widget = forms.Textarea(attrs={ 'class': 'form-control'}),
    )
    duration = forms.CharField(
        max_length=50, required=True,widget=forms.TextInput(attrs={ 'class': 'form-control'}),
    )
    max_places = forms.IntegerField(
        min_value = 0, required=True, initial = 0,widget=forms.TextInput(attrs={ 'class': 'form-control'}),
    )
    show_owners = forms.BooleanField(
        initial = False, required = False,widget=forms.CheckboxInput(attrs={ 'class': 'form-check-input'}),
    )
    requires_inscription = forms.BooleanField(
        initial = False, required = False,widget=forms.CheckboxInput(attrs={ 'class': 'form-check-input'}),
    )
    owners = forms.CharField(
        required = False,
        widget = forms.Textarea(attrs={ 'class': 'form-control'}),
    )
    organizers = forms.CharField(
        required = False,
        widget = forms.Textarea(attrs={ 'class': 'form-control'}),
    )
    text = forms.CharField(
        required = False,
        widget = forms.Textarea(attrs={ 'class': 'form-control'}),
    )
    logistics = forms.CharField(
        required = False,
        widget = forms.Textarea(attrs={ 'class': 'form-control'}),
    )
    notes_organization = forms.CharField(
        required = False,
        widget = forms.Textarea(attrs={ 'class': 'form-control'}),
    )

