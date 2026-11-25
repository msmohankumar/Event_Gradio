---
title: Event Photo Finder
emoji: 📸
colorFrom: blue
colorTo: purple
sdk: docker
app_port: 7860
pinned: false
---

# Event Photo Finder

Streamlit event-photo finder with selfie capture/upload, AI face matching, gallery provider configuration, QR access, and downloads.

## Hugging Face Spaces setup

This repository uses the **Docker SDK** because the application is Streamlit (not Gradio).

In your Space Settings, add these as Secrets if the app uses Supabase shared configuration:

- `SUPABASE_URL`
- `SUPABASE_KEY`

The app can start without these secrets; shared configuration save/load through Supabase will be unavailable until credentials are added.

The Space builds and starts the Streamlit application using the included Dockerfile.
