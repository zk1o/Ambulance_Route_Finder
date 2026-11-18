"""Automated checks:  python -m unittest discover -s tests -v"""
import os, sys, unittest
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from data.network_data import NODES_COORDINATES, ROADS_NETWORK, TRAFFIC_MULTIPLIERS
from src.utils import build_graph, calculate_heuristic
from src.algorithms import ucs_search, a_star_search, bfs_search
from src.engine import (solve_emergency_routing, compare_nearest_vs_fastest_hospital,
                        AVAILABLE_HOSPITALS, RoutingInputError)


class Requirements(unittest.TestCase):
    def test_network_size(self):
        self.assertGreaterEqual(len(NODES_COORDINATES), 20)
        self.assertGreaterEqual(len(AVAILABLE_HOSPITALS), 3)
        self.assertTrue(any(r[4] for r in ROADS_NETWORK))  # priority lanes exist

    def test_astar_equals_ucs_everywhere_and_heuristic_admissible(self):
        for t in TRAFFIC_MULTIPLIERS:
            g = build_graph(traffic_condition=t)
            for s in NODES_COORDINATES:
                for d in NODES_COORDINATES:
                    if s == d:
                        continue
                    u, a = ucs_search(g, s, d), a_star_search(g, s, d)
                    self.assertAlmostEqual(u[2], a[2], places=9, msg=f"{t} {s}->{d}")
                    self.assertLessEqual(calculate_heuristic(s, d), u[2] + 1e-9)

    def test_bfs_finds_fewest_hops(self):
        g = build_graph(traffic_condition='Low')
        self.assertLessEqual(len(bfs_search(g, 'Ambulance_Base', 'Hospital_C')[0]),
                             len(ucs_search(g, 'Ambulance_Base', 'Hospital_C')[0]))

    def test_traffic_changes_hospital_choice(self):
        low = solve_emergency_routing(traffic_condition='Low')['selected_hospital']
        heavy = solve_emergency_routing(traffic_condition='Heavy')['selected_hospital']
        self.assertNotEqual(low, heavy)

    def test_nearest_differs_from_fastest_in_heavy(self):
        self.assertFalse(compare_nearest_vs_fastest_hospital(traffic_condition='Heavy')['are_identical'])
        self.assertTrue(compare_nearest_vs_fastest_hospital(traffic_condition='Low')['are_identical'])

    def test_blocked_road_reroutes_and_costs_more(self):
        a = solve_emergency_routing(traffic_condition='Medium')
        b = solve_emergency_routing(traffic_condition='Medium', blocked_roads=[('Node_3', 'Emergency_Site')])
        self.assertNotIn('Node_3 -> Emergency_Site', ' -> '.join(b['phase1']['path']))
        self.assertGreater(b['total_time_min'], a['total_time_min'])

    def test_fully_blocked_site_reports_failure(self):
        blocked = [('Node_3', 'Emergency_Site'), ('Node_4', 'Emergency_Site'),
                   ('Emergency_Site', 'Node_8'), ('Emergency_Site', 'Node_15')]
        self.assertFalse(solve_emergency_routing(blocked_roads=blocked)['success'])

    def test_manual_hospital_and_invalid_inputs(self):
        self.assertEqual(solve_emergency_routing(selected_hospital='Hospital_C')['selected_hospital'], 'Hospital_C')
        with self.assertRaises(RoutingInputError):
            solve_emergency_routing(emergency_site='Nowhere')
        with self.assertRaises(RoutingInputError):
            solve_emergency_routing(traffic_condition='Extreme')


if __name__ == '__main__':
    unittest.main()
