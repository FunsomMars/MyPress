import re

from django.core.exceptions import ValidationError


class ComplexityValidator:
    """
    密码复杂度验证器：至少包含大写字母、小写字母、数字、特殊符号中的3种。
    """

    def validate(self, password, user=None):
        categories = 0
        if re.search(r'[A-Z]', password):
            categories += 1
        if re.search(r'[a-z]', password):
            categories += 1
        if re.search(r'[0-9]', password):
            categories += 1
        if re.search(r'[^A-Za-z0-9]', password):
            categories += 1

        if categories < 3:
            raise ValidationError(
                '密码至少需要包含大写字母、小写字母、数字、特殊符号中的3种',
                code='password_too_simple',
            )

    def get_help_text(self):
        return '密码至少需要包含大写字母、小写字母、数字、特殊符号中的3种'
