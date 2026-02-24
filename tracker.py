"""
Multi-Object Tracking with CSRT in OpenCV-Python

Performs simultaneous multi-object tracking on a video file using OpenCV's
CSRT tracker with interactive bounding box selection, real-time visualization,
and MP4 output.
"""

import sys
import time

import cv2

# Predefined list of distinct BGR colors for tracked objects
COLORS = [
    (255, 0, 0),     # Blue
    (0, 255, 0),     # Green
    (0, 255, 255),   # Yellow
    (255, 0, 255),   # Magenta
    (255, 255, 0),   # Cyan
    (0, 165, 255),   # Orange
    (147, 20, 255),  # Pink
    (0, 128, 0),     # Dark Green
]

LOST_COLOR = (0, 0, 255)  # Red for lost objects

# Maximum display dimensions for resizing large frames
MAX_DISPLAY_WIDTH = 1280
MAX_DISPLAY_HEIGHT = 720


def load_video(path):
    """Opens video capture and returns the capture object and metadata.

    Args:
        path: Path to the video file.

    Returns:
        Tuple of (cv2.VideoCapture, dict) where dict contains 'width',
        'height', and 'fps'.

    Raises:
        SystemExit: If the video cannot be opened.
    """
    cap = cv2.VideoCapture(path)
    if not cap.isOpened():
        print(f"Error: Cannot open video file '{path}'")
        sys.exit(1)

    metadata = {
        "width": int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
        "height": int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
        "fps": cap.get(cv2.CAP_PROP_FPS),
    }

    if metadata["fps"] <= 0:
        metadata["fps"] = 30.0

    return cap, metadata


def select_bounding_boxes(frame, start_index=0, allow_empty=False):
    """Handles interactive ROI selection and returns a list of bounding boxes.

    Uses cv2.selectROI in a loop. The user can:
    - Draw a bounding box and press SPACE/ENTER to confirm it.
    - Press 'q' to finish selection and begin tracking.
    - Press ESC to cancel the current selection.

    Args:
        frame: The video frame to select objects on (numpy array).
        start_index: Starting object number for labeling (0-based). Used when
            adding objects mid-tracking so labels continue from existing count.
        allow_empty: If True, return an empty list instead of exiting when no
            bounding boxes are selected. Used for mid-tracking additions.

    Returns:
        List of bounding boxes as (x, y, w, h) tuples.

    Raises:
        SystemExit: If no bounding boxes are selected and allow_empty is False.
    """
    bboxes = []
    window_name = "Select Objects - SPACE/ENTER to confirm, Q to finish, ESC to cancel"

    print("\n--- Bounding Box Selection ---")
    print("Draw a bounding box around each object you want to track.")
    print("  SPACE/ENTER : Confirm selection and add another")
    print("  ESC         : Cancel current selection")
    print("  Q           : Finish selection and begin tracking")
    print()

    while True:
        display = frame.copy()

        # Draw already-selected boxes on the display
        for i, bbox in enumerate(bboxes):
            obj_num = start_index + i + 1
            x, y, w, h = [int(v) for v in bbox]
            color = COLORS[(start_index + i) % len(COLORS)]
            cv2.rectangle(display, (x, y), (x + w, y + h), color, 2)
            cv2.putText(
                display,
                f"Object {obj_num}",
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2,
            )

        count = len(bboxes)
        next_num = start_index + count + 1
        print(f"Select object {next_num} (or press Q to start tracking with {count} new object(s))...")

        bbox = cv2.selectROI(
            window_name,
            display,
            fromCenter=False,
            showCrosshair=True,
        )

        # selectROI returns (0, 0, 0, 0) if cancelled with ESC or Q
        if bbox == (0, 0, 0, 0):
            # User cancelled / wants to finish
            break

        bboxes.append(bbox)
        obj_num = start_index + len(bboxes)
        print(f"  Added Object {obj_num}: bbox={bbox}")

    cv2.destroyWindow(window_name)

    if not bboxes and not allow_empty:
        print("Error: No bounding boxes selected. Exiting.")
        sys.exit(1)

    print(f"\n{len(bboxes)} object(s) selected for tracking.\n")
    return bboxes


def initialize_trackers(frame, bboxes, start_index=0):
    """Creates and initializes a CSRT tracker for each bounding box.

    Args:
        frame: The video frame to initialize trackers on (numpy array).
        bboxes: List of bounding boxes as (x, y, w, h) tuples.
        start_index: Starting object number for labeling (0-based). Used when
            adding trackers mid-tracking so labels continue from existing count.

    Returns:
        List of initialized cv2.TrackerCSRT instances.
    """
    trackers = []
    for i, bbox in enumerate(bboxes):
        tracker = cv2.TrackerCSRT_create()
        tracker.init(frame, bbox)
        trackers.append(tracker)
        print(f"  Tracker initialized for Object {start_index + i + 1}")

    return trackers


def draw_tracked_objects(frame, trackers, colors, last_known_positions):
    """Updates all trackers on the current frame and draws results.

    Args:
        frame: The current video frame (numpy array).
        trackers: List of cv2.TrackerCSRT instances.
        colors: List of BGR color tuples.
        last_known_positions: List of last known (x, y) for each tracker,
            updated in place.

    Returns:
        Tuple of (annotated_frame, success_list) where success_list is a
        list of booleans indicating which trackers succeeded.
    """
    success_list = []
    annotated = frame.copy()

    for i, tracker in enumerate(trackers):
        success, bbox = tracker.update(frame)
        success_list.append(success)
        color = colors[i % len(colors)]
        label = f"Object {i + 1}"

        if success:
            x, y, w, h = [int(v) for v in bbox]
            last_known_positions[i] = (x, y)
            cv2.rectangle(annotated, (x, y), (x + w, y + h), color, 2)
            cv2.putText(
                annotated,
                label,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                color,
                2,
            )
        else:
            lost_label = f"{label} - Lost"
            lx, ly = last_known_positions[i]
            cv2.putText(
                annotated,
                lost_label,
                (lx, ly - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                LOST_COLOR,
                2,
            )

    return annotated, success_list


def run_tracking(cap, trackers, writer, colors, metadata):
    """Main tracking loop: reads frames, updates trackers, writes output.

    Press P to pause tracking, select additional bounding boxes, and resume.
    Press Q to stop tracking early.

    Args:
        cap: cv2.VideoCapture object.
        trackers: List of initialized tracker instances.
        writer: cv2.VideoWriter for output file.
        colors: List of BGR color tuples.
        metadata: Dict with video metadata (width, height, fps).
    """
    frame_count = 0
    fps_display = 0.0
    lost_objects = set()

    # Track last known positions for lost object labels
    last_known_positions = [(0, 0)] * len(trackers)

    # Calculate display scale if frame is too large
    fw, fh = metadata["width"], metadata["height"]
    scale = min(MAX_DISPLAY_WIDTH / fw, MAX_DISPLAY_HEIGHT / fh, 1.0)

    print("--- Tracking Started ---")
    print("Press P to pause and add new objects.")
    print("Press Q to stop tracking early.\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        frame_count += 1
        start_time = time.time()

        # Update trackers and draw
        annotated, success_list = draw_tracked_objects(
            frame, trackers, colors, last_known_positions
        )

        # Track lost objects
        for i, success in enumerate(success_list):
            if not success:
                lost_objects.add(i + 1)

        # Calculate FPS
        elapsed = time.time() - start_time
        if elapsed > 0:
            fps_display = 1.0 / elapsed

        # Draw frame counter and FPS overlay
        info_text = f"Frame: {frame_count} | FPS: {fps_display:.1f} | Objects: {len(trackers)}"
        cv2.putText(
            annotated,
            info_text,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2,
        )

        # Draw pause hint
        cv2.putText(
            annotated,
            "P: Pause & Add Objects | Q: Quit",
            (10, fh - 15),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (200, 200, 200),
            1,
        )

        # Write frame to output
        writer.write(annotated)

        # Display frame (resize if needed)
        if scale < 1.0:
            display_w = int(fw * scale)
            display_h = int(fh * scale)
            display_frame = cv2.resize(annotated, (display_w, display_h))
        else:
            display_frame = annotated

        cv2.imshow("Multi-Object Tracking", display_frame)

        # Check for key presses
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q") or key == ord("Q"):
            print("Tracking stopped by user.")
            break
        elif key == ord("p") or key == ord("P"):
            # Pause tracking and allow new bounding box selection
            print(f"\n--- Paused at frame {frame_count} ---")
            print(f"Currently tracking {len(trackers)} object(s).")
            print("Select additional objects on the current frame.\n")

            cv2.destroyWindow("Multi-Object Tracking")

            new_bboxes = select_bounding_boxes(
                frame,
                start_index=len(trackers),
                allow_empty=True,
            )

            if new_bboxes:
                new_trackers = initialize_trackers(frame, new_bboxes,
                                                   start_index=len(trackers))
                trackers.extend(new_trackers)
                last_known_positions.extend(
                    [(int(b[0]), int(b[1])) for b in new_bboxes]
                )
                print(f"Now tracking {len(trackers)} object(s) total.")
            else:
                print("No new objects added.")

            print("\n--- Resuming Tracking ---\n")

    cv2.destroyAllWindows()

    # Print summary
    print("\n--- Tracking Summary ---")
    print(f"Total frames processed: {frame_count}")
    print(f"Total objects tracked: {len(trackers)}")
    if lost_objects:
        lost_names = ", ".join(f"Object {n}" for n in sorted(lost_objects))
        print(f"Objects lost during tracking: {lost_names}")
    else:
        print("All objects tracked successfully throughout the video.")
    print()


def main():
    """Entry point that orchestrates the full tracking pipeline."""
    # Determine video path from command-line argument or default
    if len(sys.argv) > 1:
        video_path = sys.argv[1]
    else:
        video_path = "IR.mp4"

    output_path = "output_tracked.mp4"

    print(f"Loading video: {video_path}")
    cap, metadata = load_video(video_path)
    print(f"Video loaded: {metadata['width']}x{metadata['height']} @ {metadata['fps']:.1f} FPS\n")

    # Read the first frame
    ret, first_frame = cap.read()
    if not ret:
        print("Error: Cannot read the first frame from the video.")
        cap.release()
        sys.exit(1)

    # Select bounding boxes interactively
    bboxes = select_bounding_boxes(first_frame)

    # Initialize trackers
    print("Initializing CSRT trackers...")
    trackers = initialize_trackers(first_frame, bboxes)
    print()

    # Initialize video writer
    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    writer = cv2.VideoWriter(
        output_path,
        fourcc,
        metadata["fps"],
        (metadata["width"], metadata["height"]),
    )

    if not writer.isOpened():
        print(f"Error: Cannot create output video file '{output_path}'")
        cap.release()
        sys.exit(1)

    # Reset video to beginning since we read the first frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    # Run the tracking loop
    run_tracking(cap, trackers, writer, COLORS, metadata)

    # Cleanup
    writer.release()
    cap.release()
    print(f"Output saved to: {output_path}")


if __name__ == "__main__":
    main()
