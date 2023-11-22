let target = ""
let guess_count = 0

function processGuess() {
    let input = document.getElementById("guess_text").value

    if(!validInput(input))
        return

    guess_count++
    document.getElementById("status").innerHTML = "Successful input"
    let targetArray = target.split("")
    let guessArray = input.split("")
    let colors = new Array()

    // Do the greens first
    for(let i = 0; i < 5; i++) {
        if(targetArray[i] == guessArray[i]) {
            targetArray[i] = null
            colors[i] = 'rgb(84, 162, 42)'
        } 
    }

    // Do the yellows
    for(let i = 0; i < 5; i++) {
        if(colors[i] !== 'rgb(84, 162, 42)' && targetArray.includes(guessArray[i])) {
            let index = targetArray.indexOf(guessArray[i])
            targetArray[index] = null
            colors[i] = 'rgba(198, 188, 44, 0.876)'
        } else if (colors[i] !== 'rgb(84, 162, 42)' && colors[i] !== 'rgba(198, 188, 44, 0.876)') {
            colors[i] = "grey"
        }
    }

    // Set the colors on the cells
    for(let i = 0; i < 5; i++) {
        let cell = document.getElementById(`cell_${guess_count - 1}_${i}`)
        cell.innerHTML = guessArray[i]
        cell.style.backgroundColor = colors[i]
    }    
    
    // Win or lose
    if (colors.every(color => color === 'rgb(84, 162, 42)')) {
        document.getElementById("status").innerHTML = "Win"
        
    } else if (guess_count === 6) {
        document.getElementById("status").innerHTML = "Lose"
    }

}

function startGame(){
    let input = document.getElementById("target_text").value

    if(!validInput(input))
        return

    guess_count = 0
    target = input
    clearMatrix()
    document.getElementById("status").innerHTML = "Start"           
}

function clearMatrix() {
    const cells = document.querySelectorAll('.cell')

    // Iterate through each cell to reset it
    for (const cell of cells) {
        cell.textContent = ''
        cell.style.backgroundColor = 'rgb(191, 191, 191)'
    }
}

function validInput(input) {
    if(input.length != 5) {
        document.getElementById("status").innerHTML = "Invalid input"
        return false
    } 
    
    for(let i = 0; i < 5; i++) {
        if(input[i] < 'a' || input[i] > 'z') {
            document.getElementById("status").innerHTML = "Invalid input"
            return false
        }
    }

    return true
}
