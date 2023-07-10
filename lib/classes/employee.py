from classes.__init__ import CURSOR, CONN
from classes.department import Department


class Employee:

    def __init__(self, name, job_title, department, id=None):
        self.id = id
        self.name = name
        self.job_title = job_title
        self.department = department

    def __repr__(self):
        return (
            f"<Employee {self.id}: {self.name}, {self.job_title}, "
            + f"Department: {self.department.name} >"
        )

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if isinstance(name, str) and len(name) > 0:
            self._name = name
        else:
            raise ValueError(
                "Name cannot be empty and must be a string"
            )

    @property
    def job_title(self):
        return self._job_title

    @job_title.setter
    def job_title(self, job_title):
        if isinstance(job_title, str) and len(job_title) > 0:
            self._job_title = job_title
        else:
            raise ValueError(
                "job_title cannot be empty and must be a string"
            )

    @property
    def department(self):
        return self._department

    @department.setter
    def department(self, department):
        if isinstance(department, Department) and Department.find_by_id(department.id) is not None:
            self._department = department
        else:
            raise ValueError(
                "Department must be class instance and reference existing entity in database")

    @classmethod
    def create_table(cls):
        sql = """
            CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY,
            name TEXT,
            job_title TEXT,
            department_id INTEGER,
            FOREIGN KEY (department_id) REFERENCES departments(id))
        """
        CURSOR.execute(sql)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        """ Drop the table that persists Employee class instances """
        sql = """
            DROP TABLE IF EXISTS employees;
        """
        CURSOR.execute(sql)
        CONN.commit()

    def save(self):
        sql = """
            INSERT INTO employees (name, job_title, department_id)
            VALUES (?, ?, ?)
        """

        CURSOR.execute(sql, (self.name, self.job_title, self.department.id))
        CONN.commit()

        self.id = CURSOR.lastrowid

    def update(self):
        sql = """
            UPDATE employees
            SET name = ?, job_title = ?, department_id = ?
            WHERE id = ?
        """
        CURSOR.execute(sql, (self.name, self.job_title,
                             self.department.id, self.id))
        CONN.commit()

    @classmethod
    def create(cls, name, job_title, department):
        """ Initialize a new Employee object and save the object to the database """
        employee = Employee(name, job_title, department)
        employee.save()
        return employee

    def delete(self):
        sql = """
            DELETE FROM employees
            WHERE id = ?
        """

        CURSOR.execute(sql, (self.id,))
        CONN.commit()

    @classmethod
    def new_from_db(cls, row):
        """Initialize a new Employee object using the values from the table row."""
        department = Department.find_by_id(row[3])
        employee = cls(row[1], row[2], department)
        employee.id = row[0]
        return employee

    @classmethod
    def get_all(cls):
        """Return a list containing one Employee object per table row"""
        sql = """
            SELECT *
            FROM employees
        """

        rows = CURSOR.execute(sql).fetchall()

        cls.all = [cls.new_from_db(row) for row in rows]
        return cls.all

    @classmethod
    def find_by_id(cls, id):
        """Return Employee object corresponding to the table row matching the specified primary key"""
        sql = """
            SELECT *
            FROM employees
            WHERE id = ?
        """

        row = CURSOR.execute(sql, (id,)).fetchone()
        return cls.new_from_db(row) if row else None

    @classmethod
    def find_by_name(cls, name):
        """Return Employee object corresponding to first table row matching specified name"""
        sql = """
            SELECT *
            FROM employees
            WHERE name is ?
        """

        row = CURSOR.execute(sql, (name,)).fetchone()
        return cls.new_from_db(row) if row else None
