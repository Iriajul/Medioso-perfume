"""Image storage on Cloudinary (configured from CLOUDINARY_* settings)."""

import cloudinary.uploader
from django.conf import settings
from rest_framework import serializers

MAX_IMAGE_BYTES = 10 * 1024 * 1024
IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp"}


def validate_image(file):
    if file.size > MAX_IMAGE_BYTES:
        raise serializers.ValidationError("Image must be 10MB or smaller.")
    if file.content_type not in IMAGE_TYPES:
        raise serializers.ValidationError("Image must be PNG, JPG or WebP.")
    return file


def upload_image(file, folder):
    """Uploads and returns (secure_url, public_id)."""
    result = cloudinary.uploader.upload(file, folder=f"{settings.CLOUDINARY_FOLDER}/{folder}", resource_type="image")
    return result["secure_url"], result["public_id"]


def delete_image(public_id):
    if public_id:
        cloudinary.uploader.destroy(public_id, invalidate=True)
