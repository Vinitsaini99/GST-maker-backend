import re

from rest_framework import serializers

from .models import Customer

GSTIN_PATTERN = re.compile(r'^[0-9]{2}[A-Z]{5}[0-9]{4}[A-Z]{1}[1-9A-Z]{1}Z[0-9A-Z]{1}$')
PHONE_PATTERN = re.compile(r'^[6-9]\d{9}$')


def normalize_phone(value):
    if not value:
        return ''
    digits = re.sub(r'\D', '', value)
    if len(digits) == 12 and digits.startswith('91'):
        digits = digits[2:]
    elif len(digits) == 11 and digits.startswith('0'):
        digits = digits[1:]
    return digits


def validate_gstin_value(value):
    if not value or not str(value).strip():
        return ''
    gstin = str(value).strip().upper()
    if len(gstin) != 15:
        raise serializers.ValidationError('GSTIN must be exactly 15 characters.')
    if not GSTIN_PATTERN.match(gstin):
        raise serializers.ValidationError('Invalid GSTIN format (e.g. 08ABCDE1234F1Z5).')
    return gstin


class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Customer
        fields = ['id', 'name', 'email', 'phone', 'address', 'gstin', 'created_at']
        read_only_fields = ['created_at']

    def validate_name(self, value):
        name = (value or '').strip()
        if len(name) < 2:
            raise serializers.ValidationError('Name must be at least 2 characters.')
        return name

    def validate_email(self, value):
        if not value or not str(value).strip():
            return ''
        email = str(value).strip()
        if '@' not in email or '.' not in email.split('@')[-1]:
            raise serializers.ValidationError('Enter a valid email address.')
        return email

    def validate_phone(self, value):
        if not value or not str(value).strip():
            raise serializers.ValidationError('Phone number is required.')
        phone = normalize_phone(value)
        if not PHONE_PATTERN.match(phone):
            raise serializers.ValidationError('Enter a valid 10-digit Indian mobile number.')
        return phone

    def validate_gstin(self, value):
        return validate_gstin_value(value)

    def validate_address(self, value):
        address = (value or '').strip()
        if not address:
            raise serializers.ValidationError('Address is required.')
        if len(address) < 5:
            raise serializers.ValidationError('Address must be at least 5 characters.')
        if len(address) > 500:
            raise serializers.ValidationError('Address is too long (max 500 characters).')
        return address
