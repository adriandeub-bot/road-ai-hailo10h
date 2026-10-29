"""
Road AI - Hailo-10H Lane Detection Adapter

Reusable UFLD v2 lane-detection adapter for the Road AI pipeline.

This module does not read or write video files. It receives frames,
runs UFLD v2 inference on the Hailo-10H accelerator, and returns
lane coordinates.
"""

import numpy as np

from hailo_apps.python.core.common.hailo_inference import HailoInfer

from lane_detection.lane_detection_utils import UFLDProcessing


class LaneDetectionHailo:
    """Reusable UFLD v2 lane detector running on Hailo-10H."""

    def __init__(
        self,
        hef_path: str,
        original_frame_width: int,
        original_frame_height: int,
    ) -> None:
        self.hef_path = hef_path

        self.ufld_processing = UFLDProcessing(
            num_cell_row=100,
            num_cell_col=100,
            num_row=56,
            num_col=41,
            num_lanes=4,
            crop_ratio=0.8,
            original_frame_width=original_frame_width,
            original_frame_height=original_frame_height,
            total_frames=0,
        )

        self.inference = HailoInfer(
            hef_path,
            batch_size=1,
            output_type="FLOAT32",
        )

        self.input_height, self.input_width, _ = self.inference.get_input_shape()

    def preprocess(self, frame: np.ndarray) -> np.ndarray:
        """Prepare one BGR frame for UFLD inference."""
        return self.ufld_processing.resize(
            frame,
            self.input_height,
            self.input_width,
        )

    def _inference_callback(
        self,
        completion_info,
        bindings_list,
    ) -> None:
        """Store asynchronous inference results."""
        if completion_info.exception:
            self._inference_error = completion_info.exception
            return

        self._inference_results = []

        for bindings in bindings_list:
            if len(bindings._output_names) == 1:
                result = bindings.output().get_buffer()
            else:
                result = {
                    name: np.expand_dims(
                        bindings.output(name).get_buffer(),
                        axis=0,
                    )
                    for name in bindings._output_names
                }

            self._inference_results.append(result)

    def detect(self, frame: np.ndarray):
        """
        Run UFLD inference on one frame.

        Returns:
            List of lanes, where each lane contains (x, y) coordinates.
        """
        resized_frame = self.preprocess(frame)

        self._inference_results = []
        self._inference_error = None

        job = self.inference.run(
            [resized_frame],
            self._inference_callback,
        )

        job.wait(10000)

        if self._inference_error is not None:
            raise RuntimeError(
                f"UFLD inference failed: {self._inference_error}"
            )

        if not self._inference_results:
            raise RuntimeError("UFLD inference returned no results")

        result = self._inference_results[0]

        if isinstance(result, dict):
            slices = list(result.values())
        else:
            slices = [result]

        output_tensor = np.concatenate(slices, axis=1)

        return self.ufld_processing.get_coordinates(output_tensor)

    def close(self) -> None:
        """Release the Hailo inference resources."""
        self.inference.close()
