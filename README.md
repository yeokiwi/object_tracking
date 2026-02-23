# Multi-Object Tracking with CSRT

A Python application that performs simultaneous multi-object tracking on video files using OpenCV's CSRT (Channel and Spatial Reliability Tracking) algorithm. It supports interactive bounding box selection on the first frame, real-time tracking visualization with color-coded labels, and saves the annotated output as an MP4 file.

## Features

- **Interactive object selection** - Draw bounding boxes on the first frame to select objects to track
- **Multi-object tracking** - Track multiple objects simultaneously using individual CSRT tracker instances
- **Color-coded visualization** - Each tracked object gets a distinct color for its bounding box and label
- **Lost object detection** - Objects that can no longer be tracked are marked as "Lost" in red
- **FPS and frame counter overlay** - Real-time performance metrics displayed on each frame
- **MP4 output** - Saves the full annotated video to `output_tracked.mp4`
- **Auto-resizing display** - Large frames are scaled down to fit the screen during playback
- **Terminal summary** - Prints total frames processed and which objects were lost when tracking completes

## Requirements

- Python 3.8+
- A GUI environment (X11/Wayland/macOS) for the interactive selection and display windows

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yeokiwi/object_tracking.git
   cd object_tracking
   ```

2. Install dependencies:

   ```bash
   pip install opencv-contrib-python
   ```

   > `opencv-contrib-python` is required (not just `opencv-python`) because the CSRT tracker is part of the contrib module.

## Usage

Run the tracker with a video file:

```bash
python tracker.py <video_file>
```

If no argument is provided, it defaults to `IR.mp4`:

```bash
python tracker.py
```

### Object Selection

When the application starts, the first frame is displayed for object selection:

1. **Draw** a bounding box around an object by clicking and dragging
2. Press **Space** or **Enter** to confirm the selection and add another object
3. Press **ESC** to cancel the current selection
4. Press **Q** or close the window to finish selection and begin tracking

Previously selected objects are shown with their color-coded bounding boxes while you add more.

### During Tracking

- The video plays with bounding boxes and labels drawn on each tracked object
- A frame counter and FPS reading are shown in the top-left corner
- Press **Q** at any time to stop tracking early
- When tracking ends (video complete or user stops), a summary is printed to the terminal

### Output

The annotated video is saved as `output_tracked.mp4` in the working directory.

## Code Structure

| Function | Description |
|---|---|
| `load_video(path)` | Opens video capture and returns the capture object and metadata (width, height, fps) |
| `select_bounding_boxes(frame)` | Handles interactive ROI selection loop, returns list of bounding boxes |
| `initialize_trackers(frame, bboxes)` | Creates and initializes a CSRT tracker for each bounding box |
| `draw_tracked_objects(frame, trackers, colors, last_known_positions)` | Updates all trackers on the current frame and draws results |
| `run_tracking(cap, trackers, writer, colors, metadata)` | Main tracking loop: reads frames, draws, writes output, displays in real time |
| `main()` | Entry point that orchestrates the full pipeline |
