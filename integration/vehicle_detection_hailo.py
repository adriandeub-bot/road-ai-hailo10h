"""
Road AI - Hailo-10H Vehicle Detection Adapter

Provides a reusable adapter for extracting vehicle detections
and tracking IDs from a Hailo ROI.
"""

import hailo


VEHICLE_CLASSES = {
    "car",
    "bus",
    "truck",
}


class VehicleDetectionCallbackData:
    """
    Stores the latest vehicle detections.
    """

    def __init__(self):
        self.vehicles = []


def process_detections(buffer, user_data=None):
    """
    Extract vehicle detections and tracking IDs from a Hailo buffer.

    Parameters
    ----------
    buffer:
        Hailo/GStreamer buffer containing detection metadata.

    user_data:
        Optional object used to store the latest detections.

    Returns
    -------
    list
        List of vehicle dictionaries.
    """

    if buffer is None:
        return []

    roi = hailo.get_roi_from_buffer(buffer)

    detections = roi.get_objects_typed(
        hailo.HAILO_DETECTION
    )

    vehicles = []

    for detection in detections:

        label = detection.get_label()

        if label not in VEHICLE_CLASSES:
            continue

        confidence = detection.get_confidence()

        track_objects = detection.get_objects_typed(
            hailo.HAILO_UNIQUE_ID
        )

        track_id = None

        if len(track_objects) == 1:
            track_id = track_objects[0].get_id()

        bbox = detection.get_bbox()

        vehicles.append(
            {
                "class_name": label,
                "confidence": float(confidence),
                "track_id": track_id,
                "bbox": bbox,
            }
        )

    if user_data is not None:
        user_data.vehicles = vehicles

    return vehicles
