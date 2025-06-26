import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from tenant.views import AnnouncementViewSet


@pytest.mark.parametrize(
    "query_params, index_result, num_queries",
    (({}, [2, 1, 0], 16),),
)
@pytest.mark.django_db
def test_announcement_list(
    api_rf, tenant_user_with_permissions, announcement_factory, query_params, index_result, num_queries
):
    """
    Testing :py:meth:`tenant.views.AnnouncementViewSet.list` method.
    """
    user, lease = tenant_user_with_permissions([("communication", "announcement")])

    instance_1 = announcement_factory(units=(lease.unit,), subscription=user.associated_subscription)
    instance_2 = announcement_factory(units=(lease.unit,), subscription=user.associated_subscription)
    instance_3 = announcement_factory(units=(lease.unit,), subscription=user.associated_subscription)
    announcement_factory()

    announcements = [instance_1.id, instance_2.id, instance_3.id]

    with assertNumQueries(num_queries):
        url = reverse("tenant:announcement-list")
        request = api_rf.get(url, query_params, format="json")
        request.user = user
        view = AnnouncementViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [announcements[i] for i in index_result]


@pytest.mark.django_db
def test_announcement_retrieve(api_rf, announcement_factory, tenant_user_with_permissions):
    """
    Testing :py:meth:`tenant.views.AnnouncementViewSet.retrieve` method.
    """

    user, lease = tenant_user_with_permissions([("communication", "announcement")])
    announcement = announcement_factory(subscription=user.associated_subscription, units=(lease.unit,))

    with assertNumQueries(16):
        url = reverse("tenant:announcement-detail", kwargs={"pk": announcement.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = AnnouncementViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=announcement.id)

    assert response.status_code == 200

    assert response.data.keys() == {
        "id",
        "title",
        "body",
        "selection",
        "send_by_email",
        "display_on_tenant_portal",
        "display_date",
        "expiry_date",
        "properties",
        "units",
        "created_at",
        "status",
    }
