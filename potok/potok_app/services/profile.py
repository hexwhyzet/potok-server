from django.contrib.postgres.search import TrigramSimilarity

from potok_app.models import Profile


def profile_by_id(profile_id):
    return Profile.objects.get(id=profile_id)


def search_profiles_by_screen_name_prefix(prefix, number, offset):
    return Profile.objects.filter(screen_name__istartswith=prefix)[offset:offset + number]


# def search_profiles_by_text(text, number, offset):
#     vector = SearchVector('name', 'screen_name')
#     query = SearchQuery(text)
#     return Profile.objects.annotate(rank=SearchRank(vector, query)).filter(rank__gte=0.3).order_by('rank')[
#            offset:offset + number]

def search_profiles_by_text(text, number, offset):
    return Profile.objects.annotate(similarity=TrigramSimilarity('screen_name', text)) \
               .filter(similarity__gt=0.25).order_by('-similarity')[offset:offset + number]
