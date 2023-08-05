from flask import Flask, jsonify, request, render_template

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
def page_not_found(error):
    return render_template('error.html')


@app.route('/solve', methods=['POST'])
def solve():
    # Get and check arguments from the request
    schedule = request.form.get('schedule')
    use_xl_only = request.form.get('use_xl_only')
    selected_possibilities = request.form.getlist('possibility')

    # Convert selected_possibilities to boolean values
    wantSolve = {
        'precedence_graph': 'precedence_graph' in selected_possibilities,
        'conflict_serializability': 'conflict_serializability' in selected_possibilities,
        '2pl_protocol': '2pl_protocol' in selected_possibilities,
        'timestamp': 'timestamp' in selected_possibilities
    }

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

    # Format results for conflict serializability
    msg = '<h4>Schedule provided: </h4><br>'
    msg += '<b>S: </b>' + schedule
    response += '<br>' + msg + '<br>'

    res_confl, precedence_graph = solveConflict(sched_parsed)
    if wantSolve['conflict_serializability']:
        # Format results for conflict serializability
        msg = '<h4>Conflict serializability:</i></h4><br>'
        msg += 'Is the schedule conflict serializable: <b>' + \
            str(res_confl) + '</b>'
        response += '<br>' + msg + '<br>'
    if not wantSolve['precedence_graph']:
        precedence_graph = None

    if wantSolve['2pl_protocol']:
        res_2pl = solve2PL(sched_parsed, use_xl_only)

        # Format results for 2PL
        msg = '<h4>Two phase lock protocol:</h4><br>'
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

    if wantSolve['timestamp']:
        res_ts = solveTimestamps(sched_parsed)
        # Format results for timestamps
        msg = '<h4>Timestamps (DRAFT):</h4><br>'
        if res_ts['err'] is None:
            msg += 'List of executed operations: ' + \
                str(res_ts['sol']) + '<br>'
            msg += 'List of waiting transactions at the end of schedule: ' + \
                str(res_ts['waiting_tx']) + '<br>'
            response += '<br>' + msg + '<br>'
        else:
            msg += res_ts['err'] + '<br>'
            response += '<br>' + msg + '<br>'

    response_solve = {
        'data': response,
        'precedence_graph': precedence_graph
    }

    return jsonify(response_solve)


if __name__ == "__main__":
    from os.path import isfile

    debug = isfile('.DEBUG_MODE_ON')
    isEnableDebug = isfile('.DEBUG_MODE_ON')
    if isEnableDebug:
        app.debug = True  # Enable debug mode for auto-reloading

    app.run(port=5000, debug=debug)
