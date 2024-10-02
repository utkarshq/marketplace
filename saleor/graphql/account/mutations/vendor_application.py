import graphene
from saleor.graphql.account.mutations.vendor_application import VendorApplicationMutations
from django.core.exceptions import ValidationError
from ....vendor.models import VendorApplication
from ...core.mutations import ModelMutation
from ...core.types import VendorError
from ...core.utils import get_user_or_app_from_context
from ..types import User, VendorApplication as VendorApplicationType
from ....core.exceptions import PermissionDenied
from graphql import GraphQLError  # {{ edit_1 }}

class VendorApplicationInput(graphene.InputObjectType):
    company_name = graphene.String(required=True, description="Company name of the vendor.")
    description = graphene.String(description="Description of the vendor.")

class VendorApplicationCreate(ModelMutation):
    class Arguments:
        input = VendorApplicationInput(required=True, description="Fields required to create a vendor application.")

    class Meta:
        description = "Creates a new vendor application."
        model = VendorApplication
        error_type_class = VendorError
        error_type_field = "vendor_errors"

    @classmethod
    def clean_input(cls, info, instance, data):
        cleaned_input = super().clean_input(info, instance, data)
        # Add any additional input validation here
        return cleaned_input

    @classmethod
    def perform_mutation(cls, root, info, **data):
        user = get_user_or_app_from_context(info.context)
        if not user.is_authenticated:
            raise PermissionDenied("You need to be logged in to apply as a vendor.")
        
        input_data = data.get("input", {})
        cleaned_input = cls.clean_input(info, None, input_data)
        
        try:
            vendor_application = VendorApplication.objects.create(
                user=user,
                company_name=cleaned_input["company_name"],
                description=cleaned_input.get("description", "")
            )
        except ValidationError as e:
            raise ValidationError({"company_name": str(e)})
        except Exception as e:
            raise GraphQLError("An unexpected error occurred.")

        return VendorApplicationCreate(vendor_application=vendor_application)

class VendorApplicationMutations(graphene.ObjectType):
    vendor_application_create = VendorApplicationCreate.Field()