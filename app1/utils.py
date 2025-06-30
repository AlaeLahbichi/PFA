import requests # type: ignore
from user_agents import parse as parse_user_agent # type: ignore

def get_device_info(request):
    user_agent_str = request.META.get('HTTP_USER_AGENT', '')
    user_agent = parse_user_agent(user_agent_str)

    os = user_agent.os.family
    browser = user_agent.browser.family

    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        data = response.json()
        city = data.get("city", "Ville inconnue")
        country = data.get("country", "Pays inconnu")
    except:
        city = "Inconnu"
        country = "Inconnu"

    return f"{os} • {browser} • {city}, {country}"
