from typing import List

import pytest
import requests
from packaging.version import Version

import pip_audit.service as service


def test_pypi():
    pypi = service.PyPIService()
    dep = service.Dependency("jinja2", Version("2.4.1"))
    results: List[service.VulnerabilityResult] = dict(pypi.query_all([dep]))
    assert len(results) == 1
    assert dep in results
    vulns = results[dep]
    assert len(vulns) > 0


def test_pypi_multiple_pkg():
    pypi = service.PyPIService()
    deps: List[service.Dependency] = [
        service.Dependency("jinja2", Version("2.4.1")),
        service.Dependency("flask", Version("0.5")),
    ]
    results: List[service.VulnerabilityResult] = dict(pypi.query_all(deps))
    assert len(results) == 2
    assert deps[0] in results and deps[1] in results
    assert len(results[deps[0]]) > 0
    assert len(results[deps[1]]) > 0


def test_pypi_cached():
    pypi = service.PyPIService()
    dep = service.Dependency("jinja2", Version("2.4.1"))
    results: List[service.VulnerabilityResult] = dict(pypi.query_all([dep]))
    cached_results: List[service.VulnerabilityResult] = dict(pypi.query_all([dep]))
    assert results == cached_results
    assert len(results) == 1
    assert dep in results
    vulns = results[dep]
    assert len(vulns) > 0


def test_pypi_http_error(monkeypatch):
    def get_error_response():
        class MockResponse:
            def raise_for_status(self):
                raise requests.HTTPError

        return MockResponse()

    monkeypatch.setattr(requests, "get", lambda url, headers: get_error_response())

    pypi = service.PyPIService()
    dep = service.Dependency("jinja2", Version("2.4.1"))
    with pytest.raises(service.ServiceError):
        dict(pypi.query_all([dep]))


def test_pypi_mocked_response(monkeypatch):
    def get_mock_response():
        class MockResponse:
            headers = {"ETag": "foo"}
            status_code = 200

            def raise_for_status(self):
                pass

            def json(self):
                return {
                    "vulnerabilities": [
                        {
                            "id": "VULN-0",
                            "details": "The first vulnerability",
                            "fixed_in": ["1.1", "1.4"],
                        }
                    ]
                }

        return MockResponse()

    monkeypatch.setattr(requests, "get", lambda url, headers: get_mock_response())

    pypi = service.PyPIService()
    dep = service.Dependency("foo", Version("1.0"))
    results: List[service.VulnerabilityResult] = dict(pypi.query_all([dep]))
    assert len(results) == 1
    assert dep in results
    assert len(results[dep]) == 1
    assert results[dep][0] == service.VulnerabilityResult(
        id="VULN-0",
        description="The first vulnerability",
        fix_versions=[Version("1.1"), Version("1.4")],
    )


def test_pypi_no_vuln_key(monkeypatch):
    def get_mock_response():
        class MockResponse:
            headers = {"ETag": "foo"}
            status_code = 200

            def raise_for_status(self):
                pass

            def json(self):
                return {}

        return MockResponse()

    monkeypatch.setattr(requests, "get", lambda url, headers: get_mock_response())

    pypi = service.PyPIService()
    dep = service.Dependency("foo", Version("1.0"))
    results: List[service.VulnerabilityResult] = dict(pypi.query_all([dep]))
    assert len(results) == 1
    assert dep in results
    assert not results[dep]


def test_pypi_invalid_version(monkeypatch):
    def get_mock_response():
        class MockResponse:
            headers = {"ETag": "foo"}
            status_code = 200

            def raise_for_status(self):
                pass

            def json(self):
                return {
                    "vulnerabilities": [
                        {
                            "id": "VULN-0",
                            "details": "The first vulnerability",
                            "fixed_in": ["invalid_version"],
                        }
                    ]
                }

        return MockResponse()

    monkeypatch.setattr(requests, "get", lambda url, headers: get_mock_response())

    pypi = service.PyPIService()
    dep = service.Dependency("foo", Version("1.0"))
    with pytest.raises(service.ServiceError):
        dict(pypi.query_all([dep]))


def test_pypi_not_modified_response_without_cache(monkeypatch):
    def get_mock_response():
        class MockResponse:
            status_code = 304

            def raise_for_status(self):
                pass

        return MockResponse()

    monkeypatch.setattr(requests, "get", lambda url, headers: get_mock_response())

    pypi = service.PyPIService()
    dep = service.Dependency("foo", Version("1.0"))
    with pytest.raises(service.ServiceError):
        dict(pypi.query_all([dep]))


def test_pypi_cache_invalidation(monkeypatch):
    class MockResponse:
        headers = {"ETag": "foo"}
        status_code = 200

        def raise_for_status(self):
            pass

        def json(self):
            return {
                "vulnerabilities": [
                    {
                        "id": "VULN-0",
                        "details": "The first vulnerability",
                        "fixed_in": ["1.1", "1.4"],
                    }
                ]
            }

    def get_mock_response():
        return MockResponse()

    monkeypatch.setattr(requests, "get", lambda url, headers: get_mock_response())

    pypi = service.PyPIService()
    dep = service.Dependency("foo", Version("1.0"))
    results: List[service.VulnerabilityResult] = dict(pypi.query_all([dep]))

    assert len(results) == 1
    assert dep in results
    assert len(results[dep]) == 1
    assert results[dep][0] == service.VulnerabilityResult(
        id="VULN-0",
        description="The first vulnerability",
        fix_versions=[Version("1.1"), Version("1.4")],
    )

    # Simulate the case where our cache entry is invalidated.
    def new_json():
        return {
            "vulnerabilities": [
                {
                    "id": "VULN-0",
                    "details": "The first vulnerability",
                    "fixed_in": ["1.1", "1.4"],
                },
                {
                    "id": "VULN-1",
                    "details": "The second vulnerability",
                    "fixed_in": ["1.0"],
                },
            ]
        }

    MockResponse.json = lambda _: new_json()
    new_results: List[service.VulnerabilityResult] = dict(pypi.query_all([dep]))
    assert len(new_results) == 1
    assert dep in new_results
    assert len(new_results[dep]) == 2
    print(new_results[dep])
    assert new_results[dep] == [
        service.VulnerabilityResult(
            id="VULN-0",
            description="The first vulnerability",
            fix_versions=[Version("1.1"), Version("1.4")],
        ),
        service.VulnerabilityResult(
            id="VULN-1",
            description="The second vulnerability",
            fix_versions=[Version("1.0")],
        ),
    ]
