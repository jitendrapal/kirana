I've updated your Firebase configuration to be more flexible, supporting both local development and deployment environments without needing code changes.

### What I Changed

Your `firebase_config.py` now does the following:

1.  **For Deployment:** It first looks for an environment variable named `GOOGLE_CREDENTIALS_JSON`. It expects this variable to contain the *entire content* of your Firebase service account JSON file.
2.  **For Local Development:** If `GOOGLE_CREDENTIALS_JSON` isn't found, it falls back to the previous method, using the `SERVICE_ACCOUNT_KEY_PATH` from your `.env` file.

### Why Your Deployment Failed

The `.env` file is great for local development, but it's not meant for production. Because it contains sensitive information, it's listed in your `.gitignore` file, which means it is not uploaded to your deployment server. That's why your application couldn't find the `SERVICE_ACCOUNT_KEY_PATH` variable when deployed.

### How to Fix Your Deployment

To fix this, you need to set the `GOOGLE_CREDENTIALS_JSON` environment variable in your deployment platform's settings.

1.  **Find the "Environment Variables" or "Secrets" section** in your deployment service's dashboard (e.g., Heroku, Vercel, AWS, Google Cloud).

2.  **Create a new environment variable** with the following name:
    ```
    GOOGLE_CREDENTIALS_JSON
    ```

3.  **For the value, copy and paste the entire content** of your `serviceAccountKey.json` file. It should be a long string of JSON starting with `{ "type": "service_account", ... }`.

Make sure you copy the whole file content as a single line.

Once you set this environment variable and redeploy your application, the error should be resolved.
