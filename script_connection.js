let username;

if (location.pathname == "/login") {
    let button = document.querySelector("#btn");
    document.querySelectorAll(".field").forEach(input => {
        input.addEventListener("input", () => {
            if (input.value == "") {
                button.disabled = true;
            }
            else {
                button.disabled = false;
            }
        })
        })
    
    button.addEventListener("click", () => {
        username = document.querySelector("#username").value;
        fetch("/mdp", {method: "GET"})
        .then(response => response.text())
        .then(code => {
            document.body.innerHTML = code;
            lucide.createIcons();
            
            document.querySelector("#back_btn").addEventListener("click", () => {
                location.reload();
            });

            document.querySelector("#btn").addEventListener("click", () => {    
                fetch("/login", {
                    method: "POST",
                    headers: {"Content-type": "application/json"},
                    body: JSON.stringify({
                        "action": "logging in",
                        "username": username,
                        "password": document.querySelector("#password").value,
                    })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.code == 200) {
                        location.href = data.url;
                    }
                    else {
                        message = document.querySelector("#message");
                        message.textContent = data.display;
                        message.style.color = data.color;
                        message.hidden = false; 
                    }
                })
            })
        })
    })
}

if (location.pathname == "/register") {
    document.querySelector("#btn").addEventListener("click", () => {
        
        fetch("/register", {
            method: "POST",
            headers: {"Content-type": "application/json"},
            body: JSON.stringify({
                "action": "inscription",
                "username": document.querySelector("#username").value,
                "password": document.querySelector("#password").value,
                "confirmation": document.querySelector("#confirmation").value,
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.code == 200) {
                location.href = data.redirect;
            }
            else {
                message = document.querySelector("#message");
                message.hidden = false;
                message.textContent = data.display;
                document.querySelector(`#${data.field}`).style.backgroundColor = "tomato";
            }
        })
    })
}