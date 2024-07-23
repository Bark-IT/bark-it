var menu = false;
var enabledtab = window.location.hash.replace("#","");
if (enabledtab == "") {
    enabledtab = "home";
}
const tabs = ["home","friends","search","videos","images","pages","create","profile","settings","help","theme","login","videoplayer","imageplayer","pageloader","regerror","logerror","code","codeerror","setup","codepass","nameerror"]
const menus = ["","profilemenu","notificationmenu"];
var intervalId = setInterval(update, 5000);

var socket = io.connect('http://' + document.domain + ':' + location.port);


let usrname = ""
function PlayVideo(ID,title,views,publisher) {
    document.getElementById("videosource").src = "/video/"+ID
    document.getElementById("videotitle").innerText = title + " - "+views+" views"
    
    SwitchTab("videoplayer");
    document.getElementById('videoplaying').load();
    document.getElementById('videoplaying').play();
    ReloadTabs();
    socket.emit('message', '{"packet":"updateviewcount", "id":"'+ID+'"}');
}


socket.on('message', function(data) {
    console.log(data);
    var packet = JSON.parse(data);
    
    switch (packet["packet"]) {
        case "video":
            document.getElementById("videos").innerHTML += '<div onclick="PlayVideo(\''+packet["id"]+'\',\''+packet["name"]+'\',\''+packet["views"]+'\',\''+packet["publisher"]+'\');" class="videopreview"><center><img src="/videothumbnail/'+ packet["id"]+'" style="height: 30%; width: 100%;"><p>'+packet["name"]+'</p><h6>'+packet["publisher"]+' - '+packet["views"]+' views</h6></center></div>'
        break;
        
        case "name":
            document.getElementById("namebar").textContent = packet["name"]
            usrname = packet["name"]
            document.getElementById("vidusr").innerText = usrname+" - 69 views"
        break;
        
        case "namecheck":
            console.log(packet["value"])
            if (packet["value"] == "True") {
                document.getElementById("namecheckbox").textContent = "This name is taken"
                document.getElementById("usernamebox").style.color = "red"
                document.getElementById("namecheckbutton").disabled = true
            } else {
                document.getElementById("namecheckbox").textContent = "This name is not taken"
                document.getElementById("usernamebox").style.color = "green"
                document.getElementById("namecheckbutton").disabled = false
            }
        break;
    }
    
});

function update() {
    socket.emit('message', '{"packet":"tick"}');
}



document.addEventListener("DOMContentLoaded", function(){
    ReloadTabs();
    socket.emit('message', '{"packet":"name"}');
    var usernamebox = document.getElementById('usernamebox');
    usernamebox.addEventListener('input', function() {
        usernamebox.value = usernamebox.value.replaceAll(" ","_")
        socket.emit('message', '{"packet":"namecheck","name":"'+usernamebox.value+'"}');
    });
    var vidnamebox = document.getElementById('vidnamebox');
    vidnamebox.addEventListener('input', function() {
        document.getElementById("vidname").innerText = vidnamebox.value
    });

    document.getElementById("registerLoginForm").addEventListener("submit", function(event) {
    
        if (event.submitter && event.submitter.name === "register") {
            this.action = "/register";
        } else if (event.submitter && event.submitter.name === "login") {
            this.action = "/login";
        }
        if (!actionURL) {
            this.action = "/login";
        }
    });
    var divElement = document.getElementById('videos');

    divElement.onscroll = function() {
        if (divElement.scrollHeight - divElement.scrollTop === divElement.clientHeight) {
            for (var i=0;i<50;i++) {
                socket.emit('message', '{"packet":"getalgorithmvideo"}');
            }
        }
    };

    const input = document.getElementById('thumbnailupload');
	const preview = document.getElementById('thumbnaildisplay');
	input.addEventListener('change', function() {
	  if (input.files && input.files[0]) {
		const reader = new FileReader()
		reader.onload = function(e) {
		  preview.src = e.target.result
		}
		reader.readAsDataURL(input.files[0]);
	  }
	});
    
});


function ReloadTabs() {
    const params = new URLSearchParams(window.location.search)
    const error = params.get('error');
    try {
        document.getElementById(enabledtab+"msg").textContent = error
    } catch (error) {
        
    }
    
    for (let i=0;i<tabs.length;i++) {
        document.getElementById(tabs[i]).style.display = enabledtab == tabs[i] ? "block" : "none";
    }
    if (enabledtab == "videos") {

        for (var i=0;i<50;i++) {
            socket.emit('message', '{"packet":"getalgorithmvideo"}');
        }
    } else {
        document.getElementById("videos").innerHTML = "<h1>Videos</h1>"
    }
}

function SwitchTab(tab) {
    document.getElementById('videoplaying').pause();
    oldtab = enabledtab;
    document.getElementById(enabledtab).style.display = "none"
    enabledtab = tab;
    document.getElementById(enabledtab).style.display = "block"
    window.location.hash = tab
    if (enabledtab == "videos") {

        for (var i=0;i<50;i++) {
            socket.emit('message', '{"packet":"getalgorithmvideo"}');
        }
    } else {
        document.getElementById("videos").innerHTML = "<h1>Videos</h1>"
    }
}

function HideMenus() {
    for (let i=0;i<menus.length;i++) {
        try {
            document.getElementById(menus[i]).style.display = "none";
        } catch (error) {}
        
    }
}


function ToggleProfileMenu() {
    HideMenus();
    menu = !menu;
    document.getElementById("profilemenu").style.display = menu ? "block" : "none";
}

function ToggleNoficationMenu() {
    HideMenus();
    menu = !menu;
    document.getElementById("notificationmenu").style.display = menu ? "block" : "none";
}