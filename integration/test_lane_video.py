import cv2
import time

from integration.lane_detection_hailo import LaneDetectionHailo


VIDEO_PATH = "/home/proyectomundial/Videos/hailo/Video_carro_2_h264.mp4"
HEF_PATH = "/usr/local/hailo/resources/models/hailo10h/ufld_v2_tu.hef"
OUTPUT_PATH = "/home/proyectomundial/Videos/hailo/lane_test_video_carro_2_60s.mp4"

MAX_FRAMES = 1800


def main():

    cap = cv2.VideoCapture(VIDEO_PATH)

    if not cap.isOpened():
        raise RuntimeError("No se pudo abrir el video")

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    input_fps = cap.get(cv2.CAP_PROP_FPS)

    print(f"VIDEO: {width}x{height} @ {input_fps:.2f} FPS")
    print(
        f"PRUEBA: {MAX_FRAMES} frames "
        f"(~{MAX_FRAMES / input_fps:.1f} segundos)"
    )

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")

    writer = cv2.VideoWriter(
        OUTPUT_PATH,
        fourcc,
        input_fps if input_fps > 0 else 30,
        (width, height),
    )

    if not writer.isOpened():
        cap.release()
        raise RuntimeError("No se pudo crear el video de salida")

    detector = LaneDetectionHailo(
        hef_path=HEF_PATH,
        original_frame_width=width,
        original_frame_height=height,
    )

    frame_count = 0
    frames_with_lanes = 0
    total_inference_time = 0.0

    start_time = time.perf_counter()

    try:

        while frame_count < MAX_FRAMES:

            ret, frame = cap.read()

            if not ret:
                print("Fin del video alcanzado.")
                break

            inference_start = time.perf_counter()

            lanes = detector.detect(frame)

            inference_time = time.perf_counter() - inference_start
            total_inference_time += inference_time

            if lanes:
                frames_with_lanes += 1

            for lane_index, lane in enumerate(lanes):

                if len(lane) < 2:
                    continue

                points = [
                    (int(x), int(y))
                    for x, y in lane
                ]

                for i in range(len(points) - 1):

                    cv2.line(
                        frame,
                        points[i],
                        points[i + 1],
                        (0, 255, 0),
                        5,
                        cv2.LINE_AA,
                    )

                cv2.putText(
                    frame,
                    f"Lane {lane_index + 1}",
                    points[0],
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (0, 255, 0),
                    2,
                    cv2.LINE_AA,
                )

            writer.write(frame)

            frame_count += 1

            if frame_count % 300 == 0:

                elapsed = time.perf_counter() - start_time
                processing_fps = frame_count / elapsed

                print(
                    f"Frames: {frame_count:4d} | "
                    f"Tiempo: {elapsed:6.1f}s | "
                    f"FPS procesamiento: {processing_fps:5.2f}"
                )

    finally:

        detector.close()
        cap.release()
        writer.release()

    total_time = time.perf_counter() - start_time

    print()
    print("========== RESULTADO ==========")
    print(f"Frames procesados:        {frame_count}")
    print(f"Frames con carriles:      {frames_with_lanes}")
    print(f"Tiempo total:             {total_time:.2f} s")

    if total_time > 0:
        print(
            f"FPS procesamiento:        "
            f"{frame_count / total_time:.2f}"
        )

    if frame_count > 0:
        print(
            f"Promedio inferencia:      "
            f"{(total_inference_time / frame_count) * 1000:.2f} ms/frame"
        )

    print()
    print("Video generado:")
    print(OUTPUT_PATH)


if __name__ == "__main__":
    main()
