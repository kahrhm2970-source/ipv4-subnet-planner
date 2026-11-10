import unittest
from subnet import review

class SubnetTests(unittest.TestCase):
    def test_24(self):
        r = review(['192.0.2.0/24'])['subnets'][0]
        self.assertEqual((r['first_host'], r['last_host'], r['host_count']), ('192.0.2.1', '192.0.2.254', 254))
    def test_30(self): self.assertEqual(review(['192.0.2.0/30'])['subnets'][0]['host_count'], 2)
    def test_31(self):
        r = review(['192.0.2.0/31'])['subnets'][0]
        self.assertEqual((r['first_host'], r['last_host'], r['host_count']), ('192.0.2.0', '192.0.2.1', 2))
    def test_32(self): self.assertEqual(review(['192.0.2.1/32'])['subnets'][0]['host_count'], 1)
    def test_zero(self): self.assertEqual(review(['0.0.0.0/0'])['subnets'][0]['host_count'], 4294967294)
    def test_overlap(self): self.assertEqual(review(['192.0.2.0/24', '192.0.2.128/25'])['overlaps'], [['192.0.2.0/24', '192.0.2.128/25']])
    def test_adjacent(self): self.assertFalse(review(['192.0.2.0/25', '192.0.2.128/25'])['overlaps'])
    def test_invalid(self):
        for item in ['192.0.2.1/24', '::/64', '192.0.2.0', '999.0.0.0/24', None]:
            with self.subTest(item=item), self.assertRaises(ValueError): review([item])
    def test_duplicate(self):
        with self.assertRaises(ValueError): review(['192.0.2.0/24'] * 2)
    def test_shape(self):
        for data in [[], {}, None, ['192.0.2.0/24']*257]:
            with self.subTest(data=type(data)), self.assertRaises(ValueError): review(data)

if __name__ == '__main__': unittest.main()
