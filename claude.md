## Coding Prompt: Multi-Object Tracking with CSRT in OpenCV-Python

### Overview
Build a Python application that performs simultaneous multi-object tracking on a video file using OpenCV's CSRT (Channel and Spatial Reliability Tracking) tracker. The application must support interactive bounding box selection on the first frame, real-time tracking visualization, and saving the output as an MP4 file.

---

### Requirements

**Dependencies:** `opencv-python`, `opencv-contrib-python` (required for CSRT tracker access via `cv2.TrackerCSRT_create()`).

---

### Functional Specifications

**1. Video Input**
- Accept a video file path as a command-line argument or via a hardcoded/configurable variable.
- Open the video using `cv2.VideoCapture`. If the video cannot be opened, print a clear error message and exit gracefully.
- Read and display the **first frame** of the video as the initialization frame.

**2. Bounding Box Selection (Initialization)**
- On the first frame, allow the user to draw multiple bounding boxes using OpenCV's `cv2.selectROI()` in a loop.
- After each bounding box is drawn, prompt the user (via terminal or on-screen text) whether they want to add another object or proceed to tracking.
  - Press **`S`** or **`Space`** to confirm a selection and add another.
  - Press **`Q`** or **`Enter`** to finish selection and begin tracking.
- Store all selected bounding boxes in a list.
- If no bounding box is selected, exit with an appropriate message.

**3. Tracker Initialization**
- For each bounding box in the list, create a new `cv2.TrackerCSRT_create()` instance.
- Initialize each tracker with the first frame and its corresponding bounding box.
- Store all tracker instances in a list, maintaining a 1-to-1 mapping with the bounding boxes and their assigned labels (e.g., `Object 1`, `Object 2`, ...).

**4. Real-Time Tracking Loop**
- Read frames from the video sequentially.
- For each frame, call `.update()` on every tracker instance.
- If a tracker successfully updates (`success=True`), draw a colored bounding box around the tracked object on the current frame using `cv2.rectangle()`.
  - Assign a distinct color to each tracked object (cycle through a predefined list of BGR colors).
  - Draw the object label (e.g., `Object 1`) above the bounding box using `cv2.putText()`.
- If a tracker fails (`success=False`), display the label as `Object N - Lost` in a visually distinct color (e.g., red) at the last known position or a fixed corner location.
- Display a frame counter and FPS overlay on each frame.

**5. Real-Time Display**
- Display each processed frame using `cv2.imshow()` in a window titled `"Multi-Object Tracking"`.
- Allow the user to press **`Q`** at any time during tracking to stop early.

**6. Video Output**
- Capture the video's original frame width, height, and FPS using `cv2.VideoCapture.get()`.
- Initialize a `cv2.VideoWriter` with the `mp4v` codec to save the output as `output_tracked.mp4` (or a configurable output path).
- Write every processed frame (with bounding boxes and labels drawn) to the VideoWriter.
- Release the VideoWriter when tracking ends or the video is complete.

---

### Code Structure

Organize the code with the following functions:

- `load_video(path)` — Opens video capture and returns the capture object and metadata (width, height, fps).
- `select_bounding_boxes(frame)` — Handles the interactive ROI selection loop and returns a list of bounding boxes.
- `initialize_trackers(frame, bboxes)` — Creates and initializes a CSRT tracker for each bounding box, returns a list of tracker objects.
- `draw_tracked_objects(frame, trackers, colors)` — Updates all trackers on the current frame and draws results; returns the annotated frame and a success status list.
- `run_tracking(cap, trackers, writer, colors)` — Main tracking loop: reads frames, calls draw, writes to output, and displays in real time.
- `main()` — Entry point that orchestrates the full pipeline.

---

### Edge Cases to Handle
- Video file not found or unreadable.
- User selects zero bounding boxes.
- One or more trackers losing the object mid-video (mark as lost, continue tracking others).
- Video ending before the user presses `Q`.
- Mismatch between display window size and actual frame size (resize display if frame is too large for screen).

---

### Expected Output
- A real-time window showing the video with color-coded bounding boxes and labels on all tracked objects.
- A saved file `output_tracked.mp4` in the working directory containing the full tracked video with all annotations.
- A terminal summary upon completion showing total frames processed and which objects were lost (if any).

---

### Testing
- Test the software using IR.mp4

### Notes for Implementation
- Use `opencv-contrib-python` and not just `opencv-python`, as CSRT is part of the contrib module.
- When calling `cv2.selectROI`, set `showCrosshair=True` and `fromCenter=False` for best UX.
- Consider using `cv2.selectROIs` (plural) as a built-in alternative to manual looping — it natively supports selecting multiple ROIs before returning.

---

This prompt should give you a complete and unambiguous spec to implement the software end-to-end. Let me know if you'd like me to generate the actual code instead.
