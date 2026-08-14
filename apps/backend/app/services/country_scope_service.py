from app.schemas.search import SearchRequest


COUNTRY_GROUPS = {
    "europe": ["Germany", "France", "Italy", "United Kingdom", "Spain", "Netherlands", "Poland"],
    "middle_east": ["United Arab Emirates", "Saudi Arabia", "Qatar", "Kuwait", "Oman"],
    "turkic": ["Azerbaijan", "Kazakhstan", "Uzbekistan", "Georgia"],
    "americas": ["United States", "Canada", "Mexico", "Brazil"],
    "asia": ["China", "India", "South Korea", "Japan"],
}


def target_countries(request: SearchRequest) -> list[str]:
    countries = [request.target_country]
    if request.search_all_countries:
        for group in request.country_groups:
            countries.extend(COUNTRY_GROUPS.get(group, []))
        countries.extend(request.extra_target_countries)
    return list(dict.fromkeys(country for country in countries if country))[:20]
