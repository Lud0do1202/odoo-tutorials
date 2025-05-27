from odoo.exceptions import UserError, ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged('post_install', '-at_install', 'estate')
class EstateTestCase(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.property_new = cls.env['estate.property'].create(
            {
                'name': 'Property 1',
                'description': 'Nice property',
                'expected_price': 100000,
                'selling_price': 120000,
                'living_area': 50,
                'garden_area': 20,
                'garden_orientation': 'north',
                'state': 'new',
            }
        )

        cls.property_offer_accepted = cls.env['estate.property'].create(
            {
                'name': 'Property 3',
                'description': 'Property with an offer received',
                'expected_price': 130000,
                'selling_price': 140000,
                'living_area': 60,
                'garden_area': 25,
                'garden_orientation': 'east',
                'state': 'offer_received',
                'offer_ids': [
                    (
                        0,
                        0,
                        {
                            'partner_id': cls.env.ref('base.res_partner_2').id,
                            'price': 135000,
                            'status': 'accepted',
                        },
                    )
                ],
            }
        )
        cls.property_offer_accepted.state = 'offer_accepted'

        cls.property_sold = cls.env['estate.property'].create(
            {
                'name': 'Property 2',
                'description': 'Already sold property',
                'expected_price': 150000,
                'selling_price': 180000,
                'living_area': 70,
                'garden_area': 30,
                'garden_orientation': 'south',
                'state': 'sold',
            }
        )

    def test_cannot_create_offer_for_sold_property(self):
        """You cannot create an offer for a sold property."""
        with self.assertRaises(ValidationError):
            self.env['estate.property.offer'].create(
                {
                    'property_id': self.property_sold.id,
                    'partner_id': self.env.ref('base.res_partner_2').id,
                    'price': 200000,
                }
            )

    def test_cannot_sell_property_without_accepted_offer(self):
        """You cannot sell a property if no offer has been accepted."""
        with self.assertRaises(UserError):
            self.property_new.action_sold()

    def test_can_sell_property_with_accepted_offer(self):
        """You can sell a property if there is an accepted offer."""
        self.property_offer_accepted.action_sold()
        self.assertEqual(self.property_offer_accepted.state, 'sold')

    def test_total_area_computation(self):
        """Total area = living_area + garden_area."""
        self.property_new.living_area = 40
        self.property_new.garden_area = 20
        self.property_new._compute_total_area()
        self.assertEqual(self.property_new.total_area, 60)
