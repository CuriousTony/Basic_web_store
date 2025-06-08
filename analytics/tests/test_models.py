from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from analytics.models import Report


class ReportModelTest(TestCase):
    def setUp(self):
        today = timezone.now().date()
        self.report_data = {
            'period_type': 'daily',
            'start_date': today,
            'end_date': today,
            'total_sales': 150000.50,
            'total_profit': 50000.75,
            'avg_order_value': 7500.25,
            'top_bouquets': {'bouquet1': 15, 'bouquet2': 12, 'bouquet3': 10}
        }

    def test_create_report(self):
        """Тест создания отчета с валидными данными"""
        report = Report.objects.create(**self.report_data)

        self.assertEqual(report.period_type, 'daily')
        self.assertEqual(report.start_date, timezone.now().date())
        self.assertEqual(report.end_date, timezone.now().date())
        self.assertEqual(float(report.total_sales), 150000.50)
        self.assertEqual(float(report.total_profit), 50000.75)
        self.assertEqual(float(report.avg_order_value), 7500.25)
        self.assertEqual(report.top_bouquets, {'bouquet1': 15, 'bouquet2': 12, 'bouquet3': 10})
        self.assertIsNotNone(report.created_at)
        self.assertTrue(timezone.now() - report.created_at < timedelta(seconds=1))
        self.assertEqual(report.top_bouquets_data, {'bouquet1': 15, 'bouquet2': 12, 'bouquet3': 10})

    def test_period_type_choices(self):
        """Тест валидации выбора типа периода"""
        valid_choices = ['daily', 'weekly', 'monthly']

        for choice in valid_choices:
            with self.subTest(choice=choice):
                data = self.report_data.copy()
                data['period_type'] = choice
                report = Report.objects.create(**data)
                self.assertEqual(report.period_type, choice)

    def test_decimal_fields_precision(self):
        """Тест точности десятичных полей"""
        report = Report.objects.create(**self.report_data)

        # Проверка decimal_places=2
        self.assertEqual(str(report.total_sales), '150000.5')
        self.assertEqual(str(report.total_profit), '50000.75')
        self.assertEqual(str(report.avg_order_value), '7500.25')

    def test_top_bouquets_default(self):
        """Тест значения по умолчанию для top_bouquets"""
        data = self.report_data.copy()
        del data['top_bouquets']
        report = Report.objects.create(**data)
        self.assertEqual(report.top_bouquets, {})

    def test_verbose_names(self):
        """Тест метаданных модели"""
        self.assertEqual(Report._meta.verbose_name, 'Отчёт')
        self.assertEqual(Report._meta.verbose_name_plural, 'Отчёты')

    def test_indexes(self):
        """Тест наличия индексов"""
        indexes = [idx.fields for idx in Report._meta.indexes]
        self.assertIn(['start_date', 'end_date'], indexes)

    def test_top_bouquets_json_serialization(self):
        """Тест сериализации JSON-поля"""
        complex_data = {
            'bouquets': [
                {'id': 1, 'name': 'Розы', 'sales': 25},
                {'id': 2, 'name': 'Тюльпаны', 'sales': 18}
            ],
            'total': 43
        }

        report = Report.objects.create(
            **{**self.report_data, 'top_bouquets': complex_data}
        )

        self.assertEqual(report.top_bouquets, complex_data)
        db_report = Report.objects.get(pk=report.pk)
        self.assertEqual(db_report.top_bouquets, complex_data)

    def test_date_ranges(self):
        """Тест различных временных диапазонов"""
        today = timezone.now().date()
        test_cases = [
            {
                'name': 'daily',
                'start': today,
                'end': today
            },
            {
                'name': 'weekly',
                'start': today - timedelta(days=6),
                'end': today
            },
            {
                'name': 'monthly',
                'start': today - timedelta(days=30),
                'end': today
            }
        ]

        for case in test_cases:
            with self.subTest(period=case['name']):
                data = self.report_data.copy()
                data['period_type'] = case['name']
                data['start_date'] = case['start']
                data['end_date'] = case['end']

                report = Report.objects.create(**data)
                self.assertEqual(report.period_type, case['name'])
                self.assertEqual(report.start_date, case['start'])
                self.assertEqual(report.end_date, case['end'])

    def test_future_dates(self):
        """Тест создания отчетов с будущими датами (должно быть разрешено)"""
        today = timezone.now().date()
        future_date = today + timedelta(days=10)

        report = Report.objects.create(
            period_type='daily',
            start_date=future_date,
            end_date=future_date,
            total_sales=10000,
            total_profit=5000,
            avg_order_value=1000,
            top_bouquets={}
        )
        self.assertEqual(report.start_date, future_date)

    def test_negative_values(self):
        """Тест создания отчетов с отрицательными значениями (должно быть разрешено)"""
        report = Report.objects.create(
            period_type='daily',
            start_date=timezone.now().date(),
            end_date=timezone.now().date(),
            total_sales=-10000,
            total_profit=-5000,
            avg_order_value=-1000,
            top_bouquets={}
        )
        self.assertEqual(float(report.total_sales), -10000)
