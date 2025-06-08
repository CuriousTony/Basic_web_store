from django.test import TestCase
from catalog.models import Bouquet


class BouquetModelTest(TestCase):
    def test_bouquet_creation(self):
        """Тест создания объекта Bouquet."""
        bouquet = Bouquet.objects.create(
            name="Test Bouquet",
            consists="Roses, Lilies",
            price=1000,
            cost_price=700,
            is_bestseller=True,
        )
        self.assertEqual(bouquet.name, "Test Bouquet")
        self.assertEqual(bouquet.consists, "Roses, Lilies")
        self.assertEqual(bouquet.price, 1000)
        self.assertEqual(bouquet.cost_price, 700)
        self.assertTrue(bouquet.is_bestseller)

    def test_bouquet_str_method(self):
        bouquet = Bouquet.objects.create(
            name="Test Bouquet",
            price=1000,
        )
        self.assertEqual(str(bouquet), "Test Bouquet 1000")

    def test_bouquet_average_rating_without_reviews(self):
        bouquet = Bouquet.objects.create(
            name="Test Bouquet",
            price=1000,
        )
        self.assertEqual(bouquet.average_rating, 0)
