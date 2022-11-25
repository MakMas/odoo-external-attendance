from flask import Flask, render_template, request
app = Flask(__name__)
 
import xmlrpc.client
import ssl
from datetime import datetime
from datetime import timedelta
 
url = 'insert server URL'
db = 'insert database name'
username = 'username'
password = 'password'
 
def verify_connection():
    common = xmlrpc.client.ServerProxy('{}/xmlrpc/2/common'.format(url), verbose=False, use_datetime=True, context=ssl._create_unverified_context(), allow_none=True)
    version = common.version()
    # print(version)
    uid = common.authenticate(db, username, password, {})
    # print (uid)
    return uid
 
def check_pin(pin):
    uid = verify_connection()
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    active_employee_ids = models.execute_kw(db, uid, password,
        'hr.employee', 'search_read',
        [[['active', '=', True]]], {'fields': ['id', 'name_related', 'pin']})
    employee_pins = []
    for id in active_employee_ids:
        if id['pin'] not in employee_pins:
            employee_pins.append(id['pin'])
    # print(employee_pins)

    if pin in employee_pins:
        for employee in active_employee_ids:
            # print('For function PIN:', employee['pin'])
            # print('providet PIN:', pin)
            if pin == employee['pin']:
                employee_attendance_status = check_employee_attendance(employee_id = employee['id'])
                # print('-- RETURN from check_employee_attendance:', employee_attendance_status)
                for status in employee_attendance_status:
                    if 'check_in' in status:
                        # print(status['check_in'])
                        attendance_state = {'state': 'Hello', 'employee': employee['name_related']}
                        return attendance_state
                        # return 'Hello ' + employee['name_related'] + "\n Have a Greate Day at Work!"
                    elif 'check_out' in status:
                        # print(status['check_out'])
                        attendance_state = {'state': 'Goodbye', 'employee': employee['name_related']}
                        return attendance_state
                        # return 'Goodbye ' + employee['name_related'] + "\n Have a good afternoon!"
                    else:
                        return 'Incorrect Employee status'
    else:
        return 'Incorrect PIN'
 
def check_employee_attendance(employee_id):
    datetime_now = datetime.strftime((datetime.now() - timedelta(hours=1)), "%Y-%m-%d %H:%M:%S")
    # print('Time now:', datetime_now)
    # print('Check Attendance Employee id:', employee_id)
    uid = verify_connection()
    models = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(url))
    attendances = models.execute_kw(db, uid, password,
        'hr.attendance', 'search_read',
        [[['employee_id', '=', employee_id]]], {'fields': ['id', 'check_in', 'check_out'], 'limit': 1})
    # print('Last Employee Attendance:', attendances)
    for attendance in attendances:
        if attendance['check_out'] == False:
            # print('Last Employee Attendance:', attendance['check_out'])
            models.execute_kw(db, uid, password, 'hr.attendance', 'write', [[attendance['id']], {
                'check_out': datetime_now
            }])
            return models.execute_kw(db, uid, password, 'hr.attendance', 'search_read',
                [[['id', '=', attendance['id']]]], {'fields': ['employee_id', 'check_out']})
        else:
            # print('Last Employee Attendance:', attendance['check_in'])
            id = models.execute_kw(db, uid, password, 'hr.attendance', 'create', [{
                'employee_id': employee_id, 'check_in': datetime_now
            }])
            return models.execute_kw(db, uid, password, 'hr.attendance', 'search_read',
                [[['id', '=', id]]], {'fields': ['employee_id', 'check_in']})
 
@app.route("/")
def index():
    return render_template("index.html")
 
@app.route("/", methods=['GET', 'POST'])
def index_post():
    if request.method == 'POST':
        if request.form.get('password'):
            get_pin = request.form.get('password')
            # print('get_pin', get_pin)
            return_pin = check_pin(get_pin)
            # print('return_pin', return_pin)
        else:
            return render_template('index.html')
        return render_template('index.html', user_status = return_pin)
if __name__ == '__main__':
    app.run()
