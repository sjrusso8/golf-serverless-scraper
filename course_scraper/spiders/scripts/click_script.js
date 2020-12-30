// var v = [];

// ((() => {
//     const origOpen = XMLHttpRequest.prototype.open;
//     XMLHttpRequest.prototype.open = function () {
//         this.addEventListener('load', function () {
//             console.log('request completed!');
//             console.log(this.readyState); //will always be 4 (ajax is completed successfully)
//             v = [...v, ...JSON.parse(this.responseText)];
//             console.log(this.responseText);
//         });
//         origOpen.apply(this, arguments);
//     };
// }))();



let waitLoad = () => {
    return new Promise(resolve => {
        requestAnimationFrame(resolve);
    });
}

let checkElement = (selector) => {
    if (document.querySelector(selector) === null) {
        return waitLoad().then(() => checkElement(selector));
    } else {
        return Promise.resolve(true);
    };
}


let loadContent = () => {
    checkElement(".load-more-options")
        .then((element) => {
            console.log(element)
            document.querySelector(".load-more-options").click();
        })
}

let searchKeyup = (text, input) => {
    let element = document.querySelector(input)
    let keyboardEvent = document.createEvent("KeyboardEvent");
    let initMethod = typeof keyboardEvent.initKeyboardEvent !== 'undefined' ? "initKeyboardEvent" : "initKeyEvent";

    keyboardEvent[initMethod](
        "keyup", // event type: keydown, keyup, keypress
        true,      // bubbles
        true,      // cancelable
        window,    // view: should be window
        false,     // ctrlKey
        false,     // altKey
        false,     // shiftKey
        false,     // metaKey
        40,        // keyCode: unsigned long - the virtual key code, else 0
        0          // charCode: unsigned long - the Unicode character associated with the depressed key, else 0
    );

    element.value = text;

    element.dispatchEvent(keyboardEvent);

}


var loadinterval = window.setInterval(loadContent, 2000)

// searchKeyup("TPC", "#courseFinderHeader")