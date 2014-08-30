# -*- coding: utf-8 -*-

from .models import UserProfile, Activity


def get_activities_owned_by(user):
    return Activity.objects.filter(owners = user)

def get_activities_organized_by(user):
    return Activity.objects.filter(organizers = user)

def get_activities_in_which_participates(user):
    return Activity.objects.filter(participants = user)

def get_activities_to_participate_by(user):
    return Activity.objects.filter(requires_inscription = True).exclude(participants = user)

