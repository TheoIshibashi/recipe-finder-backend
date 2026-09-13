import pytest
import httpx
from app.mealdb_client import search_by_name, lookup_by_id, random_meal, filter_by_ingredient, list_categories, _get, MealDBError

@pytest.mark.anyio
async def test_search_by_name(monkeypatch):
    async def mock_get(endpoint: str, params: dict):
        assert endpoint == "search.php"
        assert params == {"s": "chicken"}

        return {
            "meals": [
                {"idMeal": "123"}
            ]
        }

    monkeypatch.setattr("app.mealdb_client._get", mock_get)

    result = await search_by_name("chicken")

    assert result == [{"idMeal": "123"}]


@pytest.mark.anyio
async def test_search_by_name_returns_empty_list_when_meals_is_none(monkeypatch):
    async def mock_get(endpoint: str, params: dict):
            assert endpoint == "search.php"
            assert params == {"s": "unknown"}
    
            return {
                "meals": None 
            }
    
    monkeypatch.setattr("app.mealdb_client._get", mock_get)
    
    result = await search_by_name("unknown")
    
    assert result == []

@pytest.mark.anyio
async def test_lookup_by_id(monkeypatch):
     async def mock_get(endpoint: str, params: dict):
          assert endpoint == "lookup.php"
          assert params == {"i": "123"}

          return {
               "meals":[
                    {"idMeal": "123"}
               ]
          }

     monkeypatch.setattr("app.mealdb_client._get", mock_get)

     result = await lookup_by_id("123")

     assert result == {"idMeal": "123"}

@pytest.mark.anyio
async def test_lookup_by_id_returns_none_when_meals_is_none(monkeypatch):
     async def mock_get(endpoint: str, params: dict):
          assert endpoint == "lookup.php"
          assert params == {"i": "999"}

          return {
               "meals": None
          }

     monkeypatch.setattr("app.mealdb_client._get", mock_get)

     result = await lookup_by_id("999")

     assert result is None

@pytest.mark.anyio
async def test_random_meal(monkeypatch):
    async def mock_get(endpoint: str, params: dict):
         assert endpoint == "random.php"
         assert params == {}

         return {
              "meals": [
                   {"idMeal": "123"}
              ]
         }

    monkeypatch.setattr("app.mealdb_client._get", mock_get)

    result = await random_meal()

    assert result == {"idMeal": "123"}


@pytest.mark.anyio
async def test_random_meal_returns_none_when_meals_is_none(monkeypatch):
    async def mock_get(endpoint: str, params: dict):
         assert endpoint == "random.php"
         assert params == {}

         return {
              "meals": None
         }

    monkeypatch.setattr("app.mealdb_client._get", mock_get)

    result = await random_meal()

    assert result is None

@pytest.mark.anyio
async def test_filter_by_ingredient(monkeypatch):
     async def mock_get(endpoint: str, params: dict):
          assert endpoint == "filter.php"
          assert params == {"i": "chicken"}

          return {
               "meals":[
                    {"idMeal": "123"}
               ]
          }

     monkeypatch.setattr("app.mealdb_client._get", mock_get)

     result = await filter_by_ingredient("chicken")

     assert result == [{"idMeal": "123"}]

@pytest.mark.anyio
async def test_filter_by_ingredient_returns_empty_list_when_meals_is_none(monkeypatch):
     async def mock_get(endpoint: str, params: dict):
          assert endpoint == "filter.php"
          assert params == {"i": "chicken"}

          return {
               "meals": None
          }

     monkeypatch.setattr("app.mealdb_client._get", mock_get)

     result = await filter_by_ingredient("chicken")

     assert result == []

@pytest.mark.anyio
async def test_list_categories(monkeypatch):
     async def mock_get(endpoint: str, params: dict):
        assert endpoint == "categories.php"
        assert params == {}

        return {
             "categories": [
                  {"idCategory": "1", "strCategory": "Beef"}
             ]
        }

     monkeypatch.setattr("app.mealdb_client._get", mock_get)

     result = await list_categories()

     assert result == [
          {"idCategory": "1", "strCategory": "Beef"}
     ] 

@pytest.mark.anyio
async def test_list_categories_returns_empty_list_when_categories_is_none(monkeypatch):
     async def mock_get(endpoint: str, params: dict):
        assert endpoint == "categories.php"
        assert params == {}

        return {
             "categories": None
        }

     monkeypatch.setattr("app.mealdb_client._get", mock_get)

     result = await list_categories()

     assert result == []


@pytest.mark.anyio
async def test_get_success(monkeypatch):
     class MockResponse:
          def raise_for_status(self):
               pass

          def json(self):
               return {"ok": True}

     class MockAsyncClient:
          def __init__(self, timeout):
              assert timeout == 10.0

          async def __aenter__(self):
               return self

          async def __aexit__(self, exc_type, exc, tb):
               pass

          async def get(self, url, params):
               return MockResponse()

     monkeypatch.setattr("app.mealdb_client.httpx.AsyncClient", MockAsyncClient)

     result = await _get("search.php", {"s": "chicken"})

     assert result == {"ok": True}

@pytest.mark.anyio
async def test_get_timeout(monkeypatch):
     class MockAsyncClient:
          def __init__(self, timeout):
              assert timeout == 10.0

          async def __aenter__(self):
               return self

          async def __aexit__(self, exc_type, exc, tb):
               pass

          async def get(self, url, params):
               raise httpx.TimeoutException("timeout")

     monkeypatch.setattr("app.mealdb_client.httpx.AsyncClient", MockAsyncClient)

     with pytest.raises(MealDBError) as exc:
        await _get("search.php", {"s": "chicken"})

     assert str(exc.value) == "A TheMealDB demorou demais para responder."

@pytest.mark.anyio
async def test_get_http_status_error(monkeypatch):
     class MockResponse:
          def raise_for_status(self):
            request = httpx.Request("GET", "https://example.com")
            response = httpx.Response(500, request=request)

            raise httpx.HTTPStatusError(
                 "erro",
                 request=request,
                 response=response
            )
               
     class MockAsyncClient:
          def __init__(self, timeout):
              assert timeout == 10.0

          async def __aenter__(self):
               return self

          async def __aexit__(self, exc_type, exc, tb):
               pass

          async def get(self, url, params):
               return MockResponse()

     monkeypatch.setattr("app.mealdb_client.httpx.AsyncClient", MockAsyncClient)

     with pytest.raises(MealDBError) as exc:
        await _get("some_endpoint", {})

     assert str(exc.value) == "TheMealDB retornou erro 500."

@pytest.mark.anyio
async def test_get_request_error(monkeypatch):
     class MockAsyncClient:
          def __init__(self, timeout):
              assert timeout == 10.0

          async def __aenter__(self):
               return self

          async def __aexit__(self, exc_type, exc, tb):
               pass

          async def get(self, url, params):
               raise httpx.RequestError("erro")

     monkeypatch.setattr("app.mealdb_client.httpx.AsyncClient", MockAsyncClient)

     with pytest.raises(MealDBError) as exc:
        await _get("some_endpoint", {})

     assert str(exc.value) == "Não foi possível conectar à TheMealDB."
     



    