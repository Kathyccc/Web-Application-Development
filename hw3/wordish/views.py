from django.shortcuts import render
from django.shortcuts import redirect
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt


def home_page(request):
    # render takes: (1) the request,
    #               (2) the name of the view to generate, and
    #               (3) a dictionary of name-value pairs of data to be
    #                   available to the view.
    return render(request, 'wordish/start_page.html', {})

def valid_input(input_value):
    if len(input_value) != 5:
        return False
    for char in input_value:
        if char < 'a' or char > 'z':
            return False
    return True

def process_target(request):
    if request.method == "POST":
        target = request.POST['target']

        if valid_input(target):
            matrix = [[{} for _ in range(5)] for _ in range(6)]
            for i in range(6):
                for j in range(5):
                    cell = {
                        "id": f"cell_{i}_{j}",
                        "letter": '',
                        "color": 'cell'
                    }
                    matrix[i][j] = cell

            context = {
                'target': target,  
                'guess_count' : 0,
                'matrix' : matrix
            }
            return render(request, 'wordish/game_page.html', context)
        else:
            context = {
                'message': 'invalid input'
            }
            return render(request, 'wordish/start_page.html', context)
    else: 
        return redirect('wordish/start_page.html')

def guess_action(request):
    if request.method == "GET":
        context = {"message": "You're hacking.  Try again!"}
        return render(request, "wordish/start_page.html", context)
    
    try:
        target = _process_word_parameter(request.POST, "target")
        old_guesses = _process_old_guesses(request.POST)
    except Exception as e:
        return render(request, "wordish/start_page.html", {"message": f"Fatal error: {e}"})
    
    try:
        new_guess = _process_word_parameter(request.POST, "new-guess")
        context = _compute_game_context(target, ",".join(old_guesses + [new_guess]))
    except Exception as e:
        context = _compute_game_context(target,  ",".join(old_guesses))
        context["status"] = f"Invalid input: {e}"


    return render(request, "wordish/game_page.html", context)

def _compute_game_context(target, guesses):
    # Split the comma-separated 'guesses' string into a list
    guesses_list = guesses.split(",") if guesses else []

    matrix = [[{} for _ in range(5)] for _ in range(6)]

    for i in range(6):
        for j in range(5):
            cell = {
                "id": f"cell_{i}_{j}",
                "letter": '',
                "color": 'cell'
            }
            matrix[i][j] = cell

    for row, guess in enumerate(guesses_list):
        target_array = list(target)
        guess_array = list(guess)
        colors = []

        # Determine colors for each cell
        for i in range(5):
            if target_array[i] == guess_array[i]:
                target_array[i] = None
                colors.append('green')  
            else:
                colors.append(None)

        for i in range(5):
            if colors[i] is None and guess_array[i] in target_array:
                colors[i] = 'yellow'  
                index = target_array.index(guess_array[i])
                target_array[index] = None
            elif colors[i] is None:
                colors[i] = 'grey'
        
        # Populate the matrix
        for col in range(5):
            cell = {
                "id": f"cell_{row}_{col}",
                "letter": guess_array[col],
                "color": colors[col]
            }
            matrix[row][col] = cell

    # Determining the game status
    if len(guesses_list) > 0 and all(cell["color"] == 'green' for cell in matrix[len(guesses_list)-1]):
        status = "Win"
    elif len(guesses_list) >= 6:
        status = "Lose"
    else:
        status = "Ongoing"
    
    context = {
        "status": status,
        "matrix": matrix,
        "target": target,
        "guesses": ','.join(guesses_list),  
    }

    return context

def _process_old_guesses(post_data):
    old_guesses_str = post_data.get("guesses", "")
    old_guesses_list = old_guesses_str.split(",") if old_guesses_str else []

    if not old_guesses_str:
        return old_guesses_list
    else:
        for guess in old_guesses_list:
            if len(guess) != 5:
                raise ValueError(f"Invalid input")

    return old_guesses_list

def _process_word_parameter(request, word_type):
    word = request[word_type]

    if not word or len(word) != 5:
        raise ValueError('Invalid input')
    
    for char in word:
        if char < 'a' or char > 'z':
            raise ValueError('Invalid input')
    return word