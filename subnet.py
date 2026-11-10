"""Offline IPv4 subnet inventory review; no network access."""
import argparse
import ipaddress
import json
import sys
from pathlib import Path


def review(cidrs):
    if not isinstance(cidrs, list) or not 1 <= len(cidrs) <= 256:
        raise ValueError('Supply a list of 1 to 256 IPv4 CIDRs')
    networks = []
    for cidr in cidrs:
        if not isinstance(cidr, str) or '/' not in cidr:
            raise ValueError('Every entry must be an explicit IPv4 CIDR')
        net = ipaddress.IPv4Network(cidr, strict=True)
        if net in networks:
            raise ValueError('Duplicate subnet')
        networks.append(net)
    rows = []
    for net in networks:
        special = net.prefixlen >= 31
        rows.append({'cidr': str(net), 'netmask': str(net.netmask),
                     'first_host': str(net.network_address if special else net.network_address + 1),
                     'last_host': str(net.broadcast_address if special else net.broadcast_address - 1),
                     'host_count': net.num_addresses if special else net.num_addresses - 2,
                     'last_address': str(net.broadcast_address),
                     'semantics': 'point-to-point /31' if net.prefixlen == 31 else ('single host /32' if net.prefixlen == 32 else 'conventional subnet')})
    overlaps = [[str(a), str(b)] for i, a in enumerate(networks) for b in networks[i+1:] if a.overlaps(b)]
    return {'subnets': rows, 'overlaps': overlaps, 'status': 'OVERLAP' if overlaps else 'NO_OVERLAP_IN_INPUT'}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('inventory', type=Path, help='JSON array of CIDR strings')
    args = p.parse_args()
    try:
        result = review(json.loads(args.inventory.read_text(encoding='utf-8-sig')))
    except (ValueError, OSError) as exc:
        print(f'Input error: {exc}', file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 1 if result['overlaps'] else 0


if __name__ == '__main__': sys.exit(main())
