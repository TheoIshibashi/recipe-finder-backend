from app.mealdb_client import MealDBError

def test_search_recipes(client, monkeypatch):
    mock_meal_data_list = [{
    "idMeal": "123",
    "strMeal": "Chicken Test",
    "strCategory": "Chicken",
    "strArea": "Test",
    "strInstructions": "Cook it.",
    "strMealThumb": None,
    "strYoutube": None,
    "strTags": None,
    "strIngredient1": "Chicken",
    "strMeasure1": "200g",
    }]

    async def mock_search_by_name(name: str):
        assert name == "chicken"
        return mock_meal_data_list

    monkeypatch.setattr("app.routes.search_by_name", mock_search_by_name)

    response = client.get("/recipes/search?name=chicken")
    data = response.json()
    assert response.status_code == 200
    assert data[0]["id"] == "123"
    assert data[0]["name"] == "Chicken Test"
    assert data[0]["category"] == "Chicken"
    assert data[0]["ingredients"][0]["name"] == "Chicken"
    assert data[0]["ingredients"][0]["measure"] == "200g"

def test_search_by_name_empty(client, monkeypatch):
    mock_meal_data_list = []

    async def mock_search_by_name_empty(name: str):
        assert name == "empty_test"
        return mock_meal_data_list

    monkeypatch.setattr("app.routes.search_by_name", mock_search_by_name_empty)
    response = client.get("/recipes/search?name=empty_test")

    assert response.status_code == 200
    assert response.json() == []


    

def test_search_recipes_mealdb_error(client, monkeypatch):
    async def mock_search_by_name(name: str):
        raise MealDBError("Erro de teste")

    monkeypatch.setattr("app.routes.search_by_name", mock_search_by_name)
    response = client.get("/recipes/search?name=chicken")
    assert response.status_code == 500
    assert response.json() == {"detail": "Erro de teste"}

def test_search_route(client):
    response = client.get("/recipes/search?name=")
    assert response.status_code == 422

def test_search_route_only_spaces(client):
    response = client.get("/recipes/search?name=%20%20%20")
    assert response.status_code == 422