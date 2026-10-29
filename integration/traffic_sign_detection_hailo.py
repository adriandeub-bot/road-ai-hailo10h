"""Traffic-sign detector for Road AI using the existing Hailo-10H HEF."""

import cv2
import numpy as np
from hailo_platform import VDevice, FormatType, HailoSchedulingAlgorithm


CLASSES = [
    "Green Light", "Red Light", "Speed Limit 10",
    "Speed Limit 100", "Speed Limit 110", "Speed Limit 120",
    "Speed Limit 20", "Speed Limit 30", "Speed Limit 40",
    "Speed Limit 50", "Speed Limit 60", "Speed Limit 70",
    "Speed Limit 80", "Speed Limit 90", "Stop",
]

REG_MAX = 16
CONF_THRESHOLD = 0.05
NMS_THRESHOLD = 0.45
INPUT_SIZE = 640

SCALES = [
    ("traffic_sign_detector/conv51", "traffic_sign_detector/conv54", 8),
    ("traffic_sign_detector/conv62", "traffic_sign_detector/conv65", 16),
    ("traffic_sign_detector/conv77", "traffic_sign_detector/conv80", 32),
]


def sigmoid(x):
    x = np.clip(x, -80, 80)
    return 1.0 / (1.0 + np.exp(-x))


def decode_scale(reg, cls, stride):
    h, w, _ = reg.shape
    reg = reg.reshape(h, w, 4, REG_MAX)
    reg = reg - np.max(reg, axis=-1, keepdims=True)
    probs = np.exp(reg)
    probs /= np.sum(probs, axis=-1, keepdims=True) + 1e-9

    bins = np.arange(REG_MAX, dtype=np.float32)
    distances = np.sum(probs * bins, axis=-1) * stride
    scores = sigmoid(cls)

    yy, xx = np.meshgrid(np.arange(h), np.arange(w), indexing="ij")
    cx = (xx + 0.5) * stride
    cy = (yy + 0.5) * stride

    boxes = np.stack([
        cx - distances[:, :, 0],
        cy - distances[:, :, 1],
        cx + distances[:, :, 2],
        cy + distances[:, :, 3],
    ], axis=-1)

    class_ids = np.argmax(scores, axis=-1)
    confidence = np.max(scores, axis=-1)
    mask = confidence >= CONF_THRESHOLD

    return boxes[mask], confidence[mask], class_ids[mask]


def nms_per_class(boxes, scores, class_ids):
    kept = []

    for class_id in np.unique(class_ids):
        indices = np.where(class_ids == class_id)[0]
        indices = indices[np.argsort(scores[indices])[::-1]]

        while len(indices):
            current = indices[0]
            kept.append(current)
            rest = indices[1:]

            if not len(rest):
                break

            xx1 = np.maximum(boxes[current, 0], boxes[rest, 0])
            yy1 = np.maximum(boxes[current, 1], boxes[rest, 1])
            xx2 = np.minimum(boxes[current, 2], boxes[rest, 2])
            yy2 = np.minimum(boxes[current, 3], boxes[rest, 3])

            inter = np.maximum(0, xx2 - xx1) * np.maximum(0, yy2 - yy1)
            area_a = max(0, boxes[current, 2] - boxes[current, 0]) * max(
                0, boxes[current, 3] - boxes[current, 1]
            )
            area_b = np.maximum(0, boxes[rest, 2] - boxes[rest, 0]) * np.maximum(
                0, boxes[rest, 3] - boxes[rest, 1]
            )
            iou = inter / (area_a + area_b - inter + 1e-9)
            indices = rest[iou <= NMS_THRESHOLD]

    return kept


class TrafficSignDetectionHailo:
    """Persistent inference session for the 15-class traffic-sign HEF."""

    def __init__(self, hef_path):
        params = VDevice.create_params()
        params.scheduling_algorithm = HailoSchedulingAlgorithm.ROUND_ROBIN
        params.group_id = "SHARED"
        self.device = VDevice(params)
        self.model = self.device.create_infer_model(str(hef_path))
        self.model.input().set_format_type(FormatType.UINT8)

        for output in self.model.outputs:
            output.set_format_type(FormatType.FLOAT32)

        self.configured = self.model.configure()
        self.bindings = self.configured.create_bindings()
        self.output_buffers = {}

        for name in self.model.output_names:
            shape = tuple(self.model.output(name).shape)
            self.output_buffers[name] = np.empty(shape, dtype=np.float32)
            self.bindings.output(name).set_buffer(self.output_buffers[name])

        self._frame_number = 0

    def detect(self, frame):
        """Accept a BGR frame and return detections in original-frame pixels."""
        height, width = frame.shape[:2]

        scale = min(INPUT_SIZE / width, INPUT_SIZE / height)
        resized_w = round(width * scale)
        resized_h = round(height * scale)

        resized = cv2.resize(frame, (resized_w, resized_h))
        rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)

        pad_x = (INPUT_SIZE - resized_w) // 2
        pad_y = (INPUT_SIZE - resized_h) // 2

        input_image = np.full(
            (INPUT_SIZE, INPUT_SIZE, 3), 114, dtype=np.uint8
        )
        input_image[
            pad_y:pad_y + resized_h,
            pad_x:pad_x + resized_w
        ] = rgb

        self.bindings.input().set_buffer(input_image[None, ...])
        self.configured.run([self.bindings], timeout=10000)

        all_boxes, all_scores, all_classes = [], [], []

        for reg_name, cls_name, stride in SCALES:
            reg = np.asarray(
                self.bindings.output(reg_name).get_buffer()
            ).reshape(-1, 64) if False else np.asarray(
                self.bindings.output(reg_name).get_buffer()
            )
            cls = np.asarray(
                self.bindings.output(cls_name).get_buffer()
            )

            # Remove a possible batch dimension.
            reg = np.squeeze(reg)
            cls = np.squeeze(cls)

            boxes, scores, class_ids = decode_scale(reg, cls, stride)
            if len(boxes):
                all_boxes.append(boxes)
                all_scores.append(scores)
                all_classes.append(class_ids)

        if not all_boxes:
            return []

        boxes = np.concatenate(all_boxes)
        scores = np.concatenate(all_scores)
        class_ids = np.concatenate(all_classes)

        boxes[:, [0, 2]] = np.clip(boxes[:, [0, 2]], 0, INPUT_SIZE)
        boxes[:, [1, 3]] = np.clip(boxes[:, [1, 3]], 0, INPUT_SIZE)

        detections = []

        for i in nms_per_class(boxes, scores, class_ids):
            x1, y1, x2, y2 = boxes[i]

            # Undo letterbox padding and scaling.
            x1 = np.clip((x1 - pad_x) / scale, 0, width - 1)
            x2 = np.clip((x2 - pad_x) / scale, 0, width - 1)
            y1 = np.clip((y1 - pad_y) / scale, 0, height - 1)
            y2 = np.clip((y2 - pad_y) / scale, 0, height - 1)

            if x2 <= x1 or y2 <= y1:
                continue

            detections.append({
                "class_name": CLASSES[int(class_ids[i])],
                "confidence": float(scores[i]),
                "bbox": (int(x1), int(y1), int(x2), int(y2)),
            })

        return detections

    def close(self):
        """Release inference bindings before shutting down the device."""
        bindings = self.bindings
        self.bindings = None
        self.output_buffers = None
        bindings = None

        configured = self.configured
        self.configured = None

        try:
            if configured is not None:
                configured.shutdown()
        finally:
            configured = None
            self.model = None

            device = self.device
            self.device = None
            if device is not None:
                device.release()
