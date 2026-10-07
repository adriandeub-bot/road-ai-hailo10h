"""
Road AI - Integrated Pipeline

Base pipeline for combining:
- Vehicle detection
- Lane detection
- Traffic sign detection

This first version only handles:
1. Reading a video frame by frame.
2. Drawing basic information on the frames.
3. Saving the processed video.

The AI modules will be integrated incrementally.
"""

import argparse
import cv2
import os
import time


def parse_args():
    parser = argparse.ArgumentParser(
        description="Road AI integrated pipeline"
    )

    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Path to the input video."
    )

    parser.add_argument(
        "--output",
        "-o",
        default="results/road_ai_output.mp4",
        help="Path to the output video."
    )

    return parser.parse_args()


def main():
    args = parse_args()

    # Check input video
    if not os.path.isfile(args.input):
        raise FileNotFoundError(
            f"Input video not found: {args.input}"
        )

    # Create output directory
    output_dir = os.path.dirname(args.output)

    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    # Open input video
    cap = cv2.VideoCapture(args.input)

    if not cap.isOpened():
        raise RuntimeError(
            f"Could not open input video: {args.input}"
        )

    # Get video properties
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))

    if fps <= 0:
        fps = 30.0

    print("Road AI - Integrated Pipeline")
    print("--------------------------------")
    print(f"Input:        {args.input}")
    print(f"Resolution:   {width}x{height}")
    print(f"FPS:          {fps:.2f}")
    print(f"Frames:       {total_frames}")
    print(f"Output:       {args.output}")
    print("--------------------------------")

    # MP4 output using H.264-compatible codec when available.
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    writer = cv2.VideoWriter(
        args.output,
        fourcc,
        fps,
        (width, height)
    )

    if not writer.isOpened():
        cap.release()
        raise RuntimeError(
            f"Could not create output video: {args.output}"
        )

    frame_count = 0
    start_time = time.time()

    try:
        while True:
            ret, frame = cap.read()

            if not ret:
                break

            frame_count += 1

            # ---------------------------------------------------------
            # AI MODULES WILL BE ADDED HERE
            # ---------------------------------------------------------

            # Temporary information overlay
            cv2.putText(
                frame,
                "Road AI Pipeline",
                (30, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 0),
                2,
                cv2.LINE_AA
            )

            cv2.putText(
                frame,
                f"Frame: {frame_count}/{total_frames}",
                (30, 80),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.7,
                (255, 255, 255),
                2,
                cv2.LINE_AA
            )

            writer.write(frame)

    except KeyboardInterrupt:
        print("\nProcessing interrupted by user.")

    finally:
        cap.release()
        writer.release()

    elapsed = time.time() - start_time

    if elapsed > 0:
        processing_fps = frame_count / elapsed
    else:
        processing_fps = 0.0

    print()
    print("Processing finished.")
    print(f"Frames processed: {frame_count}")
    print(f"Elapsed time:     {elapsed:.2f} s")
    print(f"Processing FPS:   {processing_fps:.2f}")
    print(f"Output saved to:  {args.output}")


if __name__ == "__main__":
    main()