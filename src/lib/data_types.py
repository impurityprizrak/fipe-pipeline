class Brand:
    def __init__(self, id: str, name: str) -> None:
        self.id = id
        self.name = name

    def to_dict(self) -> dict[str, str]:
        return dict(id=self.id, name=self.name)

class Model:
    def __init__(self, brand: Brand, id: str, name: str) -> None:
        self.brand = brand
        self.id = id
        self.name = name
    
    def to_dict(self) -> dict[str, str]:
        return dict(id=self.id, name=self.name)

class Year:
    def __init__(self, model: Model, id: str, name: str) -> None:
        self.model = model
        self.id = id
        self.name = name
    
    def to_dict(self) -> dict[str, str]:
        return dict(id=self.id, name=self.name)
