
USE EmployeeCompensationDB;

-- Sample departments
INSERT INTO Department
    (DepartmentID, DepartmentName, Location)
VALUES
    (1, 'Engineering', 'Pune'),
    (2, 'HR', 'Mumbai'),
    (3, 'Finance', 'Bangalore'),
    (4, 'Marketing', 'Hyderabad');

-- Sample employees
INSERT INTO Employee
    (EmployeeID, FirstName, LastName, DepartmentID, Salary, Bonus, HireDate)
VALUES
    (1, 'Aarav', 'Sharma', 1, 90000.00, 80000.00, '2023-01-15'),
    (2, 'Diya', 'Patil', 1, 85000.00, 70000.00, '2023-03-10'),
    (3, 'Rohan', 'Mehta', 1, 95000.00, NULL, '2022-06-20'),
    (4, 'Ananya', 'Rao', 2, 60000.00, 5000.00, '2024-02-01'),
    (5, 'Ishaan', 'Verma', 2, 70000.00, NULL, '2023-08-12'),
    (6, 'Meera', 'Joshi', 3, 100000.00, 20000.00, '2022-11-05'),
    (7, 'Kabir', 'Desai', 3, 110000.00, 30000.00, '2021-09-18'),
    (8, 'Sara', 'Khan', 4, 75000.00, 10000.00, '2024-04-22');
