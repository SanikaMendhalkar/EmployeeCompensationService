
# Employee Compensation Service

A Python-based REST API built with Azure Functions and MySQL to manage employee compensation data and generate compensation reports.

## Technologies Used

- Python
- Azure Functions
- MySQL
- MySQL Connector/Python
- Postman

## Features

### Employee Management

- Retrieve all employees
- Retrieve an employee by ID
- Create a new employee
- Update employee details
- Delete an employee

### Compensation Reports

1. Calculate the total bonus paid to employees.
2. Retrieve employees whose bonus is NULL.
3. Calculate employee bonus as a percentage of salary, rounded to two decimal places.
4. Retrieve departments where total bonus exceeds average salary.
5. Rank employees by bonus, with NULL bonuses last.
6. Identify the highest-salary employee and the highest-total-compensation employee, and determine whether they are the same person.

## Project Structure

```text
EmployeeCompensationService/
│
├── function_app.py
├── host.json
├── local.settings.json
├── requirements.txt
├── database.sql
├── sample_data.sql
├── README.md
├── .gitignore
└── .funcignore
```

## Prerequisites

- Python
- Visual Studio Code
- Azure Functions Core Tools
- MySQL Server
- MySQL Workbench (optional)
- Postman (for API testing)

## Database Setup

1. Open MySQL Workbench and connect to your MySQL server.
2. Execute `database.sql` to create the database and tables.
3. For a fresh database, execute `sample_data.sql` to insert sample records.

## Local Configuration

Configure your local database connection in `local.settings.json`.

Example structure:

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "DB_HOST": "localhost",
    "DB_PORT": "3306",
    "DB_USER": "your_mysql_username",
    "DB_PASSWORD": "your_mysql_password",
    "DB_NAME": "EmployeeCompensationDB"
  }
}
```

Replace the example database credentials with your own local values. Do not commit `local.settings.json` or expose your database password.

## Installation

Activate your Python virtual environment, then install the dependencies:

```powershell
pip install -r requirements.txt
```

## Run the Application

From the project directory, start the Azure Functions host:

```powershell
func start
```

The local API base URL is:

```text
http://localhost:7071/api
```

## API Endpoints

### Employee Management

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/employees` | Retrieve all employees |
| GET | `/api/employees/{id}` | Retrieve an employee by ID |
| POST | `/api/employees` | Create an employee |
| PUT | `/api/employees/{id}` | Update an employee |
| DELETE | `/api/employees/{id}` | Delete an employee |

### Compensation Reports

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/reports/total-bonus` | Calculate total bonus |
| GET | `/api/reports/employees-null-bonus` | Retrieve employees with NULL bonuses |
| GET | `/api/reports/bonus-percentage` | Calculate bonus percentage of salary |
| GET | `/api/reports/departments-bonus-exceeds-average-salary` | Find departments where total bonus exceeds average salary |
| GET | `/api/reports/bonus-ranking` | Rank employees by bonus |
| GET | `/api/reports/highest-compensation` | Compare highest salary and highest total compensation |

## Testing

Use a browser or Postman to test GET endpoints. Use Postman for POST, PUT, and DELETE requests.

The service runs locally at `http://localhost:7071` when the Azure Functions host is started.

## Security and Configuration

- Database credentials are stored in local configuration and should not be committed to source control.
- `.gitignore` excludes local settings and virtual environment files.
- For deployment, configure database credentials using the hosting environment's application settings.

## Author

Sanika Dilip Mendhalkar
