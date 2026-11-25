---
title: Event Photo Finder
emoji: 📸
colorFrom: blue
colorTo: purple
sdk: gradio
app_file: app.py
pinned: false
---

# Event Photo Finder (ZeroGPU)

Selfie/webcam face similarity search against an organizer-managed photo gallery. GPU inference is handled by a `@spaces.GPU` function.

## Features
- Selfie upload or webcam capture
- Face matching with MTCNN + FaceNet (VGGFace2)
- Gallery upload and organizer settings
- Matching photo gallery and ZIP download

## Important
- Gallery photos uploaded here are transferred to the Space and processed on its server.
- Space disk storage may be ephemeral unless persistent storage is configured.
- Similarity matching is not identity verification. Use consent-based face processing.
- Threshold is set to 0.70 cosine similarity in `app.py`; adjust based on testing.
