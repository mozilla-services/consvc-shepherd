# AdOps Dashboard Frontend

The AdOps Dashboard is a React + Typescript + Vite + SWC app set up with Vite's plugin: [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react-swc)

# Running in development

You can run this app together with the Django app in one `docker-compose up --build` command from the root of this repo.

Visit the React frontend at http://0.0.0.0:5173/

We will need the following details to be added to settings.py in order to fix the CSRF permissions denied error for the APIs. This will be removed once CSRF authentication is implemented.

```
REST_FRAMEWORK = {
"DEFAULT_AUTHENTICATION_CLASSES": [],
"DEFAULT_PERMISSION_CLASSES": [],
}
```

# Next steps

Still missing from this setup:

- Build for production and serve React app from Django
