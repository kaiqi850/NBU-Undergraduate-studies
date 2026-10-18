function getSystemTime() {
    var date = new Date();
    var hours = date.getHours();
    var minutes = date.getMinutes();
    var seconds = date.getSeconds();
    var formattedTime = addZero(hours) + ":" + addZero(minutes) + ":" + addZero(seconds);
    return formattedTime;
}

function addZero(number) {
    if (number < 10) {
        return "0" + number;
    }
    return number;
}

function updateSystemTime() {
    var systemTimeElement = document.getElementById("system-time");
    if (systemTimeElement) {
        systemTimeElement.innerHTML = getSystemTime();
    }
}

setInterval(updateSystemTime, 1000);
