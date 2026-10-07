"""
Road AI - Vehicle Detection Hailo Integration Test

Tests the Hailo-10H vehicle detection and tracking pipeline
using the existing Hailo Apps infrastructure.
"""

import hailo

from hailo_apps.python.core.common.core import (
    get_pipeline_parser,
    get_resource_path,
    handle_list_models_flag,
    resolve_hef_path,
)

from hailo_apps.python.core.common.defines import (
    DETECTION_PIPELINE,
    DETECTION_POSTPROCESS_FUNCTION,
    DETECTION_POSTPROCESS_SO_FILENAME,
    RESOURCES_SO_DIR_NAME,
)

from hailo_apps.python.core.common.hef_utils import get_hef_labels_json
from hailo_apps.python.core.gstreamer.gstreamer_app import (
    GStreamerApp,
    app_callback_class,
)

from hailo_apps.python.core.gstreamer.gstreamer_helper_pipelines import (
    DISPLAY_PIPELINE,
    INFERENCE_PIPELINE,
    INFERENCE_PIPELINE_WRAPPER,
    TRACKER_PIPELINE,
    USER_CALLBACK_PIPELINE,
)

from vehicle_detection_hailo import (
    VEHICLE_CLASSES,
)


class VehicleTestCallback(app_callback_class):

    def __init__(self):
        super().__init__()
        self.last_frame = -1


def vehicle_callback(element, buffer, user_data):

    if buffer is None:
        return

    roi = hailo.get_roi_from_buffer(buffer)

    detections = roi.get_objects_typed(
        hailo.HAILO_DETECTION
    )

    frame_number = user_data.get_count()

    if frame_number == user_data.last_frame:
        return

    user_data.last_frame = frame_number

    print(f"\nFrame {frame_number}:")

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

        print(
            f"  {label:6s} "
            f"ID={track_id:<4} "
            f"confidence={confidence:.2f}"
        )


class RoadAIVehicleTestApp(GStreamerApp):

    def __init__(
        self,
        app_callback,
        user_data,
        parser=None,
    ):

        if parser is None:
            parser = get_pipeline_parser()

        parser.add_argument(
            "--labels-json",
            default=None,
            help="Path to custom labels JSON file",
        )

        handle_list_models_flag(
            parser,
            DETECTION_PIPELINE,
        )

        super().__init__(
            parser,
            user_data,
        )

        self.app_callback = app_callback

        if self.batch_size == 1:
            self.batch_size = 2

        nms_score_threshold = 0.3
        nms_iou_threshold = 0.45

        self.hef_path = resolve_hef_path(
            self.hef_path,
            app_name=DETECTION_PIPELINE,
            arch=self.arch,
        )

        self.post_process_so = get_resource_path(
            DETECTION_PIPELINE,
            RESOURCES_SO_DIR_NAME,
            self.arch,
            DETECTION_POSTPROCESS_SO_FILENAME,
        )

        self.post_function_name = (
            DETECTION_POSTPROCESS_FUNCTION
        )

        self.labels_json = (
            self.options_menu.labels_json
        )

        if self.labels_json is None:
            self.labels_json = get_hef_labels_json(
                self.hef_path
            )

        self.thresholds_str = (
            f"nms-score-threshold={nms_score_threshold} "
            f"nms-iou-threshold={nms_iou_threshold} "
            f"output-format-type=HAILO_FORMAT_TYPE_FLOAT32"
        )

        self.create_pipeline()

    def get_pipeline_string(self):

        source_pipeline = (
            self.get_source_pipeline()
        )

        detection_pipeline = INFERENCE_PIPELINE(
            hef_path=self.hef_path,
            post_process_so=self.post_process_so,
            post_function_name=self.post_function_name,
            batch_size=self.batch_size,
            config_json=self.labels_json,
            additional_params=self.thresholds_str,
        )

        detection_pipeline_wrapper = (
            INFERENCE_PIPELINE_WRAPPER(
                detection_pipeline
            )
        )

        tracker_pipeline = TRACKER_PIPELINE(
            class_id=-1,
            keep_past_metadata=True,
        )

        user_callback_pipeline = (
            USER_CALLBACK_PIPELINE()
        )

        display_pipeline = DISPLAY_PIPELINE(
            video_sink=self.video_sink,
            sync=self.sync,
            show_fps=self.show_fps,
        )

        return (
            f"{source_pipeline} ! "
            f"{detection_pipeline_wrapper} ! "
            f"{tracker_pipeline} ! "
            f"{user_callback_pipeline} ! "
            f"{display_pipeline}"
        )


def main():

    user_data = VehicleTestCallback()

    app = RoadAIVehicleTestApp(
        vehicle_callback,
        user_data,
    )

    app.run()


if __name__ == "__main__":
    main()
