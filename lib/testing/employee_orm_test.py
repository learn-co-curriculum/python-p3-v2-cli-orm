from models.__init__ import CONN, CURSOR
from models.employee import Employee
from models.department import Department
from faker import Faker
import pytest

class TestEmployee:
    '''Class Employee in employee.py'''

    @pytest.fixture(autouse=True)
    def drop_tables(self):
        '''drop tables prior to each test.'''

        CURSOR.execute("DROP TABLE IF EXISTS employees")
        CURSOR.execute("DROP TABLE IF EXISTS departments")

        Department.all = {}
        Employee.all = {}

    def test_creates_table(self):
        '''contains method "create_table()" that creates table "employees" if it does not exist.'''

        Department.create_table()  # ensure Department table exists due to FK constraint
        Employee.create_table()
        assert (CURSOR.execute("SELECT * FROM employees"))

    def test_drops_table(self):
        '''contains method "drop_table()" that drops table "employees" if it exists.'''

        sql = """
            CREATE TABLE IF NOT EXISTS departments
                (id INTEGER PRIMARY KEY,
                name TEXT,
                location TEXT)
        """
        CURSOR.execute(sql)

        sql = """  
            CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            job_title TEXT,
            department_id INTEGER,
            FOREIGN KEY (department_id) REFERENCES departments(id))
        """
        CURSOR.execute(sql)

        Employee.drop_table()

        # Confirm departments table exists
        sql_table_names = """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='departments'
            LIMIT 1
        """
        result = CURSOR.execute(sql_table_names).fetchone()
        assert (result)

        # Confirm employees table does not exist
        sql_table_names = """
            SELECT name FROM sqlite_master
            WHERE type='table' AND name='employees'
            LIMIT 1
        """
        result = CURSOR.execute(sql_table_names).fetchone()
        assert (result is None)

    def test_saves_employee(self):
        '''contains method "save()" that saves an Employee instance to the db and sets the instance id.'''

        Department.create_table()
        department = Department("Payroll", "Building A, 5th Floor")
        department.save()  # tested in department_test.py

        Employee.create_table()
        employee = Employee("Sasha", "Manager", department.id)
        employee.save()

        sql = """
            SELECT * FROM employees
        """

        row = CURSOR.execute(sql).fetchone()
        assert ((row[0], row[1], row[2], row[3]) ==
                (employee.id, employee.name, employee.job_title, employee.department_id) ==
                (employee.id, "Sasha", "Manager", department.id))

    def test_creates_employee(self):
        '''contains method "create()" that creates a new row in the db using the parameter data and returns an Employee instance.'''

        Department.create_table()
        department = Department("Payroll", "Building A, 5th Floor")
        department.save()  # tested in department_test.py

        Employee.create_table()
        employee = Employee.create("Kai", "Web Developer", department.id)

        sql = """
            SELECT * FROM employees
        """
        row = CURSOR.execute(sql).fetchone()
        assert ((row[0], row[1], row[2], row[3]) ==
                (employee.id, employee.name, employee.job_title, employee.department_id) ==
                (employee.id, "Kai", "Web Developer", department.id))

    def test_updates_row(self):
        '''contains a method "update()" that updates an instance's corresponding database record to match its new attribute values.'''

        Department.create_table()
        department1 = Department("Payroll", "Building A, 5th Floor")
        department1.save()
        department2 = Department("Human Resources", "Building C, 2nd Floor")
        department2.save()

        Employee.create_table()

        employee1 = Employee.create("Raha", "Accountant", department1.id)
        employee2 = Employee.create(
            "Tal", "Benefits Coordinator", department2.id)
        id1 = employee1.id
        id2 = employee2.id
        employee1.name = "Raha Lee"
        employee1.job_title = "Senior Accountant"
        employee1.department_id = department2.id
        employee1.update()

        # Confirm employee updated
        employee = Employee.find_by_id(id1)
        assert ((employee.id, employee.name, employee.job_title, employee.department_id) ==
                (employee1.id, employee1.name, employee1.job_title, employee1.department_id) ==
                (id1, "Raha Lee", "Senior Accountant", department2.id))

        # Confirm employee not updated
        employee = Employee.find_by_id(id2)
        assert ((employee.id, employee.name, employee.job_title, employee.department_id) ==
                (employee2.id, employee2.name, employee2.job_title, employee2.department_id) ==
                (id2, "Tal", "Benefits Coordinator", department2.id))

    def test_deletes_row(self):
        '''contains a method "delete()" that deletes the instance's corresponding database record'''
        Department.create_table()
        department = Department("Payroll", "Building A, 5th Floor")
        department.save()

        Employee.create_table()

        employee1 = Employee.create("Raha", "Accountant", department.id)
        id1 = employee1.id
        employee2 = Employee.create(
            "Tal", "Benefits Coordinator", department.id)
        id2 = employee2.id

        employee = Employee.find_by_id(id1)
        employee.delete()
        # assert row deleted
        assert (Employee.find_by_id(employee1.id) is None)
        # assert Employee object state is correct, id should be None
        assert ((employee1.id, employee1.name, employee1.job_title, employee1.department_id) ==
                (None, "Raha", "Accountant", department.id))
        # assert dictionary entry was deleted
        assert(Employee.all.get(id1) is None)
        
        employee = Employee.find_by_id(id2)
        # assert employee2 row not modified, employee2 object not modified
        assert ((employee.id, employee.name, employee.job_title, employee.department_id) ==
                (employee2.id, employee2.name, employee2.job_title, employee2.department_id) ==
                (id2, "Tal", "Benefits Coordinator", department.id))

    def test_instance_from_db(self):
        '''contains method "instance_from_db()" that takes a db row and creates an Employee instance.'''

        Department.create_table()
        department = Department("Payroll", "Building A, 5th Floor")
        department.save()  # tested in department_test.py

        Employee.create_table()
        sql = """
            INSERT INTO employees (name, job_title, department_id)
            VALUES ('Amir', 'Programmer', ?)
        """
        CURSOR.execute(sql, (department.id,))

        sql = """
            SELECT * FROM employees
        """
        row = CURSOR.execute(sql).fetchone()

        employee = Employee.instance_from_db(row)
        assert ((row[0], row[1], row[2], row[3]) ==
                (employee.id, employee.name, employee.job_title, employee.department_id) ==
                (employee.id, "Amir", "Programmer", department.id))

    def test_gets_all(self):
        '''contains method "get_all()" that returns a list of Employee instances for every record in the db.'''

        Department.create_table()
        department = Department("Payroll", "Building A, 5th Floor")
        department.save()

        Employee.create_table()
        employee1 = Employee.create(
            "Tristan", "Fullstack Developer", department.id)
        employee2 = Employee.create("Sasha", "Manager", department.id)

        employees = Employee.get_all()
        assert (len(employees) == 2)
        assert ((employees[0].id, employees[0].name, employees[0].job_title, employees[0].department_id) ==
                (employee1.id, employee1.name, employee1.job_title, employee1.department_id))
        assert ((employees[1].id, employees[1].name, employees[1].job_title, employees[1].department_id) ==
                (employee2.id, employee2.name, employee2.job_title, employee2.department_id))

    def test_finds_by_name(self):
        '''contains method "find_by_name()" that returns an Employee instance corresponding to the db row retrieved by name.'''

        Department.create_table()
        department = Department("Payroll", "Building A, 5th Floor")
        department.save()
        Employee.create_table()
        faker = Faker()
        employee1 = Employee.create(faker.name(), "Manager", department.id)
        employee2 = Employee.create(
            faker.name(), "Web Developer", department.id)

        employee = Employee.find_by_name(employee1.name)
        assert (
            (employee.id, employee.name, employee.job_title, employee.department_id) ==
            (employee1.id, employee1.name,
             employee1.job_title, employee1.department_id)
        )
        employee = Employee.find_by_name(employee2.name)
        assert (
            (employee.id, employee.name, employee.job_title, employee.department_id) ==
            (employee2.id, employee2.name,
             employee2.job_title, employee2.department_id)
        )
        employee = Employee.find_by_name("Unknown")
        assert (employee is None)

    def test_finds_by_id(self):
        '''contains method "find_by_id()" that returns a Employee instance corresponding to its db row retrieved by id.'''

        Department.create_table()
        department = Department("Payroll", "Building A, 5th Floor")
        department.save()
        Employee.create_table()
        faker = Faker()
        employee1 = Employee.create(faker.name(), "Manager", department.id)
        employee2 = Employee.create(
            faker.name(), "Web Developer", department.id)

        employee = Employee.find_by_id(employee1.id)
        assert (
            (employee.id, employee.name, employee.job_title, employee.department_id) ==
            (employee1.id, employee1.name,
             employee1.job_title, employee1.department_id)
        )

        employee = Employee.find_by_id(employee2.id)
        assert (
            (employee.id, employee.name, employee.job_title, employee.department_id) ==
            (employee2.id, employee2.name,
             employee2.job_title, employee2.department_id)
        )

        employee = Employee.find_by_id(3)
        assert (employee is None)