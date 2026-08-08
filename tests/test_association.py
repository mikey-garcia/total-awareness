from total_awareness.fusion.association import angular_difference_deg, bearing_compatibility


def test_bearing_wraparound():
    assert angular_difference_deg(359.0, 1.0) == 2.0
    assert bearing_compatibility(10.0, 10.0) == 1.0
    assert bearing_compatibility(10.0, 90.0) < 0.01
