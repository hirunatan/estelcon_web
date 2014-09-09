# -*- encoding: utf-8 -*-

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
        max_length=100, required=True,
    )
    subtitle = forms.CharField(
        required = False,
        widget = forms.Textarea,
    )
    duration = forms.CharField(
        max_length=50, required=True,
    )
    max_places = forms.IntegerField(
        min_value = 0, required=True,
    )
    show_owners = forms.BooleanField(
        initial = False, required = False,
    )
    requires_inscription = forms.BooleanField(
        initial = False, required = False,
    )
    owners = forms.CharField(
        required = False,
        widget = forms.Textarea,
    )
    organizers = forms.CharField(
        required = False,
        widget = forms.Textarea,
    )
    text = forms.CharField(
        required = False,
        widget = forms.Textarea,
    )
    logistics = forms.CharField(
        required = False,
        widget = forms.Textarea,
    )
    notes_organization = forms.CharField(
        required = False,
        widget = forms.Textarea,
    )

