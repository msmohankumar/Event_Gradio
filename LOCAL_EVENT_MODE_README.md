# Event Photo Finder — Local Internal/External Drive Mode

This mode runs the face-matching server on the event laptop and reads image files directly from a folder on that laptop. The folder may be on the internal drive (e.g. `C:\...`), an external USB drive (e.g. `E:\...`), or a mapped/network drive accessible to Windows.

## Important: Cloud mode and local mode are different

The existing `app.py` remains the GitHub/Streamlit Cloud version. `local_event_app.py` is the local host version. It cannot be hosted on Streamlit Cloud because Cloud cannot access folders on your laptop. Guests must connect to the same Wi-Fi network as the laptop running Local Event Mode.

## Windows setup

1. Install Python 3.10 or 3.11 (64-bit) and select **Add Python to PATH** during installation.
2. Extract this project to a folder on the event laptop.
3. Open Command Prompt/PowerShell in that folder.
4. Install dependencies: `python -m pip install -r requirements.txt`
5. Run `run_local_event.bat` (or run the command below):
   `python -m streamlit run local_event_app.py --server.address 0.0.0.0 --server.port 8501`
6. In the browser on the laptop, open the local Organizer/setup page (usually `http://localhost:8501`).
7. Enter the photo folder path, such as `C:\Wedding\Photos`, `D:\Photos`, or `E:\Wedding Photos`, and click **Scan photo folder**.
8. The page shows the LAN QR URL. The phones and laptop must be on the same Wi-Fi network. Scan the QR on a phone to test.
9. Move the setup page/browser to your extended display and use F11 to show the QR code full-screen.

## Windows Firewall

When Windows asks whether Python/Streamlit should communicate through the firewall, allow it on **Private networks** only. Do not expose the server on public networks. Use a trusted venue Wi-Fi network and avoid guest Wi-Fi isolation, which can prevent phones from reaching the laptop.

## Supported image formats

JPG, JPEG, PNG, WEBP, BMP. Subfolders are scanned recursively. Keep the hard drive connected and the server running during the event.

## Performance

Face matching scans photos when a guest searches. Large photo collections can take time and RAM. For very large collections, split the folder into event subfolders or use a dedicated local indexing/cache improvement in a future version.

## Privacy

In local mode, guest selfies and gallery images are processed by the laptop running the app rather than uploaded to Dropbox by this local app. Matching results and uploaded selfies may exist in Streamlit session memory until the session/app is restarted. Avoid public exposure of the laptop server and stop it after the event.
