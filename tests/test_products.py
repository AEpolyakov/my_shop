import pytest
from sqlalchemy import select

from app.product.models import Product


@pytest.fixture
async def inserted_product(product_list: list[dict], db_session):
    product_dict = product_list[0]

    product = Product(**product_dict)
    db_session.add(product)
    await db_session.commit()

    return product


class TestProducts:

    async def test_create_product(self, client, db_session, product_list):

        product_dict = product_list[0]

        response = await client.post("/products/", json=product_dict)
        assert response.status_code == 201

        data = response.json()

        assert data["name"] == product_dict["name"]
        assert data["price"] == product_dict["price"]
        assert data["id"]

        data_from_db = (await db_session.execute(select(Product).where(Product.id == data["id"]))).scalar_one_or_none()
        assert data_from_db.id == data["id"]

    async def test_get_products(self, client, db_session, product_list):

        for product_dict in product_list:
            product = Product(**product_dict)
            db_session.add(product)

        await db_session.commit()

        response = await client.get("/products/")
        assert response.status_code == 200
        product_response = response.json()
        assert product_response["total"] == len(product_list)

        limit = 2
        response = await client.get("/products/", params={"limit": limit})
        assert response.status_code == 200
        product_response = response.json()
        assert len(product_response["results"]) == limit

        skip = 2
        response = await client.get("/products/", params={"skip": skip})
        assert response.status_code == 200
        product_response = response.json()
        assert len(product_response["results"]) == len(product_list) - skip

    async def test_update_product(self, client, db_session, product_list, inserted_product):

        update_product_dict = product_list[1]

        response = await client.put(f"/products/{inserted_product.id}", json=update_product_dict)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == update_product_dict["name"]
        assert data["price"] == update_product_dict["price"]
        assert data["category_id"] == update_product_dict["category_id"]
        assert data["id"] == inserted_product.id

    async def test_delete_product(self, client, db_session, product_list, inserted_product):

        response = await client.delete(f"/products/{inserted_product.id}")
        assert response.status_code == 204
