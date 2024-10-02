import graphene
from ....vendor.models import VendorApplication
from ....tests.utils import get_graphql_content

VENDOR_APPLICATION_CREATE_MUTATION = """
mutation VendorApplicationCreate($input: VendorApplicationInput!) {
  vendorApplicationCreate(input: $input) {
    vendorApplication {
      id
      companyName
      description
      isApproved
      createdAt
      updatedAt
    }
    errors {
      field
      message
      code
    }
  }
}
"""

def test_vendor_application_create_mutation(
    permission_manage_vendors,
    app_api_client,
    staff_user,
):
    query = VENDOR_APPLICATION_CREATE_MUTATION
    staff_user.user_permissions.add(permission_manage_vendors)

    variables = {
        "input": {
            "companyName": "New Vendor",
            "description": "Description of the new vendor."
        }
    }
    
    response = app_api_client.post_graphql(query, variables=variables)
    content = get_graphql_content(response)

    vendor_application_data = content["data"]["vendorApplicationCreate"]["vendorApplication"]
    assert vendor_application_data["companyName"] == "New Vendor"
    assert vendor_application_data["description"] == "Description of the new vendor."
    assert vendor_application_data["isApproved"] is False  # Assuming default is not approved

def test_vendor_application_create_mutation_without_permissions(
    app_api_client,
    staff_user,
):
    query = VENDOR_APPLICATION_CREATE_MUTATION

    variables = {
        "input": {
            "companyName": "New Vendor",
            "description": "Description of the new vendor."
        }
    }
    
    response = app_api_client.post_graphql(query, variables=variables)
    content = get_graphql_content(response)

    errors = content["data"]["vendorApplicationCreate"]["errors"]
    assert errors
    assert errors[0]["field"] == "permissions"
    assert errors[0]["code"] == "OUT_OF_SCOPE_PERMISSION"

def test_vendor_application_create_mutation_with_validation_error(
    permission_manage_vendors,
    app_api_client,
    staff_user,
):
    query = VENDOR_APPLICATION_CREATE_MUTATION
    staff_user.user_permissions.add(permission_manage_vendors)

    variables = {
        "input": {
            "companyName": "",  # Missing required field
            "description": "Description of the new vendor."
        }
    }
    
    response = app_api_client.post_graphql(query, variables=variables)
    content = get_graphql_content(response)

    errors = content["data"]["vendorApplicationCreate"]["errors"]
    assert errors
    assert errors[0]["field"] == "companyName"
    assert errors[0]["code"] == "REQUIRED"