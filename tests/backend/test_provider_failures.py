from backend.src.api import products, shops


class _Ok:
    def __init__(self, items):
        self.items = items

    def get_product(self, query):
        return self.items

    def get_shops(self, postcode):
        return self.items


class _Fail:
    def get_product(self, query):
        raise RuntimeError("down")

    def get_shops(self, postcode):
        raise RuntimeError("down")


def test_all_shops_survive_tesco_failure(monkeypatch):
    from backend.src.classes.shop import Shop

    def shop(i):
        return Shop(address_id=i, shop_address="a", shop_name=i, latitude=1.0, longitude=1.0, postal_code="X")

    class Cursor:
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def execute(self, *a): pass
        def fetchone(self): return ("G1 1AA",)
        def cursor(self): return self

    monkeypatch.setattr(shops, "get_connection", lambda: Cursor())
    monkeypatch.setattr(shops, "get_coordinates", lambda p: (1.0, 1.0))
    monkeypatch.setattr(shops, "Morrisons", lambda: _Ok([shop("m")]))
    monkeypatch.setattr(shops, "Sainsburys", lambda: _Ok([shop("s")]))
    monkeypatch.setattr(shops, "Tesco", _Fail)

    result = shops.get_shops_for_user(user_id=1)

    assert sorted(s.supermarket for s in result) == ["morrisons", "sainsburys"]
