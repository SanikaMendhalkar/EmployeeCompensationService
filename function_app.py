
import azure.functions as func
import logging
import os
import json
import mysql.connector

app = func.FunctionApp()


@app.route(route="HelloFunction", auth_level=func.AuthLevel.ANONYMOUS)
def HelloFunction(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    name = req.params.get("name")
    if not name:
        try:
            req_body = req.get_json()
        except ValueError:
            pass
        else:
            name = req_body.get("name")

    if name:
        return func.HttpResponse(
            f"Hello, {name}. This HTTP triggered function executed successfully."
        )

    return func.HttpResponse(
        "This HTTP triggered function executed successfully. "
        "Pass a name in the query string or in the request body.",
        status_code=200
    )


@app.route(route="TestDatabase", auth_level=func.AuthLevel.ANONYMOUS)
def TestDatabase(req: func.HttpRequest) -> func.HttpResponse:
    connection = None

    try:
        connection = mysql.connector.connect(
            host=os.environ["DB_HOST"],
            port=int(os.environ["DB_PORT"]),
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            database=os.environ["DB_NAME"],
            connection_timeout=5
        )

        cursor = connection.cursor()
        cursor.execute("SELECT DATABASE()")
        result = cursor.fetchone()
        cursor.close()

        return func.HttpResponse(
            f"Database connected successfully: {result[0]}",
            status_code=200
        )

    except Exception:
        logging.exception("Database connection failed.")
        return func.HttpResponse(
            "Could not connect to the database. Check the local settings and MySQL server.",
            status_code=500
        )

    finally:
        if connection is not None and connection.is_connected():
            connection.close()


@app.route(
    route="employees",
    methods=["GET"],
    auth_level=func.AuthLevel.ANONYMOUS
)
def GetAllEmployees(req: func.HttpRequest) -> func.HttpResponse:
    connection = None
    cursor = None

    try:
        # Read optional department filter
        department_id = req.params.get("departmentId")

        if department_id is not None:
            try:
                department_id = int(department_id)
                if department_id <= 0:
                    raise ValueError
            except ValueError:
                return func.HttpResponse(
                    json.dumps({
                        "error": "departmentId must be a positive integer."
                    }),
                    status_code=400,
                    mimetype="application/json"
                )

        connection = mysql.connector.connect(
            host=os.environ["DB_HOST"],
            port=int(os.environ["DB_PORT"]),
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            database=os.environ["DB_NAME"],
            connection_timeout=5
        )

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                e.EmployeeID,
                e.FirstName,
                e.LastName,
                e.DepartmentID,
                d.DepartmentName,
                e.Salary,
                e.Bonus,
                e.HireDate
            FROM Employee e
            JOIN Department d
                ON e.DepartmentID = d.DepartmentID
        """

        if department_id is not None:
            query += " WHERE e.DepartmentID = %s"
            cursor.execute(query + " ORDER BY e.EmployeeID", (department_id,))
        else:
            cursor.execute(query + " ORDER BY e.EmployeeID")

        employees = cursor.fetchall()

        return func.HttpResponse(
            json.dumps(employees, default=str),
            status_code=200,
            mimetype="application/json"
        )

    except Exception:
        logging.exception("Failed to retrieve employees.")
        return func.HttpResponse(
            json.dumps({"error": "Could not retrieve employees."}),
            status_code=500,
            mimetype="application/json"
        )

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()

@app.route(
    route="employees/{id:int}",
    methods=["GET"],
    auth_level=func.AuthLevel.ANONYMOUS
)
def GetEmployeeById(req: func.HttpRequest) -> func.HttpResponse:
    connection = None
    cursor = None

    try:
        employee_id = int(req.route_params.get("id"))

        connection = mysql.connector.connect(
            host=os.environ["DB_HOST"],
            port=int(os.environ["DB_PORT"]),
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            database=os.environ["DB_NAME"],
            connection_timeout=5
        )

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                e.EmployeeID,
                e.FirstName,
                e.LastName,
                e.DepartmentID,
                d.DepartmentName,
                e.Salary,
                e.Bonus,
                e.HireDate
            FROM Employee e
            JOIN Department d
                ON e.DepartmentID = d.DepartmentID
            WHERE e.EmployeeID = %s
        """

        cursor.execute(query, (employee_id,))
        employee = cursor.fetchone()

        if employee is None:
            return func.HttpResponse(
                json.dumps({"error": "Employee not found."}),
                status_code=404,
                mimetype="application/json"
            )

        return func.HttpResponse(
            json.dumps(employee, default=str),
            status_code=200,
            mimetype="application/json"
        )

    except Exception:
        logging.exception("Failed to retrieve employee.")
        return func.HttpResponse(
            json.dumps({"error": "Could not retrieve employee."}),
            status_code=500,
            mimetype="application/json"
        )

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()

@app.route(
    route="employees",
    methods=["POST"],
    auth_level=func.AuthLevel.ANONYMOUS
)
def CreateEmployee(req: func.HttpRequest) -> func.HttpResponse:
    connection = None
    cursor = None

    try:
        # Parse JSON request body
        try:
            data = req.get_json()
        except ValueError:
            return func.HttpResponse(
                json.dumps({"error": "Request body must be valid JSON."}),
                status_code=400,
                mimetype="application/json"
            )

        if not isinstance(data, dict):
            return func.HttpResponse(
                json.dumps({"error": "Request body must be a JSON object."}),
                status_code=400,
                mimetype="application/json"
            )

        # Validate required fields
        required_fields = [
            "FirstName", "LastName", "DepartmentID", "Salary"
        ]

        for field in required_fields:
            if field not in data or data[field] in (None, ""):
                return func.HttpResponse(
                    json.dumps({"error": f"{field} is required."}),
                    status_code=400,
                    mimetype="application/json"
                )

        # Validate numeric fields and apply default bonus
        try:
            department_id = int(data["DepartmentID"])
            salary = float(data["Salary"])

            if "Bonus" not in data:
                bonus = round(salary * 0.05, 2)
            else:
                bonus = data["Bonus"]
                if bonus is not None:
                    bonus = float(bonus)

        except (ValueError, TypeError):
            return func.HttpResponse(
                json.dumps({
                    "error": "DepartmentID, Salary and Bonus must be valid numbers."
                }),
                status_code=400,
                mimetype="application/json"
            )

        # Validate values
        if department_id <= 0 or salary < 0 or (
            bonus is not None and bonus < 0
        ):
            return func.HttpResponse(
                json.dumps({
                    "error": "DepartmentID must be positive; Salary and Bonus cannot be negative."
                }),
                status_code=400,
                mimetype="application/json"
            )

        # Connect to database
        connection = mysql.connector.connect(
            host=os.environ["DB_HOST"],
            port=int(os.environ["DB_PORT"]),
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            database=os.environ["DB_NAME"],
            connection_timeout=5
        )

        cursor = connection.cursor()

        # Insert employee
        query = """
            INSERT INTO Employee
            (FirstName, LastName, DepartmentID, Salary, Bonus, HireDate)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        cursor.execute(query, (
            str(data["FirstName"]).strip(),
            str(data["LastName"]).strip(),
            department_id,
            salary,
            bonus,
            data.get("HireDate")
        ))

        connection.commit()
        new_employee_id = cursor.lastrowid

        return func.HttpResponse(
            json.dumps({
                "message": "Employee created successfully.",
                "EmployeeID": new_employee_id
            }),
            status_code=201,
            mimetype="application/json"
        )

    except mysql.connector.IntegrityError:
        logging.exception("Invalid department or employee data.")
        return func.HttpResponse(
            json.dumps({"error": "Invalid department or employee data."}),
            status_code=400,
            mimetype="application/json"
        )

    except Exception:
        logging.exception("Failed to create employee.")
        return func.HttpResponse(
            json.dumps({"error": "Could not create employee."}),
            status_code=500,
            mimetype="application/json"
        )

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()

@app.route(
    route="employees/{id:int}",
    methods=["PUT"],
    auth_level=func.AuthLevel.ANONYMOUS
)
def UpdateEmployee(req: func.HttpRequest) -> func.HttpResponse:
    connection = None
    cursor = None

    try:
        employee_id = int(req.route_params.get("id"))
        data = req.get_json()

        required_fields = ["FirstName", "LastName", "DepartmentID", "Salary"]

        for field in required_fields:
            if field not in data or data[field] in (None, ""):
                return func.HttpResponse(
                    json.dumps({"error": f"{field} is required."}),
                    status_code=400,
                    mimetype="application/json"
                )

        try:
            department_id = int(data["DepartmentID"])
            salary = float(data["Salary"])
            bonus = data.get("Bonus")

            if bonus is not None:
                bonus = float(bonus)

        except (ValueError, TypeError):
            return func.HttpResponse(
                json.dumps({"error": "DepartmentID, Salary and Bonus must be valid numbers."}),
                status_code=400,
                mimetype="application/json"
            )

        if department_id <= 0 or salary < 0 or (bonus is not None and bonus < 0):
            return func.HttpResponse(
                json.dumps({"error": "DepartmentID must be positive; Salary and Bonus cannot be negative."}),
                status_code=400,
                mimetype="application/json"
            )

        first_name = str(data["FirstName"]).strip()
        last_name = str(data["LastName"]).strip()

        if not first_name or not last_name:
            return func.HttpResponse(
                json.dumps({"error": "FirstName and LastName cannot be blank."}),
                status_code=400,
                mimetype="application/json"
            )

        connection = mysql.connector.connect(
            host=os.environ["DB_HOST"],
            port=int(os.environ["DB_PORT"]),
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            database=os.environ["DB_NAME"],
            connection_timeout=5
        )

        cursor = connection.cursor()

        # Check whether the employee exists
        cursor.execute(
            "SELECT EmployeeID FROM Employee WHERE EmployeeID = %s",
            (employee_id,)
        )

        if cursor.fetchone() is None:
            return func.HttpResponse(
                json.dumps({"error": "Employee not found."}),
                status_code=404,
                mimetype="application/json"
            )

        # Update employee details
        query = """
            UPDATE Employee
            SET FirstName = %s,
                LastName = %s,
                DepartmentID = %s,
                Salary = %s,
                Bonus = %s,
                HireDate = %s
            WHERE EmployeeID = %s
        """

        cursor.execute(query, (
            first_name,
            last_name,
            department_id,
            salary,
            bonus,
            data.get("HireDate"),
            employee_id
        ))

        connection.commit()

        return func.HttpResponse(
            json.dumps({
                "message": "Employee updated successfully.",
                "EmployeeID": employee_id
            }),
            status_code=200,
            mimetype="application/json"
        )

    except ValueError:
        return func.HttpResponse(
            json.dumps({"error": "Request body must be valid JSON."}),
            status_code=400,
            mimetype="application/json"
        )

    except mysql.connector.IntegrityError:
        logging.exception("Invalid department or employee data.")
        return func.HttpResponse(
            json.dumps({"error": "Invalid department or employee data."}),
            status_code=400,
            mimetype="application/json"
        )

    except Exception:
        logging.exception("Failed to update employee.")
        return func.HttpResponse(
            json.dumps({"error": "Could not update employee."}),
            status_code=500,
            mimetype="application/json"
        )

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()

@app.route(
    route="employees/{id:int}",
    methods=["DELETE"],
    auth_level=func.AuthLevel.ANONYMOUS
)
def DeleteEmployee(req: func.HttpRequest) -> func.HttpResponse:
    connection = None
    cursor = None

    try:
        employee_id = int(req.route_params.get("id"))

        connection = mysql.connector.connect(
            host=os.environ["DB_HOST"],
            port=int(os.environ["DB_PORT"]),
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            database=os.environ["DB_NAME"],
            connection_timeout=5
        )

        cursor = connection.cursor()

        query = """
            DELETE FROM Employee
            WHERE EmployeeID = %s
        """

        cursor.execute(query, (employee_id,))

        if cursor.rowcount == 0:
            connection.rollback()
            return func.HttpResponse(
                json.dumps({"error": "Employee not found."}),
                status_code=404,
                mimetype="application/json"
            )

        connection.commit()

        return func.HttpResponse(
            json.dumps({
                "message": "Employee deleted successfully.",
                "EmployeeID": employee_id
            }),
            status_code=200,
            mimetype="application/json"
        )

    except Exception:
        logging.exception("Failed to delete employee.")
        if connection is not None and connection.is_connected():
            connection.rollback()

        return func.HttpResponse(
            json.dumps({"error": "Could not delete employee."}),
            status_code=500,
            mimetype="application/json"
        )

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()

@app.route(
    route="reports/total-bonus",
    methods=["GET"],
    auth_level=func.AuthLevel.ANONYMOUS
)
def GetTotalBonus(req: func.HttpRequest) -> func.HttpResponse:
    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(
            host=os.environ["DB_HOST"],
            port=int(os.environ["DB_PORT"]),
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            database=os.environ["DB_NAME"],
            connection_timeout=5
        )

        cursor = connection.cursor()

        query = """
            SELECT COALESCE(SUM(Bonus), 0)
            FROM Employee
        """

        cursor.execute(query)
        total_bonus = cursor.fetchone()[0]

        return func.HttpResponse(
            json.dumps({
                "totalBonusPaid": float(total_bonus)
            }),
            status_code=200,
            mimetype="application/json"
        )

    except Exception:
        logging.exception("Failed to calculate total bonus.")
        return func.HttpResponse(
            json.dumps({"error": "Could not calculate total bonus."}),
            status_code=500,
            mimetype="application/json"
        )

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()

@app.route(
    route="reports/employees-null-bonus",
    methods=["GET"],
    auth_level=func.AuthLevel.ANONYMOUS
)
def GetEmployeesWithNullBonus(req: func.HttpRequest) -> func.HttpResponse:
    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(
            host=os.environ["DB_HOST"],
            port=int(os.environ["DB_PORT"]),
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            database=os.environ["DB_NAME"],
            connection_timeout=5
        )

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                e.EmployeeID,
                e.FirstName,
                e.LastName,
                d.DepartmentName,
                e.Salary,
                e.Bonus
            FROM Employee e
            JOIN Department d
                ON e.DepartmentID = d.DepartmentID
            WHERE e.Bonus IS NULL
            ORDER BY e.EmployeeID
        """

        cursor.execute(query)
        employees = cursor.fetchall()

        return func.HttpResponse(
            json.dumps(employees, default=str),
            status_code=200,
            mimetype="application/json"
        )

    except Exception:
        logging.exception("Failed to retrieve employees with NULL bonuses.")
        return func.HttpResponse(
            json.dumps({"error": "Could not retrieve employees with NULL bonuses."}),
            status_code=500,
            mimetype="application/json"
        )

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()
@app.route(
    route="reports/bonus-percentage",
    methods=["GET"],
    auth_level=func.AuthLevel.ANONYMOUS
)
def GetBonusPercentage(req: func.HttpRequest) -> func.HttpResponse:
    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(
            host=os.environ["DB_HOST"],
            port=int(os.environ["DB_PORT"]),
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            database=os.environ["DB_NAME"],
            connection_timeout=5
        )

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                e.EmployeeID,
                e.FirstName,
                e.LastName,
                d.DepartmentName,
                e.Salary,
                e.Bonus,
                ROUND((e.Bonus / e.Salary) * 100, 2) AS BonusPercentage
            FROM Employee e
            JOIN Department d
                ON e.DepartmentID = d.DepartmentID
            WHERE e.Bonus IS NOT NULL
            ORDER BY e.EmployeeID
        """

        cursor.execute(query)
        employees = cursor.fetchall()

        return func.HttpResponse(
            json.dumps(employees, default=str),
            status_code=200,
            mimetype="application/json"
        )

    except Exception:
        logging.exception("Failed to calculate bonus percentages.")
        return func.HttpResponse(
            json.dumps({"error": "Could not calculate bonus percentages."}),
            status_code=500,
            mimetype="application/json"
        )

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()
@app.route(
    route="reports/departments-bonus-exceeds-average-salary",
    methods=["GET"],
    auth_level=func.AuthLevel.ANONYMOUS
)
def GetDepartmentsBonusExceedsAverageSalary(req: func.HttpRequest) -> func.HttpResponse:
    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(
            host=os.environ["DB_HOST"],
            port=int(os.environ["DB_PORT"]),
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            database=os.environ["DB_NAME"],
            connection_timeout=5
        )

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                d.DepartmentID,
                d.DepartmentName,
                COALESCE(SUM(e.Bonus), 0) AS TotalBonus,
                ROUND(AVG(e.Salary), 2) AS AverageSalary
            FROM Department d
            JOIN Employee e
                ON d.DepartmentID = e.DepartmentID
            GROUP BY d.DepartmentID, d.DepartmentName
            HAVING COALESCE(SUM(e.Bonus), 0) > AVG(e.Salary)
            ORDER BY TotalBonus DESC
        """

        cursor.execute(query)
        departments = cursor.fetchall()

        return func.HttpResponse(
            json.dumps(departments, default=str),
            status_code=200,
            mimetype="application/json"
        )

    except Exception:
        logging.exception("Failed to retrieve departments by bonus and average salary.")
        return func.HttpResponse(
            json.dumps({"error": "Could not retrieve department report."}),
            status_code=500,
            mimetype="application/json"
        )

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()
@app.route(
    route="reports/bonus-ranking",
    methods=["GET"],
    auth_level=func.AuthLevel.ANONYMOUS
)
def GetBonusRanking(req: func.HttpRequest) -> func.HttpResponse:
    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(
            host=os.environ["DB_HOST"],
            port=int(os.environ["DB_PORT"]),
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            database=os.environ["DB_NAME"],
            connection_timeout=5
        )

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                e.EmployeeID,
                e.FirstName,
                e.LastName,
                d.DepartmentName,
                e.Salary,
                e.Bonus,
                RANK() OVER (
                    ORDER BY e.Bonus DESC
                ) AS BonusRank
            FROM Employee e
            JOIN Department d
                ON e.DepartmentID = d.DepartmentID
            ORDER BY
                e.Bonus IS NULL ASC,
                e.Bonus DESC,
                e.EmployeeID ASC
        """

        cursor.execute(query)
        employees = cursor.fetchall()

        return func.HttpResponse(
            json.dumps(employees, default=str),
            status_code=200,
            mimetype="application/json"
        )

    except Exception:
        logging.exception("Failed to retrieve employee bonus rankings.")
        return func.HttpResponse(
            json.dumps({"error": "Could not retrieve bonus rankings."}),
            status_code=500,
            mimetype="application/json"
        )

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()           
@app.route(
    route="reports/highest-compensation",
    methods=["GET"],
    auth_level=func.AuthLevel.ANONYMOUS
)
def GetHighestCompensation(req: func.HttpRequest) -> func.HttpResponse:
    connection = None
    cursor = None

    try:
        connection = mysql.connector.connect(
            host=os.environ["DB_HOST"],
            port=int(os.environ["DB_PORT"]),
            user=os.environ["DB_USER"],
            password=os.environ["DB_PASSWORD"],
            database=os.environ["DB_NAME"],
            connection_timeout=5
        )

        cursor = connection.cursor(dictionary=True)

        query = """
            SELECT
                e.EmployeeID,
                e.FirstName,
                e.LastName,
                d.DepartmentName,
                e.Salary,
                e.Bonus,
                e.Salary + COALESCE(e.Bonus, 0) AS TotalCompensation
            FROM Employee e
            JOIN Department d
                ON e.DepartmentID = d.DepartmentID
        """

        cursor.execute(query)
        employees = cursor.fetchall()

        if not employees:
            return func.HttpResponse(
                json.dumps({"message": "No employees found."}),
                status_code=404,
                mimetype="application/json"
            )

        highest_salary_employee = max(
            employees,
            key=lambda e: e["Salary"]
        )

        highest_compensation_employee = max(
            employees,
            key=lambda e: e["TotalCompensation"]
        )

        same_employee = (
            highest_salary_employee["EmployeeID"]
            == highest_compensation_employee["EmployeeID"]
        )

        result = {
            "highestSalaryEmployee": highest_salary_employee,
            "highestTotalCompensationEmployee": highest_compensation_employee,
            "isSameEmployee": same_employee
        }

        return func.HttpResponse(
            json.dumps(result, default=str),
            status_code=200,
            mimetype="application/json"
        )

    except Exception:
        logging.exception("Failed to retrieve highest compensation report.")
        return func.HttpResponse(
            json.dumps({"error": "Could not retrieve highest compensation report."}),
            status_code=500,
            mimetype="application/json"
        )

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()            