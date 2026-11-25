"""One-time helper to obtain a Dropbox OAuth refresh token."""
import requests


def main():
    app_key = input("Paste your Dropbox App Key: ").strip()
    app_secret = input("Paste your Dropbox App Secret: ").strip()
    if not app_key or not app_secret:
        print("App Key and App Secret are required.")
        return

    url = (
        "https://www.dropbox.com/oauth2/authorize?client_id="
        + app_key
        + "&response_type=code&token_access_type=offline"
    )
    print("\nOpen this authorization URL in your browser:\n")
    print(url)
    print("\nApprove the app, then copy the authorization code from the page/URL.\n")
    code = input("Paste the authorization code here: ").strip()

    response = requests.post(
        "https://api.dropbox.com/oauth2/token",
        data={"code": code, "grant_type": "authorization_code"},
        auth=(app_key, app_secret),
        timeout=30,
    )
    if not response.ok:
        print("\nToken exchange failed:", response.status_code, response.text)
        return

    data = response.json()
    refresh_token = data.get("refresh_token")
    if refresh_token:
        print("\nSUCCESS. Your Dropbox refresh token is:\n")
        print(refresh_token)
        print("\nStore it securely in Streamlit Cloud Secrets as DROPBOX_REFRESH_TOKEN.")
    else:
        print("Response did not contain a refresh token:", data)


if __name__ == "__main__":
    main()
