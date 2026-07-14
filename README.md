# Basic backend projects using fastapi (python)

## Included various projects with different database options-

- SQLite(Simple Checkout Cart)
- ***PostgreSQL(ExpenseTrackerAPI)(UnderProgress)***

> [!NOTE]
> Switch branch for different types of project/database options.

## PostgreSQL(ExpenseTrackerAPI)

An api (Application Programming Interface) for maintaining simple expenses with categories. CRUD styled expenses management for various users with JWT cookie authentication systems. Users can login and logout to maintain their privacy and management of expenses.

### Detailed information (bullet)

- Sign up as a new user.
- Generate and validate JWTs for handling authentication and user session.
- List and filter your past expenses. You can add the following filters:
  - Past week.
  - Last month.
  - Last 3 months.
  - Custom (to specify a start and end date of your choosing).
- Add new expenses.
- Remove existing expenses.
- Update existing expenses.

## Startup instructions

```bash
sudo docker-compose up --build
```

## API documentation

Use `http://localhost:8000/docs` for api documentation and various commands.
