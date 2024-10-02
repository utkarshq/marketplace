import graphene
from django.core.exceptions import ValidationError
from ....account.models import User
from ....vendor.models import Vendor
from ...core.mutations import ModelMutation
from ...core.types import VendorError
from ..types import VendorInput

class VendorCreate(ModelMutation):
    class Arguments:
        input = VendorInput(required=True, description="Fields required to create a vendor.")

    class Meta:
        description = "Creates a new Vendor."
        model = Vendor
        error_type_class = VendorError
        error_type_field = "vendor_errors"

    @classmethod
    def clean_input(cls, info, instance, data):
        cleaned_input = super().clean_input(info, instance, data)
        user = info.context.user
        if not user.is_authenticated:
            raise ValidationError("You need to be logged in to apply as a vendor.")
        cleaned_input["user"] = user
        return cleaned_input

    @classmethod
    def save(cls, info, instance, cleaned_input):
        instance.save()
        # Send notification to admin (implement this later)
        return instance