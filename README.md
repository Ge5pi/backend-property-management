# README

This README would normally document whatever steps are necessary to get your application up and running.

### What is this repository for?

-   Quick summary
-   Version
-   [Learn Markdown](https://bitbucket.org/tutorials/markdowndemo)

### How do I get set up?

-   Summary of set up
-   Configuration
-   Dependencies
-   Database configuration
-   How to run tests
-   Deployment instructions

### Contribution guidelines

-   Writing tests
-   Code review
-   Other guidelines

### Who do I talk to?

-   Repo owner or admin
-   Other community or team contact

## URL Endpoints

-   `/admin/` - Admin dashboard
-   `/` - API documentation
-   `/api/` - API root

## To have the access in application you can use following credentials:

Once the initial fixtures are loaded, you can login to the Django Admin page with the credentials: **admin@ppm.com:Z3ZA6A9@AdminPPM** at `http://localhost:8000/admin/`.
(If you read this in plaintext, ignore the backslash character in the password).

### Visual Studio Code Configuration

The following workspace configuration can be used to configure Visual Studio Code properly (as of 04.09.2020):

```json
{
	"python.pythonPath": "<path to python binary, e.g. in virtual environment>",
	// Linting & Formatting (Flake8, Black, Mypy)
	"flake8.args": ["--config=./backend/setup.cfg"],
	"black-formatter.args": ["config=./backen/pyproject.toml"],
	"isort.args": ["--settings-path=./backend/pyproject.toml"],
	"[python]": {
		"editor.formatOnSave": true,
		"editor.codeActionsOnSave": {
			"source.organizeImports": true
		},
		"editor.rulers": [120],
		"editor.wordWrapColumn": 120
	},
	// Testing (Pytest)
	"python.testing.pytestArgs": ["backend"],
	"python.testing.unittestEnabled": false,
	"python.testing.pytestEnabled": true
}
```

## Fixtures

### Update Initial Fixtures

Just run the script to dumpdata. Because there is a specific order of the models to dump the data. Default order by django breaks our system on loading the data.

```bash
sh ./scripts/dump_data.sh
```

Make sure to review the new dump and remove anything that is not absolutely necessary.

## Type Checking [WIP]

We use the program mypy to do static type checking of our backend code base. This is still a WIP.

In the following, we list common problems with adding static type support for the backend and how we solved them. Please make sure to regularly check these, maybe some of them are already resolved in newer versions of mypy. To check the mypy linting on the backend we can run following command:

```bash
mypy .
```

We are still using an old version of mypy you can get some garbage output, just remove `.mypy_cache/` directory to make it work properly.

### Callable Attributes

Unfortunately, mypy currently doesn't support assigning attributes to a callable, a common pattern in Django, especially Django Admin. By adding `# type: ignore[attr-defined]` to relevant parts, we tell mypy to ignore this.

More information can be found here: https://github.com/python/mypy/issues/708

### Commands

1. `python manage.py runserver` - Run the server
2. `celery -A property_management worker -l info` - Run the celery worker in production
3. `celery -A property_management worker -l info --pool=solo` - Run the celery worker in development
4. `celery -A property_management beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler` - Run the celery beat
5. `celery -A property_management purge` - Purge the celery queue

## Celery

### Dependencies

-   Python 3.x
-   RabbitMQ (message broker)
-   Celery-results (for task results)

### Setting up Celery Beat Tasks

1. **Start Celery Beat**:
    - Run Celery Beat using `celery -A your_project_name beat -l info`.
    - This command schedules tasks based on their defined schedule.

### Accessing Celery Beat Tasks in the Admin Panel

1. **Celery Admin Interface**:

    - Celery provides an admin interface (`django_celery_beat`) that integrates with Django's admin site.

2. **Accessing Task Schedules**:
    - Log in to your Django admin panel.
    - Navigate to the Celery Beat section.
    - Here, you can view, add, edit, or delete periodic tasks defined through Celery Beat.

### Viewing Task Outputs with Celery-results

1. **Configure Celery-results**:

    - Ensure `CELERY_RESULT_BACKEND` is set to use a suitable backend for storing task results (e.g., Django database, Redis, etc.).

2. **Access Task Results**:
    - In your Django admin panel, go to the Celery Results section.
    - You can view completed, failed, and pending tasks along with their outputs, status, and other relevant details.

Remember to handle security aspects, such as access control and authentication, when exposing the admin panel.

Always refer to the official documentation for detailed and updated information on Celery, Celery Beat, and Celery-results integration.

## Setup Stripe Payment Gateway

-   Download and install the Stripe CLI from [here](https://stripe.com/docs/stripe-cli)
-   Run `stripe login` to login to your Stripe account
-   Run `stripe listen --forward-to localhost:8000/api/accounting/stripe/webhook/` to listen to Stripe events
-   Set the `DJSTRIPE_WEBHOOK_SECRET` in the `.env` file

## Setup Stripe

-   Run `python manage.py djstripe_sync_models Price Product` to sync products from Stripe
-   Enable Customer Portal in Stripe. Link: https://dashboard.stripe.com/settings/billing/portal
