import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from pytest_django.asserts import assertNumQueries
from rest_framework_simplejwt.tokens import RefreshToken  # type: ignore[import]

User = get_user_model()


@pytest.mark.parametrize(
    "email, password, status_code, expected_response",
    (
        (
            None,
            None,
            400,
            {
                "email": ["This field is required."],
                "password": ["This field is required."],
            },
        ),
        (
            "",
            "",
            400,
            {
                "email": ["This field may not be blank."],
                "password": ["This field may not be blank."],
            },
        ),
        ("test@example.com", None, 400, {"password": ["This field is required."]}),
        (None, "test", 400, {"email": ["This field is required."]}),
        (
            "invalid@invalid.com",
            "invalid",
            401,
            {"detail": "No active account found with the given credentials"},
        ),
        (
            "xdavenport@example.com",
            "wrong_password",
            401,
            {"detail": "No active account found with the given credentials"},
        ),
        (
            "kelly@example.com",
            "A6*WMu)k%0",
            400,
            {"detail": ["You are not allowed to login. Please contact your administrator."]},
        ),
        (
            "heatherknight@example.net",
            "&aZ4Ui+f6(",
            400,
            {"detail": ["You are not allowed to login. Please contact your administrator."]},
        ),
    ),
)
@pytest.mark.django_db
def test_admin_token_obtain_pair_give_errors(
    api_client, user_factory, tenant_factory, email, password, status_code, expected_response
):
    """
    Testing that token obtain pair raises errors when invalid input is provided.
    """
    # Normal user
    user_factory(email="xdavenport@example.com", password="&aZ4Ui+f6(")
    # User without Subscription
    user_factory(email="kelly@example.com", password="A6*WMu)k%0", associated_subscription=None)
    # tenant user
    tenant_user = user_factory(email="heatherknight@example.net", password="&aZ4Ui+f6(")
    tenant = tenant_factory(user=tenant_user)
    tenant.user = tenant_user
    tenant.save()

    request_data = {}
    if email is not None:
        request_data["email"] = email
    if password is not None:
        request_data["password"] = password

    response = api_client.post(reverse("authentication:admin_token_obtain_pair"), request_data)

    assert response.status_code == status_code
    assert response.data == expected_response


@pytest.mark.parametrize(
    "email, password",
    (("matthewhughes@example.net", "Q)t8JXi_(5"),),
)
@pytest.mark.django_db
def test_admin_token_obtain_pair_give_success(api_client, user_factory, email, password):
    """
    Testing that token obtain pair executes successfully when valid input is provided.
    """
    user_factory(username="lindacarr", email="matthewhughes@example.net", password="Q)t8JXi_(5")
    request_data = {"email": email, "password": password}

    with assertNumQueries(4):
        response = api_client.post(reverse("authentication:admin_token_obtain_pair"), request_data)

    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.parametrize(
    "email, password, status_code, expected_response",
    (
        (
            None,
            None,
            400,
            {
                "email": ["This field is required."],
                "password": ["This field is required."],
            },
        ),
        (
            "",
            "",
            400,
            {
                "email": ["This field may not be blank."],
                "password": ["This field may not be blank."],
            },
        ),
        ("test@example.com", None, 400, {"password": ["This field is required."]}),
        (None, "test", 400, {"email": ["This field is required."]}),
        (
            "invalid@invalid.com",
            "invalid",
            401,
            {"detail": "No active account found with the given credentials"},
        ),
        (
            "xdavenport@example.com",
            "wrong_password",
            401,
            {"detail": "No active account found with the given credentials"},
        ),
        (
            "kelly@example.com",
            "A6*WMu)k%0",
            400,
            {"detail": ["You are not allowed to login. Please contact your administrator."]},
        ),
        (
            "matthewhughes@example.com",
            "Q)t8JXi_(5",
            400,
            {"detail": ["You are not allowed to login. Please contact your administrator."]},
        ),
        (
            "xdavenport@example.com",
            "&aZ4Ui+f6(",
            400,
            {"detail": ["You are not allowed to login. Please contact your administrator."]},
        ),
    ),
)
@pytest.mark.django_db
def test_tenant_token_obtain_pair_give_errors(
    api_client, user_factory, subscription_factory, email, password, status_code, expected_response
):
    """
    Testing that token obtain pair raises errors when invalid input is provided.
    """
    subscription = subscription_factory()
    # Non-tenant user
    user_factory(email="xdavenport@example.com", password="&aZ4Ui+f6(")
    # Admin user
    user = user_factory(email="matthewhughes@example.com", password="Q)t8JXi_(5")
    subscription.purchased_by = user
    subscription.save()
    user.associated_subscription = subscription
    user.save()
    # User without Subscription
    user_factory(email="kelly@example.com", password="A6*WMu)k%0", associated_subscription=None)
    # tenant user

    request_data = {}
    if email is not None:
        request_data["email"] = email
    if password is not None:
        request_data["password"] = password

    response = api_client.post(reverse("authentication:tenant_token_obtain_pair"), request_data)

    assert response.status_code == status_code
    assert response.data == expected_response


@pytest.mark.parametrize(
    "email, password",
    (("matthewhughes@example.net", "Q)t8JXi_(5"),),
)
@pytest.mark.django_db
def test_tenant_token_obtain_pair_give_success(api_client, user_factory, email, password, lease_factory):
    """
    Testing that token obtain pair executes successfully when valid input is provided.
    """

    tenant_user = user_factory(email="matthewhughes@example.net", password="Q)t8JXi_(5")
    lease = lease_factory(status="ACTIVE")
    lease.primary_tenant.user = tenant_user
    lease.primary_tenant.save()

    request_data = {"email": email, "password": password}

    with assertNumQueries(4):
        response = api_client.post(reverse("authentication:tenant_token_obtain_pair"), request_data)

    assert response.status_code == 200
    assert "access" in response.data
    assert "refresh" in response.data


@pytest.mark.parametrize(
    "refresh, status_code, expected_response",
    (
        (None, 400, {"refresh": ["This field is required."]}),
        ("", 400, {"refresh": ["This field may not be blank."]}),
        (
            "invalid",
            401,
            {"detail": "Token is invalid or expired", "code": "token_not_valid"},
        ),
    ),
)
def test_token_refresh_give_errors(api_client, refresh, status_code, expected_response):
    """
    Testing that token refresh raises errors when invalid input is provided.
    """
    request_data = {}
    if refresh is not None:
        request_data["refresh"] = refresh

    response = api_client.post(reverse("token_refresh"), request_data)

    assert response.status_code == status_code
    assert response.data == expected_response


@pytest.mark.django_db
def test_token_refresh_give_success(api_client, user_factory):
    """
    Testing that token refresh executes successfully when valid input is provided.
    """
    user = user_factory()
    token = RefreshToken.for_user(user)
    refresh_token = str(token)

    with assertNumQueries(1):
        response = api_client.post(reverse("token_refresh"), {"refresh": refresh_token})

    assert response.status_code == 200
    assert "access" in response.data


@pytest.mark.parametrize(
    "token, status_code, expected_response",
    (
        (None, 400, {"token": ["This field is required."]}),
        ("", 400, {"token": ["This field may not be blank."]}),
        (
            "invalid",
            401,
            {"detail": "Token is invalid or expired", "code": "token_not_valid"},
        ),
    ),
)
def test_token_verify_give_errors(api_client, token, status_code, expected_response):
    """
    Testing that token verify raises errors when invalid input is provided.
    """
    request_data = {}
    if token is not None:
        request_data["token"] = token

    response = api_client.post(reverse("token_verify"), request_data)

    assert response.status_code == status_code
    assert response.data == expected_response


@pytest.mark.django_db
def test_token_verify_give_success(api_client, user_factory):
    """
    Testing that token verify executes successfully when valid input is provided.
    """
    user = user_factory()
    token = RefreshToken.for_user(user)
    access_token = str(token.access_token)
    refresh_token = str(token)

    # Making sure no DB query is happening to verify the token
    with assertNumQueries(0):
        response_verify_access = api_client.post(reverse("token_verify"), {"token": access_token})
        response_verify_refresh = api_client.post(reverse("token_verify"), {"token": refresh_token})

    assert response_verify_access.status_code == 200
    assert response_verify_refresh.status_code == 200
