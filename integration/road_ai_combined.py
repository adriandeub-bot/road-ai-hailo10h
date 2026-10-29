"""
Road AI - Combined Vehicle + Lane Detection

Combines:
- YOLO vehicle detection on Hailo-10H
- Hailo tracker with persistent IDs
- UFLD v2 lane detection on Hailo-10H
- OpenCV visualization

The existing vehicle detection infrastructure is preserved.
"""

import cv2
import hailo

from hailo_apps.python.core.common.buffer_utils import (
    get_caps_from_pad,
    get_numpy_from_buffer,
)

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

from hailo_apps.python.core.common.hef_utils import (
    get_hef_labels_json,
)

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

from integration.vehicle_detection_hailo import VEHICLE_CLASSES

from integration.lane_detection_hailo import LaneDetectionHailo
from integration.traffic_sign_detection_hailo import TrafficSignDetectionHailo


LANE_HEF = (
    "/usr/local/hailo/resources/models/"
    "hailo10h/ufld_v2_tu.hef"
)

LANE_FRAME_WIDTH = 1920
LANE_FRAME_HEIGHT = 1080
SIGN_HEF = "/home/proyectomundial/hailo-apps/my_projects/traffic_sign_hailo10h/traffic_sign_detector.hef"
LANE_INFERENCE_INTERVAL = 5
SIGN_INFERENCE_INTERVAL = 10


class RoadAICombinedData(app_callback_class):
    """
    Runtime data for the combined Road AI pipeline.
    """

    def __init__(self):
        super().__init__()

        self.vehicles = []
        self.lane_detector = None
        self.last_lane_count = 0
        self.lane_frame_counter = 0
        self.last_lane_coordinates = None
        self.last_error = None
        self.sign_detector = None
        self.sign_detections = []
        self.sign_frame_counter = 0


def draw_lane_lines(frame, lane_coordinates):
    """
    Draw continuous lane lines returned by UFLD.
    """

    if lane_coordinates is None:
        return

    for lane in lane_coordinates:

        if lane is None or len(lane) < 2:
            continue

        points = []

        for point in lane:

            if point is None or len(point) < 2:
                continue

            x = int(point[0])
            y = int(point[1])

            if (
                0 <= x < frame.shape[1]
                and 0 <= y < frame.shape[0]
            ):
                points.append((x, y))

        if len(points) < 2:
            continue

        for p1, p2 in zip(
            points[:-1],
            points[1:],
        ):
            cv2.line(
                frame,
                p1,
                p2,
                (0, 255, 0),
                4,
                cv2.LINE_AA,
            )


def combined_callback(
    element,
    buffer,
    user_data,
):
    """
    Combined vehicle + lane callback.

    Vehicle detections come from Hailo metadata.

    The video frame is extracted from the same Gst.Buffer
    and passed to UFLD for lane detection.
    """

    if buffer is None:
        return

    # ---------------------------------------------------------------
    # Get video frame from the GStreamer buffer
    # ---------------------------------------------------------------

    pad = element.get_static_pad("src")

    if pad is None:
        return

    format, width, height = get_caps_from_pad(
        pad
    )

    if (
        format is None
        or width is None
        or height is None
    ):
        return

    frame = get_numpy_from_buffer(
        buffer,
        format,
        width,
        height,
    )

    if frame is None:
        return

    # Hailo Apps provides RGB frames.
    # Convert to BGR for OpenCV/UFLD.
    frame = cv2.cvtColor(
        frame,
        cv2.COLOR_RGB2BGR,
    )

    # ---------------------------------------------------------------
    # VEHICLE DETECTION + TRACKING
    # ---------------------------------------------------------------

    roi = hailo.get_roi_from_buffer(
        buffer
    )

    detections = roi.get_objects_typed(
        hailo.HAILO_DETECTION
    )

    

    vehicles = []

    for detection in detections:

        label = detection.get_label()

        if label not in VEHICLE_CLASSES:
            continue

        confidence = float(
            detection.get_confidence()
        )

        track_objects = (
            detection.get_objects_typed(
                hailo.HAILO_UNIQUE_ID
            )
        )

        track_id = None

        if len(track_objects) == 1:
            track_id = track_objects[0].get_id()

        bbox = detection.get_bbox()

        xmin = int(
            bbox.xmin() * width
        )
        ymin = int(
            bbox.ymin() * height
        )
        xmax = int(
            bbox.xmax() * width
        )
        ymax = int(
            bbox.ymax() * height
        )

        # Keep coordinates inside frame.
        xmin = max(
            0,
            min(xmin, width - 1)
        )
        ymin = max(
            0,
            min(ymin, height - 1)
        )
        xmax = max(
            0,
            min(xmax, width - 1)
        )
        ymax = max(
            0,
            min(ymax, height - 1)
        )

        vehicles.append(
            {
                "class_name": label,
                "confidence": confidence,
                "track_id": track_id,
                "bbox": bbox,
            }
        )

        # Vehicle bounding box
        cv2.rectangle(
            frame,
            (xmin, ymin),
            (xmax, ymax),
            (255, 0, 0),
            2,
        )

        if track_id is not None:
            text = (
                f"{label} "
                f"ID:{track_id} "
                f"{confidence:.2f}"
            )
        else:
            text = (
                f"{label} "
                f"{confidence:.2f}"
            )

        cv2.putText(
            frame,
            text,
            (
                xmin,
                max(25, ymin - 8),
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (255, 0, 0),
            2,
            cv2.LINE_AA,
        )

    user_data.vehicles = vehicles

    # ---------------------------------------------------------------
    # LANE DETECTION: inferir cada 5 fotogramas.
    user_data.lane_frame_counter += 1

    if (
        user_data.last_lane_coordinates is None
        or user_data.lane_frame_counter % LANE_INFERENCE_INTERVAL == 1
    ):
        try:
            user_data.last_lane_coordinates = (
                user_data.lane_detector.detect(frame)
            )
            user_data.last_lane_count = (
                len(user_data.last_lane_coordinates)
                if user_data.last_lane_coordinates is not None
                else 0
            )
        except Exception as e:
            error_text = str(e)
            if error_text != user_data.last_error:
                print(f"LANE ERROR: {error_text}")
                user_data.last_error = error_text

    if user_data.last_lane_coordinates is not None:
        draw_lane_lines(frame, user_data.last_lane_coordinates)

    # TRAFFIC SIGN DETECTION (run every few frames)
    # ---------------------------------------------------------------
    user_data.sign_frame_counter += 1
    if user_data.sign_frame_counter % SIGN_INFERENCE_INTERVAL == 1:
        try:
            user_data.sign_detections = user_data.sign_detector.detect(frame)
        except Exception as e:
            error_text = str(e)
            if error_text != user_data.last_error:
                print(f"SIGN ERROR: {error_text}")
                user_data.last_error = error_text

    for sign in user_data.sign_detections:
        x1, y1, x2, y2 = sign["bbox"]
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 165, 255), 2)
        label = f'{sign["class_name"]} {sign["confidence"]:.2f}'
        cv2.putText(
            frame, label, (x1, max(20, y1 - 7)),
            cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 165, 255), 2, cv2.LINE_AA
        )

    # ---------------------------------------------------------------
    # INFORMATION
    # ---------------------------------------------------------------

    vehicle_count = len(
        user_data.vehicles
    )

    cv2.putText(
        frame,
        f"Vehicles: {vehicle_count}",
        (30, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1.0,
        (0, 255, 255),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        f"Lanes: {user_data.last_lane_count}",
        (30, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (0, 255, 0),
        2,
        cv2.LINE_AA,
    )

    cv2.putText(
        frame,
        f"Frame: {user_data.get_count()}",
        (30, 115),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (255, 255, 255),
        2,
        cv2.LINE_AA,
    )

    # ---------------------------------------------------------------
    # Send processed BGR frame to OpenCV display process.
    # ---------------------------------------------------------------

    user_data.set_frame(
        frame
    )


class RoadAICombinedApp(GStreamerApp):
    """
    Hailo Apps application combining vehicle detection
    and UFLD lane detection.
    """

    def __init__(
        self,
        app_callback,
        user_data,
        parser=None,
    ):

        if parser is None:
            parser = get_pipeline_parser()

        parser.set_defaults(width=1920, height=1080)
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

        import threading

        self._shutdown_lock = threading.Lock()
        self.app_callback = app_callback
        self._shutdown_started = False

        # Force frame extraction/display because the
        # combined callback needs the actual video frame.
        self.options_menu.use_frame = True
        self.user_data.use_frame = True

        # -----------------------------------------------------------
        # Vehicle model configuration
        # -----------------------------------------------------------

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

        # -----------------------------------------------------------
        # Lane model
        # -----------------------------------------------------------

        self.lane_detector = LaneDetectionHailo(
            hef_path=LANE_HEF,
            original_frame_width=LANE_FRAME_WIDTH,
            original_frame_height=LANE_FRAME_HEIGHT,
        )

        self.user_data.lane_detector = (
            self.lane_detector
        )

        self.sign_detector = TrafficSignDetectionHailo(SIGN_HEF)
        self.user_data.sign_detector = self.sign_detector

        # Build GStreamer pipeline.
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

    def shutdown(
        self,
        signum=None,
        frame=None,
    ):
        # Solo una llamada puede iniciar el cierre.
        if not self._shutdown_lock.acquire(blocking=False):
            return

        try:
            if self._shutdown_started:
                return

            self._shutdown_started = True
        finally:
            self._shutdown_lock.release()
        print("\nShutting down Road AI...")

        # Detener GStreamer antes de liberar los modelos.
        try:
            super().shutdown(signum, frame)
        finally:
            if self.lane_detector is not None:
                try:
                    self.lane_detector.close()
                except Exception as e:
                    print(f"Error closing lane detector: {e}")
                finally:
                    self.lane_detector = None

            if self.sign_detector is not None:
                try:
                    self.sign_detector.close()
                except Exception as e:
                    print(f"Error closing sign detector: {e}")
                finally:
                    self.sign_detector = None


def main():

    user_data = RoadAICombinedData()

    app = RoadAICombinedApp(
        combined_callback,
        user_data,
    )

    app.run()


if __name__ == "__main__":
    main()
