import pytest
from unittest.mock import Mock

from requests.models import Response

from sources.rest_api.paginators import (
    SinglePagePaginator,
    OffsetPaginator,
    HeaderLinkPaginator,
    JSONResponsePaginator,
)


class TestHeaderLinkPaginator:
    def test_update_state_with_next(self):
        paginator = HeaderLinkPaginator()
        response = Mock(Response)
        response.links = {"next": {"url": "http://example.com/next"}}
        paginator.update_state(response)
        assert paginator.next_reference == "http://example.com/next"
        assert paginator.has_next_page is True

    def test_update_state_without_next(self):
        paginator = HeaderLinkPaginator()
        response = Mock(Response)
        response.links = {}
        paginator.update_state(response)
        assert paginator.has_next_page is False


class TestJSONResponsePaginator:
    def test_update_state_with_next(self):
        paginator = JSONResponsePaginator()
        response = Mock(
            Response, json=lambda: {"next": "http://example.com/next", "results": []}
        )
        paginator.update_state(response)
        assert paginator.next_reference == "http://example.com/next"
        assert paginator.has_next_page is True

    def test_update_state_without_next(self):
        paginator = JSONResponsePaginator()
        response = Mock(Response, json=lambda: {"results": []})
        paginator.update_state(response)
        assert paginator.next_reference is None
        assert paginator.has_next_page is False


class TestSinglePagePaginator:
    def test_update_state(self):
        paginator = SinglePagePaginator()
        response = Mock(Response)
        paginator.update_state(response)
        assert paginator.has_next_page is False

    def test_update_state_with_next(self):
        paginator = SinglePagePaginator()
        response = Mock(
            Response, json=lambda: {"next": "http://example.com/next", "results": []}
        )
        response.links = {"next": {"url": "http://example.com/next"}}
        paginator.update_state(response)
        assert paginator.has_next_page is False


class TestOffsetPaginator:
    def test_update_state(self):
        paginator = OffsetPaginator(0, 10)
        response = Mock(Response, json=lambda: {"total": 20})
        paginator.update_state(response)
        assert paginator.offset == 10
        assert paginator.has_next_page is True

        # Test for reaching the end
        paginator.update_state(response)
        assert paginator.has_next_page is False

    def test_update_state_without_total(self):
        paginator = OffsetPaginator(0, 10)
        response = Mock(Response, json=lambda: {})
        with pytest.raises(ValueError):
            paginator.update_state(response)

    def test_prepare_next_request_args(self):
        paginator = OffsetPaginator(0, 10)
        updated_url, updated_params, updated_json = paginator.prepare_next_request_args(
            "http://example.com", {}, {}
        )
        assert updated_url == "http://example.com"
        assert updated_params == {"offset": 0, "limit": 10}
        assert updated_json == {}
