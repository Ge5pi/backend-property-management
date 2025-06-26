import pytest
from django.urls import reverse
from pytest_django.asserts import assertNumQueries

from authentication.views import GroupViewSet


@pytest.mark.django_db
def test_group_list(api_rf, user_factory, group_factory):
    """
    Testing :py:meth:`authentication.views.GroupViewSet.list` method.
    """
    user = user_factory()

    instance_1 = group_factory(name="Fly.")
    instance_2 = group_factory(name="Toward.")
    instance_3 = group_factory(name="Himself.")

    groups = [instance_1.id, instance_2.id, instance_3.id]
    index_result = [2, 1, 0]

    with assertNumQueries(1):
        url = reverse("authentication:group-list")
        request = api_rf.get(url, {}, format="json")
        request.user = user
        view = GroupViewSet.as_view({"get": "list"})
        response = view(request)

    assert response.status_code == 200
    assert len(response.data) == len(index_result)
    response_ids = [i["id"] for i in response.data]
    assert response_ids == [groups[i] for i in index_result]


@pytest.mark.django_db
def test_group_retrieve(api_rf, group_factory, user_factory):
    """
    Testing :py:meth:`authentication.views.GroupViewSet.retrieve` method.
    """

    user = user_factory()
    group = group_factory()

    with assertNumQueries(1):
        url = reverse("authentication:group-detail", kwargs={"pk": group.id})
        request = api_rf.get(url, format="json")
        request.user = user
        view = GroupViewSet.as_view({"get": "retrieve"})
        response = view(request, pk=group.id)

    assert response.status_code == 200

    assert response.data.keys() == {"id", "name"}
