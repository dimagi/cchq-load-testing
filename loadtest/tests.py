from django.utils import unittest
import casegenerator
from propertygenerartors import PropertyValueGenerator, ALPHA, NUMBERS
import specmaker

class SpecmakerTestCase(unittest.TestCase):
    def setUp(self):
        self.output = specmaker.getspec(4)

    def test_spec_making(self):
        self.assertFalse(self.output["explicit"])
        self.assertEqual(len(self.output), 2)
        self.assertEqual(len(self.output["case"]), 4)

class PropertyGeneratorTestCase(unittest.TestCase):

    def test_text_pvg(self):
        pvg = PropertyValueGenerator('text', 3, False)
        self.assertEqual(len(pvg.getValue()),3)

    def test_number_pvg(self):
        pvg = PropertyValueGenerator('alphanumeric', 3, False)
        self.assertEqual(len(pvg.getValue()), 3)

    def test_number(self):
        pvg = PropertyValueGenerator('number', 3, False)
        self.assertEqual(len(pvg.getValue()), 3)
        self.assertTrue(isinstance(int(pvg.getValue()), int))




