from django import template

register = template.Library()

'''
Definition of a filter for the skipper list to filter only active skippers.
'''
@register.filter
def active_skipper(skippers):
    skipper_list = []

    try:
        for skipper in skippers:
            if 'active' in skipper and skipper['active']:
                skipper_list.append(skipper)
    except:
        pass

    return skipper_list

'''
Definition of a filter for the skipper list to filter only inactive skippers.
'''
@register.filter
def inactive_skipper(skippers):
    skipper_list = []

    try:
        for skipper in skippers:
            if 'active' in skipper and not skipper['active']:
                skipper_list.append(skipper)
    except:
        pass

    return skipper_list