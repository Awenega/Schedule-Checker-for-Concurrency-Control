from flask import Flask, jsonify, request, render_template

# Import functions from other files
from SolverForViewSerializability import SolveViewSerializability
from SolverFor2PL import solve2PL
from SolverForConflictSerializability import SolveConflictSerializability
from SolverForTimestamps import solveTimestamps
from SolverForRecoverable import SolveRecoverability
from SolverForRigorous import SolveRigorousness
from SolverForACR import SolveACR
from SolverForStrict import SolveStrict
from SolverForOCSR import solveOCSR
from Scheduler import parseTheSchedule
from ComputePG import ComputePrecedenceGraph

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
        'timestamp': 'timestamp' in selected_possibilities,
        'view_serializability': 'view_serializability' in selected_possibilities,
        'recoverability': 'recoverability' in selected_possibilities,
        'acr': 'acr' in selected_possibilities,
        'strict': 'strict' in selected_possibilities,
        'rigorousness': 'rigorousness' in selected_possibilities,
        'ocsr': 'ocsr' in selected_possibilities
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
    sched_parsed = parseTheSchedule(schedule)
    print(sched_parsed)

    if type(sched_parsed) == str:  # Parsing error message
        errors_in_schedule = '<br>' + 'Parsing error: ' + sched_parsed + '<br>'
        return errors_in_schedule

    response = ''
    precedence_graph = None
    # Format results for conflict serializability
    msg = '<h4>Schedule provided: </h4><br>'
    msg += '<b>S: </b>' + schedule
    response += '<br>' + msg + '<br>'

    if wantSolve['view_serializability']:
        res_view, res_equiv = SolveViewSerializability(sched_parsed)
        msg = '<h4>View Serializability:</i></h4><br>'
        msg += 'Is the schedule view serializable: <b>' + \
            str(res_view) + '</b>'
        if res_equiv != None:
            msg += ', is view equivalent to this serial schedule: ' + res_equiv + '<br>'
        response += '<br>' + msg + '<br>'

    if wantSolve['conflict_serializability']:
        res_confl = SolveConflictSerializability(sched_parsed)
        msg = '<h4>Conflict serializability:</i></h4><br>'
        msg += 'Is the schedule conflict serializable: <b>' + \
            str(res_confl) + '</b>'
        response += '<br>' + msg + '<br>'
    if wantSolve['precedence_graph']:
        precedence_graph = ComputePrecedenceGraph(sched_parsed)

    if wantSolve['recoverability']:
        res_rec, conflict_pair = SolveRecoverability(sched_parsed)
        msg = '<h4>Recoverability:</i></h4><br>'
        msg += 'Is the schedule recoverable: <b>' + \
            str(res_rec) + '</b>'
        if conflict_pair != None:
            msg += ', because transaction T' + \
                conflict_pair[0] + ' commit before transaction T' + \
                conflict_pair[1] + '.<br>'
        response += '<br>' + msg + '<br>'

    if wantSolve['acr']:
        res_acr, conflict_pair = SolveACR(sched_parsed)
        msg = '<h4>ACR:</i></h4><br>'
        msg += 'Is the schedule ACR: <b>' + \
            str(res_acr) + '</b>'
        if conflict_pair != None:
            msg += ', because transaction T' + \
                conflict_pair[0] + ' read from transaction T' + \
                conflict_pair[1] + ' that not have commited.<br>'
        response += '<br>' + msg + '<br>'

    if wantSolve['strict']:
        res_strict = SolveStrict(sched_parsed)
        msg = '<h4>Strict:</i></h4><br>'
        msg += 'Is the schedule Strict: <b>' + \
            str(res_strict) + '</b>'
        response += '<br>' + msg + '<br>'
        # TO-DO: aggiungere motivazione

    if wantSolve['2pl_protocol']:
        solved_schedule, is_strict, is_strong_strict = solve2PL(sched_parsed, use_xl_only)
        if is_strict is None or is_strong_strict is None:
            response += '<br><h4>2PL:</h4>' + solved_schedule + '<br>'
        else:
            response += f'<br><h4>2PL:</h4>Solution: {solved_schedule} <br><br>Strict-2PL: <i><strong>{is_strict}</strong></i> <br>Strong-Strict-2PL: <i><strong>{is_strong_strict}</strong></i><br>'

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

    if wantSolve['rigorousness']:
        res_rig = SolveRigorousness(sched_parsed)
        msg = '<h4>Rigorousness:</i></h4><br>'
        msg += 'Is the schedule rigorous: <b>' + \
            str(res_rig) + '</b>'
        response += '<br>' + msg + '<br>'
        # TO-DO: aggiungere motivazione
    
    if wantSolve['ocsr']:
        res_ocsr, motivation = solveOCSR(sched_parsed)
        msg = '<h4>OCSR:</i></h4>'
        msg += f'Is the schedule OCSR: <b><strong>{res_ocsr}</strong></b> {motivation}'
        response += '<br>' + msg + '<br>'
        # TO-DO: aggiungere motivazione

    response_solve = {
        'data': response,
        'precedence_graph': precedence_graph
    }

    return jsonify(response_solve)


if __name__ == "__main__":
    from os.path import isfile

    isEnableDebug = isfile('.DEBUG_MODE_ON')
    if isEnableDebug:
        app.debug = True  # Enable debug mode for auto-reloading

    app.run(port=5000, debug=isEnableDebug)
