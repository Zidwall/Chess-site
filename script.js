document.querySelectorAll(".tab").forEach(tab => {
    tab.addEventListener("click", () => {
        location.href = tab.getAttribute("data-href");
    })
})
document.querySelector("#btn_menu").addEventListener("click", () => {
    if (document.querySelector("#menu").hidden == true) {
        document.querySelector("#menu").hidden = false;
    }
    else {
        document.querySelector("#menu").hidden = true;
    } 
})

if (location.pathname == "/") {
    function leave() {
        fetch("/", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "action": "leave_game",
                "game_id": game_id, 
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.code == 200) {
                location.reload()
            }
        })
    }


    document.querySelector("#leave_game").addEventListener("click", leave);
    window.addEventListener("beforeunload", () => {
        leave
    });

    let game_id = 0;
    let game = false;
    let board1;
    let white_id = 0;
    let black_id = 0;
    document.addEventListener("DOMContentLoaded", () => {
        board1 = Chessboard('board1', {
            position: 'start',
            pieceTheme: '/static/img/chesspieces/wikipedia/{piece}.png',
            draggable: true,
            dropOffBoard: 'snapback',
            onDrop: function(source, target, piece, newPos, oldPos, orientation) {
                //console.log(source, target, piece, newPos, oldPos, orientation);
                return fetch("/", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        "action": "move",
                        "target": target,
                        "source": source,
                        "piece": piece,
                        "orientation": orientation,
                        "oldPos": oldPos,
                        "newPos": newPos,
                        "game_id": game_id,
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.code != 200) {
                        board1.position(oldPos);
                    }
                    else {
                        console.log(typeof(board1.position()))
                        console.log(typeof(oldPos))
                        if (board1.position() != oldPos) {
                            fetch("/", {
                            method: "POST",
                            headers: {"Content-Type": "application/json"},
                            body: JSON.stringify({
                                "action": "change_turn",
                                "orientation": orientation,
                                "game_id": game_id,
                            })
                        })
                        }
                    }

                })
            }
        })   
    })
    function game_launched() {
        if (game == true) {
            setInterval(() => {
                fetch("/time", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                        "game_id": game_id,
                        "white_id": white_id,
                        "black_id": black_id,
                    })
                })
                .then(response => response.json())
                .then(data => {
                    document.querySelector("#white_clock").textContent = data.white_time;
                    document.querySelector("#black_clock").textContent = data.black_time;
                })
            }, 1000);
            setInterval(() => {
                fetch("/position", {
                    method: "POST",
                    headers: {"Content-Type": "application/json"},
                    body: JSON.stringify({
                    "game_id": game_id,
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.code == 200) {
                        board1.position(data.position);
                    }
                    else if (data.code == 300) {
                        location.reload();
                    }
                })
            }, 700)
        }
    }

    function intervalle() {        
        const intervalle_state = setInterval(() => {
            fetch("/", {
                method: "POST",
                headers: {"Content-Type": "application/json"},
                body: JSON.stringify({
                    "action": "check_game",
                    "game_id": game_id,
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.code == 200) {
                    game = true;
                    black_id = data.black_id;
                    white_id = data.white_id;
                    clearInterval(intervalle_state);
                    game_launched();
                }
            })
        }, 500)
    }

    document.querySelector("#startGame").addEventListener("click", () => {
        fetch("/", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                "action": "start",
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.color == "black") {
                board1.flip()
            }
            if (data.code == 200) {
                document.querySelector("#startGame").hidden = true;
                game_id = data.game_id;
                black_id = data.black_id;
                white_id = data.white_id;
                game = true;
                game_launched();
            }
            else if (data.code == 300) {
                fetch("/", {
                method: "POST",
                headers: {"Content-type": "application/json"},
                body: JSON.stringify({
                    "action": "create_game",
                    "position": board1.position,
                    })
                })
                .then(response => response.json())
                .then(data => {
                    game_id = data.game_id;
                    intervalle();
                })
            }
        })
    })

    document.querySelector("#startBtn").addEventListener("click", () => {
        board1.start();
    });
    document.querySelector("#clearBtn").addEventListener("click", () => {
        board1.clear();
    });
}

if (location.pathname == "/profile") {
    document.querySelector("#loggingOut").addEventListener("click", () => {
        fetch("/logging_out")
        .then(response => response.json())
        .then(data => {
            if (data.code == 200) {
                window.location.reload();
            }
        })
    })
}

if (location.pathname == "/infos_players") {
    const list_caracts = ["name", "federation", "year", "title", "blitz", "rapid", "standard"]
    document.querySelector("#submit").addEventListener("click", () => {
        document.querySelector("#caracts").replaceChildren();
        let name = document.querySelector("#name").value;
        fetch("/infos_players", {
                method: "POST",
                headers: {"Content-type": "application/json"},
                body: JSON.stringify({
                    "action": "get_infos",
                    "name": name,
                })
        })
        .then(response => response.json())
        .then(data => {
            let player = data[0];
            let caracts = document.querySelector("#caracts");
            for (i=0; i<list_caracts.length; i++) {
                let caract = caracts.appendChild(document.createElement("li"));
                let element = caract.appendChild(document.createElement("p"));
                element.style.color = "white";
                element.textContent = `${list_caracts[i]} : ${player[list_caracts[i]]}`;
            }  
        })
        
    })
}
