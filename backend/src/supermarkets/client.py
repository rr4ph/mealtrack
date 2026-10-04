from abc import ABC, abstractmethod

class SupermarketClient(ABC):
    @abstractmethod
    def get_product(self, query):
        pass

    @abstractmethod
    def convert_product(self, data):
        pass

    @abstractmethod
    def get_shops(self, location=None):
        pass

    @abstractmethod
    def convert_shops(self, data):
        pass