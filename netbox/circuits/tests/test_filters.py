from django.test import TestCase

from circuits.constants import CIRCUIT_STATUS_ACTIVE, CIRCUIT_STATUS_OFFLINE, CIRCUIT_STATUS_PLANNED
from circuits.filters import *
from circuits.models import Circuit, CircuitTermination, CircuitType, Provider
from dcim.models import Region, Site


class ProviderTestCase(TestCase):
    queryset = Provider.objects.all()
    filterset = ProviderFilter

    @classmethod
    def setUpTestData(cls):

        providers = (
            Provider(name='Provider 1', slug='provider-1', asn=65001, account='1234'),
            Provider(name='Provider 2', slug='provider-2', asn=65002, account='2345'),
            Provider(name='Provider 3', slug='provider-3', asn=65003, account='3456'),
            Provider(name='Provider 4', slug='provider-4', asn=65004, account='4567'),
            Provider(name='Provider 5', slug='provider-5', asn=65005, account='5678'),
        )
        Provider.objects.bulk_create(providers)

        regions = (
            Region(name='Test Region 1', slug='test-region-1'),
            Region(name='Test Region 2', slug='test-region-2'),
        )
        # Can't use bulk_create for models with MPTT fields
        for r in regions:
            r.save()

        sites = (
            Site(name='Test Site 1', slug='test-site-1', region=regions[0]),
            Site(name='Test Site 2', slug='test-site-2', region=regions[1]),
        )
        Site.objects.bulk_create(sites)

        circuit_types = (
            CircuitType(name='Test Circuit Type 1', slug='test-circuit-type-1'),
            CircuitType(name='Test Circuit Type 2', slug='test-circuit-type-2'),
        )
        CircuitType.objects.bulk_create(circuit_types)

        circuits = (
            Circuit(provider=providers[0], type=circuit_types[0], cid='Test Circuit 1'),
            Circuit(provider=providers[1], type=circuit_types[1], cid='Test Circuit 1'),
        )
        Circuit.objects.bulk_create(circuits)

        CircuitTermination.objects.bulk_create((
            CircuitTermination(circuit=circuits[0], site=sites[0], term_side='A', port_speed=1000),
            CircuitTermination(circuit=circuits[1], site=sites[0], term_side='A', port_speed=1000),
        ))

    def test_name(self):
        params = {'name': ['Provider 1', 'Provider 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_slug(self):
        params = {'slug': ['provider-1', 'provider-2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_asn(self):
        params = {'asn': ['65001', '65002']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_account(self):
        params = {'account': ['1234', '2345']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_id__in(self):
        id_list = self.queryset.values_list('id', flat=True)[:3]
        params = {'id__in': ','.join([str(id) for id in id_list])}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class CircuitTypeTestCase(TestCase):
    queryset = CircuitType.objects.all()
    filterset = CircuitTypeFilter

    @classmethod
    def setUpTestData(cls):

        CircuitType.objects.bulk_create((
            CircuitType(name='Circuit Type 1', slug='circuit-type-1'),
            CircuitType(name='Circuit Type 2', slug='circuit-type-2'),
            CircuitType(name='Circuit Type 3', slug='circuit-type-3'),
        ))

    def test_id(self):
        params = {'id': [self.queryset.first().pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_name(self):
        params = {'name': ['Circuit Type 1']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)

    def test_slug(self):
        params = {'slug': ['circuit-type-1']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 1)


class CircuitTestCase(TestCase):
    queryset = Circuit.objects.all()
    filterset = CircuitFilter

    @classmethod
    def setUpTestData(cls):

        regions = (
            Region(name='Test Region 1', slug='test-region-1'),
            Region(name='Test Region 2', slug='test-region-2'),
            Region(name='Test Region 3', slug='test-region-3'),
        )
        # Can't use bulk_create for models with MPTT fields
        for r in regions:
            r.save()

        sites = (
            Site(name='Test Site 1', slug='test-site-1', region=regions[0]),
            Site(name='Test Site 2', slug='test-site-2', region=regions[1]),
            Site(name='Test Site 3', slug='test-site-3', region=regions[2]),
        )
        Site.objects.bulk_create(sites)

        circuit_types = (
            CircuitType(name='Test Circuit Type 1', slug='test-circuit-type-1'),
            CircuitType(name='Test Circuit Type 2', slug='test-circuit-type-2'),
        )
        CircuitType.objects.bulk_create(circuit_types)

        providers = (
            Provider(name='Provider 1', slug='provider-1'),
            Provider(name='Provider 2', slug='provider-2'),
        )
        Provider.objects.bulk_create(providers)

        circuits = (
            Circuit(provider=providers[0], type=circuit_types[0], cid='Test Circuit 1', install_date='2020-01-01', commit_rate=1000, status=CIRCUIT_STATUS_ACTIVE),
            Circuit(provider=providers[0], type=circuit_types[0], cid='Test Circuit 2', install_date='2020-01-02', commit_rate=2000, status=CIRCUIT_STATUS_ACTIVE),
            Circuit(provider=providers[0], type=circuit_types[0], cid='Test Circuit 3', install_date='2020-01-03', commit_rate=3000, status=CIRCUIT_STATUS_PLANNED),
            Circuit(provider=providers[1], type=circuit_types[1], cid='Test Circuit 4', install_date='2020-01-04', commit_rate=4000, status=CIRCUIT_STATUS_PLANNED),
            Circuit(provider=providers[1], type=circuit_types[1], cid='Test Circuit 5', install_date='2020-01-05', commit_rate=5000, status=CIRCUIT_STATUS_OFFLINE),
            Circuit(provider=providers[1], type=circuit_types[1], cid='Test Circuit 6', install_date='2020-01-06', commit_rate=6000, status=CIRCUIT_STATUS_OFFLINE),
        )
        Circuit.objects.bulk_create(circuits)

        circuit_terminations = ((
            CircuitTermination(circuit=circuits[0], site=sites[0], term_side='A', port_speed=1000),
            CircuitTermination(circuit=circuits[1], site=sites[1], term_side='A', port_speed=1000),
            CircuitTermination(circuit=circuits[2], site=sites[2], term_side='A', port_speed=1000),
        ))
        CircuitTermination.objects.bulk_create(circuit_terminations)

    def test_cid(self):
        params = {'cid': ['Test Circuit 1', 'Test Circuit 2']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_install_date(self):
        params = {'install_date': ['2020-01-01', '2020-01-02']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_commit_rate(self):
        params = {'commit_rate': ['1000', '2000']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_id__in(self):
        id_list = self.queryset.values_list('id', flat=True)[:3]
        params = {'id__in': ','.join([str(id) for id in id_list])}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_provider(self):
        provider = Provider.objects.first()
        params = {'provider_id': [provider.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {'provider': [provider.slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_type(self):
        circuit_type = CircuitType.objects.first()
        params = {'type_id': [circuit_type.pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)
        params = {'type': [circuit_type.slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_status(self):
        params = {'status': [CIRCUIT_STATUS_ACTIVE, CIRCUIT_STATUS_PLANNED]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_region(self):
        regions = Region.objects.all()[:2]
        params = {'region_id': [regions[0].pk, regions[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'region': [regions[0].slug, regions[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)


class CircuitTerminationTestCase(TestCase):
    queryset = CircuitTermination.objects.all()
    filterset = CircuitTerminationFilter

    @classmethod
    def setUpTestData(cls):

        sites = (
            Site(name='Test Site 1', slug='test-site-1'),
            Site(name='Test Site 2', slug='test-site-2'),
            Site(name='Test Site 3', slug='test-site-3'),
        )
        Site.objects.bulk_create(sites)

        circuit_types = (
            CircuitType(name='Test Circuit Type 1', slug='test-circuit-type-1'),
        )
        CircuitType.objects.bulk_create(circuit_types)

        providers = (
            Provider(name='Provider 1', slug='provider-1'),
        )
        Provider.objects.bulk_create(providers)

        circuits = (
            Circuit(provider=providers[0], type=circuit_types[0], cid='Test Circuit 1'),
            Circuit(provider=providers[0], type=circuit_types[0], cid='Test Circuit 2'),
            Circuit(provider=providers[0], type=circuit_types[0], cid='Test Circuit 3'),
        )
        Circuit.objects.bulk_create(circuits)

        circuit_terminations = ((
            CircuitTermination(circuit=circuits[0], site=sites[0], term_side='A', port_speed=1000, upstream_speed=1000, xconnect_id='ABC'),
            CircuitTermination(circuit=circuits[0], site=sites[1], term_side='Z', port_speed=1000, upstream_speed=1000, xconnect_id='DEF'),
            CircuitTermination(circuit=circuits[1], site=sites[1], term_side='A', port_speed=2000, upstream_speed=2000, xconnect_id='GHI'),
            CircuitTermination(circuit=circuits[1], site=sites[2], term_side='Z', port_speed=2000, upstream_speed=2000, xconnect_id='JKL'),
            CircuitTermination(circuit=circuits[2], site=sites[2], term_side='A', port_speed=3000, upstream_speed=3000, xconnect_id='MNO'),
            CircuitTermination(circuit=circuits[2], site=sites[0], term_side='Z', port_speed=3000, upstream_speed=3000, xconnect_id='PQR'),
        ))
        CircuitTermination.objects.bulk_create(circuit_terminations)

    def test_term_side(self):
        params = {'term_side': 'A'}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 3)

    def test_port_speed(self):
        params = {'port_speed': ['1000', '2000']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_upstream_speed(self):
        params = {'upstream_speed': ['1000', '2000']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_xconnect_id(self):
        params = {'xconnect_id': ['ABC', 'DEF']}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 2)

    def test_circuit_id(self):
        circuits = Circuit.objects.all()[:2]
        params = {'circuit_id': [circuits[0].pk, circuits[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)

    def test_site(self):
        sites = Site.objects.all()[:2]
        params = {'site_id': [sites[0].pk, sites[1].pk]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
        params = {'site': [sites[0].slug, sites[1].slug]}
        self.assertEqual(self.filterset(params, self.queryset).qs.count(), 4)
