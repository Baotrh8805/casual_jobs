from django.contrib.auth.password_validation import (
    UserAttributeSimilarityValidator,
    MinimumLengthValidator, 
    NumericPasswordValidator
)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

# Ghi đè các validator mặc định với thông báo tiếng Việt
class VietnameseUserAttributeSimilarityValidator(UserAttributeSimilarityValidator):
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError(
                _("Mật khẩu quá giống với thông tin cá nhân của bạn."),
                code="password_too_similar",
            )

class VietnameseMinimumLengthValidator(MinimumLengthValidator):
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError(
                _("Mật khẩu quá ngắn. Phải có ít nhất %(min_length)d ký tự.") % {'min_length': self.min_length},
                code="password_too_short",
            )

class VietnameseNumericPasswordValidator(NumericPasswordValidator):
    def validate(self, password, user=None):
        try:
            super().validate(password, user)
        except ValidationError:
            raise ValidationError(
                _("Mật khẩu không thể chỉ chứa số."),
                code="password_entirely_numeric",
            )