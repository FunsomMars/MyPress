from django import template

register = template.Library()

@register.filter
def has_group(user, group_name):
    """检查用户是否属于某个用户组"""
    return user.groups.filter(name=group_name).exists()
