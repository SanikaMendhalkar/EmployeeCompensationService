
CREATE DATABASE IF NOT EXISTS EmployeeCompensationDB;

USE EmployeeCompensationDB;

-- Department table
CREATE TABLE IF NOT EXISTS Department (
    DepartmentID INT AUTO_INCREMENT PRIMARY KEY,
    DepartmentName VARCHAR(100) NOT NULL,
    Location VARCHAR(100)
);

-- Employee table
CREATE TABLE IF NOT EXISTS Employee (
    EmployeeID INT AUTO_INCREMENT PRIMARY KEY,
    FirstName VARCHAR(50) NOT NULL,
    LastName VARCHAR(50) NOT NULL,
    DepartmentID INT NOT NULL,
    Salary DECIMAL(12,2) NOT NULL,
    Bonus DECIMAL(12,2) NULL,
    HireDate DATE,
    CONSTRAINT fk_employee_department
        FOREIGN KEY (DepartmentID)
        REFERENCES Department(DepartmentID)
);
