import base64
import binascii
import uuid

from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework import serializers


class Base64ImageField(serializers.ImageField):
    def to_internal_value(self, base64_data):
        if isinstance(base64_data, str) and ";base64," in base64_data:

            header, base64_data = base64_data.split(";base64,")
            mime_type = header.replace("data:", "")
            file_name = str(uuid.uuid4())
            file_extension = mime_type.split("/")[-1]

            try:
                decoded_data = base64.b64decode(base64_data)
            except (TypeError, ValueError, binascii.Error):
                raise ValidationError("Ошибка при декодировании картинки")

            data = SimpleUploadedFile(
                name=f"{file_name}.{file_extension}",
                content=decoded_data,
                content_type=mime_type,
            )

            return super().to_internal_value(data)

        raise ValidationError(
            f"Неверный тип, не является base64 строкой: {type(base64_data)}"
        )
