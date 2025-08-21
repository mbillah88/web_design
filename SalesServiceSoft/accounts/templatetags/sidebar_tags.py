from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def is_active_group(context, *url_names):
    current_url = context['request'].resolver_match.url_name
    return 'show' if current_url in url_names else ''
