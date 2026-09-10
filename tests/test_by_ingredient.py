from app.mealdb_client import MealDBError

def test_by_ingredient(client, monkeypatch):
    mock_ingredients = [
        {"idMeal": "123", 
         "strMeal": "Chicken Test",
         "strMealThumb": None},
    ]

    async def mock_filter_by_ingredient(ingredient: str):
        assert ingredient == "chicken"
        return mock_ingredients

    monkeypatch.setattr("app.routes.filter_by_ingredient", mock_filter_by_ingredient)

    response = client.get("/recipes/by-ingredient?ingredient=chicken")
    data = response.json()
    assert response.status_code == 200
    assert data[0]["id"] == "123"
    assert data[0]["name"] == "Chicken Test"
    assert data[0]["thumbnail"] is None

def test_search_route(client):
    response = client.get("/recipes/search?ingredients=")
    assert response.status_code == 422

def test_search_route_only_spaces(client):
    response = client.get("/recipes/search?ingredients=%20%20%20")
    assert response.status_code == 422

def test_by_ingredient_mealdb_error(client, monkeypatch):
    async def mock_filter_by_ingredient(ingredient: str):
        raise MealDBError("Erro de teste")

    monkeypatch.setattr("app.routes.filter_by_ingredient", mock_filter_by_ingredient)
    response = client.get("/recipes/by-ingredient?ingredient=chicken")
    assert response.status_code == 500
    assert response.json() == {"detail": "Erro de teste"}

def test_by_ingredient_empty(client, monkeypatch):
    mock_meal_data_list = []

    async def mock_search_by_ingredient_empty(ingredient: str):
        assert ingredient == "empty_test"
        return mock_meal_data_list

    monkeypatch.setattr("app.routes.filter_by_ingredient", mock_search_by_ingredient_empty)
    response = client.get("/recipes/by-ingredient?ingredient=empty_test")

    assert response.status_code == 200
    assert response.json() == []
    
