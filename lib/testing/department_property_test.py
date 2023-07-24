from models.department import Department
import pytest



class TestDepartmentProperties:
    '''Class Department in department.py'''

    @pytest.fixture(autouse=True)
    def clear_dictionary(self):
        '''clear out the class dictionary.'''
        Department.all = {}

    def test_name_location_valid(self):
        '''validates name and location assigned valid non-empty strings'''
        # should not throw an exception
        department = Department("Payroll", "Building A, 5th Floor")

    def test_name_is_string(self):
        '''validates name property is assigned a string'''
        with pytest.raises(ValueError):
            department = Department("Payroll", "Building A, 5th Floor")
            department.name = 7

    def test_name_string_length(self):
        '''validates name property length > 0'''
        with pytest.raises(ValueError):
            department = Department("Payroll", "Building A, 5th Floor")
            department.name = ''

    def test_location_is_string(self):
        '''validates location property is assigned a string'''
        with pytest.raises(ValueError):
            department = Department("Payroll", "Building A, 5th Floor")
            department.location = True

    def test_location_string_length(self):
        '''validates location property length > 0'''
        with pytest.raises(ValueError):
            department = Department("Payroll", "Building A, 5th Floor")
            department.name = ''
