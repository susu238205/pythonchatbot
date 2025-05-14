// UI

const sendbtn = document.getElementById("send-btn");
const userinput = document.getElementById("userinput");
const displaybox = document.getElementById("displaybox");
const clearhistory = document.getElementById("clear-history");

// // for localhost
// let ws = new WebSocket("ws://localhost:8000/image");

// for cloud server https deployment 

let websocketstring = '';

if(window.location.hostname === "localhost" || window.location.hostname === "127.0.0.1"){
    websocketstring = `ws://localhost:8000/image`; // local
}else{
    websocketstring = `${window.location.protocol === "https:" ? "wss" : "ws"}://${window.location.hostname}/image`; // https deployment
}

let ws = new WebSocket(websocketstring);


let lastmessagediv = null;
let isnewinput = true;

ws.onopen = function(){
    console.log("WebSocket connection established");
};

ws.onerror = function(err){
    console.log("WebSocket connection error:",err);
    document.getElementById("loading-spinner").style.display = "none";
};

ws.onclose = function(event){
    console.log("WebSocket connection closed:",event);
    document.getElementById("loading-spinner").style.display = "none";
};

ws.onmessage = function(event){


    let message = event.data;
    // console.log(event);
    // console.log(message);

    let img = document.createElement("img");
    img.src = message;
    img.className = "responseimg";
    displaybox.appendChild(img);

    savetolocal("ai-response",message); // to localstorage

    document.getElementById("loading-spinner").style.display = "none";

    
}

sendbtn.addEventListener("click", function (e) {
    e.preventDefault();
    
    let getinputval = userinput.value.trim();

    if(getinputval){
        
        let userinputdiv = document.createElement("div");
        userinputdiv.className = "p-3 ms-3 chat-message user-input";
        userinputdiv.textContent = getinputval;
        displaybox.appendChild(userinputdiv);

        ws.send(getinputval); // to websocket
        savetolocal("user-input",getinputval) // to localstorage

        userinput.value = "";
        userinput.focus();

        lastmessagediv = null;
        isnewinput = true;

        document.getElementById("loading-spinner").style.display = "block";

    }
});

window.onload = function(){

    const clearImageHistoryBtn = document.getElementById("clear-image-history");
    if (clearImageHistoryBtn) {
        clearImageHistoryBtn.addEventListener("click", () => {
            localStorage.removeItem("imghistory");
            displaybox.innerHTML = `<small class="text-muted">No image available.</small>`;
        });
    }
  
    let storagedatas = JSON.parse(localStorage.getItem("imghistory") || "[]" );


    if(storagedatas.length > 0){

        let currole = null;
        let curcontent = '';

        storagedatas.forEach((storagedata,idx)=>{

            if(storagedata.role === currole){
                curcontent += storagedata.content;
            }else{

                // console.log(currole); // undefined

                if(currole){   

                    if(currole === "user-input"){

                        let messagediv = document.createElement("div");
                        messagediv.className = "p-3 ms-3 chat-message "+ currole;
                        messagediv.textContent = curcontent;
                        displaybox.appendChild(messagediv);

                    }else if(currole === "ai-response"){

                        let img = document.createElement("img");
                        img.src = curcontent;
                        img.className = "responseimg";
                        displaybox.appendChild(img);
                    }
                    
                }

                // start new message
                currole = storagedata.role;
                curcontent = storagedata.content;

                // console.log(currole); // user-input, api-response

            }

            // console.log(curcontent);

            if(idx === storagedatas.length -1){
                let img = document.createElement("img");
                img.src = curcontent;
                img.className = "responseimg";
                displaybox.appendChild(img);
            }

        });

    }else{
        displaybox.innerHTML = `<small class="text-muted">No image available.</small>`;
    }
};


function savetolocal(role,content){
    let getdatas = JSON.parse(localStorage.getItem("imghistory") || "[]" );
    getdatas.push({role:role,content:content});
    localStorage.setItem("imghistory", JSON.stringify(getdatas));
}



document.addEventListener("DOMContentLoaded", function () {
    const clearImageHistoryBtn = document.getElementById("clear-image-history");
    if (clearImageHistoryBtn) {
        clearImageHistoryBtn.addEventListener("click", () => {
            localStorage.removeItem("imagehistory");
            displaybox.innerHTML = `<small class="text-muted">No image available.</small>`;
        });
    }

    const clearhistory = document.getElementById("clear-history");
    if (clearhistory) {
        clearhistory.addEventListener("click", function () {
            localStorage.removeItem("imghistory");
            location.reload();
        });
    }
});