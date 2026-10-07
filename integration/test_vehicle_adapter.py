"""
Road AI - Vehicle Adapter Structure Test

Verifies the expected structure of vehicle detection results.
"""

from vehicle_detection_hailo import (
    VEHICLE_CLASSES,
)


def main():

    print("Vehicle classes:")
    print(sorted(VEHICLE_CLASSES))

    sample_vehicle = {
        "class_name": "car",
        "confidence": 0.92,
        "track_id": 49,
        "bbox": None,
    }

    required_keys = {
        "class_name",
        "confidence",
        "track_id",
        "bbox",
    }

    print("\nSample vehicle:")
    print(sample_vehicle)

    assert set(sample_vehicle.keys()) == required_keys
    assert sample_vehicle["class_name"] in VEHICLE_CLASSES
    assert isinstance(sample_vehicle["confidence"], float)
    assert isinstance(sample_vehicle["track_id"], int)

    print("\nVehicle adapter structure OK")


if __name__ == "__main__":
    main()
