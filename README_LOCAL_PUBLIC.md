# Event Photo Finder - Local Gallery (Windows)

This project scans photos from a folder on the organizer's Windows PC. The photo gallery is not uploaded to a cloud photo bucket. Guest selfie matching runs on the host PC.

## Requirements
- Windows 10/11
- Python 3.10 (recommended for the pinned TensorFlow version)
- Internet connection for installation/model setup and, if guests are outside the local Wi-Fi, a Cloudflare Quick Tunnel

## Setup
1. Install Python 3.10 from https://www.python.org/downloads/ and enable Add Python to PATH.
2. Extract this ZIP to a folder.
3. Open Command Prompt in the extracted project folder.
4. Run: `python -m venv .venv`
5. Run: `.venv\\Scripts\\activate`
6. Run: `python -m pip install --upgrade pip`
7. Run: `pip install -r requirements-local.txt`
8. Start the app with `run_local_event.bat`.
9. In Organizer setup, click Browse, select your photo folder, then Scan photo folder.

## Guests on the same Wi-Fi
The Organizer screen displays a LAN URL and QR code. Guests connect to the same Wi-Fi and scan the QR code.

## Guests outside your Wi-Fi (temporary public URL)
1. Download cloudflared for Windows from https://developers.cloudflare.com/cloudflare-one/connections/connect-networks/downloads/ and place `cloudflared.exe` in this project folder (or add it to PATH).
2. Start the local app using `run_local_event.bat`.
3. In a second window, run `start_public_url.bat`.
4. Cloudflare prints a temporary `https://...trycloudflare.com` URL.
5. In Organizer setup, paste that URL into Optional public guest URL and use the displayed QR code.

The tunnel URL is temporary and changes when restarted. Both the local app and tunnel process must remain running. Anyone with the tunnel URL can access the guest interface while it is active. This is a temporary/demo tunnel, not a guaranteed permanent service. Avoid sharing sensitive photo galleries through an unrestricted public URL.

## Important
The organizer's computer hosts the gallery and does face matching. Keep the computer awake and connected. Face-recognition processing may be slow on CPU for large galleries. Test with a small folder first.
