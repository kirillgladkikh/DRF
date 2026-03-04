from rest_framework.serializers import ValidationError

youtube = "youtube.com"
# pattern = r'^(https?://)?(www\.)?youtube\.com(/.*)?$'


def validate_youtube(value):
    if youtube not in value.lower():  # через вхождение строки
        # if not re.match(pattern, value, re.IGNORECASE):  # через регулярные выражения
        raise ValidationError("Разрешено использовать ссылку только на youtube.com")
