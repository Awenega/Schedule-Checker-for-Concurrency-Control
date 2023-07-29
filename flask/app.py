from flask import Flask, request, render_template

# Import functions from other files
from check2PL import solve2PL
from checkConflict import solveConflict
from checkTimestamps import solveTimestamps
from utils import parse_schedule

app = Flask(__name__, template_folder='static/templates')


@app.route('/', methods=['GET'])
def index():
    return render_template('solver.html')


@app.route('/instruction', methods=['GET'])
def instruction():
    return render_template('instruction.html')


@app.errorhandler(404)
def page_not_found(eror):
    return render_template('error.html')


@app.route('/solve', methods=['POST'])
def solve():
    # Get and check arguments from the request
    schedule = request.form.get('schedule')
    use_xl_only = request.form.get('use_xl_only')

    # Initialize the response with the cached HTML page
    response = "Must provide a schedule!"

    if schedule is None:
        return response

    # Remove any whitespaces from the schedule input
    schedule = schedule.replace(' ', '')

    if schedule == '':
        empty_schedule = '<br>' + 'Empty schedule!' + '<br>'
        return empty_schedule

    # Parse the input schedule to extract transactions and operations
    sched_parsed = parse_schedule(schedule)

    if type(sched_parsed) == str:  # Parsing error message
        errors_in_schedule = '<br>' + 'Parsing error: ' + sched_parsed + '<br>'
        return errors_in_schedule

    response = ''
    # Solve for conflict serializability, 2PL, and timestamps
    res_confl = solveConflict(sched_parsed)
    res_2pl = solve2PL(sched_parsed, use_xl_only)
    res_ts = solveTimestamps(sched_parsed)

    # Format results for conflict serializability
    msg = '<b><i>Conflict serializability</i></b><br>'
    msg += 'Is the schedule conflict serializable: <i>' + \
        str(res_confl) + '</i>'
    response += '<br>' + msg + '<br>'

    # Format results for 2PL
    msg = '<b><i>Two phase lock protocol</i></b><br>'
    if res_2pl['sol'] is None:
        msg += res_2pl['err']
        response += '<br>' + msg + '<br>'
    else:
        msg += """
        Solution: {} <br>
        Is the schedule strict-2PL: <i>{}</i> <br>
        Is the schedule strong strict-2PL: <i>{}</i>
        """.format(res_2pl['sol'], res_2pl['strict'], res_2pl['strong'])
        response += '<br>' + msg + '<br>'

    # Format results for timestamps
    msg = '<b><i>Timestamps (DRAFT)</i></b><br>'
    if res_ts['err'] is None:
        msg += 'List of executed operations: ' + str(res_ts['sol']) + '<br>'
        msg += 'List of waiting transactions at the end of schedule: ' + \
            str(res_ts['waiting_tx']) + '<br>'
        response += '<br>' + msg + '<br>'
    else:
        msg += res_ts['err'] + '<br>'
        response += '<br>' + msg + '<br>'

    return response


if __name__ == "__main__":
    from os.path import isfile

    debug = isfile('.DEBUG_MODE_ON')
    isEnableDebug = isfile('.DEBUG_MODE_ON')
    if isEnableDebug:
        app.debug = True  # Enable debug mode for auto-reloading

    app.run(port=5000, debug=debug)
