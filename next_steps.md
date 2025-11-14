I have configured your application to use a `.env` file for managing environment variables, which is a safer and more flexible approach.

Here's what you need to do:

1.  **Create a new file** named `.env` in the root of your project directory (`c:\Users\Archana\Downloads\kirana`).

2.  **Add the following line** to the `.env` file, replacing `"path/to/your/serviceAccountKey.json"` with the *actual, full path* to your Firebase service account key file:

    ```
    SERVICE_ACCOUNT_KEY_PATH="path/to/your/serviceAccountKey.json"
    ```

    For example, if your key file is located at `c:\Users\Archana\secrets\serviceAccountKey.json`, the line should look like this:

    ```
    SERVICE_ACCOUNT_KEY_PATH="c:\Users\Archana\secrets\serviceAccountKey.json"
    ```

After you've created and configured the `.env` file, the `ValueError` you were seeing should be resolved. Your `.gitignore` file is already set up to ignore `.env` files, so your credentials will not be accidentally committed.
