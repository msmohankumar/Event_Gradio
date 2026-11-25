---
title: Event Photo Finder
emoji: 📸
colorFrom: blue
colorTo: purple
sdk: gradio
app_file: app.py
pinned: false
---

# Event Photo Finder

Guests can upload or capture a selfie to search for event photos using face similarity matching.

## Organizer
Use the **Organizer** tab to configure the event and add event-gallery photos.

## Notes
- The app stores its gallery in `./data` or `/data` if that directory exists.
- On Hugging Face Spaces, runtime storage may be ephemeral unless persistent storage is configured.
- Uploaded gallery images are stored on the Space server.
- This is a similarity-based face search, not identity verification. Obtain consent before uploading or processing faces.
