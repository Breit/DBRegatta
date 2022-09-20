from django import template

register = template.Library()

'''
Definition of a filter for the heat rankings list to filter for brackets.
'''
@register.filter
def ranks_bracket(ranks, bracket):
    filtered_ranks = []

    try:
        for rank in ranks:
            if 'races' in rank and rank['races'] == bracket:
                filtered_ranks.append(rank)
    except:
        pass

    return filtered_ranks
