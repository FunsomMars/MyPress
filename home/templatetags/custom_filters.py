from django import template

register = template.Library()

@register.filter
def has_group(user, group_name):
    """检查用户是否属于某个用户组"""
    return user.groups.filter(name=group_name).exists()

@register.filter
def group_name_cn(group_name):
    """将英文用户组名转换为中文"""
    group_map = {
        'Editors': '编辑',
        'Moderators': '版主',
        'Administrators': '管理员'
    }
    return group_map.get(group_name, group_name)
